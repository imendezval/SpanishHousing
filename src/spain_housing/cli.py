"""Thin scenario validation and offline dataset commands."""

import argparse
import re
import sys
from collections.abc import Sequence
from pathlib import Path

from spain_housing.application import evaluate_scenario
from spain_housing.application.export import export_run, replay_run, run_json
from spain_housing.config import load_mapping, load_scenario, scenario_json
from spain_housing.ingestion.release import build_release
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.dataset import BuildRecipe
from spain_housing.models.market import MarketQuery
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import GeographicReference
from spain_housing.storage.release import canonical_json, load_release


def _municipal_code(value: str) -> str:
    if re.fullmatch(r"[0-9]{5}", value) is None:
        raise argparse.ArgumentTypeError("locations require five-digit municipal codes")
    return value


def _evaluate(args: argparse.Namespace) -> RunResult:
    repository = SnapshotMarketRepository.from_release(
        args.release, allow_synthetic=args.allow_synthetic
    )
    context = repository.evaluation_context
    if args.command == "replay-run":
        saved = RunResult.model_validate(load_mapping(args.run))
        return replay_run(saved, market_data=repository, context=context)
    scenario = load_scenario(args.defaults, args.scenario)
    locations = (
        tuple(GeographicReference(level="municipality", code=code) for code in args.locations)
        if args.locations is not None
        else tuple(record.location for record in context.locations)
    )
    return evaluate_scenario(
        scenario, market_data=repository, context=context, mapped_locations=locations
    )


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
    evaluate = commands.add_parser(
        "evaluate-scenario", help="evaluate a local/local scenario offline"
    )
    evaluate.add_argument("--defaults", type=Path, required=True)
    evaluate.add_argument("--scenario", type=Path, required=True)
    evaluate.add_argument("--locations", type=_municipal_code, nargs="+")
    replay = commands.add_parser("replay-run", help="exactly reproduce a saved economic run")
    replay.add_argument("--run", type=Path, required=True)
    serve_command = commands.add_parser("serve", help="launch the optional local map app")
    for name in ("defaults", "scenario", "release"):
        serve_command.add_argument(f"--{name}", type=Path, required=True)
    serve_command.add_argument("--allow-synthetic", action="store_true")
    serve_command.add_argument("--port", type=int, default=8501)
    for command in (evaluate, replay):
        command.add_argument("--release", type=Path, required=True)
        command.add_argument("--output-dir", type=Path)
    for command in (build, check_release, query, evaluate, replay):
        command.add_argument(
            "--allow-synthetic",
            action="store_true",
            help="explicitly allow labelled synthetic fixtures/demos",
        )
    args = parser.parse_args(argv)

    try:
        if args.command == "serve":
            from spain_housing.launcher import serve

            return serve(
                defaults=args.defaults,
                scenario=args.scenario,
                release=args.release,
                allow_synthetic=args.allow_synthetic,
                port=args.port,
            )
        if args.command in ("evaluate-scenario", "replay-run"):
            run = _evaluate(args)
            if args.output_dir is not None:
                export_run(run, args.output_dir)
            sys.stdout.write(run_json(run))
            return 0
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
