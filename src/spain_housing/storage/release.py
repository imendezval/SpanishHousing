"""One canonical format, verifier and atomic publisher for offline releases."""

from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter

from spain_housing.models.dataset import (
    BoundaryCollection,
    BuildRecipe,
    CoverageCell,
    CoverageSummary,
    FileRecord,
    FileRole,
    LocationRecord,
    ReferenceProfile,
    ReleasedObservation,
    ReleaseManifest,
    UsageScope,
)
from spain_housing.models.market import MarketObservation

from .files import (
    canonical_json as canonical_json,
)
from .files import (
    contained_path as contained_path,
)
from .files import (
    publish_artifact,
)
from .files import (
    read_capture as read_capture,
)
from .files import (
    sha256 as sha256,
)
from .files import (
    strict_json as strict_json,
)
from .geometry import validate_polygon
from .permissions import (
    redistribution_scope,
)
from .permissions import (
    validate_capture_permission as validate_capture_permission,
)
from .permissions import (
    validate_source_use as validate_source_use,
)

PAYLOADS: dict[FileRole, str] = {
    "observations": "observations.jsonl",
    "locations": "locations.json",
    "boundaries": "boundaries.geojson",
    "coverage": "coverage.json",
}


def validate_recipe(recipe: BuildRecipe, *, allow_synthetic: bool = False) -> None:
    if recipe.kind == "synthetic" and not allow_synthetic:
        raise ValueError("synthetic releases require explicit allow_synthetic opt-in")
    decisions = {item.source_id: item for item in recipe.decisions}
    captures = {item.capture_id: item for item in recipe.captures}
    for decision in decisions.values():
        validate_source_use(decision, recipe.kind)
    for capture in captures.values():
        capture_decision = decisions.get(capture.source_id)
        if capture_decision is None:
            raise ValueError("capture references an unknown source/permission decision")
        validate_capture_permission(capture, capture_decision, recipe.kind)
    required = (
        *recipe.observation_capture_ids,
        recipe.geography.registry_capture_id,
        *recipe.geography.boundary_capture_ids,
    )
    if not recipe.geography.boundary_capture_ids or not set(required) <= captures.keys():
        raise ValueError("missing required capture reference")
    for profile in recipe.profiles:
        if profile.source_id not in decisions:
            raise ValueError("profile references an unknown source")
    for location in recipe.locations:
        if (
            location.registry_version != recipe.geography.registry_version
            or location.boundary_version != recipe.geography.boundary_version
        ):
            raise ValueError("location registry/boundary version disagrees with geography")
        if not all(mapping.source_id in decisions for mapping in location.source_mappings):
            raise ValueError("crosswalk references an unknown source")
    gap_keys = [(cell.location_code, cell.profile_id) for cell in recipe.declared_gaps]
    expected = {
        (loc.location.code, p.profile_id) for loc in recipe.locations for p in recipe.profiles
    }
    if (
        len(gap_keys) != len(set(gap_keys))
        or not set(gap_keys) <= expected
        or any(cell.status == "available" for cell in recipe.declared_gaps)
    ):
        raise ValueError("declared gaps must be unique expected gaps")


def selected_profile(observation: MarketObservation, recipe: BuildRecipe) -> ReferenceProfile:
    matches = [
        profile
        for profile in recipe.profiles
        if (
            profile.metric == observation.metric
            and profile.period_start == observation.period_start
            and profile.period_end == observation.period_end
            and profile.segment == observation.segment
            and profile.source_id == observation.source_id
            and profile.statistic == observation.statistic
            and profile.basis == observation.basis
        )
    ]
    if len(matches) != 1:
        raise ValueError("observation does not match exactly one selected reference profile")
    return matches[0]


def observation_key(row: ReleasedObservation) -> str:
    obs = row.observation
    return canonical_json(
        [
            obs.location.level,
            obs.location.code,
            obs.period_start.isoformat(),
            obs.period_end.isoformat(),
            obs.metric,
            obs.segment.model_dump(mode="json"),
        ]
    ).decode()


