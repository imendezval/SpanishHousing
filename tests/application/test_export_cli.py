import csv
import io
import json
import subprocess
from pathlib import Path

import pytest

from conftest import FIXTURES
from spain_housing.application import evaluate_scenario
from spain_housing.application.export import export_run, replay_run, run_json, summary_csv
from spain_housing.config import load_scenario
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import Scenario

ROOT = Path(__file__).resolve().parents[2]


def test_complete_cli_build_then_evaluate_and_replay(tmp_path: Path) -> None:
    build = command(
        tmp_path,
        "build-release",
        "--config",
        str(FIXTURES / "recipe.json"),
        "--data-root",
        str(FIXTURES),
        "--release-root",
        str(tmp_path / "releases"),
        "--allow-synthetic",
    )
    assert build.returncode == 0 and not build.stderr
    release = json.loads(build.stdout)["path"]
    check = command(tmp_path, "validate-release", "--release", release, "--allow-synthetic")
    assert check.returncode == 0
    output = tmp_path / "run"
    run = command(
        tmp_path,
        "evaluate-scenario",
        "--defaults",
        str(ROOT / "configs/defaults.yaml"),
        "--scenario",
        str(ROOT / "configs/scenarios/phase4_room_demo.yaml"),
        "--release",
        release,
        "--allow-synthetic",
        "--output-dir",
        str(output),
    )
    assert run.returncode == 0
    replay = command(
        tmp_path,
        "replay-run",
        "--run",
        str(output / "run.json"),
        "--release",
        release,
        "--allow-synthetic",
    )
    assert replay.returncode == 0 and replay.stdout == run.stdout


def evaluate(repo: SnapshotMarketRepository, scenario: Scenario) -> RunResult:
    return evaluate_scenario(
        scenario,
        market_data=repo,
        context=repo.evaluation_context,
        mapped_locations=tuple(loc.location for loc in repo.locations),
    )


def command(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["spain-housing", *args], cwd=tmp_path, text=True, capture_output=True, check=False
    )


