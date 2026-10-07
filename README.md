# Spain housing affordability simulator

Typed contracts, the financial engine, offline datasets and callable scenario evaluation with CLI export/replay are available. Phase 4 engineering is verified separately from observed-data readiness: market acquisition remains blocked. Official municipal geography is independently ready. The interactive map belongs to Phase 5.

See the [project brief](docs/PROJECT_BRIEF.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md), [Phase 1 guide](docs/phases/PHASE_1_foundations.md), [Phase 2 progress](docs/progress/PHASE_2.md), [Phase 3 progress](docs/progress/PHASE_3.md), [Phase 4 progress](docs/progress/PHASE_4.md), [architecture](docs/ARCHITECTURE.md), [data audit](docs/DATA_COVERAGE.md), and [current data access/readiness](docs/DATA_ACCESS.md). Supplied Phase 2–4 execution guides remain local untracked inputs; documentation links use tracked progress records.

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
wheel_env_dir="$(mktemp -d)"
uv venv "$wheel_env_dir" --python 3.12
uv pip install --python "$wheel_env_dir/bin/python" "$repo_dir/dist/spain_housing-0.1.0-py3-none-any.whl"
(cd /tmp && "$wheel_env_dir/bin/spain-housing" --help)
(cd /tmp && "$wheel_env_dir/bin/spain-housing" validate-scenario --defaults "$repo_dir/configs/defaults.yaml" --scenario "$repo_dir/configs/scenarios/room_only.yaml" --json)
```

## Financial Python API

This synthetic example saves €2,000 in one month, reaching €60,000. It supplies a single borrower's monthly income separately and returns a savings-limited €200,000 budget. All income, rent, expenses and debt below are already monthly EUR; rates are decimal fractions.

```python
from datetime import date
from math import isclose

from spain_housing.finance import (
    ProportionalPurchaseCostPolicy,
    calculate_fixed_financing_capacity,
    simulate_savings,
)
from spain_housing.models.contracts import PurchaseContext
from spain_housing.models.results import PreparedMonthlyBudget
from spain_housing.models.scenario import (
    GeographicReference,
    MortgageAssumptions,
    PurchaseCostAssumptions,
    TargetProperty,
)

savings = simulate_savings(
    (
        PreparedMonthlyBudget(
            month=date(2026, 1, 1),
            net_income_eur=4_000,
            rent_eur=1_000,
            nonhousing_expenses_eur=1_000,
            other_debt_eur=0,
        ),
    ),
    starting_savings_eur=58_000,
    retained_reserve_eur=0,
)
result = calculate_fixed_financing_capacity(
    savings_result=savings,
    borrower_monthly_net_income_eur=3_000,
    borrower_monthly_other_debt_eur=0,
    mortgage=MortgageAssumptions(
        financed_fraction=0.8,
        maximum_debt_ratio=0.35,
        term_years=25,
        annual_nominal_interest_fraction=0,
    ),
    cost_policy=ProportionalPurchaseCostPolicy(
        PurchaseCostAssumptions(
            policy="proportional",
            allowance_fraction=0.1,
        )
    ),
    purchase_context=PurchaseContext(
        buying_location=GeographicReference(level="municipality", code="28079"),
        purchase_month=date(2026, 2, 1),
        target_property=TargetProperty(
            property_type="flat",
            area_m2=100,
            condition="ordinary",
        ),
    ),
    target_price_eur=250_000,
)
assert savings.usable_savings_eur == 60_000
assert isclose(result.maximum_price_eur, 200_000, abs_tol=1e-7)
assert result.binding_constraint == "savings"
assert isclose(result.target_cash_shortfall_eur, 15_000, abs_tol=1e-7)
print(result.model_dump_json(indent=2))
```

Run this example with the wheel environment's Python from `/tmp` to verify the installed financial API. The engine also exports `monthly_payment`, `maximum_loan`, `maximum_mortgage_payment`, and `required_upfront_cash`.

Budgets must be nonempty and consecutive. Negative balances remain visible; any balance below −€0.00000001 permanently marks the path `funds_exhausted`, and purchase capacity refuses that path. The reserve is retained at purchase. Without a target, every target diagnostic is `None`. A `None` savings price limit means no cash constraint under full financing with zero costs; the mortgage limit remains finite. Binding labels use €0.01 absolute tolerance while capacity retains the actual minimum.

Phase 3 starts with the restricted pilot and source limitations in `docs/DATA_COVERAGE.md`. Phase 4 prepares exactly N budgets, keeps savers and borrowers separate, samples borrower income/debt at purchase offset N, and translates exhaustion to an unviable location. It then resolves market targets and run metadata; these operations reuse the financial engine.

## Offline dataset workflow

The real recipe is `configs/sources/pilot.yaml`: Madrid, Barcelona and Jaén are core; Getafe is the additional gap case. Selected asking-price profiles are September 2026 pooled sale and whole-home unit rent, and Q2 2026 mean room rent. No real market observations have been acquired under unresolved copying permission. `build-release` with that recipe deliberately fails with a source-use error. The historical audit is evidence of leads, not an input release.

Run the self-authored fixture through the same pipeline with explicit synthetic opt-in:

```bash
uv run --locked spain-housing build-release \
  --config tests/fixtures/synthetic/pilot/recipe.json \
  --data-root tests/fixtures/synthetic/pilot \
  --release-root /tmp/spain-housing-fixture-releases --allow-synthetic