def generate_coverage(
    recipe: BuildRecipe, rows: tuple[ReleasedObservation, ...]
) -> tuple[CoverageCell, ...]:
    available = {
        (row.observation.location.code, selected_profile(row.observation, recipe).profile_id)
        for row in rows
    }
    gaps = {(cell.location_code, cell.profile_id): cell for cell in recipe.declared_gaps}
    if available & gaps.keys():
        raise ValueError("declared gap contradicts an available observation")
    result = []
    for location in sorted(recipe.locations, key=lambda item: item.location.code):
        for profile in sorted(recipe.profiles, key=lambda item: item.profile_id):
            key = (location.location.code, profile.profile_id)
            if key in available:
                cell = CoverageCell(location_code=key[0], profile_id=key[1], status="available")
            else:
                cell = gaps.get(key) or CoverageCell(
                    location_code=key[0],
                    profile_id=key[1],
                    status="missing",
                    reason="no captured observation for selected profile",
                )
            result.append(cell)
    return tuple(result)


def validate_geometry(
    boundaries: BoundaryCollection, locations: tuple[LocationRecord, ...]
) -> None:
    registry = {loc.location.code: loc for loc in locations}
    codes = [feature.properties.location_code for feature in boundaries.features]
    ids = [feature.id for feature in boundaries.features]
    if len(codes) != len(set(codes)) or len(ids) != len(set(ids)) or set(codes) != registry.keys():
        raise ValueError(
            "geometry must join each registry code exactly once with unique feature IDs"
        )
    for feature in boundaries.features:
        location = registry[feature.properties.location_code]
        if (
            feature.id != location.geometry_feature_id
            or feature.properties.boundary_version != location.boundary_version
        ):
            raise ValueError("geometry ID/version disagrees with registry")
        validate_polygon(feature.geometry)


def _coverage_summary(cells: tuple[CoverageCell, ...]) -> CoverageSummary:
    return CoverageSummary(
        expected=len(cells),
        available=sum(c.status == "available" for c in cells),
        missing=sum(c.status == "missing" for c in cells),
        unsupported=sum(c.status == "unsupported" for c in cells),
    )


def _redistribution(recipe: BuildRecipe) -> UsageScope:
    return redistribution_scope(recipe.decisions)


def _readiness(recipe: BuildRecipe, cells: tuple[CoverageCell, ...]) -> str:
    if recipe.kind == "synthetic":
        return "synthetic_only"
    core_codes = {loc.location.code for loc in recipe.locations if loc.core}
    return (
        "incomplete"
        if any(cell.status != "available" and cell.location_code in core_codes for cell in cells)
        else "ready"
    )


def content_identity(metadata: dict[str, object]) -> tuple[str, str]:
    """Hash canonical manifest metadata excluding its own ID/digest, including payload hashes."""
    digest = sha256(canonical_json(metadata))
    recipe = BuildRecipe.model_validate(metadata["recipe"])
    return f"{'synthetic' if recipe.kind == 'synthetic' else 'pilot'}-{digest}", digest


@dataclass(frozen=True)
class ReleaseBundle:
    manifest: ReleaseManifest
    observations: tuple[ReleasedObservation, ...]
    locations: tuple[LocationRecord, ...]
    boundaries: BoundaryCollection
    coverage: tuple[CoverageCell, ...]


