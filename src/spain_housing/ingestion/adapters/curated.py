"""Read an explicit reviewed CSV; curation does not establish source permission."""

import csv
import io

from pydantic import StrictStr

from spain_housing.models.base import Month, Record
from spain_housing.models.market import MarketBasis, MarketStatistic


class CuratedRow(Record):
    profile_id: StrictStr
    source_location: StrictStr
    geographic_scope: StrictStr
    raw_value: StrictStr
    raw_unit: StrictStr
    period_start: Month
    period_end: Month
    statistic: MarketStatistic
    basis: MarketBasis
    source_locator: StrictStr
    evidence_kind: StrictStr
    estimation_method: StrictStr
    quality_notes: StrictStr


def read_curated_csv(data: bytes) -> tuple[CuratedRow, ...]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")), strict=True)
    headers = reader.fieldnames
    if (
        headers is None
        or len(headers) != len(set(headers))
        or set(headers) != CuratedRow.model_fields.keys()
    ):
        raise ValueError("curated CSV requires the exact, unique documented headers")
    result = []
    try:
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("curated CSV has an inconsistent row width")
            result.append(CuratedRow.model_validate(row))
    except csv.Error as exc:
        raise ValueError(f"malformed curated CSV: {exc}") from exc
    return tuple(result)
