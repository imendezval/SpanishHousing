"""Strict source-coverage diagnostics with fingerprinted, unmodified provider defects."""

import shapely
from shapely.geometry import shape

from spain_housing.models.geography import AtlasCollection, SourceConflict

from .files import canonical_json, sha256


def validate_source_coverage(
    boundaries: AtlasCollection, conflicts: tuple[SourceConflict, ...]
) -> bool:
    geometries = [
        shape(feature.geometry.model_dump(mode="json")) for feature in boundaries.features
    ]
    valid = bool(shapely.coverage_is_valid(geometries))
    if valid:
        if conflicts:
            raise ValueError("declared source conflict is absent from the supplied geometry")
        return True
    invalid = shapely.coverage_invalid_edges(geometries)
    invalid_ids = {
        feature.id
        for feature, edge in zip(boundaries.features, invalid, strict=True)
        if not edge.is_empty
    }
    declared = {identity for conflict in conflicts for identity in conflict.feature_ids}
    if not conflicts or invalid_ids != declared:
        raise ValueError(
            f"official polygons do not form edge-matched coverage: {sorted(invalid_ids)}"
        )
    by_id = {
        feature.id: (feature, geometry)
        for feature, geometry in zip(boundaries.features, geometries, strict=True)
    }
    for conflict in conflicts:
        first, second = conflict.feature_ids
        if first == second:
            raise ValueError("source conflict must identify two distinct polygons")
        for identity, expected in zip(conflict.feature_ids, conflict.geometry_sha256, strict=True):
            if (
                sha256(canonical_json(by_id[identity][0].geometry.model_dump(mode="json")))
                != expected
            ):
                raise ValueError("source conflict geometry differs from inspected provider bytes")
        if by_id[first][1].intersection(by_id[second][1]).area <= 0:
            raise ValueError("declared source overlap is not present")
    # False is intentional: canonical data remains the actual, imperfect source.
    # It is not approved as simplifier input by this exception.
    return False
