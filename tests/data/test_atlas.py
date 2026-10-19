"""Self-authored geography fixtures; these shapes are not official observations."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.ingestion.atlas import build_geography
from spain_housing.models.dataset import BuildRecipe, BuildRecipeV2, CaptureRecord, SourceDecision
from spain_housing.models.geography import GeographyRecipe
from spain_housing.storage.files import canonical_json, sha256, strict_json
from spain_housing.storage.geography import load_geography
from spain_housing.storage.release import validate_recipe


def atlas_inputs(root: Path, *, defect: str | None = None) -> GeographyRecipe:
    root.mkdir()
    decisions = tuple(
        SourceDecision(
            source_id=source,
            product="Self-authored geographic test fixture, not official data",
            primary_url="https://www.ine.es/fixture"
            if source.startswith("ine")
            else "https://api-features.ign.es/fixture",
            terms_url="https://example.org/self-authored",
            local_use="permitted",
            redistribution="permitted",
            evidence_reference="Self-authored test bytes only",
            attribution="Synthetic test geometry",
            reviewed_on="2026-10-19",
            acquisition_route="curated test fixture",
        )
        for source in ("ine-municipalities", "ign-administrativeunit")
    )
    registry = b"CPRO,CMUN,DC,NOMBRE\n28,001,0,Same name\n28,002,1,Same name\n"
    first = [[[-4.0, 40.0], [-3.5, 40.0], [-3.5, 40.5], [-3.5, 41.0], [-4.0, 41.0], [-4.0, 40.0]]]
    second = [[[-3.5, 40.0], [-3.0, 40.0], [-3.0, 41.0], [-3.5, 41.0], [-3.5, 40.5], [-3.5, 40.0]]]
    if defect == "edge":
        second[0].pop(-2)
    features = []
    for identity, code, coordinates in (("one", "28001", first), ("two", "28002", second)):
        features.append(
            dict(
                type="Feature",
                id=identity,
                properties=dict(
                    country="ES",
                    nationallevelname="Municipio",
                    nationalcode="341328" + code,
                    nameunit="Same name",
                ),
                geometry=dict(type="Polygon", coordinates=coordinates),
            )
        )
    if defect == "duplicate":
        features[-1] = features[0]
    if defect == "axis":
        features[0]["geometry"]["coordinates"][0][0] = [40.0, -4.0]
    if defect == "level":
        features[0]["properties"]["nationallevelname"] = "Provincia"
    page = dict(
        type="FeatureCollection", features=features, numberMatched=2, numberReturned=2, links=[]
    )
    if defect == "pagination":
        page["links"] = [dict(rel="next", href="https://api-features.ign.es/missing")]
    province = dict(
        type="Feature",
        id="province",
        properties=dict(
            country="ES",
            nationallevelname="Provincia",
            nationalcode="34132800000",
            nameunit="Fixture province",
        ),
        geometry=dict(
            type="Polygon",
            coordinates=[[[-4.0, 40.0], [-3.0, 40.0], [-3.0, 41.0], [-4.0, 41.0], [-4.0, 40.0]]],
        ),
    )
    contents = (
        ("registry_csv", registry, "csv", decisions[0]),
        ("municipal_json", canonical_json(page), "geojson", decisions[1]),
        (
            "province_json",
            canonical_json(
                dict(
                    type="FeatureCollection",
                    features=[province],
                    numberMatched=1,
                    numberReturned=1,
                    links=[],
                )
            ),
            "geojson",
            decisions[1],
        ),
    )
    captures = []
    for name, data, fmt, decision in contents:
        (root / name).write_bytes(data)
        captures.append(
            CaptureRecord(
                capture_id=name,
                source_id=decision.source_id,
                path=name,
                sha256=sha256(data),
                byte_size=len(data),
                primary_url="https://api-features.ign.es/" + name,
                captured_at="2026-10-19T00:00:00Z",
                route="curated_extract",
                format=fmt,
                permission_reference=decision.evidence_reference,
            )
        )
    return GeographyRecipe(
        registry_version="Self-authored fixture",
        registry_effective_on="2026-01-01",
        boundary_version="fixture-boundary",
        attribution="Synthetic test geometry",
        decisions=decisions,
        captures=tuple(captures),
        registry_capture_id="registry_csv",
        municipal_page_ids=("municipal_json",),
        province_page_ids=("province_json",),
        support_capture_ids=(),
        processing_notes=("Self-authored shapes, not official geography",),
    )


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