```

Use the returned release path for validation and queries:

```bash
uv run --locked spain-housing validate-release --release /absolute/release/path --allow-synthetic
uv run --locked spain-housing query-market --release /absolute/release/path \
  --query tests/fixtures/synthetic/pilot/query_sale.json --allow-synthetic
uv run --locked spain-housing query-market --release /absolute/release/path \
  --query tests/fixtures/synthetic/pilot/query_missing_room.json --allow-synthetic
```

The fixture contains 11 synthetic observations across four synthetic municipalities, 12 expected profile cells, and one intentional missing Getafe room cell. Every output retains synthetic evidence. Missing/unsupported queries return exit 0; invalid releases/inputs or omitted opt-in return exit 2. Commands work from another working directory with absolute config/data/query/release paths. Build is offline; permitted acquisition is separate.

`SnapshotMarketRepository.from_release(path, allow_synthetic=False)` implements `MarketData`. Its `get(MarketQuery)` uses exact start/end equality and explicit segment matching. Quarterly rooms never stand in for a monthly observation; pooled homes never silently stand in for flats/houses. Unknown size/bedroom/contract dimensions cannot satisfy specific requests. Ambiguous selection returns unsupported. The repository exposes immutable `manifest`, `locations` and `boundaries`, and returns original observations with provenance. Opening verifies the full bundle; queries use the in-memory index without network or file access.

Each portable release contains `manifest.json`, `observations.jsonl`, `locations.json`, `boundaries.geojson`, and `coverage.json`. Captures remain outside it. Canonical UTF-8 JSON uses sorted keys and newline termination; observations, locations, features and coverage are sorted by their semantic keys. Identity hashes manifest metadata excluding its own ID/digest, including payload hashes, recipe and actual processing-source fingerprint. Identical fixed inputs/code/config produce identical bytes/IDs. Releases publish atomically, verify existing IDs and never overwrite them. Hashes check integrity; they are not signatures.

## Retained official geography and reconstruction

The actual INE 2026 dictionary, in-year changes and four complete IGN responses are retained locally under `data/raw/pilot-geography/captures/`, with hash-addressed bytes and capture sidecars. The verified four-feature subset is under `data/processed/pilot-geography/`. These ignored artifacts must be backed up; they are not embedded in the wheel or stored as a real market release. [Geography metadata](data/manifests/pilot_geography.json) records hashes and attribution. The recipe records the explicit source IDs, municipal crosswalks, full IGN national codes and separate INE control digits.

Reconstruct and verify the subset from retained bytes:

```bash
uv run --locked python scripts/verify_pilot_geography.py \
  --config configs/sources/pilot.yaml --data-root data/raw/pilot-geography \
  --output-root data/processed/pilot-geography
```

Copy `data/raw/pilot-geography/` and the small recipe/manifests together to a backup or another machine. Restore the raw tree, run the command and compare its file hashes to `data/manifests/pilot_geography.json`; source URLs/hashes alone cannot reconstruct lost bytes. After permitted market captures exist, retain their immutable bytes/sidecars and updated recipe alongside every observed release, and rebuild with explicit `--data-root`/`--release-root`. Corrections require new captures and a new release ID. Permission changes require evidence and explicit review, not an opt-in bypass.

Scenario evaluation uses the explicit synthetic fixture while the market blocker remains. Production integration needs a permitted observed release. Application/market rules own temporal selection, labelled proxies, conversions, shares, growth and monthly preparation; the financial engine and dataset builder retain their separate responsibilities.

## Scenario evaluation, export and replay

First build the labelled synthetic release with the offline command above. Set
`release_dir` to the exact path returned in its JSON; do not substitute the real
geography-only subset or assume a fixed fixture release ID.

```bash
release_dir=/absolute/path/to/the-returned-synthetic-release
uv run --locked spain-housing evaluate-scenario \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase4_room_demo.yaml \
  --release "$release_dir" --locations 28079 08019 23050 28065 \
  --output-dir outputs/room-demo --allow-synthetic
