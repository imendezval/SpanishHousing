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
            starting_savings_eur=value,  # type: ignore[arg-type]
            retained_reserve_eur=0,
        )
