"""Offline coverage simplification and measured metric quality, never financial work."""

from collections import defaultdict
from pathlib import Path

import pyproj
import shapely
from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry

from spain_housing.models.geography import (
    AtlasCollection,
    AtlasFeature,
    DisplayQuality,
    NeutralConflict,
)
from spain_housing.storage.files import canonical_json
from spain_housing.storage.geography import (
    file_record,
    geography_reference,
    geometry_counts,
    load_geography,
    write_display,
)

METRIC_CRS = {"mainland": "EPSG:25830", "balearics": "EPSG:25831", "canarias": "EPSG:4083"}


def _group(feature: AtlasFeature) -> str:
    province = feature.properties.province_code
    return (
        "canarias" if province in ("35", "38") else "balearics" if province == "07" else "mainland"
    )


def _transform(geometry: BaseGeometry, transformer: Transformer) -> BaseGeometry:
    # The installed stub does not model Shapely's public interleaved=False callback.
    return shapely.transform(geometry, transformer.transform, interleaved=False)  # type: ignore[arg-type]


def _structure(geometry: BaseGeometry) -> tuple[int, tuple[int, ...]]:
    polygons = list(shapely.get_parts(geometry))
    return len(polygons), tuple(sorted(len(p.interiors) for p in polygons))


def prepare_display(
    geography_dir: Path,
    *,
    artifact_root: Path,
    tolerance_m: float = 50.0,
    neutral_source_conflicts: bool = False,
) -> Path:
    if tolerance_m not in (20.0, 50.0, 100.0):
        raise ValueError(
            "display tolerance must be one of the bounded candidates 20, 50, 100 metres"
        )
    geography = load_geography(geography_dir)
    assert geography.boundaries is not None and geography.provinces is not None
    source = list(geography.boundaries.features)
    neutral_conflicts = []
    if neutral_source_conflicts:
        by_id = {f.id: index for index, f in enumerate(source)}
        for conflict in geography.manifest.recipe.source_conflicts:
            first, second = (source[by_id[identity]] for identity in conflict.feature_ids)
            if first.properties.province_code != second.properties.province_code:
                raise ValueError(
                    "neutral conflict crosses provinces; an explicit orientation policy is required"
                )
            original = [shape(f.geometry.model_dump(mode="json")) for f in (first, second)]
            # Shared line-only boundaries carry no conflicting area or ownership.
            intersection = original[0].intersection(original[1])
            patch = shapely.union_all(
                [
                    part
                    for part in shapely.get_parts(intersection)
                    if part.geom_type in ("Polygon", "MultiPolygon")
                ]
            )
            if patch.is_empty or patch.geom_type not in ("Polygon", "MultiPolygon"):
                raise ValueError("source conflict has no polygonal intersection")
            metric_crs = METRIC_CRS[_group(first)]
            forward = Transformer.from_crs("OGC:CRS84", metric_crs, always_xy=True)
            identity = "source-conflict:" + ":".join(sorted(conflict.feature_ids))
            neutral_conflicts.append(
                NeutralConflict(
                    feature_id=identity,
                    source_feature_ids=conflict.feature_ids,
                    area_m2=_transform(patch, forward).area,
                    metric_crs=metric_crs,
                )
            )
            for feature, geometry in zip((first, second), original, strict=True):
                source[by_id[feature.id]] = AtlasFeature.model_validate(
                    feature.model_dump(mode="json")
                    | {"geometry": mapping(geometry.difference(patch))}
                )
            source.append(
                AtlasFeature.model_validate(
                    dict(
                        id=identity,
                        properties=dict(
                            location_code=None,
                            name="Source boundary conflict: "
                            + first.properties.name
                            + " / "
                            + second.properties.name,
                            province_code=first.properties.province_code,
                            kind="source_conflict",
                            source_national_code="intersection:" + ":".join(conflict.feature_ids),
                        ),
                        geometry=mapping(patch),
                    )
                )
            )
    groups: dict[str, list[AtlasFeature]] = defaultdict(list)
    for feature in source:
        groups[_group(feature)].append(feature)
    canonical = {f.id: f for f in geography.boundaries.features}
    display_features: list[AtlasFeature] = []
    area_errors: list[tuple[float, str]] = []
    displacements: list[tuple[float, str]] = []
    for group, features in sorted(groups.items()):
        metric_crs = METRIC_CRS[group]
        forward = Transformer.from_crs("OGC:CRS84", metric_crs, always_xy=True)
        backward = Transformer.from_crs(metric_crs, "OGC:CRS84", always_xy=True)
        original = [
            _transform(shape(f.geometry.model_dump(mode="json")), forward) for f in features
        ]
        if not shapely.coverage_is_valid(original):
            raise ValueError(f"{group}: source does not form metric edge-matched coverage")
        simplified = shapely.coverage_simplify(original, tolerance_m)
        if not shapely.coverage_is_valid(simplified):
            raise ValueError("coverage simplification introduced invalid shared topology")
        for feature, before, after in zip(features, original, simplified, strict=True):
            geographic = _transform(after, backward)
            # Measure what is actually serialized, including the inverse transformation.
            actual = _transform(geographic, forward)
            code = feature.properties.location_code or feature.id
            if actual.is_empty or not actual.is_valid or _structure(actual) != _structure(before):
                raise ValueError(f"display loses polygon components/holes or validity: {code}")
            reference = (
                _transform(shape(canonical[feature.id].geometry.model_dump(mode="json")), forward)
                if feature.id in canonical
                else before
            )
            if _structure(actual) != _structure(reference):
                raise ValueError(f"display loses canonical polygon components/holes: {code}")
            relative_area = abs(actual.area - reference.area) / reference.area
            displacement = float(
                shapely.hausdorff_distance(reference.boundary, actual.boundary, densify=0.25)
            )
            if relative_area > 0.02 or displacement > 250:
                raise ValueError(
                    f"display fidelity gate failed for {code}: area={relative_area:.6g}, "
                    f"displacement_m={displacement:.6g}"
                )
            area_errors.append((relative_area, code))
            displacements.append((displacement, code))
            display_features.append(
                AtlasFeature.model_validate(
                    feature.model_dump(mode="json") | {"geometry": mapping(geographic)}
                )
            )
    boundaries = AtlasCollection(features=tuple(sorted(display_features, key=lambda f: f.id)))
    if not shapely.coverage_is_valid(
        [shape(f.geometry.model_dump(mode="json")) for f in boundaries.features]
    ):
        raise ValueError("inverse transform introduced invalid geographic coverage")
    province_sources = {f.properties.province_code: f for f in geography.provinces.features}
    province_members: dict[str, list[BaseGeometry]] = defaultdict(list)
    for feature in boundaries.features:
        if feature.properties.province_code is not None:
            province_members[feature.properties.province_code].append(
                shape(feature.geometry.model_dump(mode="json"))
            )
    provinces = AtlasCollection(
        features=tuple(
            AtlasFeature.model_validate(
                province_sources[code].model_dump(mode="json")
                | {"geometry": mapping(shapely.union_all(members))}
            )
            for code, members in sorted(province_members.items())
        )
    )
    counts = geometry_counts(boundaries, len(provinces.features))
    worst_area, area_code = max(area_errors)
    worst_displacement, displacement_code = max(displacements)
    quality = DisplayQuality(
        tolerance_m=tolerance_m,
        metric_crs=tuple(METRIC_CRS[group] for group in sorted(groups)),
        algorithm=(
            "coverage-vw-v1; shared/outer edges; metric QA; "
            "symmetric GEOS Hausdorff densify=0.25; province unions of rendered coverage"
        ),
        shapely_version=shapely.__version__,
        geos_version=shapely.geos_version_string,
        pyproj_version=pyproj.__version__,
        max_relative_area_change=worst_area,
        max_boundary_displacement_m=worst_displacement,
        worst_area_code=area_code,
        worst_displacement_code=displacement_code,
        original_vertices=geography.manifest.counts.vertices,
        display_vertices=counts.vertices,
        coverage_valid=True,
    )
    payloads = {
        "display.geojson": canonical_json(boundaries.model_dump(mode="json")),
        "provinces.geojson": canonical_json(provinces.model_dump(mode="json")),
    }
    metadata = dict(
        schema_version=1,
        parent=geography_reference(geography.manifest).model_dump(mode="json"),
        files=[
            file_record(name, data, count).model_dump(mode="json")
            for (name, data), count in zip(
                payloads.items(), (len(boundaries.features), len(provinces.features)), strict=True
            )
        ],
        quality=quality.model_dump(mode="json"),
        neutral_conflicts=[c.model_dump(mode="json") for c in neutral_conflicts],
        counts=counts.model_dump(mode="json"),
        attribution=geography.manifest.recipe.attribution
        + " Simplified display derivative; not a legal boundary survey."
        + (
            " Source overlaps are neutral display context, assigned to neither municipality."
            if neutral_conflicts
            else ""
        ),
        redistribution=geography.manifest.redistribution,
    )
    return write_display(artifact_root, metadata, payloads, geography)