def load_release(release_dir: Path, *, allow_synthetic: bool = False) -> ReleaseBundle:
    manifest = ReleaseManifest.model_validate(
        strict_json(contained_path(release_dir, "manifest.json").read_bytes())
    )
    validate_recipe(manifest.recipe, allow_synthetic=allow_synthetic)
    if manifest.recipe.producer.code_fingerprint is None:
        raise ValueError("released recipe lacks the actual producer code fingerprint")
    files = {item.role: item for item in manifest.files}
    if len(files) != len(manifest.files) or files.keys() != PAYLOADS.keys():
        raise ValueError("release requires exactly the four canonical payload roles")
    payloads: dict[FileRole, bytes] = {}
    for role, filename in PAYLOADS.items():
        record = files[role]
        if record.path != filename:
            raise ValueError("noncanonical payload path")
        data = contained_path(release_dir, record.path).read_bytes()
        if sha256(data) != record.sha256 or len(data) != record.byte_size:
            raise ValueError(f"payload hash/size mismatch: {record.path}")
        payloads[role] = data
    rows = tuple(
        ReleasedObservation.model_validate(strict_json(line))
        for line in payloads["observations"].splitlines()
    )
    locations = TypeAdapter(tuple[LocationRecord, ...]).validate_python(
        strict_json(payloads["locations"])
    )
    boundaries = BoundaryCollection.model_validate(strict_json(payloads["boundaries"]))
    cells = TypeAdapter(tuple[CoverageCell, ...]).validate_python(strict_json(payloads["coverage"]))
    counts: dict[FileRole, int] = {
        "observations": len(rows),
        "locations": len(locations),
        "boundaries": len(boundaries.features),
        "coverage": len(cells),
    }
    if any(files[role].record_count != count for role, count in counts.items()):
        raise ValueError("payload record count mismatch")
    if locations != tuple(sorted(manifest.recipe.locations, key=lambda loc: loc.location.code)):
        raise ValueError("released registry disagrees with recipe")
    validate_geometry(boundaries, locations)
    captures = {item.capture_id: item for item in manifest.recipe.captures}
    location_map = {loc.location.code: loc for loc in locations}
    keys = [observation_key(row) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate semantic observation key")
    for row in rows:
        observation = row.observation
        capture = captures.get(row.capture_id)
        if capture is None or row.capture_id not in manifest.recipe.observation_capture_ids:
            raise ValueError("observation has missing/unselected capture lineage")
        if (
            observation.source_id,
            observation.source_url,
            observation.retrieved_at,
            observation.source_release,
            observation.methodology_version,
        ) != (
            capture.source_id,
            capture.primary_url,
            capture.captured_at,
            capture.source_release,
            capture.methodology_version,
        ):
            raise ValueError("observation provenance disagrees with its capture")
        if (observation.evidence_kind == "synthetic") != (manifest.kind == "synthetic"):
            raise ValueError("synthetic/observed observation mixing is prohibited")
        location = location_map.get(observation.location.code)
        if (
            location is None
            or observation.location != location.location
            or observation.boundary_version != location.boundary_version
        ):
            raise ValueError("observation lacks its matching registry/geometry version")
        selected_profile(observation, manifest.recipe)
    expected_cells = generate_coverage(manifest.recipe, rows)
    if cells != expected_cells or manifest.coverage != _coverage_summary(cells):
        raise ValueError("coverage contradicts observations/recipe/counts")
    if manifest.redistribution != _redistribution(
        manifest.recipe
    ) or manifest.readiness != _readiness(manifest.recipe, cells):
        raise ValueError("release usage/readiness overstates its inputs")
    metadata = manifest.model_dump(mode="json", exclude={"release_id", "content_digest"})
    identity, digest = content_identity(metadata)
    if (manifest.release_id, manifest.content_digest) != (identity, digest):
        raise ValueError("release content identity mismatch")
    return ReleaseBundle(manifest, rows, locations, boundaries, cells)


def write_release(
    release_root: Path,
    *,
    recipe: BuildRecipe,
    observations: tuple[ReleasedObservation, ...],
    boundaries: BoundaryCollection,
    allow_synthetic: bool = False,
) -> Path:
    validate_recipe(recipe, allow_synthetic=allow_synthetic)
    rows = tuple(sorted(observations, key=observation_key))
    locations = tuple(sorted(recipe.locations, key=lambda loc: loc.location.code))
    boundaries = boundaries.model_copy(
        update={
            "features": tuple(sorted(boundaries.features, key=lambda f: f.properties.location_code))
        }
    )
    coverage = generate_coverage(recipe, rows)
    data: dict[FileRole, bytes] = {
        "observations": b"".join(canonical_json(row.model_dump(mode="json")) for row in rows),
        "locations": canonical_json([loc.model_dump(mode="json") for loc in locations]),
        "boundaries": canonical_json(boundaries.model_dump(mode="json")),
        "coverage": canonical_json([cell.model_dump(mode="json") for cell in coverage]),
    }
    counts = (len(rows), len(locations), len(boundaries.features), len(coverage))
    files = tuple(
        FileRecord(
            path=PAYLOADS[role],
            role=role,
            sha256=sha256(payload),
            byte_size=len(payload),
            record_count=count,
        )
        for (role, payload), count in zip(data.items(), counts, strict=True)
    )
    metadata: dict[str, object] = {
        "schema_version": 1,
        "recipe": recipe.model_dump(mode="json"),
        "files": [file.model_dump(mode="json") for file in files],
        "coverage": _coverage_summary(coverage).model_dump(mode="json"),
        "redistribution": _redistribution(recipe),
        "readiness": _readiness(recipe, coverage),
    }
    identity, digest = content_identity(metadata)
    manifest = ReleaseManifest.model_validate(
        metadata | {"release_id": identity, "content_digest": digest}
    )
    payloads = {PAYLOADS[role]: payload for role, payload in data.items()}
    payloads["manifest.json"] = canonical_json(manifest.model_dump(mode="json"))
    return publish_artifact(
        release_root,
        identity,
        payloads,
        lambda path: load_release(path, allow_synthetic=allow_synthetic),
    )
