import pytest
from pydantic import ValidationError

from spain_housing.models.results import PurchaseResult


def test_purchase_result_target_coherence_and_round_trip() -> None:
    base = dict(
        savings_price_limit_eur=200_000,
        mortgage_price_limit_eur=300_000,
        maximum_price_eur=200_000,
        binding_constraint="savings",
    )
    finite = PurchaseResult(**base)
    assert PurchaseResult.model_validate_json(finite.model_dump_json()) == finite
    unbounded = PurchaseResult(**(base | {"savings_price_limit_eur": None}))
    assert PurchaseResult.model_validate_json(unbounded.model_dump_json()) == unbounded
    with pytest.raises(ValidationError, match="all present or all absent"):
        PurchaseResult(**(base | {"target_price_eur": 250_000}))
    target = PurchaseResult(
        **base,
        target_price_eur=250_000,
        target_loan_eur=200_000,
        target_upfront_cash_eur=75_000,
        target_monthly_payment_eur=1_000,
        target_cash_shortfall_eur=15_000,
        target_payment_shortfall_eur=0,
    )
    assert PurchaseResult.model_validate_json(target.model_dump_json()) == target
