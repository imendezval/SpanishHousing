"""Fixed-financing purchase capacity and optional target diagnostics."""

from typing import Literal

from spain_housing.models.contracts import PurchaseContext
from spain_housing.models.results import PurchaseResult, SavingsResult
from spain_housing.models.scenario import MortgageAssumptions

from ._validation import finite_result, nonnegative, positive
from .costs import ProportionalPurchaseCostPolicy, required_upfront_cash
from .mortgage import maximum_loan, maximum_mortgage_payment, monthly_payment

BINDING_TOLERANCE_EUR = 0.01


def calculate_fixed_financing_capacity(
    *,
    savings_result: SavingsResult,
    borrower_monthly_net_income_eur: float,
    borrower_monthly_other_debt_eur: float,
    mortgage: MortgageAssumptions,
    cost_policy: ProportionalPurchaseCostPolicy,
    purchase_context: PurchaseContext,
    target_price_eur: float | None = None,
) -> PurchaseResult:
    """Calculate the cash and repayment limits for a fixed financed fraction."""
    if not isinstance(savings_result, SavingsResult):
        raise ValueError("savings_result must be SavingsResult")
    if savings_result.viability == "funds_exhausted":
        raise ValueError("purchase capacity is unavailable after savings funds were exhausted")
    income = nonnegative(borrower_monthly_net_income_eur, "borrower_monthly_net_income_eur")
    other_debt = nonnegative(borrower_monthly_other_debt_eur, "borrower_monthly_other_debt_eur")
    if not isinstance(mortgage, MortgageAssumptions):
        raise ValueError("mortgage must be MortgageAssumptions")
    if not isinstance(cost_policy, ProportionalPurchaseCostPolicy):
        raise ValueError("cost_policy must be ProportionalPurchaseCostPolicy")
    if not isinstance(purchase_context, PurchaseContext):
        raise ValueError("purchase_context must be PurchaseContext")

    financed_fraction = mortgage.financed_fraction
    upfront_fraction = cost_policy.upfront_cash_fraction(financed_fraction)
    savings_limit = (
        None
        if upfront_fraction == 0
        else finite_result(
            savings_result.usable_savings_eur / upfront_fraction, "savings price limit"
        )
    )
    payment_limit = maximum_mortgage_payment(income, other_debt, mortgage.maximum_debt_ratio)
    loan_limit = maximum_loan(payment_limit, mortgage)
    mortgage_limit = finite_result(loan_limit / financed_fraction, "mortgage price limit")
    maximum_price = mortgage_limit if savings_limit is None else min(savings_limit, mortgage_limit)
    binding = _binding_constraint(savings_limit, mortgage_limit)

    target_price = target_loan = target_cash = target_payment = None
    cash_shortfall = payment_shortfall = None
    if target_price_eur is not None:
        target_price = positive(target_price_eur, "target_price_eur")
        target_loan = finite_result(financed_fraction * target_price, "target loan")
        target_cash = required_upfront_cash(
            target_price,
            financed_fraction=financed_fraction,
            cost_policy=cost_policy,
            context=purchase_context,
        )
        target_payment = monthly_payment(target_loan, mortgage)
        cash_shortfall = max(0.0, target_cash - savings_result.usable_savings_eur)
        payment_shortfall = max(0.0, target_payment - payment_limit)

    return PurchaseResult(
        savings_price_limit_eur=savings_limit,
        mortgage_price_limit_eur=mortgage_limit,
        maximum_price_eur=maximum_price,
        binding_constraint=binding,
        target_price_eur=target_price,
        target_loan_eur=target_loan,
        target_upfront_cash_eur=target_cash,
        target_monthly_payment_eur=target_payment,
        target_cash_shortfall_eur=cash_shortfall,
        target_payment_shortfall_eur=payment_shortfall,
    )


def _binding_constraint(
    savings_limit_eur: float | None, mortgage_limit_eur: float
) -> Literal["savings", "mortgage", "both"]:
    if savings_limit_eur is None:
        return "mortgage"
    if abs(savings_limit_eur - mortgage_limit_eur) <= BINDING_TOLERANCE_EUR:
        return "both"
    return "savings" if savings_limit_eur < mortgage_limit_eur else "mortgage"
