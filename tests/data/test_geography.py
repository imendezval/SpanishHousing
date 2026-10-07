import io

import pytest
from conftest import FIXTURES
from openpyxl import Workbook

from spain_housing.ingestion.geography import select_boundaries, verify_registry
from spain_housing.models.dataset import BoundaryCollection, BuildRecipe
from spain_housing.storage.release import (
    canonical_json,
    read_capture,
    strict_json,
    validate_geometry,
)


def boundaries(recipe: BuildRecipe) -> BoundaryCollection:
    captures = {c.capture_id: read_capture(FIXTURES, c) for c in recipe.captures}
    return select_boundaries(recipe, captures)


def test_control_digit_leading_zero_full_multipart_and_holes(recipe: BuildRecipe) -> None:
    capture = next(c for c in recipe.captures if c.capture_id == "registry")
    verify_registry(read_capture(FIXTURES, capture), "csv", recipe.locations)
    selected = boundaries(recipe)
    barcelona = next(f for f in selected.features if f.properties.location_code == "08019")
    madrid = next(f for f in selected.features if f.properties.location_code == "28079")
    assert barcelona.geometry.type == "MultiPolygon"
    assert len(barcelona.geometry.coordinates) == 2
    assert len(madrid.geometry.coordinates) == 2  # exterior plus retained hole
    with pytest.raises(ValueError, match="INE identity"):
        verify_registry(
            read_capture(FIXTURES, capture).replace(b"08,019,0", b"08,019,1"),
            "csv",
            recipe.locations,
        )


def test_actual_xlsx_adapter_reads_documented_numeric_column_widths(recipe: BuildRecipe) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["Official table title"])
    sheet.append(["CODAUTO", "CPRO", "CMUN", "DC", "NOMBRE"])
    for location in recipe.locations:
        sheet.append(
            [
                0,
                int(location.province_code),
                int(location.location.code[2:]),
                0,
                location.official_name,
            ]
        )
    buffer = io.BytesIO()
    workbook.save(buffer)
    workbook.close()
    verify_registry(buffer.getvalue(), "xlsx", recipe.locations)


@pytest.mark.parametrize(
    "defect", ["province", "wrong_id", "missing", "duplicate", "pagination", "projected"]
)
def test_source_identity_and_completeness_failures(recipe: BuildRecipe, defect: str) -> None:
    captures = {c.capture_id: read_capture(FIXTURES, c) for c in recipe.captures}
    source = strict_json(captures["boundaries"])
    if defect == "province":
        source["features"][0]["properties"]["nationallevelname"] = "Provincia"
    elif defect == "wrong_id":
        source["features"][0]["properties"]["nationalcode"] = "unverified"
    elif defect == "missing":
        source["features"].pop()
    elif defect == "duplicate":
        source["features"][-1] = source["features"][0]
    elif defect == "pagination":
        source["links"] = [{"rel": "next", "href": "https://example.org/page2"}]
    else:
        source["crs"] = "EPSG:3857"
    captures["boundaries"] = canonical_json(source)
    with pytest.raises(ValueError):
        select_boundaries(recipe, captures)


@pytest.mark.parametrize(
    "coordinates",
    [
        [],
        [[[-4, 40], [-3, 41], [-4, 41], [-3, 40], [-4, 40]]],
        [[[-4, 40], [-3, 40], [-3, 41]]],
        [[[40, -4], [41, -4], [41, -3], [40, -3], [40, -4]]],
    ],
)
def test_empty_open_self_intersecting_and_axis_errors(
    recipe: BuildRecipe, coordinates: list
) -> None:
    original = boundaries(recipe).model_dump(mode="json")
    original["features"][0]["geometry"] = {"type": "Polygon", "coordinates": coordinates}
    with pytest.raises(ValueError):
        validate_geometry(BoundaryCollection.model_validate(original), recipe.locations)
