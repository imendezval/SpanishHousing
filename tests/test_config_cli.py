"""Loading, merge, CLI failure modes and deterministic JSON."""

import json
import subprocess
from pathlib import Path

import pytest

from spain_housing.config import load_mapping, load_scenario, merge_mappings, scenario_json
from spain_housing.models.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "configs/defaults.yaml"
EXAMPLES = ROOT / "configs/scenarios"


@pytest.mark.parametrize(
    "content,suffix",
    [("a: 1\na: 2\n", ".yaml"), ('{"a":1,"a":2}', ".json"), ("a:\n  b: 1\n  b: 2\n", ".yaml")],
)
def test_duplicate_keys_fail(tmp_path: Path, content: str, suffix: str) -> None:
    path = tmp_path / f"bad{suffix}"
    path.write_text(content)
    with pytest.raises(ValueError, match="duplicate"):
        load_mapping(path)


def test_merge_replaces_lists_and_nulls_without_mutation() -> None:
    defaults = {"nested": {"a": 1, "items": [1, 2], "b": 2}}
    changed = merge_mappings(defaults, {"nested": {"items": [3], "b": None}})
    assert changed == {"nested": {"a": 1, "items": [3], "b": None}}
    assert defaults["nested"]["items"] == [1, 2]


@pytest.mark.parametrize("name", ["room_only", "staged_living", "joint_saving"])
def test_examples_round_trip(name: str) -> None:
    scenario = load_scenario(DEFAULTS, EXAMPLES / f"{name}.yaml")
    assert Scenario.model_validate_json(scenario_json(scenario)) == scenario
    assert scenario_json(scenario) == scenario_json(scenario)


def test_sequential_loads_do_not_change_defaults() -> None:
    before = load_mapping(DEFAULTS)
    load_scenario(DEFAULTS, EXAMPLES / "joint_saving.yaml")
    load_scenario(DEFAULTS, EXAMPLES / "room_only.yaml")
    assert load_mapping(DEFAULTS) == before


def test_missing_interest_fails(tmp_path: Path) -> None:
    scenario = load_scenario(DEFAULTS, EXAMPLES / "room_only.yaml")
    data = scenario.model_dump(mode="json")
    del data["mortgage"]["annual_nominal_interest_fraction"]
    path = tmp_path / "missing.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="annual_nominal_interest_fraction"):
        load_scenario(DEFAULTS, path)


def test_cli_from_another_working_directory(tmp_path: Path) -> None:
    command = [
        "spain-housing",
        "validate-scenario",
        "--defaults",
        str(DEFAULTS),
        "--scenario",
        str(EXAMPLES / "room_only.yaml"),
        "--json",
    ]
    result = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert Scenario.model_validate_json(result.stdout).purchase_month.isoformat() == "2033-10-01"
    bad = subprocess.run(
        command[:-1] + ["--scenario", str(tmp_path / "missing.yaml")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad.returncode == 2
    assert bad.stdout == ""
    assert "missing.yaml" in bad.stderr
