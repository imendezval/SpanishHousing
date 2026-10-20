import pytest

from fixtures import PILOT
from spain_housing.ingestion.adapters.curated import read_curated_csv
from spain_housing.ingestion.normalize import normalize_rows, parse_numeric
from spain_housing.models.dataset import BuildRecipe
from spain_housing.storage.release import read_capture


@pytest.mark.parametrize(
    "raw,format,expected",
    [
        ("6.458", "es", 6458),
        ("23,4", "es", 23.4),
        ("1.234,56", "es", 1234.56),
        ("23.4", "plain", 23.4),
        ("", "es", None),
        ("n/d", "es", None),
        ("..", "plain", None),
    ],
)
def test_explicit_locale_references(raw: str, format: str, expected: float | None) -> None:
    assert parse_numeric(raw, format) == expected


@pytest.mark.parametrize(
    "raw,format",
    [
        ("23.4", "es"),
        ("1,200", "plain"),
        ("5%", "es"),
        ("NaN", "plain"),
        ("inf", "es"),
        ("true", "es"),
        ("1.2.3", "es"),
    ],
)
def test_invalid_or_percent_only_values_are_rejected(raw: str, format: str) -> None:
    with pytest.raises(ValueError, match="absolute price"):
        parse_numeric(raw, format)


def test_normalized_values_keep_capture_time_periods_and_source_meaning(
    recipe: BuildRecipe,
) -> None:
    capture = next(c for c in recipe.captures if c.capture_id == "prices")
    rows = read_curated_csv(read_capture(PILOT, capture))
    result = normalize_rows(rows, capture, recipe)
    assert result[0].observation.value == 3_000
    assert result[1].observation.value == 12.5
    assert result[0].observation.retrieved_at == capture.captured_at
    assert result[0].observation.statistic == "weighted_zonal_medians"
    assert result[0].observation.segment.property_type == "pooled"
    assert result[0].source_locator == "row 1"
    room_capture = next(c for c in recipe.captures if c.capture_id == "rooms")
    rooms = normalize_rows(
        read_curated_csv(read_capture(PILOT, room_capture)), room_capture, recipe
    )
    assert rooms[0].observation.period_start.isoformat() == "2026-04-01"
    assert rooms[0].observation.period_end.isoformat() == "2026-07-01"
    assert rooms[0].observation.statistic == "mean"


@pytest.mark.parametrize(
    "change",
    [
        {"raw_unit": "%"},
        {"period_end": "2026-11-01"},
        {"statistic": "median"},
        {"basis": "valuation"},
        {"source_location": "Madrid province"},
        {"geographic_scope": "province"},
        {"raw_value": "0"},
        {"raw_value": "-1"},
        {"raw_value": "9" * 400},
        {"profile_id": "unknown"},
    ],
)
def test_wrong_source_details_are_not_silently_normalized(
    recipe: BuildRecipe, change: dict
) -> None:
    capture = next(c for c in recipe.captures if c.capture_id == "prices")
    original = read_curated_csv(read_capture(PILOT, capture))[0]
    row = type(original).model_validate(original.model_dump() | change)
    with pytest.raises(ValueError):
        normalize_rows((row,), capture, recipe)


def test_suppressed_values_are_missing_and_csv_errors_are_rejected(recipe: BuildRecipe) -> None:
    capture = next(c for c in recipe.captures if c.capture_id == "prices")
    original = read_curated_csv(read_capture(PILOT, capture))[0]
    assert (
        normalize_rows((original.model_copy(update={"raw_value": "suppressed"}),), capture, recipe)
        == ()
    )
    with pytest.raises(ValueError, match="headers"):
        read_curated_csv(b"raw_value,raw_value\n1,2\n")
    with pytest.raises(ValueError, match="headers"):
        read_curated_csv(b"<html>error</html>")
