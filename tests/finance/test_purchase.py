from datetime import date

import pytest

from spain_housing.finance import (
    ProportionalPurchaseCostPolicy,
    calculate_fixed_financing_capacity,
    required_upfront_cash,
    simulate_savings,
)
from spain_housing.finance.mortgage import maximum_mortgage_payment, monthly_payment
from spain_housing.models.contracts import PurchaseContext, PurchaseCostBreakdown
from spain_housing.models.results import PreparedMonthlyBudget, SavingsResult
from spain_housing.models.scenario import (
    GeographicReference,
    MortgageAssumptions,
    PurchaseCostAssumptions,
    TargetProperty,
)


def context(code: str = "28079") -> PurchaseContext:
    return PurchaseContext(
        buying_location=GeographicReference(level="municipality", code=code),
        purchase_month=date(2027, 4, 1),
        target_property=TargetProperty(property_type="flat", area_m2=100, condition="ordinary"),
    )


def mortgage(
    *, rate: float = 0, financed: float = 0.8, debt_ratio: float = 0.35, years: int = 25
) -> MortgageAssumptions:
    return MortgageAssumptions(
        financed_fraction=financed,
        maximum_debt_ratio=debt_ratio,
        term_years=years,
        annual_nominal_interest_fraction=rate,
    )


def policy(allowance: float = 0.1) -> ProportionalPurchaseCostPolicy:
    return ProportionalPurchaseCostPolicy(
        PurchaseCostAssumptions(policy="proportional", allowance_fraction=allowance)
    )


def savings(usable: float, *, viability: str = "viable") -> SavingsResult:
    return SavingsResult(
        monthly_path=(),
        ending_savings_eur=usable,
        usable_savings_eur=usable,
        viability=viability,
    )


class DistinctCosts:
    def costs(self, price_eur: float, context: PurchaseContext) -> PurchaseCostBreakdown:
        assert context.purchase_month == date(2027, 4, 1)
        return PurchaseCostBreakdown(
            purchase_cost_eur=0.08 * price_eur,
            mortgage_formalisation_cost_eur=0.02 * price_eur,
        )


def test_common_upfront_cash_includes_each_component_once() -> None:
    assert required_upfront_cash(
        100_000,
        financed_fraction=0.8,
        cost_policy=DistinctCosts(),
        context=context(),
    ) == pytest.approx(30_000)
    assert policy().costs(100_000, context()) == PurchaseCostBreakdown(
        purchase_cost_eur=10_000, mortgage_formalisation_cost_eur=0
    )


