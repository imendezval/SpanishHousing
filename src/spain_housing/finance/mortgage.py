"""Fixed-rate, level monthly mortgage payments in nominal euros."""

import math

from spain_housing.models.scenario import MortgageAssumptions

from ._validation import finite_result, nonnegative


def _annuity_factor(mortgage: MortgageAssumptions) -> float:
    if not isinstance(mortgage, MortgageAssumptions):
        raise ValueError("mortgage must be MortgageAssumptions")
    try:
        periods = float(12 * mortgage.term_years)
    except OverflowError as exc:
        raise ValueError("mortgage term is too large for a finite annuity factor") from exc
    finite_result(periods, "mortgage payment count")
    rate = mortgage.annual_nominal_interest_fraction / 12
    if rate == 0:
        return periods
    factor = -math.expm1(-periods * math.log1p(rate)) / rate
    return finite_result(factor, "annuity factor")


def monthly_payment(principal_eur: float, mortgage: MortgageAssumptions) -> float:
    """Monthly EUR payment, first due one month after origination."""
    principal = nonnegative(principal_eur, "principal_eur")
    return finite_result(principal / _annuity_factor(mortgage), "monthly payment")


def maximum_loan(monthly_payment_eur: float, mortgage: MortgageAssumptions) -> float:
    """Principal in EUR supported by a monthly EUR payment cap."""
    payment = nonnegative(monthly_payment_eur, "monthly_payment_eur")
    return finite_result(payment * _annuity_factor(mortgage), "maximum loan")


def maximum_mortgage_payment(
    net_monthly_income_eur: float,
    other_monthly_debt_eur: float,
    maximum_debt_ratio: float,
) -> float:
    """Available monthly mortgage payment after all other borrower debt."""
    income = nonnegative(net_monthly_income_eur, "net_monthly_income_eur")
    debt = nonnegative(other_monthly_debt_eur, "other_monthly_debt_eur")
    ratio = nonnegative(maximum_debt_ratio, "maximum_debt_ratio")
    if ratio > 1:
        raise ValueError("maximum_debt_ratio must be at most 1")
    return finite_result(max(0.0, ratio * income - debt), "maximum mortgage payment")
