from pathlib import Path

import pytest

from spain_housing.application.export import run_json, summary_csv
from spain_housing.cli import main
from spain_housing.config import load_scenario
from spain_housing.launcher import compose
from spain_housing.ui.controls import draft_scenario, scenario_draft
from spain_housing.ui.state import Session

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("dataset", ["release_dir", "expanded_dir"])
@pytest.mark.parametrize("name", ["phase4_room_demo", "phase4_staged_growth_demo"])
def test_applied_exports_match_cli_and_replay(name, dataset, request, tmp_path, capsys):
    release_dir = request.getfixturevalue(dataset)
    initial, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / f"configs/scenarios/{name}.yaml",
        release_dir,
        allow_synthetic=True,
    )
    # Reconstruct exactly what the complete controls submit.
    session = Session(scenario_draft(initial))
    assert draft_scenario(session.draft) == initial
    assert session.apply(session.draft, services)
    scenario = tmp_path / "scenario.json"
    scenario.write_text(services.encode_scenario(session.applied.resolved_scenario))
    assert load_scenario(ROOT / "configs/defaults.yaml", scenario) == initial
    output = tmp_path / "cli"
    common = ["--release", str(release_dir), "--allow-synthetic"]
    assert (
        main(
            [
                "evaluate-scenario",
                "--defaults",
                str(ROOT / "configs/defaults.yaml"),
                "--scenario",
                str(scenario),
                "--locations",
                *[r.code for r in services.destinations],
                "--output-dir",
                str(output),
                *common,
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert (output / "run.json").read_text() == run_json(session.applied)
    assert (output / "summary.csv").read_text() == summary_csv(session.applied)
    replay = tmp_path / "replay"
    assert (
        main(
            [
                "replay-run",
                "--run",
                str(output / "run.json"),
                "--output-dir",
                str(replay),
                *common,
            ]
        )
        == 0
    )
    assert (replay / "run.json").read_bytes() == (output / "run.json").read_bytes()