def test_deterministic_exports_csv_agreement_and_replay(
    release_dir: Path, scenario: Scenario, tmp_path: Path
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    run = evaluate(repo, scenario)
    assert run_json(run) == run_json(evaluate(repo, scenario))
    assert RunResult.model_validate_json(run_json(run)) == run
    rows = list(csv.DictReader(io.StringIO(summary_csv(run))))
    assert [row["buying_code"] for row in rows] == ["08019", "23050", "28065", "28079"]
    for result, row in zip(run.results, rows, strict=True):
        assert row["calculation_status"] == result.calculation_status
        assert row["dataset_kind"] == "synthetic" and row["dataset_readiness"] == "synthetic_only"
        assert row["affordable_area_status"] == result.affordable_area_m2.status
        if result.purchase:
            assert float(row["maximum_price_eur"]) == result.purchase.maximum_price_eur
            assert (
                float(row["target_cash_shortfall_eur"]) == result.purchase.target_cash_shortfall_eur
            )
        else:
            assert row["maximum_price_eur"] == "" and row["ending_savings_eur"] == ""
    output = export_run(run, tmp_path / "run")
    assert {p.name for p in output.iterdir()} == {"run.json", "summary.csv"}
    assert (output / "run.json").read_text() == run_json(run)
    assert (output / "summary.csv").read_text() == summary_csv(run)
    assert (
        replay_run(
            RunResult.model_validate_json((output / "run.json").read_bytes()),
            market_data=repo,
            context=repo.evaluation_context,
        )
        == run
    )
    with pytest.raises(ValueError, match="already exists"):
        export_run(run, output)
    assert (output / "run.json").read_text() == run_json(run)


@pytest.mark.parametrize(
    "field", ["code_version", "model_version", "runtime_evidence", "release", "result", "legacy"]
)
def test_replay_rejects_mismatched_evidence(
    release_dir: Path, scenario: Scenario, field: str
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    run = evaluate(repo, scenario)
    if field in ("code_version", "model_version"):
        saved = run.model_copy(update={field: "other"})
    elif field == "runtime_evidence":
        saved = run.model_copy(
            update={field: run.runtime_evidence.model_copy(update={"python_version": "0.0.0"})}
        )
    elif field == "release":
        saved = run.model_copy(update={"dataset_release_id": "other"})
    elif field == "result":
        saved = run.model_copy(
            update={
                "results": (
                    run.results[0].model_copy(update={"explanation": "tampered"}),
                    *run.results[1:],
                )
            }
        )
    else:
        saved = run.model_copy(update={"evaluation_context": None, "runtime_evidence": None})
    with pytest.raises(ValueError, match="mismatch|differs|legacy"):
        replay_run(saved, market_data=repo, context=repo.evaluation_context)


def test_export_failure_cleans_only_owned_staging(
    release_dir: Path, scenario: Scenario, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    run = evaluate(repo, scenario)
    unrelated = tmp_path / ".run.other"
    unrelated.mkdir()
    (unrelated / "user").write_text("keep")
    original = Path.write_text

    def fail(self: Path, *args, **kwargs):
        if self.name == "summary.csv":
            raise OSError("simulated disk failure")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail)
    with pytest.raises(OSError, match="disk failure"):
        export_run(run, tmp_path / "run")
    assert not (tmp_path / "run").exists() and (unrelated / "user").read_text() == "keep"
    assert list(tmp_path.glob(".run.*")) == [unrelated]
    assert not (tmp_path / ".run.lock").exists()
    lock = tmp_path / ".run.lock"
    lock.write_bytes(b"other writer")
    with pytest.raises(FileExistsError):
        export_run(run, tmp_path / "run")
    assert lock.read_bytes() == b"other writer"


@pytest.mark.parametrize("example", ["phase4_room_demo", "phase4_staged_growth_demo"])
def test_cli_python_export_replay_outside_checkout(
    release_dir: Path, tmp_path: Path, example: str
) -> None:
    defaults = ROOT / "configs/defaults.yaml"
    config = ROOT / f"configs/scenarios/{example}.yaml"
    output = tmp_path / "economic-run"
    args = [
        "evaluate-scenario",
        "--defaults",
        str(defaults),
        "--scenario",
        str(config),
        "--release",
        str(release_dir),
        "--output-dir",
        str(output),
    ]
    prohibited = command(tmp_path, *args)
    assert prohibited.returncode == 2 and prohibited.stdout == "" and not output.exists()
    result = command(tmp_path, *args, "--allow-synthetic")
    assert result.returncode == 0 and result.stderr == ""
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    expected = evaluate(repo, load_scenario(defaults, config))
    assert result.stdout == run_json(expected) == (output / "run.json").read_text()
    assert expected.results[2].buying_location.code == "28065"
    assert expected.results[2].calculation_status == "missing_input"
    repeat = command(tmp_path, *args, "--allow-synthetic")
    assert repeat.returncode == 2 and repeat.stdout == "" and "already exists" in repeat.stderr
    replay = command(
        tmp_path,
        "replay-run",
        "--run",
        str(output / "run.json"),
        "--release",
        str(release_dir),
        "--allow-synthetic",
        "--output-dir",
        str(tmp_path / "replayed"),
    )
    assert replay.returncode == 0 and replay.stderr == "" and replay.stdout == result.stdout
    explicit = command(
        tmp_path,
        "evaluate-scenario",
        "--defaults",
        str(defaults),
        "--scenario",
        str(config),
        "--release",
        str(release_dir),
        "--allow-synthetic",
        "--locations",
        "28079",
        "08019",
        "99999",
    )
    assert explicit.returncode == 0
    explicit_run = RunResult.model_validate_json(explicit.stdout)
    assert [r.buying_location.code for r in explicit_run.results] == ["08019", "28079", "99999"]
    assert explicit_run.results[-1].calculation_status == "missing_input"
    for codes in [("28079", "28079"), ("8019",), ("Madrid",)]:
        bad = command(
            tmp_path,
            "evaluate-scenario",
            "--defaults",
            str(defaults),
            "--scenario",
            str(config),
            "--release",
            str(release_dir),
            "--allow-synthetic",
            "--locations",
            *codes,
        )
        assert bad.returncode == 2 and bad.stdout == ""


def test_cli_fixed_saving_and_failure_stdout(release_dir: Path, tmp_path: Path) -> None:
    result = command(
        tmp_path,
        "evaluate-scenario",
        "--defaults",
        str(ROOT / "configs/defaults.yaml"),
        "--scenario",
        str(ROOT / "configs/scenarios/joint_saving.yaml"),
        "--release",
        str(release_dir),
        "--allow-synthetic",
    )
    assert result.returncode == 0 and result.stderr == ""
    assert all(
        r.calculation_status == "unsupported"
        for r in RunResult.model_validate_json(result.stdout).results
    )
    saved = tmp_path / "saved.json"
    data = json.loads(result.stdout)
    data["code_version"] = "wrong"
    saved.write_text(json.dumps(data))
    mismatch = command(
        tmp_path,
        "replay-run",
        "--run",
        str(saved),
        "--release",
        str(release_dir),
        "--allow-synthetic",
    )
    assert (
        mismatch.returncode == 2
        and mismatch.stdout == ""
        and "code_version mismatch" in mismatch.stderr
    )
