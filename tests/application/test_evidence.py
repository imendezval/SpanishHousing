import csv
import io
import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.application import evaluate_scenario
from spain_housing.application import version as evidence
from spain_housing.application.export import run_json, summary_csv
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.results import LocationResult
from spain_housing.models.scenario import GeographicReference, Scenario

MADRID = GeographicReference(level="municipality", code="28079")


def test_fingerprint_tracks_actual_source_not_paths_times_or_caches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    package = tmp_path / "package"
    (package / "application").mkdir(parents=True)
    (package / "__init__.py").write_text("# actual source\n")
    module = package / "application/version.py"
    module.write_text("# version source\n")
    monkeypatch.setattr(evidence, "__file__", str(module))
    first = evidence.code_version()
    os.utime(module, (0, 0))
    (package / "__pycache__").mkdir()
    (package / "__pycache__/test.pyc").write_bytes(b"cache")
    assert evidence.code_version() == first
    (package / "cli.py").write_text("# CLI calculation composition\n")
    assert evidence.code_version() != first
    (package / "cli.py").unlink()
    assert evidence.code_version() == first
    module.write_text("# changed actual source\n")
    assert evidence.code_version() != first


def test_finite_encoding_unbounded_csv_and_buying_evidence(
    release_dir: Path, scenario: Scenario
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    data = scenario.model_dump(mode="json")
    data["mortgage"]["financed_fraction"] = 1
    data["purchase_costs"]["allowance_fraction"] = 0
    run = evaluate_scenario(
        Scenario.model_validate(data),
        market_data=repo,
        context=repo.evaluation_context,
        mapped_locations=(MADRID,),
    )
    row = next(csv.DictReader(io.StringIO(summary_csv(run))))
    assert row["unbounded_cash_constraint"] == "True" and row["savings_price_limit_eur"] == ""
    bad = run.results[0].model_copy(
        update={
            "affordable_area_m2": run.results[0].affordable_area_m2.model_copy(
                update={"value": float("nan")}
            )
        }
    )
    with pytest.raises(ValueError):
        run_json(run.model_copy(update={"results": (bad,)}))
    data = run.results[0].model_dump(mode="json")
    data["affordable_area_m2"]["observations"] = [
        run.results[0].market_inputs[0].observation.model_dump(mode="json")
    ]
    with pytest.raises(ValidationError, match="buying evidence"):
        LocationResult.model_validate(data)


def test_aggregate_overflow_is_error_not_missing(release_dir: Path, scenario: Scenario) -> None:
    data = scenario.model_dump(mode="json")
    data["participants"][0]["net_annual_income"]["milestones"][0]["amount_eur"] = 1e308
    second = dict(data["participants"][0], participant_id="second")
    data["participants"].append(second)
    data["saver_ids"].append("second")
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    with pytest.raises(ValueError, match="aggregate overflow"):
        evaluate_scenario(
            Scenario.model_validate(data),
            market_data=repo,
            context=repo.evaluation_context,
            mapped_locations=(MADRID,),
        )
