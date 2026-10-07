from datetime import date

import pytest

from spain_housing.finance.savings import simulate_savings
from spain_housing.models.results import PreparedMonthlyBudget


def budget(month: date, *, income: float = 2_000, rent: float = 400) -> PreparedMonthlyBudget:
    return PreparedMonthlyBudget(
        month=month,
        net_income_eur=income,
        rent_eur=rent,
        nonhousing_expenses_eur=600,
        other_debt_eur=100,
    )


def test_staged_rent_reference_path_and_input_immutability() -> None:
    budgets = (
        budget(date(2026, 10, 1)),
        budget(date(2026, 11, 1)),
        budget(date(2026, 12, 1), rent=700),
        budget(date(2027, 1, 1), rent=700),
        budget(date(2027, 2, 1), rent=500),
        budget(date(2027, 3, 1), rent=500),
    )
    original = tuple(item.model_dump() for item in budgets)
    result = simulate_savings(budgets, starting_savings_eur=10_000, retained_reserve_eur=2_000)
    assert [point.contribution_eur for point in result.monthly_path] == [
        900,
        900,
        600,
        600,
        800,
        800,
    ]
    assert [point.closing_savings_eur for point in result.monthly_path] == [
        10_900,
        11_800,
        12_400,
        13_000,
        13_800,
        14_600,
    ]
    assert result.ending_savings_eur == 14_600
    assert result.usable_savings_eur == 12_600
    assert result.viability == "viable"
    assert tuple(item.model_dump() for item in budgets) == original


@pytest.mark.parametrize(
    ("starting", "incomes", "expected_balances", "viability"),
    [
        (1_000, (300, 1_700), (400, 1_200), "viable"),
        (100, (700, 1_200), (-100, 200), "funds_exhausted"),
        (600, (300,), (0,), "viable"),
    ],
)
def test_negative_contributions_and_persistent_exhaustion(
    starting: float,
    incomes: tuple[float, ...],
    expected_balances: tuple[float, ...],
    viability: str,
) -> None:
    months = (date(2026, 12, 1), date(2027, 1, 1))
    budgets = tuple(
        budget(month, income=income, rent=200)
        for month, income in zip(months, incomes, strict=False)
    )
    result = simulate_savings(budgets, starting_savings_eur=starting, retained_reserve_eur=0)
    assert tuple(point.closing_savings_eur for point in result.monthly_path) == expected_balances
    assert result.viability == viability


def test_reserve_can_reduce_usable_savings_to_zero() -> None:
    result = simulate_savings(
        (budget(date(2026, 1, 1)),),
        starting_savings_eur=1_000,
        retained_reserve_eur=2_000,
    )
    assert result.ending_savings_eur == 1_900
    assert result.usable_savings_eur == 0


def test_rounding_epsilon_does_not_hide_or_rewrite_reported_balance() -> None:
    near_zero = PreparedMonthlyBudget(
        month=date(2026, 1, 1),
        net_income_eur=0,
        rent_eur=1e-9,
        nonhousing_expenses_eur=0,
        other_debt_eur=0,
    )
    result = simulate_savings((near_zero,), starting_savings_eur=0, retained_reserve_eur=0)
    assert result.monthly_path[0].closing_savings_eur == -1e-9
    assert result.viability == "viable"


@pytest.mark.parametrize(
    "months",
    [
        (),
        (date(2026, 1, 1), date(2026, 1, 1)),
        (date(2026, 1, 1), date(2026, 3, 1)),
        (date(2026, 2, 1), date(2026, 1, 1)),
    ],
)
def test_invalid_budget_sequences_are_rejected(months: tuple[date, ...]) -> None:
    with pytest.raises(ValueError, match="nonempty|consecutive"):
        simulate_savings(
            tuple(budget(month) for month in months),
            starting_savings_eur=0,
            retained_reserve_eur=0,
        )


@pytest.mark.parametrize("value", [-1, True, float("nan"), float("inf"), "100"])
def test_invalid_savings_scalars_are_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="starting_savings_eur"):
        simulate_savings(
            (budget(date(2026, 1, 1)),),
            starting_savings_eur=value,
            retained_reserve_eur=0,
        )


@pytest.mark.parametrize("value", [-1, True, "100", float("nan"), float("inf")])
def test_invalid_reserve_is_rejected(value: object) -> None:
    with pytest.raises(ValueError, match="retained_reserve_eur"):
        simulate_savings(
            (budget(date(2026, 1, 1)),), starting_savings_eur=0, retained_reserve_eur=value
        )


@pytest.mark.parametrize("budgets", [None, "2026-01-01", iter(()), ({"month": "2026-01-01"},)])
def test_nonsequence_or_unvalidated_budgets_are_rejected(budgets: object) -> None:
    with pytest.raises(ValueError, match="monthly_budgets"):
        simulate_savings(budgets, starting_savings_eur=0, retained_reserve_eur=0)


def test_ending_deficit_remains_signed_and_nonfinite_balances_are_rejected() -> None:
    result = simulate_savings(
        (budget(date(2010, 1, 1), income=0),),
        starting_savings_eur=100,
        retained_reserve_eur=0,
    )
    assert result.ending_savings_eur == -1_000
    assert result.usable_savings_eur == 0
    assert result.viability == "funds_exhausted"
    with pytest.raises(ValueError, match="closing savings.*not finite"):
        simulate_savings(
            (budget(date(2026, 1, 1), income=1e308),),
            starting_savings_eur=1e308,
            retained_reserve_eur=0,
        )
