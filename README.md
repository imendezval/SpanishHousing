# Spain housing affordability simulator

Phase 1 establishes typed scenario and market contracts, deterministic configuration, and a bounded data coverage audit. Financial calculations, real market ingestion, and the map follow in later phases.

See the [project brief](docs/PROJECT_BRIEF.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md), [Phase 1 guide](docs/phases/PHASE_1_foundations.md), [architecture](docs/ARCHITECTURE.md), and [data audit](docs/DATA_COVERAGE.md).

## Development

Python 3.12 and `uv` are required. From the repository root:

```bash
uv sync --locked
uv run --locked spain-housing --help
bash scripts/check.sh
uv build
```

Scenario validation uses explicit paths:

```bash
uv run --locked spain-housing validate-scenario --defaults configs/defaults.yaml --scenario configs/scenarios/room_only.yaml --json
```

The CLI accepts absolute paths when run from another directory. The `--json` output is the fully resolved scenario, suitable for saving and validating again.

To verify the built wheel rather than the editable development install:

```bash
repo_dir="$(pwd)"
uv venv /tmp/spain-housing-wheel-smoke --python 3.12
uv pip install --python /tmp/spain-housing-wheel-smoke/bin/python dist/spain_housing-0.1.0-py3-none-any.whl
(cd /tmp && /tmp/spain-housing-wheel-smoke/bin/spain-housing --help)
(cd /tmp && /tmp/spain-housing-wheel-smoke/bin/spain-housing validate-scenario --defaults "$repo_dir/configs/defaults.yaml" --scenario "$repo_dir/configs/scenarios/room_only.yaml" --json)
```

Phase 2 starts at `models.results.PreparedMonthlyBudget`, `SavingsResult` and `PurchaseResult`; implement the financial engine in `finance` against those records. Phase 3 starts with the restricted pilot and source limitations in `docs/DATA_COVERAGE.md`; keep acquisition out of evaluation and leave unsupported room locations missing.
