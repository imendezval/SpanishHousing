"""Market observation units, evidence and source coherence."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.models.market import MarketLookup, MarketObservation

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests/fixtures/synthetic/market_cases.json"


def test_synthetic_fixture_and_missing_metric() -> None:
    data = json.loads(FIXTURE.read_text())
    observations = [MarketObservation.model_validate(item) for item in data["observations"]]
    assert {item.location.code for item in observations} == {"28079", "08019", "46169"}
    assert {item.metric.value for item in observations} == {
        "purchase_price_per_m2",
        "whole_home_rent_per_m2_month",
        "whole_home_rent_per_month",
        "room_rent_per_month",
    }
    assert all(item.evidence_kind == "synthetic" for item in observations)
    missing = MarketLookup.model_validate(data["missing"])
    assert missing.observation is None


@pytest.mark.parametrize(
    "change",
    [
        {"unit": "eur_per_month"},
        {"value": 0},
        {"value": True},
        {"value": float("nan")},
        {"source_id": "idealista"},
        {"evidence_kind": "estimated"},
        {"period_end": "2026-09-01"},
        {"sample_count": 0},
    ],
)
def test_observation_inconsistency_rejected(change: dict) -> None:
    item = json.loads(FIXTURE.read_text())["observations"][0]
    item.update(change)
    with pytest.raises(ValidationError):
        MarketObservation.model_validate(item)


def test_estimate_requires_method_and_real_source() -> None:
    item = json.loads(FIXTURE.read_text())["observations"][0]
    item.update(
        evidence_kind="estimated",
        source_id="example-report",
        source_url="https://example.org/report",
        estimation_method="documented interpolation",
    )
    assert MarketObservation.model_validate(item).evidence_kind == "estimated"
