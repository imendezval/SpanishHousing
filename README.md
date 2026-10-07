# Spain housing affordability simulator

Typed scenario and market contracts, deterministic configuration, and a bounded data coverage audit are available. Phase 2 adds a financial engine over prepared monthly budgets and explicit purchase assumptions. Market ingestion and map evaluation follow in later phases.

See the [project brief](docs/PROJECT_BRIEF.md), [implementation plan](docs/IMPLEMENTATION_PLAN.md), [Phase 1 guide](docs/phases/PHASE_1_foundations.md), [Phase 2 guide](docs/phases/PHASE_2_financial.md), [architecture](docs/ARCHITECTURE.md), and [data audit](docs/DATA_COVERAGE.md).

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
    (PreparedMonthlyBudget(
        month=date(2026, 1, 1),
        net_income_eur=4_000,
        rent_eur=1_000,
        nonhousing_expenses_eur=1_000,
        other_debt_eur=0,
    ),),
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
    cost_policy=ProportionalPurchaseCostPolicy(PurchaseCostAssumptions(
        policy="proportional", allowance_fraction=0.1,
    )),
    purchase_context=PurchaseContext(
        buying_location=GeographicReference(level="municipality", code="28079"),
        purchase_month=date(2026, 2, 1),
        target_property=TargetProperty(
            property_type="flat", area_m2=100, condition="ordinary",
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