@pytest.mark.parametrize(
    ("usable", "income", "debt", "cash_limit", "mortgage_limit", "maximum", "binding"),
    [
        (60_000, 3_000, 0, 200_000, 393_750, 200_000, "savings"),
        (90_000, 2_000, 0, 300_000, 262_500, 262_500, "mortgage"),
        (78_750, 2_000, 0, 262_500, 262_500, 262_500, "both"),
        (90_000, 2_000, 100, 300_000, 225_000, 225_000, "mortgage"),
        (60_000, 2_000, 700, 200_000, 0, 0, "mortgage"),
        (12_600, 2_000, 100, 42_000, 225_000, 42_000, "savings"),
        (0, 0, 0, 0, 0, 0, "both"),
    ],
)
def test_zero_interest_capacity_references(
    usable: float,
    income: float,
    debt: float,
    cash_limit: float,
    mortgage_limit: float,
    maximum: float,
    binding: str,
) -> None:
    result = calculate_fixed_financing_capacity(
        savings_result=savings(usable),
        borrower_monthly_net_income_eur=income,
        borrower_monthly_other_debt_eur=debt,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    assert result.savings_price_limit_eur == pytest.approx(cash_limit)
    assert result.mortgage_price_limit_eur == pytest.approx(mortgage_limit)
    assert result.maximum_price_eur == pytest.approx(maximum)
    assert result.binding_constraint == binding


def test_unbounded_cash_and_near_equal_explanation_keep_actual_minimum() -> None:
    unbounded = calculate_fixed_financing_capacity(
        savings_result=savings(0),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(financed=1),
        cost_policy=policy(0),
        purchase_context=context(),
    )
    assert unbounded.savings_price_limit_eur is None
    assert unbounded.maximum_price_eur == unbounded.mortgage_price_limit_eur == 210_000
    assert unbounded.binding_constraint == "mortgage"

    near = calculate_fixed_financing_capacity(
        savings_result=savings(78_749.9985),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    assert near.binding_constraint == "both"
    assert near.maximum_price_eur == pytest.approx(262_499.995)


def test_positive_rate_and_nondefault_assumptions() -> None:
    positive = calculate_fixed_financing_capacity(
        savings_result=savings(1_000_000),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(rate=0.035),
        cost_policy=policy(),
        purchase_context=context(),
    )
    assert positive.mortgage_price_limit_eur == pytest.approx(
        174_782.0222580517, rel=1e-10, abs=1e-7
    )
    nondefault = calculate_fixed_financing_capacity(
        savings_result=savings(50_000),
        borrower_monthly_net_income_eur=3_000,
        borrower_monthly_other_debt_eur=100,
        mortgage=mortgage(financed=0.7, debt_ratio=0.4, years=20),
        cost_policy=policy(0.05),
        purchase_context=context(),
    )
    assert nondefault.savings_price_limit_eur == pytest.approx(50_000 / 0.35)
    assert nondefault.maximum_price_eur == min(
        nondefault.savings_price_limit_eur, nondefault.mortgage_price_limit_eur
    )


def test_target_diagnostics_for_both_reference_cases() -> None:
    cash_limited = calculate_fixed_financing_capacity(
        savings_result=savings(60_000),
        borrower_monthly_net_income_eur=3_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
        target_price_eur=250_000,
    )
    assert cash_limited.target_loan_eur == 200_000
    assert cash_limited.target_upfront_cash_eur == pytest.approx(75_000)
    assert cash_limited.target_monthly_payment_eur == pytest.approx(666.6666666666666)
    assert cash_limited.target_cash_shortfall_eur == pytest.approx(15_000)
    assert cash_limited.target_payment_shortfall_eur == 0

    mortgage_limited = calculate_fixed_financing_capacity(
        savings_result=savings(90_000),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
        target_price_eur=300_000,
    )
    assert mortgage_limited.target_loan_eur == 240_000
    assert mortgage_limited.target_upfront_cash_eur == pytest.approx(90_000)
    assert mortgage_limited.target_monthly_payment_eur == 800
    assert mortgage_limited.target_cash_shortfall_eur == 0
    assert mortgage_limited.target_payment_shortfall_eur == 100


def test_target_can_have_both_or_neither_shortfall() -> None:
    arguments = dict(
        savings_result=savings(60_000),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    expensive = calculate_fixed_financing_capacity(**arguments, target_price_eur=300_000)
    assert expensive.target_cash_shortfall_eur == pytest.approx(30_000)
    assert expensive.target_payment_shortfall_eur == 100
    affordable = calculate_fixed_financing_capacity(**arguments, target_price_eur=100_000)
    assert affordable.target_cash_shortfall_eur == 0
    assert affordable.target_payment_shortfall_eur == 0


def test_returned_price_is_feasible_and_capacity_is_monotonic() -> None:
    base = dict(
        borrower_monthly_net_income_eur=2_500,
        borrower_monthly_other_debt_eur=100,
        mortgage=mortgage(rate=0.035),
        cost_policy=policy(),
        purchase_context=context(),
    )
    result = calculate_fixed_financing_capacity(savings_result=savings(70_000), **base)
    assert (
        required_upfront_cash(
            result.maximum_price_eur,
            financed_fraction=base["mortgage"].financed_fraction,
            cost_policy=base["cost_policy"],
            context=base["purchase_context"],
        )
        <= 70_000 + 1e-7
    )
    assert (
        monthly_payment(
            base["mortgage"].financed_fraction * result.maximum_price_eur, base["mortgage"]
        )
        <= maximum_mortgage_payment(2_500, 100, 0.35) + 1e-7
    )

    more_savings = calculate_fixed_financing_capacity(savings_result=savings(80_000), **base)
    more_income = calculate_fixed_financing_capacity(
        savings_result=savings(70_000), **(base | {"borrower_monthly_net_income_eur": 3_000})
    )
    more_debt = calculate_fixed_financing_capacity(
        savings_result=savings(70_000), **(base | {"borrower_monthly_other_debt_eur": 300})
    )
    higher_cost = calculate_fixed_financing_capacity(
        savings_result=savings(70_000), **(base | {"cost_policy": policy(0.2)})
    )
    assert more_savings.maximum_price_eur >= result.maximum_price_eur
    assert more_income.maximum_price_eur >= result.maximum_price_eur
    assert more_debt.maximum_price_eur <= result.maximum_price_eur
    assert higher_cost.maximum_price_eur <= result.maximum_price_eur


def test_composed_workflow_separates_prepared_savers_from_borrower_inputs() -> None:
    budgets = tuple(
        PreparedMonthlyBudget(
            month=date(2026, month, 1),
            net_income_eur=4_000,
            rent_eur=1_000,
            nonhousing_expenses_eur=1_000,
            other_debt_eur=0,
        )
        for month in (1, 2, 3)
    )
    accumulated = simulate_savings(budgets, starting_savings_eur=54_000, retained_reserve_eur=0)
    result = calculate_fixed_financing_capacity(
        savings_result=accumulated,
        borrower_monthly_net_income_eur=3_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    assert accumulated.usable_savings_eur == 60_000
    assert result.maximum_price_eur == pytest.approx(200_000)


def test_context_does_not_change_baseline_and_results_round_trip() -> None:
    arguments = dict(
        savings_result=savings(60_000),
        borrower_monthly_net_income_eur=3_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
    )
    first = calculate_fixed_financing_capacity(**arguments, purchase_context=context("28079"))
    second_context = context("08019").model_copy(update={"purchase_month": date(2017, 1, 1)})
    second = calculate_fixed_financing_capacity(**arguments, purchase_context=second_context)
    assert first == second
    assert type(first).model_validate_json(first.model_dump_json()) == first


@pytest.mark.parametrize("financed, allowance", [(0.8, 0.1), (1.0, 0.0)])
@pytest.mark.parametrize("target", [None, 100_000, 300_000])
def test_calculated_results_serialize_with_absent_present_and_unbounded_fields(
    financed: float, allowance: float, target: float | None
) -> None:
    result = calculate_fixed_financing_capacity(
        savings_result=savings(60_000),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=100,
        mortgage=mortgage(financed=financed),
        cost_policy=policy(allowance),
        purchase_context=context(),
        target_price_eur=target,
    )
    serialized = result.model_dump_json()
    assert "Infinity" not in serialized and "NaN" not in serialized
    assert type(result).model_validate_json(serialized) == result
    target_fields = [
        value for key, value in result.model_dump().items() if key.startswith("target_")
    ]
    assert (
        all(value is None for value in target_fields)
        if target is None
        else all(value is not None for value in target_fields)
    )


@pytest.mark.parametrize("usable", [0, 60_000, 100_000])
@pytest.mark.parametrize("rate", [0.0, 0.035])
def test_feasibility_at_limit_and_constraint_failure_above_it(usable: float, rate: float) -> None:
    assumptions = mortgage(rate=rate)
    costs = policy()
    result = calculate_fixed_financing_capacity(
        savings_result=savings(usable),
        borrower_monthly_net_income_eur=2_000,
        borrower_monthly_other_debt_eur=100,
        mortgage=assumptions,
        cost_policy=costs,
        purchase_context=context(),
    )
    cash = required_upfront_cash(
        result.maximum_price_eur,
        financed_fraction=assumptions.financed_fraction,
        cost_policy=costs,
        context=context(),
    )
    payment = monthly_payment(assumptions.financed_fraction * result.maximum_price_eur, assumptions)
    assert cash <= usable + 1e-7
    assert payment <= 600 + 1e-7
    above = result.maximum_price_eur + 100
    if result.binding_constraint == "savings":
        assert (
            required_upfront_cash(
                above,
                financed_fraction=assumptions.financed_fraction,
                cost_policy=costs,
                context=context(),
            )
            > usable
        )
    else:
        assert monthly_payment(assumptions.financed_fraction * above, assumptions) > 600


def test_recovered_but_exhausted_composition_is_refused() -> None:
    budgets = (
        PreparedMonthlyBudget(
            month=date(2026, 1, 1),
            net_income_eur=0,
            rent_eur=200,
            nonhousing_expenses_eur=0,
            other_debt_eur=0,
        ),
        PreparedMonthlyBudget(
            month=date(2026, 2, 1),
            net_income_eur=300,
            rent_eur=0,
            nonhousing_expenses_eur=0,
            other_debt_eur=0,
        ),
    )
    accumulated = simulate_savings(budgets, starting_savings_eur=100, retained_reserve_eur=0)
    assert accumulated.ending_savings_eur == accumulated.usable_savings_eur == 200
    with pytest.raises(ValueError, match="exhausted"):
        calculate_fixed_financing_capacity(
            savings_result=accumulated,
            borrower_monthly_net_income_eur=3_000,
            borrower_monthly_other_debt_eur=0,
            mortgage=mortgage(),
            cost_policy=policy(),
            purchase_context=context(),
        )


@pytest.mark.parametrize("value", [-1, True, "100", float("nan"), float("inf")])
def test_invalid_price_and_borrower_scalars_are_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="price_eur"):
        policy().costs(value, context())
    with pytest.raises(ValueError, match="price_eur"):
        required_upfront_cash(value, financed_fraction=0.8, cost_policy=policy(), context=context())
    arguments = dict(
        savings_result=savings(60_000),
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    with pytest.raises(ValueError, match="borrower_monthly_net_income_eur"):
        calculate_fixed_financing_capacity(
            **arguments, borrower_monthly_net_income_eur=value, borrower_monthly_other_debt_eur=0
        )
    with pytest.raises(ValueError, match="borrower_monthly_other_debt_eur"):
        calculate_fixed_financing_capacity(
            **arguments,
            borrower_monthly_net_income_eur=2_000,
            borrower_monthly_other_debt_eur=value,
        )
    with pytest.raises(ValueError, match="target_price_eur"):
        calculate_fixed_financing_capacity(
            **arguments,
            borrower_monthly_net_income_eur=2_000,
            borrower_monthly_other_debt_eur=0,
            target_price_eur=value,
        )


@pytest.mark.parametrize("value", [0, -1, 1.1, True, "0.8", float("nan"), float("inf")])
def test_invalid_financed_fraction_is_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="financed_fraction"):
        policy().upfront_cash_fraction(value)
    with pytest.raises(ValueError, match="financed_fraction"):
        required_upfront_cash(
            100_000, financed_fraction=value, cost_policy=policy(), context=context()
        )


def test_nonfinite_derived_costs_and_capacity_are_rejected() -> None:
    with pytest.raises(ValueError, match="purchase cost.*not finite"):
        policy(10).costs(1e308, context())
    with pytest.raises(ValueError, match="required upfront cash.*not finite"):
        required_upfront_cash(
            1e308, financed_fraction=0.1, cost_policy=policy(1), context=context()
        )
    with pytest.raises(ValueError, match="savings price limit.*not finite"):
        calculate_fixed_financing_capacity(
            savings_result=savings(1e308),
            borrower_monthly_net_income_eur=2_000,
            borrower_monthly_other_debt_eur=0,
            mortgage=mortgage(financed=1),
            cost_policy=policy(1e-308),
            purchase_context=context(),
        )


def test_unbounded_cash_with_zero_payment_capacity() -> None:
    result = calculate_fixed_financing_capacity(
        savings_result=savings(0),
        borrower_monthly_net_income_eur=0,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(financed=1),
        cost_policy=policy(0),
        purchase_context=context(),
    )
    assert result.savings_price_limit_eur is None
    assert result.maximum_price_eur == result.mortgage_price_limit_eur == 0
    assert result.binding_constraint == "mortgage"


def test_exhausted_savings_and_invalid_target_are_rejected() -> None:
    arguments = dict(
        borrower_monthly_net_income_eur=3_000,
        borrower_monthly_other_debt_eur=0,
        mortgage=mortgage(),
        cost_policy=policy(),
        purchase_context=context(),
    )
    with pytest.raises(ValueError, match="exhausted"):
        calculate_fixed_financing_capacity(
            savings_result=savings(200, viability="funds_exhausted"), **arguments
        )
    with pytest.raises(ValueError, match="target_price_eur"):
        calculate_fixed_financing_capacity(
            savings_result=savings(60_000), target_price_eur=0, **arguments
        )
