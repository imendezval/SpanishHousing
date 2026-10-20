"""Installed scenario-validation command and its stdout/stderr contract."""

import subprocess
from pathlib import Path

from spain_housing.models.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "configs/defaults.yaml"
EXAMPLES = ROOT / "configs/scenarios"


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
