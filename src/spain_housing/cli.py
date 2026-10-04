"""Phase 1 command-line entry point."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from spain_housing.config import load_scenario, scenario_json


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="spain-housing")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-scenario", help="validate a scenario file")
    validate.add_argument("--defaults", type=Path, required=True)
    validate.add_argument("--scenario", type=Path, required=True)
    validate.add_argument("--json", action="store_true", help="print resolved scenario as JSON")
    args = parser.parse_args(argv)

    try:
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
