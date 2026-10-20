"""Result states, target coherence and serialization contracts."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.config import load_scenario
from spain_housing.models.market import MarketLookup
from spain_housing.models.results import Indicator, PurchaseResult, RunResult

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/synthetic/market_cases.json"


def test_lookup_and_indicator_states() -> None:
    with pytest.raises(ValidationError):
        MarketLookup(
            status="missing",
            observation=json.loads(FIXTURE.read_text())["observations"][0],
            reason="gap",
        )
    assert Indicator(status="missing", reason="no room data").value is None
    with pytest.raises(ValidationError):
        Indicator(status="available", value=None)


def test_run_metadata_round_trip() -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/room_only.yaml"
    )
    run = RunResult(
        schema_version=1,
        resolved_scenario=scenario,
        dataset_release_id="synthetic-test-1",
        model_version="phase1-contracts",
        code_version="test",
        results=(),
    )
    assert RunResult.model_validate_json(run.model_dump_json()) == run


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
