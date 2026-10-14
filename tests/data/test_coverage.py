import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from fixtures.synthetic.expand import GAPS, prepare_fixture
from spain_housing.application import evaluate_scenario
from spain_housing.cli import main
from spain_housing.config import load_scenario
from spain_housing.ingestion.release import build_release
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.scenario import Scenario
from spain_housing.storage.release import load_release

ROOT = Path(__file__).resolve().parents[2]


def test_report_is_validated_ordered_immutable_and_cli_owned(expanded_dir, capsys):
    repository = SnapshotMarketRepository.from_release(expanded_dir, allow_synthetic=True)
    report = repository.coverage_report
    assert report.schema_version == 1 and report.kind == "synthetic"
    assert report.counts.model_dump() == dict(expected=48, available=43, missing=4, unsupported=1)
    assert report.evidence.model_dump() == dict(observed=0, estimated=0, synthetic=43)
    assert [(p.profile.profile_id, p.counts.available) for p in report.profiles] == [
        ("rent", 15),
        ("room", 13),
        ("sale", 15),
    ]
    assert [
        (c.location_code, c.profile_id, c.status) for c in report.cells if c.status != "available"
    ] == [(code, profile, status) for (code, profile), status in sorted(GAPS.items())]
    assert len(report.cells) == len(report.locations) * len(report.profiles)
    assert list(report.cells) == sorted(report.cells, key=lambda c: (c.location_code, c.profile_id))
    assert report.counts == load_release(expanded_dir, allow_synthetic=True).manifest.coverage
    assert sum(p.evidence.synthetic for p in report.profiles) == report.counts.available
    with pytest.raises(ValidationError):
        report.readiness = "ready"
    before = sorted(p.name for p in expanded_dir.iterdir())
    assert main(["inspect-release", "--release", str(expanded_dir), "--allow-synthetic"]) == 0
    assert json.loads(capsys.readouterr().out) == report.model_dump(mode="json")
    assert sorted(p.name for p in expanded_dir.iterdir()) == before
    assert main(["inspect-release", "--release", str(expanded_dir)]) == 2
    assert "opt-in" in capsys.readouterr().err
    (expanded_dir / "coverage.json").write_bytes(b"[]")
    assert main(["inspect-release", "--release", str(expanded_dir), "--allow-synthetic"]) == 2
    assert "payload hash/size mismatch" in capsys.readouterr().err


def test_partial_products_and_suitability_preserve_engine(expanded_dir):
    repo = SnapshotMarketRepository.from_release(expanded_dir, allow_synthetic=True)
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/phase4_room_demo.yaml"
    )

    def run(value):
        return {
            r.buying_location.code: r
            for r in evaluate_scenario(
                value,
                market_data=repo,
                context=repo.evaluation_context,
                mapped_locations=tuple(loc.location for loc in repo.locations),
            ).results
        }

    room = run(scenario)
    assert room["28079"].purchase.maximum_price_eur == pytest.approx(38000)
    assert room["08019"].purchase.maximum_price_eur == pytest.approx(36000)
    assert room["23050"].purchase.maximum_price_eur == pytest.approx(44000)
    assert room["08015"].calculation_status == "missing_input"
    assert room["44216"].calculation_status == "available" and room["44216"].savings
    assert room["44216"].purchase and room["44216"].purchase.target_price_eur is None
    assert room["44216"].affordable_area_m2.status == "missing"
    data = scenario.model_dump(mode="json")
    data["living_stages"] = [
        dict(
            arrangement="flat_alone",
            start_month_offset=0,
            end_month_offset=12,
            rent_share=1,
            rental_area_m2=80,
            rent_includes_utilities=False,
        )
    ]
    flat = run(Scenario.model_validate(data))
    assert flat["08015"].calculation_status == "available"
    assert flat["28065"].calculation_status == "available"
    # A source-declared unsupported cell is still an absent exact query row.
    # Report that source gap separately from the existing query-capability rules.
    assert flat["41038"].calculation_status == "missing_input"
    data["market_selection"]["maximum_reference_age_months"] = 0
    data["market_policy"]["base_month"] = "2026-11-01"
    data["start_month"] = "2026-11-01"
    before = repo.coverage_report
    assert run(Scenario.model_validate(data))["08015"].calculation_status == "missing_input"
    assert repo.coverage_report == before


def test_rebuild_restore_and_segmented_case(tmp_path):
    first = tmp_path / "inputs-a"
    second = tmp_path / "inputs-b"
    recipe = prepare_fixture(first, segmented=True)
    recipe2 = prepare_fixture(second, segmented=True)
    assert recipe == recipe2
    a = build_release(recipe, data_root=first, release_root=tmp_path / "a", allow_synthetic=True)
    b = build_release(recipe2, data_root=second, release_root=tmp_path / "b", allow_synthetic=True)
    assert a.name == b.name
    assert {p.name: p.read_bytes() for p in a.iterdir()} == {
        p.name: p.read_bytes() for p in b.iterdir()
    }
    repo = SnapshotMarketRepository.from_release(a, allow_synthetic=True)
    assert (
        repo.coverage_report.counts.expected == 64 and repo.coverage_report.counts.available == 59
    )
    from spain_housing.models.market import MarketQuery, MarketSegment
    from spain_housing.models.scenario import GeographicReference

    query = MarketQuery(
        location=GeographicReference(level="municipality", code="08015"),
        metric="purchase_price_per_m2",
        period_start="2026-09-01",
        period_end="2026-10-01",
        segment=MarketSegment(property_type="flat", bedrooms=2),
    )
    assert repo.get(query).status == "available"
    assert (
        repo.get(
            query.model_copy(update={"segment": MarketSegment(property_type="flat", bedrooms=3)})
        ).status
        == "unsupported"
    )
