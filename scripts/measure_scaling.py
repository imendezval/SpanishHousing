"""Measure synthetic pipeline owners; timings never enter economic identities."""

import argparse
import json
import platform
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from fixtures.synthetic.expand import PILOT, prepare_fixture  # noqa: E402
from spain_housing.config import load_mapping  # noqa: E402
from spain_housing.ingestion.release import build_release  # noqa: E402
from spain_housing.launcher import _snapshot, compose  # noqa: E402
from spain_housing.markets.coverage import coverage_report  # noqa: E402
from spain_housing.markets.repository import SnapshotMarketRepository  # noqa: E402
from spain_housing.models.dataset import BuildRecipe  # noqa: E402
from spain_housing.models.scenario import Scenario  # noqa: E402
from spain_housing.storage.release import load_release  # noqa: E402
from spain_housing.ui.controls import scenario_draft  # noqa: E402
from spain_housing.ui.map import decorate  # noqa: E402
from spain_housing.ui.presentation import Metric  # noqa: E402
from spain_housing.ui.state import Session  # noqa: E402


def measure_case(size: int, work_root: Path, sample_count: int) -> dict[str, Any]:
    inputs = PILOT if size == 4 else work_root / f"inputs-{size}"
    recipe = (
        BuildRecipe.model_validate(load_mapping(PILOT / "recipe.json"))
        if size == 4
        else prepare_fixture(inputs, size)
    )
    release = build_release(
        recipe, data_root=inputs, release_root=work_root / "releases", allow_synthetic=True
    )
    timings: dict[str, float] = {}

    def measure(label: str, action: Any) -> Any:
        samples = []
        value = None
        for _ in range(sample_count):
            start = time.perf_counter()
            value = action()
            samples.append((time.perf_counter() - start) * 1000)
        timings[label] = statistics.median(samples)
        return value

    repo = measure(
        "validate_index_ms",
        lambda: SnapshotMarketRepository.from_release(release, allow_synthetic=True),
    )
    initial, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release,
        allow_synthetic=True,
    )
    data = initial.model_dump(mode="json")
    if size == 250:
        data["saving_months"] = 84
        data["living_stages"][0]["end_month_offset"] = 84
    scenario = Scenario.model_validate(data)
    run = measure("evaluate_ms", lambda: services.evaluate(scenario, services.destinations))
    bundle = load_release(release, allow_synthetic=True)
    measure(
        "report_ms",
        lambda: coverage_report(
            bundle.manifest, bundle.locations, bundle.coverage, bundle.observations
        ),
    )
    measure(
        "map_prepare_ms",
        lambda: decorate(run, services.context, services.boundaries, Metric.PRICE),
    )
    calls = []

    def counted(value: Scenario, locations: Any) -> Any:
        calls.append(value)
        return services.evaluate(value, locations)

    injected = replace(services, evaluate=counted)
    session = Session(scenario_draft(scenario))
    assert session.apply(session.draft, injected)
    measure("memo_hit_ms", lambda: session.apply(session.draft, injected))
    assert len(calls) == 1
    for metric in Metric:
        decorate(session.applied, services.context, services.boundaries, metric)
    assert len(calls) == 1
    changed = scenario.model_copy(
        update={"retained_reserve_eur": scenario.retained_reserve_eur + 1}
    )
    start = time.perf_counter()
    assert session.apply(scenario_draft(changed), injected)
    timings["changed_apply_ms"] = (time.perf_counter() - start) * 1000
    assert len(calls) == 2
    _snapshot.cache_clear()
    with patch(
        "spain_housing.launcher.SnapshotMarketRepository.from_release",
        wraps=SnapshotMarketRepository.from_release,
    ) as opens:
        for _ in range(2):
            compose(
                ROOT / "configs/defaults.yaml",
                ROOT / "configs/scenarios/phase4_room_demo.yaml",
                release,
                allow_synthetic=True,
            )
        assert opens.call_count == 1
    vertices = 0

    def visit(value: Any) -> None:
        nonlocal vertices
        if isinstance(value, (list, tuple)):
            if len(value) == 2 and all(isinstance(v, (float, int)) for v in value):
                vertices += 1
            else:
                for child in value:
                    visit(child)

    for feature in repo.boundaries.features:
        visit(feature.geometry.coordinates)
    return dict(
        locations=size,
        profiles=len(recipe.profiles),
        observations=repo.coverage_report.counts.available,
        saving_months=scenario.saving_months,
        vertices=vertices,
        geometry_bytes=(release / "boundaries.geojson").stat().st_size,
        release_id=repo.manifest.release_id,
        code=run.code_version,
        runtime=run.runtime_evidence.model_dump(mode="json"),
        evaluator_calls=dict(
            first=1, equal_additional=0, presentation_additional=0, changed_additional=1
        ),
        cached_validation_calls=1,
        median_ms=timings,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    if args.samples < 3:
        parser.error("at least three samples required")
    results = [measure_case(size, args.work_root, args.samples) for size in (4, 16, 250)]
    print(
        json.dumps(
            dict(
                platform=platform.platform(),
                cpu=platform.processor(),
                samples=args.samples,
                synthetic=True,
                cases=results,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
