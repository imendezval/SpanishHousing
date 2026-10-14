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
from spain_housing.models.dataset import BuildRecipe
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


def test_simulated_evidence_label_aggregation(expanded_dir, tmp_path):
    """Pure label counting with test records; never publish these mixed inputs."""
    from spain_housing.markets.coverage import coverage_report

    bundle = load_release(expanded_dir, allow_synthetic=True)
    rows = list(bundle.observations)
    for index, kind in enumerate(("observed", "estimated")):
        data = rows[index].observation.model_dump(mode="json")
        data.update(
            evidence_kind=kind,
            source_id="test-only-publisher",
            source_url="https://example.invalid/test-only-not-a-capture",
            estimation_method="Hypothetical publisher method for unit test"
            if kind == "estimated"
            else None,
        )
        from spain_housing.models.market import MarketObservation

        rows[index] = rows[index].model_copy(
            update={"observation": MarketObservation.model_validate(data)}
        )
    report = coverage_report(bundle.manifest, bundle.locations, bundle.coverage, tuple(rows))
    assert report.evidence.model_dump() == dict(observed=1, estimated=1, synthetic=41)
    assert sum(p.evidence.observed for p in report.profiles) == 1
    assert sum(p.evidence.estimated for p in report.profiles) == 1
    from spain_housing.storage.release import write_release

    # Such hypothetical records cannot enter the synthetic release pipeline.
    with pytest.raises(ValueError):
        write_release(
            tmp_path / "forbidden",
            recipe=bundle.manifest.recipe,
            observations=tuple(rows),
            boundaries=bundle.boundaries,
            allow_synthetic=True,
        )
    assert not (tmp_path / "forbidden").exists()


def test_expanded_newer_gap_never_falls_back_to_available_older_cell(tmp_path):
    import csv
    from datetime import date

    from spain_housing.models.market import MarketQuery, MarketSegment
    from spain_housing.models.scenario import GeographicReference
    from spain_housing.storage.release import sha256

    inputs = tmp_path / "inputs"
    recipe = prepare_fixture(inputs)
    data = recipe.model_dump(mode="json")
    profile = next(p for p in data["profiles"] if p["profile_id"] == "sale").copy()
    profile.update(profile_id="older-sale", period_start="2026-08-01", period_end="2026-09-01")
    data["profiles"].append(profile)
    file = inputs / "prices.csv"
    with file.open() as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    older = next(row for row in rows if row["profile_id"] == "sale").copy()
    older.update(
        profile_id="older-sale",
        source_location="Synthetic Teruel",
        raw_value="3000",
        period_start="2026-08-01",
        period_end="2026-09-01",
        source_locator="self-authored:older-teruel",
    )
    with file.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([*rows, older])
    capture = next(c for c in data["captures"] if c["capture_id"] == "prices")
    capture.update(sha256=sha256(file.read_bytes()), byte_size=file.stat().st_size)
    path = build_release(
        BuildRecipe.model_validate(data),
        data_root=inputs,
        release_root=tmp_path / "releases",
        allow_synthetic=True,
    )
    repo = SnapshotMarketRepository.from_release(path, allow_synthetic=True)
    query = MarketQuery(
        location=GeographicReference(level="municipality", code="44216"),
        metric="purchase_price_per_m2",
        period_start=date(2026, 8, 1),
        period_end=date(2026, 9, 1),
        segment=MarketSegment(property_type="pooled"),
    )
    assert repo.get(query).status == "available"
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/phase4_room_demo.yaml"
    )
    run = evaluate_scenario(
        scenario,
        market_data=repo,
        context=repo.evaluation_context,
        mapped_locations=(query.location,),
    )
    assert run.results[0].purchase and run.results[0].affordable_area_m2.status == "missing"
    assert repo.coverage_report.counts.available == 44
    assert any(
        c.location_code == "44216" and c.profile_id == "sale" and c.status == "missing"
        for c in repo.coverage_report.cells
    )