uv run --locked spain-housing evaluate-scenario \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase4_staged_growth_demo.yaml \
  --release "$release_dir" --output-dir outputs/growth-demo --allow-synthetic
uv run --locked spain-housing replay-run \
  --run outputs/room-demo/run.json --release "$release_dir" --allow-synthetic
```

Absolute input paths work from another directory. Omit `--locations` to evaluate
all released municipalities in canonical order. Omit `--output-dir` to write only
the full run JSON to stdout. Existing output directories are refused. Errors
return exit 2 with empty stdout; expected gaps/unviability return exit 0 with
typed per-location results. Both demos show Getafe's missing room input; an
all-flat scenario does not require room evidence. A missing buying price preserves
financial capacity with missing comparison indicators and absent target diagnostics.

Exports contain authoritative `run.json` and one-row-per-location `summary.csv`.
The CSV preserves full numeric precision, empty unavailable values, separate
indicator statuses and an explicit unbounded-cash flag. Import municipality codes
as spreadsheet **text** to preserve leading zeros. Replay uses the saved resolved
scenario without remerging defaults and requires the same release, model, actual
source fingerprint and runtime versions. Older contract-only runs cannot establish
exact replay. Evaluating saved inputs under new code is a new run.

### Scenario assumptions

- Saving offsets are 0 through N−1; borrower income/debt is sampled at purchase
  offset N. Net annual income is divided by 12. Paths use their declared linear
  or step rule and hold the final milestone thereafter.
- Savers and borrowers are independent sets. The growth demo has two savers and
  one borrower. Non-saver income/savings/debt do not enter the saving pool.
- One stage prices one unit. `rent_share` is the combined saving pool's share;
  rent and the aggregate non-housing budget are not multiplied by saver count.
  Unit rent needs explicit rental area; direct monthly rent does not use area.
- Non-housing spending is effective cash expenditure, including only utilities
  paid outside rent. Inclusion flags record user assumptions, not verified source
  bill coverage. Change expense milestones explicitly when bills change; the
  growth demo does this at offset 3. No utility amount is inferred or subtracted.
- Default property matching is strict. These demos explicitly enable pooled
  proxies for flats. Requested bedrooms still need matching data; unknown source
  bedrooms cannot satisfy them. New/renovation targets have unsupported market
  comparisons while financial capacity can remain available. Room area/bedroom
  selectors are unsupported. Room rent is never derived from flat rent.
- Reference profiles must be complete at base and within the default 12-month
  age limit. Selection uses one source/basis/statistic series and exact repository
  periods. Ambiguity needs explicit profile IDs; missing selected cells never
  trigger older-source fallback.
- Frozen policy keeps source values throughout the horizon, with distinct source
  periods visible. Growth compounds from each reference's last covered month:
  June for Q2 rooms, September for September sale/rent. It bridges reference to
  base/start once and never grows income/expense paths. Earlier starts than base
  are unsupported. These are snapshot counterfactuals, not historical forecasts.
- Exhausted savings remain unviable after recovery. Viable zero capacity remains
  available; target coverage ratios can exceed one. No estimate guarantees bank
  approval or an available property. `fixed_saving` still loads but evaluation
  reports it as deferred; existing examples remain unchanged.

### Callable Python evaluator

The launcher composes configuration and the concrete repository. Application
accepts the protocol and immutable public context; it performs no acquisition.

```python
from pathlib import Path

from spain_housing.application import evaluate_scenario
from spain_housing.application.export import export_run
from spain_housing.config import load_scenario
from spain_housing.markets.repository import SnapshotMarketRepository

scenario = load_scenario(
    Path("configs/defaults.yaml"), Path("configs/scenarios/phase4_room_demo.yaml")
)
repository = SnapshotMarketRepository.from_release(
    Path("/absolute/path/to/the-returned-synthetic-release"), allow_synthetic=True
)
run = evaluate_scenario(
    scenario,
    market_data=repository,
    context=repository.evaluation_context,
    mapped_locations=tuple(record.location for record in repository.locations),
)
export_run(run, Path("outputs/python-demo"))
```

`prepare_savings` is separately callable without a buying destination.
`evaluate_location` accepts separate saving/buying references; `evaluate_purchase`
reuses an existing savings result and purchase finances for destination work.
Phase 5 renders these typed budgets, paths, limits, shortfalls, statuses and
original market traces. Geometry remains on the repository for a launcher to
join by municipality code/version. UI controls must call the same evaluator.
Observed integration remains blocked; synthetic results are never market evidence.
