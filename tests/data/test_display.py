"""Display fidelity, neutral source conflicts and lossless geometry encodings.

Small synthetic shapes exercise topology; the attributed IGN pair is actual
retained source evidence and is never replaced by a synthetic observation.
"""

from pathlib import Path

import pytest

from fixtures.synthetic.atlas import atlas_inputs
from spain_housing.ingestion.atlas import build_geography
from spain_housing.storage.files import canonical_json, sha256, strict_json
from spain_housing.storage.geography import load_geography


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
    (display / "display.delta.json").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="size mismatch"):
        load_display(display, geography)


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


def test_approved_neutral_display_preserves_source_and_all_economic_identities(
    tmp_path: Path,
) -> None:
    from shapely.geometry import shape

    from spain_housing.ingestion.map_geometry import prepare_display
    from spain_housing.models.geography import SourceConflict
    from spain_housing.storage.geography import load_display

    raw = tmp_path / "raw"
    recipe = atlas_inputs(raw, defect="overlap_small")
    page = strict_json((raw / "municipal_json").read_bytes())
    conflict = SourceConflict(
        feature_ids=("one", "two"),
        geometry_sha256=tuple(sha256(canonical_json(f["geometry"])) for f in page["features"]),
        reason="Self-authored narrow overlap, approved neutral display test",
        evidence_capture_ids=("municipal_json",),
    )
    atlas = build_geography(
        recipe.model_copy(update={"source_conflicts": (conflict,)}),
        data_root=raw,
        artifact_root=tmp_path / "atlas",
    )
    original = {p.name: p.read_bytes() for p in atlas.iterdir()}
    display = prepare_display(
        atlas, artifact_root=tmp_path / "display", neutral_source_conflicts=True
    )
    bundle = load_display(display, load_geography(atlas, full=False))
    assert {p.name: p.read_bytes() for p in atlas.iterdir()} == original
    assert {f.properties.location_code for f in bundle.boundaries.features} == {
        "28001",
        "28002",
        None,
    }
    patches = [f for f in bundle.boundaries.features if f.properties.kind == "source_conflict"]
    assert len(patches) == 1 and patches[0].properties.location_code is None
    assert bundle.manifest.neutral_conflicts[0].source_feature_ids == ("one", "two")
    assert bundle.manifest.neutral_conflicts[0].area_m2 > 0
    polygons = [shape(f.geometry.model_dump(mode="json")) for f in bundle.boundaries.features]
    assert all(
        a.intersection(b).area == 0 for i, a in enumerate(polygons) for b in polygons[i + 1 :]
    )
    assert bundle.manifest.counts.polygon_components == 3
    assert bundle.manifest.counts.municipalities == 2
    assert (
        prepare_display(atlas, artifact_root=tmp_path / "display", neutral_source_conflicts=True)
        == display
    )


def test_fidelity_failure_retains_source_edges_with_consistent_neighbors(tmp_path: Path) -> None:
    from spain_housing.ingestion.map_geometry import prepare_display
    from spain_housing.storage.geography import load_display

    raw = tmp_path / "raw"
    atlas = build_geography(
        atlas_inputs(raw, defect="spike"), data_root=raw, artifact_root=tmp_path / "atlas"
    )
    display = prepare_display(atlas, artifact_root=tmp_path / "display", tolerance_m=100)
    bundle = load_display(display, load_geography(atlas, full=False))
    assert "one" in bundle.manifest.quality.retained_feature_ids
    assert bundle.manifest.quality.max_boundary_displacement_m <= 250
    one = next(f for f in bundle.boundaries.features if f.id == "one")
    assert any(point[0] == -4.004 for ring in one.geometry.coordinates for point in ring)
    assert bundle.manifest.quality.coordinate_decimals == 7


def test_retained_official_pair_has_the_pinned_real_source_overlap() -> None:
    import shapely
    from pyproj import Transformer
    from shapely.geometry import shape

    root = Path(__file__).parents[1] / "fixtures/geography/ign_overlap"
    raw = (root / "features.geojson").read_bytes()
    provenance = strict_json((root / "provenance.json").read_bytes())
    assert sha256(raw) == provenance["extract_sha256"]
    features = strict_json(raw)["features"]
    assert [sha256(canonical_json(f["geometry"])) for f in features] == provenance["conflict"][
        "geometry_sha256"
    ]
    geometries = [shape(f["geometry"]) for f in features]
    assert all(g.is_valid for g in geometries)
    assert not shapely.coverage_is_valid(geometries)
    overlap = geometries[0].intersection(geometries[1])
    project = Transformer.from_crs("OGC:CRS84", "EPSG:25831", always_xy=True)
    metric = shapely.transform(overlap, project.transform, interleaved=False)
    assert metric.area == pytest.approx(1440.944794, abs=0.001)


@pytest.mark.parametrize("encoding", ["delta-7-v1", "delta-7-v2"])
def test_display_delta_encoding_preserves_geometry_and_rejects_malformed_pairs(
    atlas_dir: Path,
    encoding: str,
) -> None:
    from spain_housing.storage.geography import decode_display, encode_display

    collection = load_geography(atlas_dir).boundaries
    assert collection is not None
    encoded = encode_display(collection, encoding=encoding)
    assert decode_display(encoded, encoding) == collection
    assert (
        decode_display(canonical_json(collection.model_dump(mode="json")), "geojson") == collection
    )
    wrong = strict_json(encoded)
    if encoding == "delta-7-v1":
        wrong["features"][0]["geometry"]["coordinates"][0][0][0] = True
    else:
        wrong["features"][0][7][0][0][0] = True
    with pytest.raises(ValueError, match="integers"):
        decode_display(canonical_json(wrong), encoding)
    with pytest.raises(ValueError, match="header"):
        decode_display(canonical_json(collection.model_dump(mode="json")), encoding)
