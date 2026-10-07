import math

import pytest

from spain_housing.finance.mortgage import (
    maximum_loan,
    maximum_mortgage_payment,
    monthly_payment,
)
from spain_housing.models.scenario import MortgageAssumptions


def mortgage(rate: float, *, years: int = 25) -> MortgageAssumptions:
    return MortgageAssumptions(
        financed_fraction=0.8,
        maximum_debt_ratio=0.35,
        term_years=years,
        annual_nominal_interest_fraction=rate,
    )


def test_zero_and_positive_rate_references() -> None:
    assert monthly_payment(200_000, mortgage(0)) == pytest.approx(666.6666666666666)
    assert maximum_loan(700, mortgage(0)) == 210_000
    assert monthly_payment(200_000, mortgage(0.035)) == pytest.approx(
        1_001.247140518986, rel=1e-10, abs=1e-7
    )
    assert maximum_loan(700, mortgage(0.035)) == pytest.approx(
        139_825.61780644136, rel=1e-10, abs=1e-7
    )


def test_small_positive_rate_is_stable_and_distinct_from_zero() -> None:
    small = monthly_payment(200_000, mortgage(1e-12))
    zero = monthly_payment(200_000, mortgage(0))
    assert math.isfinite(small)
    assert small > zero
    assert small == pytest.approx(666.6666666750278, rel=1e-12)


def test_total_debt_capacity() -> None:
    assert maximum_mortgage_payment(2_000, 100, 0.35) == 600
    assert maximum_mortgage_payment(2_000, 700, 0.35) == 0
    assert maximum_mortgage_payment(0, 0, 0.35) == 0


def test_round_trip_and_monotonicity_grid() -> None:
    for rate in (0.0, 0.01, 0.035, 0.1):
        for principal in (0.0, 1.0, 200_000.0):
            assumptions = mortgage(rate)
            assert maximum_loan(
                monthly_payment(principal, assumptions), assumptions
            ) == pytest.approx(principal)
    assert maximum_loan(700, mortgage(0.035, years=30)) > maximum_loan(
        700, mortgage(0.035, years=20)
    )
    assert maximum_loan(700, mortgage(0.05)) < maximum_loan(700, mortgage(0.02))


@pytest.mark.parametrize("value", [-1, True, float("nan"), float("inf"), "100"])
def test_invalid_money_scalars_are_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        monthly_payment(value, mortgage(0.035))  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        maximum_loan(value, mortgage(0.035))  # type: ignore[arg-type]


@pytest.mark.parametrize("ratio", [-1, 1.1, True, float("nan"), float("inf")])
def test_invalid_debt_ratio_is_rejected(ratio: object) -> None:
    with pytest.raises(ValueError):
        maximum_mortgage_payment(2_000, 0, ratio)  # type: ignore[arg-type]
