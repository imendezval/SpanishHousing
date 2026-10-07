"""Thin scenario validation and offline dataset commands."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from spain_housing.config import load_mapping, load_scenario, scenario_json
from spain_housing.ingestion.release import build_release
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.dataset import BuildRecipe
from spain_housing.models.market import MarketQuery
from spain_housing.storage.release import canonical_json, load_release


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spain-housing")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-scenario", help="validate a scenario file")
    validate.add_argument("--defaults", type=Path, required=True)
    validate.add_argument("--scenario", type=Path, required=True)
    validate.add_argument("--json", action="store_true", help="print resolved scenario as JSON")
    build = commands.add_parser(
        "build-release", help="build an immutable release from retained local inputs"
    )
    build.add_argument("--config", type=Path, required=True)
    build.add_argument("--data-root", type=Path, required=True)
    build.add_argument("--release-root", type=Path, required=True)
    check_release = commands.add_parser(
        "validate-release", help="verify every release payload and relationship"
    )
    check_release.add_argument("--release", type=Path, required=True)
    query = commands.add_parser(
        "query-market", help="query exact market intervals and segments offline"
    )
    query.add_argument("--release", type=Path, required=True)
    query.add_argument("--query", type=Path, required=True)
    for command in (build, check_release, query):
        command.add_argument(
            "--allow-synthetic",
            action="store_true",
            help="explicitly allow labelled synthetic fixtures/demos",
        )
    args = parser.parse_args(argv)

    try:
        if args.command != "validate-scenario":
            if args.command == "build-release":
                recipe = BuildRecipe.model_validate(load_mapping(args.config))
                path = build_release(
                    recipe,
                    data_root=args.data_root,
                    release_root=args.release_root,
                    allow_synthetic=args.allow_synthetic,
                )
            else:
                path = args.release
            if args.command == "query-market":
                repository = SnapshotMarketRepository.from_release(
                    path, allow_synthetic=args.allow_synthetic
                )
                lookup = repository.get(MarketQuery.model_validate(load_mapping(args.query)))
                sys.stdout.write(canonical_json(lookup.model_dump(mode="json")).decode())
            else:
                manifest = load_release(path, allow_synthetic=args.allow_synthetic).manifest
                sys.stdout.write(
                    canonical_json(
                        {
                            "release_id": manifest.release_id,
                            "path": str(path),
                            "kind": manifest.kind,
                            "readiness": manifest.readiness,
                            "coverage": manifest.coverage.model_dump(mode="json"),
                        }
                    ).decode()
                )
            return 0
        scenario = load_scenario(args.defaults, args.scenario)
    except (OSError, ValueError) as exc:
        print(f"spain-housing: {exc}", file=sys.stderr)
        return 2

    if args.json:
        sys.stdout.write(scenario_json(scenario))
    else:
        print(
            f"Valid scenario: {scenario.saving_months} saving months, "
            f"purchase {scenario.purchase_month.isoformat()}, mode {scenario.locations.mode}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
