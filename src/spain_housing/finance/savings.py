"""Monthly cash accumulation from already prepared household budgets."""

from collections.abc import Sequence

from spain_housing.models.base import add_months
from spain_housing.models.results import MonthlySavingsPoint, PreparedMonthlyBudget, SavingsResult

from ._validation import finite_result, nonnegative

CASH_EXHAUSTION_EPSILON_EUR = 1e-8


def simulate_savings(
    monthly_budgets: Sequence[PreparedMonthlyBudget],
    *,
    starting_savings_eur: float,
    retained_reserve_eur: float,
) -> SavingsResult:
    """Accumulate signed EUR/month contributions; retain the reserve at purchase."""
    balance = nonnegative(starting_savings_eur, "starting_savings_eur")
    reserve = nonnegative(retained_reserve_eur, "retained_reserve_eur")
    if not isinstance(monthly_budgets, Sequence) or isinstance(monthly_budgets, (str, bytes)):
        raise ValueError("monthly_budgets must be a nonempty sequence")
    if not monthly_budgets:
        raise ValueError("monthly_budgets must be a nonempty sequence")
    path: list[MonthlySavingsPoint] = []
    exhausted = False
    previous = None
    for budget in monthly_budgets:
        if not isinstance(budget, PreparedMonthlyBudget):
            raise ValueError("monthly_budgets must contain PreparedMonthlyBudget records")
        if previous is not None and budget.month != add_months(previous, 1):
            raise ValueError("monthly_budgets must have consecutive ascending months")
        contribution = finite_result(
            budget.net_income_eur
            - budget.rent_eur
            - budget.nonhousing_expenses_eur
            - budget.other_debt_eur,
            "monthly contribution",
        )
        balance = finite_result(balance + contribution, "closing savings")
        exhausted |= balance < -CASH_EXHAUSTION_EPSILON_EUR
        path.append(
            MonthlySavingsPoint(
                month=budget.month,
                contribution_eur=contribution,
                closing_savings_eur=balance,
            )
        )
        previous = budget.month
    return SavingsResult(
        monthly_path=tuple(path),
        ending_savings_eur=balance,
        usable_savings_eur=finite_result(max(0.0, balance - reserve), "usable savings"),
        viability="funds_exhausted" if exhausted else "viable",
    )
