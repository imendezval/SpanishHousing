"""Purchase-cost policies and common upfront cash arithmetic."""

from dataclasses import dataclass

from spain_housing.models.contracts import (
    PurchaseContext,
    PurchaseCostBreakdown,
    PurchaseCostPolicy,
)
from spain_housing.models.scenario import PurchaseCostAssumptions

from ._validation import finite_result, nonnegative


@dataclass(frozen=True, slots=True)
class ProportionalPurchaseCostPolicy:
    """Apply one explicit allowance fraction to the property price."""

    assumptions: PurchaseCostAssumptions

    def __post_init__(self) -> None:
        if not isinstance(self.assumptions, PurchaseCostAssumptions):
            raise ValueError("assumptions must be PurchaseCostAssumptions")

    def costs(self, price_eur: float, context: PurchaseContext) -> PurchaseCostBreakdown:
        price = nonnegative(price_eur, "price_eur")
        if not isinstance(context, PurchaseContext):
            raise ValueError("context must be PurchaseContext")
        return PurchaseCostBreakdown(
            purchase_cost_eur=finite_result(
                price * self.assumptions.allowance_fraction, "purchase cost"
            ),
            mortgage_formalisation_cost_eur=0,
        )

    def upfront_cash_fraction(self, financed_fraction: float) -> float:
        financed = _financed_fraction(financed_fraction)
        return finite_result(
            1 - financed + self.assumptions.allowance_fraction,
            "upfront cash fraction",
        )


def _financed_fraction(value: float) -> float:
    fraction = nonnegative(value, "financed_fraction")
    if fraction == 0 or fraction > 1:
        raise ValueError("financed_fraction must be greater than 0 and at most 1")
    return fraction


def required_upfront_cash(
    price_eur: float,
    *,
    financed_fraction: float,
    cost_policy: PurchaseCostPolicy,
    context: PurchaseContext,
) -> float:
    """Return down payment plus each policy-supplied upfront cost exactly once."""
    price = nonnegative(price_eur, "price_eur")
    financed = _financed_fraction(financed_fraction)
    if not isinstance(context, PurchaseContext):
        raise ValueError("context must be PurchaseContext")
    costs = cost_policy.costs(price, context)
    return finite_result(
        (1 - financed) * price + costs.purchase_cost_eur + costs.mortgage_formalisation_cost_eur,
        "required upfront cash",
    )
