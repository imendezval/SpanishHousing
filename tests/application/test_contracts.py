from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.config import load_scenario
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.results import Indicator, RunResult
from spain_housing.models.scenario import MarketSelectionPolicy

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "change",
    [
        {"maximum_reference_age_months": True},
        {"maximum_reference_age_months": -1},
        {"allow_pooled_property_proxy": 1},
        {"profile_ids": [""]},
        {"profile_ids": ["a", "a"]},
        {"strategy": "nearest"},
    ],
)
def test_selection_strict(change: dict) -> None:
    with pytest.raises(ValidationError):
        MarketSelectionPolicy.model_validate(change)


def test_defaulted_scenario_and_explicit_null() -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/room_only.yaml"
    )
    data = scenario.model_dump(mode="json")
    data.pop("market_selection")
    assert type(scenario).model_validate(data).market_selection == MarketSelectionPolicy()
    data["market_selection"] = None
    with pytest.raises(ValidationError):
        type(scenario).model_validate(data)
    assert Indicator(status="available", value=0).value == 0
    assert Indicator(status="available", value=1.2).value == 1.2
    assert Indicator(status="unviable", reason="cash exhausted").value is None


def test_public_context_is_immutable_and_run_consistent(release_dir: Path) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    assert context.kind == "synthetic" and len(context.locations) == 4
    with pytest.raises(ValidationError):
        context.release_id = "other"
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/room_only.yaml"
    )
    with pytest.raises(ValidationError, match="disagree"):
        RunResult(
            schema_version=1,
            resolved_scenario=scenario,
            dataset_release_id="other",
            model_version="test",
            code_version="test",
            results=(),
            evaluation_context=context,
        )
