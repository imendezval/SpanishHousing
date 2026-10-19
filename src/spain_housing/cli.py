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
from spain_housing.models.market import MarketQuery
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import GeographicReference
from spain_housing.storage.release import canonical_json, load_release, parse_recipe


def _municipal_code(value: str) -> str:
    if re.fullmatch(r"[0-9]{5}", value) is None:
        raise argparse.ArgumentTypeError("locations require five-digit municipal codes")
    return value


def _evaluate(args: argparse.Namespace) -> RunResult:
    repository = SnapshotMarketRepository.from_release(
        args.release, allow_synthetic=args.allow_synthetic, geography_dir=args.geography
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
    inspect = commands.add_parser("inspect-release", help="inspect validated coverage offline")
    inspect.add_argument("--release", type=Path, required=True)
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
    for command in (build, check_release, inspect, query, evaluate, replay):
        command.add_argument(
            "--allow-synthetic",
            action="store_true",
            help="explicitly allow labelled synthetic fixtures/demos",
        )
    for command in (build, check_release, inspect, query, evaluate, replay, serve_command):
        command.add_argument(
            "--geography",
            type=Path,
            help="explicit canonical geography directory for schema-2 releases",
        )
    serve_command.add_argument(
        "--display-geography", type=Path, help="explicit compatible simplified display directory"
    )
    atlas_build = commands.add_parser(
        "build-geography", help="build canonical geography from retained official bytes"
    )
    atlas_build.add_argument("--config", type=Path, required=True)
    atlas_build.add_argument("--data-root", type=Path, required=True)
    atlas_build.add_argument("--artifact-root", type=Path, required=True)
    atlas_check = commands.add_parser(
        "validate-geography", help="verify complete canonical geography and optional display"
    )
    atlas_check.add_argument("--geography", type=Path, required=True)
    atlas_check.add_argument("--display-geography", type=Path)
    display_build = commands.add_parser(
        "build-map-display", help="prepare a topology-aware metric display derivative"
    )
    display_build.add_argument("--geography", type=Path, required=True)
    display_build.add_argument("--artifact-root", type=Path, required=True)
    display_build.add_argument(
        "--tolerance-m", type=float, choices=(20.0, 50.0, 100.0), default=50.0
    )
    display_build.add_argument(
        "--neutral-source-conflicts",
        action="store_true",
        help="retain pinned source overlaps as neutral display context, with neither owner",
    )
    demo = commands.add_parser(
        "generate-demo", help="prepare explicitly synthetic economic inputs over a canonical atlas"
    )
    demo.add_argument("--geography", type=Path, required=True)
    demo.add_argument("--config", type=Path, required=True)
    demo.add_argument("--output-root", type=Path, required=True)
    demo.add_argument("--variant", choices=("complete", "partial"), default="complete")
    args = parser.parse_args(argv)

    try:
        payload: dict[str, object]
        if args.command in (
            "build-geography",
            "validate-geography",
            "build-map-display",
            "generate-demo",
        ):
            from spain_housing.storage.geography import load_display, load_geography

            if args.command == "build-geography":
                from spain_housing.ingestion.atlas import build_geography
                from spain_housing.models.geography import GeographyRecipe

                path = build_geography(
                    GeographyRecipe.model_validate(load_mapping(args.config)),
                    data_root=args.data_root,
                    artifact_root=args.artifact_root,
                )
                atlas_manifest = load_geography(path, full=False).manifest
                payload = dict(
                    path=str(path),
                    artifact_id=atlas_manifest.artifact_id,
                    counts=atlas_manifest.counts.model_dump(mode="json"),
                )
            elif args.command == "build-map-display":
                from spain_housing.ingestion.map_geometry import prepare_display

                path = prepare_display(
                    args.geography,
                    artifact_root=args.artifact_root,
                    tolerance_m=args.tolerance_m,
                    neutral_source_conflicts=args.neutral_source_conflicts,
                )
                payload = dict(path=str(path), artifact_id=path.name)
            elif args.command == "generate-demo":
                from spain_housing.ingestion.demo import generate_demo
                from spain_housing.models.demo import DemoConfig

                path = generate_demo(
                    args.geography,
                    DemoConfig.model_validate(load_mapping(args.config)),
                    output_root=args.output_root,
                    variant=args.variant,
                )
                payload = dict(path=str(path), recipe=str(path / "recipe.json"), kind="synthetic")
            else:
                geography = load_geography(args.geography)
                display_id = (
                    load_display(args.display_geography, geography).manifest.artifact_id
                    if args.display_geography
                    else None
                )
                payload = dict(
                    artifact_id=geography.manifest.artifact_id,
                    counts=geography.manifest.counts.model_dump(mode="json"),
                    display_id=display_id,
                    source_coverage_valid=geography.coverage_valid,
                    source_conflicts=[
                        c.model_dump(mode="json")
                        for c in geography.manifest.recipe.source_conflicts
                    ],
                )
            sys.stdout.write(canonical_json(payload).decode())
            return 0
        if args.command == "inspect-release":
            repository = SnapshotMarketRepository.from_release(
                args.release, allow_synthetic=args.allow_synthetic, geography_dir=args.geography
            )
            sys.stdout.write(
                canonical_json(repository.coverage_report.model_dump(mode="json")).decode()
            )
            return 0
        if args.command == "serve":
            from spain_housing.launcher import serve

            return serve(
                defaults=args.defaults,
                scenario=args.scenario,
                release=args.release,
                allow_synthetic=args.allow_synthetic,
                port=args.port,
                geography_dir=args.geography,
                display_geography=args.display_geography,
            )
        if args.command in ("evaluate-scenario", "replay-run"):
            run = _evaluate(args)
            if args.output_dir is not None:
                export_run(run, args.output_dir)
            sys.stdout.write(run_json(run))
            return 0
        if args.command != "validate-scenario":
            if args.command == "build-release":
                recipe = parse_recipe(load_mapping(args.config))
                path = build_release(
                    recipe,
                    data_root=args.data_root,
                    release_root=args.release_root,
                    allow_synthetic=args.allow_synthetic,
                    geography_dir=args.geography,
                )
            else:
                path = args.release
            if args.command == "query-market":
                repository = SnapshotMarketRepository.from_release(
                    path, allow_synthetic=args.allow_synthetic, geography_dir=args.geography
                )
                lookup = repository.get(MarketQuery.model_validate(load_mapping(args.query)))
                sys.stdout.write(canonical_json(lookup.model_dump(mode="json")).decode())
            else:
                manifest = load_release(
                    path, allow_synthetic=args.allow_synthetic, geography_dir=args.geography
                ).manifest
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
