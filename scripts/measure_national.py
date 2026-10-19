"""Measure existing national evaluator owners using explicit retained artifacts.

This script acquires nothing and creates no synthetic identities or prices.
This is economic-only evidence, not national render verification.
"""

import argparse
import gc
import json
import platform
import resource
import statistics
import time
from pathlib import Path
from typing import Any

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("release", "geography", "defaults", "scenario", "output"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    result = measure(args.release, args.geography, load_scenario(args.defaults, args.scenario))
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
