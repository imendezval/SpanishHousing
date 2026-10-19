"""Shared unchanged-coordinate polygon checks for legacy releases and atlas artifacts."""

from shapely.geometry import shape
from shapely.validation import explain_validity

from spain_housing.models.dataset import MultiPolygonGeometry, PolygonGeometry


def validate_polygon(geometry: PolygonGeometry | MultiPolygonGeometry) -> None:
    polygons = (geometry.coordinates,) if geometry.type == "Polygon" else geometry.coordinates
    if not polygons:
        raise ValueError("empty polygon geometry")
    for polygon in polygons:
        if not polygon:
            raise ValueError("empty polygon")
        for ring in polygon:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise ValueError(
                    "polygon rings must be explicitly closed with at least four positions"
                )
            for longitude, latitude in ring:
                # Inspected IGN Spain extent catches projected coordinates and swapped axes.
                if not (-19 <= longitude <= 5 and 27 <= latitude <= 44):
                    raise ValueError("coordinates must be Spain longitude/latitude in OGC:CRS84")
    polygon_shape = shape(geometry.model_dump(mode="json"))
    if polygon_shape.is_empty or not polygon_shape.is_valid:
        raise ValueError(f"invalid polygon topology: {explain_validity(polygon_shape)}")
