"""Immutable atlas/display persistence; metadata reads never parse canonical polygons."""

from dataclasses import dataclass
from pathlib import Path

import shapely
from pydantic import TypeAdapter
from shapely.geometry import shape

from spain_housing.models.geography import (
    ArtifactFile,
    AtlasCollection,
    DisplayManifest,
    GeographyCounts,
    GeographyManifest,
    GeographyReference,
    Municipality,
)

from .coverage_geometry import validate_source_coverage
from .files import canonical_json, contained_path, publish_artifact, sha256, strict_json
from .geometry import validate_polygon
from .permissions import redistribution_scope, validate_capture_permission, validate_source_use

MAX_PAYLOAD = 1024 * 1024 * 1024


def artifact_identity(prefix: str, metadata: dict[str, object]) -> tuple[str, str]:
    digest = sha256(canonical_json(metadata))
    return f"{prefix}-{digest}", digest


def file_record(name: str, data: bytes, count: int) -> ArtifactFile:
    return ArtifactFile(path=name, sha256=sha256(data), byte_size=len(data), record_count=count)


def read_payload(root: Path, record: ArtifactFile) -> bytes:
    path = contained_path(root, record.path)
    if path.stat().st_size != record.byte_size or record.byte_size > MAX_PAYLOAD:
        raise ValueError(f"artifact payload size mismatch: {record.path}")
    data = path.read_bytes()
    if sha256(data) != record.sha256:
        raise ValueError(f"artifact payload hash mismatch: {record.path}")
    return data


def geography_reference(manifest: GeographyManifest) -> GeographyReference:
    return GeographyReference(
        redistribution=manifest.redistribution,
        artifact_id=manifest.artifact_id,
        registry_sha256=manifest.registry_sha256,
        registry_version=manifest.recipe.registry_version,
        boundary_version=manifest.recipe.boundary_version,
        attribution=manifest.recipe.attribution,
    )


def geometry_counts(collection: AtlasCollection, provinces: int) -> GeographyCounts:
    components = holes = vertices = 0
    for feature in collection.features:
        geometry = feature.geometry
        polygons = (geometry.coordinates,) if geometry.type == "Polygon" else geometry.coordinates
        components += len(polygons)
        for polygon in polygons:
            holes += len(polygon) - 1
            vertices += sum(len(ring) for ring in polygon)
    return GeographyCounts(
        municipalities=sum(f.properties.kind == "municipality" for f in collection.features),
        context_territories=sum(f.properties.kind == "context" for f in collection.features),
        provinces=provinces,
        polygon_components=components,
        holes=holes,
        vertices=vertices,
    )


def validate_atlas(collection: AtlasCollection, registry: tuple[Municipality, ...]) -> None:
    codes = [r.code for r in registry]
    ids = [f.id for f in collection.features]
    features = {
        f.properties.location_code: f
        for f in collection.features
        if f.properties.kind == "municipality"
    }
    if len(codes) != len(set(codes)) or len(ids) != len(set(ids)) or set(codes) != features.keys():
        raise ValueError("atlas requires one unique municipality feature for every registry code")
    for item in registry:
        feature = features[item.code]
        if (
            feature.id,
            feature.properties.name,
            feature.properties.province_code,
            feature.properties.source_national_code,
        ) != (item.feature_id, item.official_name, item.province_code, item.national_code):
            raise ValueError(f"atlas registry identity mismatch: {item.code}")
    for feature in collection.features:
        validate_polygon(feature.geometry)


@dataclass(frozen=True)
class GeographyBundle:
    manifest: GeographyManifest
    registry: tuple[Municipality, ...]
    boundaries: AtlasCollection | None = None
    provinces: AtlasCollection | None = None


