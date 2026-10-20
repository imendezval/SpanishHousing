"""Canonical atlas assembly, integrity, pagination and immutable publication."""

from pathlib import Path

import pytest

from fixtures.synthetic.atlas import atlas_inputs
from spain_housing.ingestion.atlas import build_geography
from spain_housing.storage.geography import load_geography


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
