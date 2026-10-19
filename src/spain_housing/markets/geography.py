"""Read-only official display composition and a compatible legacy fixture projection."""

from pathlib import Path

from spain_housing.models.dataset import BoundaryCollection
from spain_housing.models.evaluation import EvaluationContext
from spain_housing.models.geography import AtlasCollection, AtlasFeature, MapGeography, Municipality
from spain_housing.storage.geography import load_display, load_geography


def open_map_geography(geography_dir: Path, display_dir: Path) -> MapGeography:
    geography = load_geography(geography_dir, full=False)
    display = load_display(display_dir, geography)
    return MapGeography(
        geography_id=geography.manifest.artifact_id,
        display_id=display.manifest.artifact_id,
        boundary_version=geography.manifest.recipe.boundary_version,
        origin="official",
        attribution=display.manifest.attribution,
        municipalities=geography.registry,
        boundaries=display.boundaries,
        provinces=display.provinces,
    )


def embedded_map_geography(
    context: EvaluationContext, boundaries: BoundaryCollection
) -> MapGeography:
    """Retain legacy geometry/provenance; never relabel synthetic fixture coordinates."""
    locations = {r.location.code: r for r in context.locations}
    features = tuple(
        AtlasFeature.model_validate(
            dict(
                id=f.id,
                properties=dict(
                    location_code=f.properties.location_code,
                    name=locations[f.properties.location_code].official_name,
                    province_code=locations[f.properties.location_code].province_code,
                    kind="municipality",
                    source_national_code=locations[
                        f.properties.location_code
                    ].geometry_national_code,
                ),
                geometry=f.geometry.model_dump(mode="json"),
            )
        )
        for f in boundaries.features
    )
    municipalities = tuple(
        Municipality(
            code=r.location.code,
            official_name=r.official_name,
            province_code=r.province_code,
            control_digit=r.control_digit,
            feature_id=r.geometry_feature_id,
            national_code=r.geometry_national_code,
            source_name=r.official_name,
        )
        for r in context.locations
    )
    return MapGeography(
        geography_id="embedded:" + context.release_id,
        display_id="embedded:" + context.release_id,
        boundary_version=context.boundary_version,
        origin="synthetic" if context.kind == "synthetic" else "official",
        attribution=context.attribution,
        municipalities=municipalities,
        boundaries=AtlasCollection(features=features),
        provinces=AtlasCollection(features=()),
    )
