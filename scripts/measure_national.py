"""Measure existing national evaluator owners using explicit retained artifacts.

This script acquires nothing and creates no synthetic identities or prices.
Without --display-geography this is economic-only evidence. With it, the script
measures backend composition/session/projection/serialization, not browser rendering.
"""

import argparse
import gc
import json
import platform
import resource
import statistics
import time
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

from spain_housing.application.overview import detail_run, evaluate_overview
from spain_housing.config import load_scenario
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.scenario import Scenario


def measure(release: Path, geography: Path, scenario: Scenario) -> dict[str, Any]:
    started = time.perf_counter()
    repo = SnapshotMarketRepository.from_release(
        release, allow_synthetic=True, geography_dir=geography
    )
    load_s = time.perf_counter() - started
    context = repo.evaluation_context
    destinations = tuple(row.location for row in context.locations)
    baseline_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    times = []
    # One warm-up and three measured runs, retaining two applied overviews at most.
    previous = None
    for index in range(4):
        started = time.perf_counter()
        current = evaluate_overview(
            scenario, market_data=repo, context=context, mapped_locations=destinations
        )
        elapsed = time.perf_counter() - started
        if index:
            times.append(elapsed)
        previous = current
        gc.collect()
    assert previous is not None
    detail_times = []
    for code in (
        destinations[0].code,
        destinations[len(destinations) // 2].code,
        destinations[-1].code,
    ):
        started = time.perf_counter()
        detail_run(previous, code, market_data=repo, context=context)
        detail_times.append(time.perf_counter() - started)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return dict(
        platform=platform.platform(),
        locations=len(destinations),
        months=scenario.saving_months,
        release=context.release_id,
        code=previous.code_version,
        runtime=previous.runtime_evidence.model_dump(mode="json"),
        load_s=load_s,
        warmups=1,
        samples_s=times,
        median_s=statistics.median(times),
        detail_samples_s=detail_times,
        baseline_peak_KiB=baseline_peak,
        maxrss_KiB=peak,
        incremental_peak_KiB=peak - baseline_peak,
        scope="economic overview and selected detail; display/browser not measured",
        memory_method="Linux process peak; two overviews retained, no full export",
    )


def measure_map(
    release: Path,
    geography: Path,
    display: Path,
    defaults: Path,
    scenario_path: Path,
) -> dict[str, Any]:
    """Exercise public application/session/render owners, with no browser claims."""
    from spain_housing.launcher import compose
    from spain_housing.ui.controls import scenario_draft
    from spain_housing.ui.map import decorate, render_map, viewport
    from spain_housing.ui.presentation import Metric
    from spain_housing.ui.state import Session

    started = time.perf_counter()
    scenario, services = compose(
        defaults,
        scenario_path,
        release,
        allow_synthetic=True,
        geography_dir=geography,
        display_geography=display,
        reload=True,
    )
    cold_load_s = time.perf_counter() - started
    assert services.map_geography is not None
    gc.collect()
    baseline_rss = next(
        int(line.split()[1])
        for line in Path("/proc/self/status").read_text().splitlines()
        if line.startswith("VmRSS:")
    )
    baseline_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    samples: dict[str, list[float]] = {}

    def sample(label: str, action: Any) -> Any:
        result = None
        durations = []
        for index in range(4):
            started = time.perf_counter()
            result = action()
            duration = time.perf_counter() - started
            gc.collect()
            if index:
                durations.append(duration)
        samples[label] = durations
        return result

    calls = 0

    def counted(value: Any, destinations: Any) -> Any:
        nonlocal calls
        calls += 1
        return services.evaluate(value, destinations)

    injected = replace(services, evaluate=counted)
    session = Session(scenario_draft(scenario))
    assert session.apply(session.draft, injected)
    sample("equal_apply_s", lambda: session.apply(session.draft, injected))
    assert calls == 1
    view = dict(longitude=-3.5, latitude=40.0, zoom=4.5)

    def project(metric: Metric) -> Any:
        return decorate(
            session.applied,
            services.context,
            services.boundaries,
            metric,
            geography=services.map_geography,
            market_geography=services.coverage.geography,
            destinations=services.destinations,
            share_immutable_coordinates=True,
        )

    def encode(features: Any, metric: Metric) -> int:
        outlines = [f.model_dump(mode="json") for f in services.map_geography.provinces.features]
        # Capture the actual deck owner at its public Streamlit output boundary.
        with (
            patch("spain_housing.ui.map.st.markdown"),
            patch("spain_housing.ui.map.st.caption"),
            patch(
                "spain_housing.ui.map.st.pydeck_chart",
                side_effect=lambda deck, **kw: len(deck.to_json().encode()),
            ),
        ):
            size = render_map(features, metric, view, outlines=outlines)
            assert isinstance(size, int)
            return size

    def applied() -> int:
        nonlocal calls
        value = scenario.model_copy(
            update={"retained_reserve_eur": scenario.retained_reserve_eur + calls}
        )
        assert session.apply(scenario_draft(value), injected)
        return encode(project(Metric.RATIO), Metric.RATIO)

    serialized_bytes = sample("warm_changed_apply_through_serialization_s", applied)
    before = calls
    for metric in Metric:
        sample(
            "metric_" + metric.name.lower() + "_project_encode_s",
            lambda metric=metric: encode(project(metric), metric),
        )
    sample("view_bounds_s", lambda: viewport(project(Metric.RATIO)))
    assert calls == before
    details = []
    for code in ("28079", "07040", "35016", "51001", "52001"):
        if code in {d.code for d in services.destinations}:
            started = time.perf_counter()
            session.detail(injected, code)
            details.append(dict(code=code, seconds=time.perf_counter() - started))
    assert len(session.memo) <= 2 and len(session.details) <= 2

    def export() -> int:
        session.full_export = None
        session.prepare_export(injected)
        return len(session.full_export or b"")

    export_bytes = sample("full_export_preparation_s", export)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return dict(
        scope="Backend session, projection and actual PyDeck serialization; no browser timing",
        code=services.code_version,
        runtime=services.runtime.model_dump(mode="json"),
        release=services.context.release_id,
        display=services.map_geography.display_id,
        locations=len(services.destinations),
        months=scenario.saving_months,
        cold_compose_s=cold_load_s,
        warmups=1,
        samples_s=samples,
        medians_s={key: statistics.median(values) for key, values in samples.items()},
        serialized_deck_bytes=serialized_bytes,
        full_export_bytes=export_bytes,
        baseline_peak_KiB=baseline_peak,
        maxrss_KiB=peak,
        incremental_peak_KiB=peak - baseline_peak,
        details=details,
        presentation_evaluator_calls=calls - before,
        baseline_current_rss_KiB=baseline_rss,
        incremental_peak_upper_bound_KiB=peak - baseline_rss,
        memo_entries=len(session.memo),
        detail_entries=len(session.details),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("release", "geography", "defaults", "scenario", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--display-geography", type=Path)
    args = parser.parse_args()
    result = (
        measure_map(
            args.release, args.geography, args.display_geography, args.defaults, args.scenario
        )
        if args.display_geography
        else measure(args.release, args.geography, load_scenario(args.defaults, args.scenario))
    )
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