def load_geography(root: Path, *, full: bool = True) -> GeographyBundle:
    manifest_path = contained_path(root, "manifest.json")
    if manifest_path.stat().st_size > 10 * 1024 * 1024:
        raise ValueError("geography manifest exceeds 10 MiB")
    raw_manifest = TypeAdapter(dict[str, object]).validate_python(
        strict_json(manifest_path.read_bytes())
    )
    manifest = GeographyManifest.model_validate(raw_manifest)
    decisions = {d.source_id: d for d in manifest.recipe.decisions}
    for decision in decisions.values():
        validate_source_use(decision, "observed")
    for capture in manifest.recipe.captures:
        capture_decision = decisions.get(capture.source_id)
        if capture_decision is None:
            raise ValueError("geography capture references unknown permission")
        validate_capture_permission(capture, capture_decision, "observed")
    if manifest.redistribution != redistribution_scope(manifest.recipe.decisions):
        raise ValueError("geography redistribution overstates input permissions")
    metadata = {
        key: value
        for key, value in raw_manifest.items()
        if key not in ("artifact_id", "content_digest")
    }
    if (manifest.artifact_id, manifest.content_digest) != artifact_identity("geography", metadata):
        raise ValueError("geography content identity mismatch")
    records = {r.path: r for r in manifest.files}
    if len(records) != len(manifest.files) or records.keys() != {
        "registry.json",
        "canonical.geojson",
        "provinces.geojson",
        "report.json",
    }:
        raise ValueError("geography requires its four canonical payloads")
    raw_registry = read_payload(root, records["registry.json"])
    if sha256(raw_registry) != manifest.registry_sha256:
        raise ValueError("geography registry identity mismatch")
    registry = TypeAdapter(tuple[Municipality, ...]).validate_python(strict_json(raw_registry))
    if (
        tuple(sorted(registry, key=lambda m: m.code)) != registry
        or len({m.code for m in registry}) != len(registry)
        or len(registry) != manifest.counts.municipalities
        or records["registry.json"].record_count != len(registry)
    ):
        raise ValueError("geography registry count/order/uniqueness mismatch")
    if not full:
        return GeographyBundle(manifest, registry)
    boundaries = AtlasCollection.model_validate(
        strict_json(read_payload(root, records["canonical.geojson"]))
    )
    provinces = AtlasCollection.model_validate(
        strict_json(read_payload(root, records["provinces.geojson"]))
    )
    report = strict_json(read_payload(root, records["report.json"]))
    if not isinstance(report, dict):
        raise ValueError("geography report must be an object")
    validate_atlas(boundaries, registry)
    validate_source_coverage(boundaries, manifest.recipe.source_conflicts)
    for feature in provinces.features:
        if feature.properties.kind != "province":
            raise ValueError("province layer contains non-province features")
        validate_polygon(feature.geometry)
    if geometry_counts(boundaries, len(provinces.features)) != manifest.counts:
        raise ValueError("geography geometry counts mismatch")
    for name, count in (
        ("canonical.geojson", len(boundaries.features)),
        ("provinces.geojson", len(provinces.features)),
        ("report.json", 1),
    ):
        if records[name].record_count != count:
            raise ValueError("geography payload record count mismatch")
    return GeographyBundle(manifest, registry, boundaries, provinces)


@dataclass(frozen=True)
class DisplayBundle:
    manifest: DisplayManifest
    boundaries: AtlasCollection
    provinces: AtlasCollection


def load_display(root: Path, geography: GeographyBundle) -> DisplayBundle:
    path = contained_path(root, "manifest.json")
    if path.stat().st_size > 1024 * 1024:
        raise ValueError("display manifest exceeds 1 MiB")
    manifest = DisplayManifest.model_validate(strict_json(path.read_bytes()))
    metadata = manifest.model_dump(mode="json", exclude={"artifact_id", "content_digest"})
    if (manifest.artifact_id, manifest.content_digest) != artifact_identity("display", metadata):
        raise ValueError("display content identity mismatch")
    if manifest.parent != geography_reference(geography.manifest):
        raise ValueError("display parent geography identity mismatch")
    if manifest.redistribution != geography.manifest.redistribution:
        raise ValueError("display redistribution differs from its geographic parent")
    records = {r.path: r for r in manifest.files}
    if len(records) != len(manifest.files) or records.keys() != {
        "display.geojson",
        "provinces.geojson",
    }:
        raise ValueError("display requires its two canonical payloads")
    boundaries = AtlasCollection.model_validate(
        strict_json(read_payload(root, records["display.geojson"]))
    )
    provinces = AtlasCollection.model_validate(
        strict_json(read_payload(root, records["provinces.geojson"]))
    )
    validate_atlas(boundaries, geography.registry)
    if not shapely.coverage_is_valid(
        [shape(feature.geometry.model_dump(mode="json")) for feature in boundaries.features]
    ):
        raise ValueError("display geography is not an edge-matched polygon coverage")
    if any(
        getattr(manifest.counts, field) != getattr(geography.manifest.counts, field)
        for field in (
            "municipalities",
            "context_territories",
            "provinces",
            "polygon_components",
            "holes",
        )
    ):
        raise ValueError("display has lost canonical features/components/holes")
    for feature in provinces.features:
        if feature.properties.kind != "province":
            raise ValueError("display orientation layer contains non-province features")
        validate_polygon(feature.geometry)
    if (
        geometry_counts(boundaries, len(provinces.features)) != manifest.counts
        or records["display.geojson"].record_count != len(boundaries.features)
        or records["provinces.geojson"].record_count != len(provinces.features)
    ):
        raise ValueError("display geometry counts mismatch")
    return DisplayBundle(manifest, boundaries, provinces)


def write_geography(root: Path, metadata: dict[str, object], payloads: dict[str, bytes]) -> Path:
    identity, digest = artifact_identity("geography", metadata)
    manifest = GeographyManifest.model_validate(
        metadata | {"artifact_id": identity, "content_digest": digest}
    )
    return publish_artifact(
        root,
        identity,
        payloads | {"manifest.json": canonical_json(manifest.model_dump(mode="json"))},
        load_geography,
    )


def write_display(
    root: Path, metadata: dict[str, object], payloads: dict[str, bytes], geography: GeographyBundle
) -> Path:
    identity, digest = artifact_identity("display", metadata)
    manifest = DisplayManifest.model_validate(
        metadata | {"artifact_id": identity, "content_digest": digest}
    )
    return publish_artifact(
        root,
        identity,
        payloads | {"manifest.json": canonical_json(manifest.model_dump(mode="json"))},
        lambda path: load_display(path, geography),
    )
