"""Self-authored geography fixtures; these shapes are not official observations."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from fixtures.synthetic.atlas import atlas_inputs, demo_config
from spain_housing.ingestion.atlas import build_geography
from spain_housing.models.dataset import BuildRecipe, BuildRecipeV2
from spain_housing.storage.files import canonical_json, sha256, strict_json
from spain_housing.storage.geography import load_geography
from spain_housing.storage.release import validate_recipe


def test_independent_atlas_identity_metadata_and_immutable_publication(tmp_path: Path) -> None:
    recipe = atlas_inputs(tmp_path / "raw")
    path = build_geography(recipe, data_root=tmp_path / "raw", artifact_root=tmp_path / "atlas")
    bundle = load_geography(path)
    assert [m.code for m in bundle.registry] == ["28001", "28002"]
    assert bundle.manifest.counts.municipalities == 2
    assert bundle.manifest.counts.provinces == 1
    assert (
        build_geography(recipe, data_root=tmp_path / "raw", artifact_root=tmp_path / "atlas")
        == path
    )
    (path / "canonical.geojson").write_bytes(b"corrupt")
    # Economic metadata reads have an explicit narrow scope; full verification detects corruption.
    assert load_geography(path, full=False).registry == bundle.registry
    with pytest.raises(ValueError, match="size mismatch"):
        load_geography(path)
    with pytest.raises(ValueError):
        build_geography(recipe, data_root=tmp_path / "raw", artifact_root=tmp_path / "atlas")


@pytest.mark.parametrize("defect", ["duplicate", "axis", "level", "pagination", "edge"])
def test_official_assembly_rejects_identity_topology_and_incomplete_pages(
    tmp_path: Path, defect: str
) -> None:
    recipe = atlas_inputs(tmp_path / "raw", defect=defect)
    with pytest.raises(ValueError):
        build_geography(recipe, data_root=tmp_path / "raw", artifact_root=tmp_path / "atlas")
    assert not (tmp_path / "atlas").exists()


def test_market_versions_are_strict_and_legacy_shape_is_unchanged(recipe: BuildRecipe) -> None:
    raw = recipe.model_dump(mode="json")
    assert (
        BuildRecipe.model_validate(strict_json(canonical_json(raw))).model_dump(mode="json") == raw
    )
    reference = dict(
        artifact_id="geography-" + "a" * 64,
        redistribution="permitted",
        registry_sha256="b" * 64,
        registry_version=recipe.geography.registry_version,
        boundary_version=recipe.geography.boundary_version,
        attribution="Official geographic fixture",
    )
    v2 = raw | dict(schema_version=2, geography=reference)
    assert BuildRecipeV2.model_validate(v2).schema_version == 2
    for version in (1, True, 2.0, "2", 3):
        with pytest.raises(ValidationError):
            BuildRecipeV2.model_validate(v2 | dict(schema_version=version))
    with pytest.raises(ValidationError):
        BuildRecipe.model_validate(v2)
    # The legacy rule remains strict; real geography is not injected into a synthetic v1 recipe.
    observed = recipe.decisions[0].model_copy(update={"source_id": "official-source"})
    altered = recipe.model_copy(update={"decisions": (observed, *recipe.decisions[1:])})
    with pytest.raises(ValueError, match="real source decisions"):
        validate_recipe(altered, allow_synthetic=True)


@pytest.fixture
def atlas_dir(tmp_path: Path) -> Path:
    recipe = atlas_inputs(tmp_path / "source")
    return build_geography(
        recipe, data_root=tmp_path / "source", artifact_root=tmp_path / "geography"
    )


def test_display_identity_parent_qa_and_explicit_corruption(
    atlas_dir: Path, tmp_path: Path
) -> None:
    from spain_housing.ingestion.map_geometry import prepare_display
    from spain_housing.storage.geography import load_display

    display = prepare_display(atlas_dir, artifact_root=tmp_path / "displays", tolerance_m=50.0)
    geography = load_geography(atlas_dir, full=False)
    loaded = load_display(display, geography)
    assert loaded.manifest.parent.artifact_id == geography.manifest.artifact_id
    assert loaded.manifest.quality.max_relative_area_change < 0.02
    assert loaded.manifest.quality.max_boundary_displacement_m <= 250
    assert loaded.manifest.counts.polygon_components == geography.manifest.counts.polygon_components
    assert (
        prepare_display(atlas_dir, artifact_root=tmp_path / "displays", tolerance_m=50.0) == display
    )
    other = prepare_display(atlas_dir, artifact_root=tmp_path / "displays", tolerance_m=20.0)
    assert other != display
    assert load_geography(atlas_dir, full=False).manifest == geography.manifest
    (display / "display.geojson").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="size mismatch"):
        load_display(display, geography)


def test_synthetic_v2_uses_existing_builder_and_requires_explicit_geography(
    atlas_dir: Path, tmp_path: Path
) -> None:
    from spain_housing.ingestion.demo import generate_demo, synthetic_factor
    from spain_housing.ingestion.release import build_release
    from spain_housing.markets.repository import SnapshotMarketRepository
    from spain_housing.models.dataset import BuildRecipeV2
    from spain_housing.models.market import MarketMetric, MarketQuery
    from spain_housing.models.scenario import GeographicReference
    from spain_housing.storage.release import load_release, parse_recipe

    config = demo_config()
    inputs = generate_demo(atlas_dir, config, output_root=tmp_path / "inputs")
    assert generate_demo(atlas_dir, config, output_root=tmp_path / "inputs") == inputs
    # Code-local assumptions do not depend on registry iteration or extra municipalities.
    assert {c: synthetic_factor(config, c) for c in ("28001", "28002")} == {
        c: synthetic_factor(config, c) for c in reversed(("28001", "28002"))
    }
    assert synthetic_factor(config, "28001") == synthetic_factor(
        config.model_copy(update={"partial_codes": ("28001", "28003")}), "28001"
    )
    recipe = parse_recipe(strict_json((inputs / "recipe.json").read_bytes()))
    assert isinstance(recipe, BuildRecipeV2)
    with pytest.raises(ValueError, match="explicit --geography"):
        build_release(
            recipe, data_root=inputs, release_root=tmp_path / "releases", allow_synthetic=True
        )
    release = build_release(
        recipe,
        data_root=inputs,
        release_root=tmp_path / "releases",
        allow_synthetic=True,
        geography_dir=atlas_dir,
    )
    assert not (release / "boundaries.geojson").exists()
    bundle = load_release(release, allow_synthetic=True, geography_dir=atlas_dir)
    assert bundle.boundaries is None and len(bundle.observations) == 6
    assert all(row.observation.evidence_kind == "synthetic" for row in bundle.observations)
    repository = SnapshotMarketRepository.from_release(
        release, allow_synthetic=True, geography_dir=atlas_dir
    )
    query = MarketQuery(
        location=GeographicReference(level="municipality", code="28001"),
        metric=MarketMetric.ROOM_RENT_PER_MONTH,
        period_start=config.period_start,
        period_end=config.period_end,
    )
    assert repository.get(query).observation.value == 400
    with pytest.raises(ValueError, match="external"):
        _ = repository.boundaries
    assert (
        repository.coverage_report.geography.artifact_id
        == load_geography(atlas_dir, full=False).manifest.artifact_id
    )
    with pytest.raises(ValueError, match="opt-in"):
        load_release(release, geography_dir=atlas_dir)


def test_hand_calculated_four_month_reference_and_purchase_only_gap(
    atlas_dir: Path, tmp_path: Path, scenario
) -> None:
    from spain_housing.application import evaluate_scenario
    from spain_housing.ingestion.demo import generate_demo
    from spain_housing.ingestion.release import build_release
    from spain_housing.markets.repository import SnapshotMarketRepository
    from spain_housing.models.scenario import Scenario
    from spain_housing.storage.release import parse_recipe

    data = scenario.model_dump(mode="json")
    data["saving_months"] = 4
    data["retained_reserve_eur"] = 1200
    data["target_property"]["area_m2"] = 60
    data["participants"][0]["starting_savings_eur"] = 10000
    data["household_nonhousing_expenses"]["milestones"] = [dict(month_offset=0, amount_eur=600)]
    data["living_stages"][1]["end_month_offset"] = 4
    reference = Scenario.model_validate(data)
    results = []
    for variant in ("complete", "partial"):
        inputs = generate_demo(
            atlas_dir, demo_config(), output_root=tmp_path / variant, variant=variant
        )
        recipe = parse_recipe(strict_json((inputs / "recipe.json").read_bytes()))
        release = build_release(
            recipe,
            data_root=inputs,
            release_root=tmp_path / "releases",
            allow_synthetic=True,
            geography_dir=atlas_dir,
        )
        market = SnapshotMarketRepository.from_release(
            release, allow_synthetic=True, geography_dir=atlas_dir
        )
        run = evaluate_scenario(
            reference,
            market_data=market,
            context=market.evaluation_context,
            mapped_locations=(market.locations[0].location,),
        )
        results.append(run.results[0])
    complete, gap = results
    assert complete.savings.ending_savings_eur == pytest.approx(13200)
    assert complete.savings.usable_savings_eur == pytest.approx(12000)
    purchase = complete.purchase
    assert purchase.savings_price_limit_eur == pytest.approx(40000)
    assert purchase.mortgage_price_limit_eur == pytest.approx(225000)
    assert purchase.maximum_price_eur == pytest.approx(40000)
    assert purchase.target_price_eur == pytest.approx(120000)
    assert purchase.target_cash_shortfall_eur == pytest.approx(24000)
    assert purchase.target_loan_eur == pytest.approx(96000)
    assert purchase.target_monthly_payment_eur == pytest.approx(320)
    assert complete.affordable_area_m2.value == pytest.approx(20)
    assert complete.target_affordability_ratio.value == pytest.approx(1 / 3)
    assert gap.purchase.maximum_price_eur == pytest.approx(40000)
    assert gap.affordable_area_m2.status == "missing"


def test_inspected_source_conflict_is_retained_but_never_becomes_simplifier_input(
    tmp_path: Path,
) -> None:
    from spain_housing.ingestion.map_geometry import prepare_display
    from spain_housing.models.geography import SourceConflict

    raw = tmp_path / "raw"
    recipe = atlas_inputs(raw, defect="overlap")
    page = strict_json((raw / "municipal_json").read_bytes())
    conflict = SourceConflict(
        feature_ids=("one", "two"),
        geometry_sha256=tuple(sha256(canonical_json(f["geometry"])) for f in page["features"]),
        reason="Self-authored test of explicit unmodified source defects",
        evidence_capture_ids=("municipal_json",),
    )
    retained = recipe.model_copy(update={"source_conflicts": (conflict,)})
    path = build_geography(retained, data_root=raw, artifact_root=tmp_path / "atlas")
    assert load_geography(path).manifest.recipe.source_conflicts == (conflict,)
    assert strict_json((path / "report.json").read_bytes())["coverage_valid"] is False
    with pytest.raises(ValueError, match="edge-matched"):
        prepare_display(path, artifact_root=tmp_path / "display")
    changed = conflict.model_copy(
        update={"geometry_sha256": ("a" * 64, conflict.geometry_sha256[1])}
    )
    with pytest.raises(ValueError, match="inspected"):
        build_geography(
            recipe.model_copy(update={"source_conflicts": (changed,)}),
            data_root=raw,
            artifact_root=tmp_path / "atlas",
        )
