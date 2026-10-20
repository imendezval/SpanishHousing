"""Lossless draft controls and preservation of participant trajectories."""

from copy import deepcopy
from pathlib import Path

import pytest

from spain_housing.config import load_scenario
from spain_housing.ui.controls import draft_scenario, scenario_draft

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "name", ["room_only", "phase4_room_demo", "phase4_staged_growth_demo", "joint_saving"]
)
def test_lossless_roundtrip(name: str) -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / f"configs/scenarios/{name}.yaml"
    )
    draft = scenario_draft(scenario)
    assert draft_scenario(draft) == scenario
    original = deepcopy(draft)
    draft_scenario(draft)
    assert draft == original


def test_participant_removal_and_future_paths_retained() -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/phase4_staged_growth_demo.yaml"
    )
    draft = scenario_draft(scenario)
    assert any(point["month_offset"] > scenario.saving_months for point in draft["income"])
    draft["participants"].pop()
    with pytest.raises(ValueError, match="unknown participant"):
        draft_scenario(draft)
