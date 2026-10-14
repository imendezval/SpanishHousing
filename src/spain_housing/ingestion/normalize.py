"""Translate retained, reviewed source rows into the existing market contract."""

import re

from spain_housing.models.dataset import BuildRecipe, CaptureRecord, ReleasedObservation
from spain_housing.models.market import METRIC_UNITS, MarketObservation, MarketUnit

from .adapters.curated import CuratedRow

RAW_UNITS = {
    "eur_per_m2": MarketUnit.EUR_PER_M2,
    "€/m²": MarketUnit.EUR_PER_M2,
    "eur_per_m2_month": MarketUnit.EUR_PER_M2_MONTH,
    "€/m²/mes": MarketUnit.EUR_PER_M2_MONTH,
    "eur_per_month": MarketUnit.EUR_PER_MONTH,
    "€/mes": MarketUnit.EUR_PER_MONTH,
}


def parse_numeric(raw_value: str, numeric_format: str) -> float | None:
    value = raw_value.strip().replace("\u00a0", " ")
    if value.casefold() in ("", "-", "..", "n/d", "unreported", "suppressed"):
        return None
    if numeric_format == "es":
        pattern = r"-?(?:\d+|\d{1,3}(?:\.\d{3})+)(?:,\d+)?"
        normalized = value.replace(".", "").replace(",", ".")
    elif numeric_format == "plain":
        pattern = r"-?\d+(?:\.\d+)?"
        normalized = value
    else:
        raise ValueError("numeric format must be explicitly es or plain")
    if re.fullmatch(pattern, value, flags=re.ASCII) is None:
        raise ValueError(f"invalid absolute price in {numeric_format} format: {raw_value!r}")
    return float(normalized)


def normalize_rows(
    rows: tuple[CuratedRow, ...], capture: CaptureRecord, recipe: BuildRecipe
) -> tuple[ReleasedObservation, ...]:
    profiles = {profile.profile_id: profile for profile in recipe.profiles}
    crosswalk = {
        (mapping.source_id, mapping.label): location
        for location in recipe.locations
        for mapping in location.source_mappings
    }
    result = []
    for number, row in enumerate(rows, start=2):
        try:
            profile = profiles.get(row.profile_id)
            location = crosswalk.get((capture.source_id, row.source_location))
            if profile is None or profile.source_id != capture.source_id:
                raise ValueError("curated row references an unselected source/profile")
            if location is None or row.geographic_scope != "municipality":
                raise ValueError("unresolved or nonmunicipal source location")
            if (row.period_start, row.period_end, row.statistic, row.basis) != (
                profile.period_start,
                profile.period_end,
                profile.statistic,
                profile.basis,
            ):
                raise ValueError("source period/statistic/basis changed from the selected profile")
            unit = RAW_UNITS.get(row.raw_unit)
            if unit != METRIC_UNITS[profile.metric]:
                raise ValueError("source raw unit disagrees with metric")
            value = parse_numeric(row.raw_value, recipe.numeric_format)
            if value is None:
                continue
            observation = MarketObservation.model_validate(
                {
                    "location": location.location,
                    "boundary_version": location.boundary_version,
                    "period_start": row.period_start,
                    "period_end": row.period_end,
                    "retrieved_at": capture.captured_at,
                    "source_release": capture.source_release,
                    "methodology_version": capture.methodology_version,
                    "metric": profile.metric,
                    "value": value,
                    "unit": unit,
                    "statistic": profile.statistic,
                    "basis": profile.basis,
                    "segment": profile.segment,
                    "source_id": capture.source_id,
                    "source_url": capture.primary_url,
                    "evidence_kind": row.evidence_kind,
                    "estimation_method": row.estimation_method or None,
                    "quality_notes": tuple(
                        note.strip() for note in row.quality_notes.split("|") if note.strip()
                    ),
                }
            )
            result.append(
                ReleasedObservation(
                    observation=observation,
                    capture_id=capture.capture_id,
                    source_locator=row.source_locator,
                )
            )
        except ValueError as exc:
            raise ValueError(
                f"capture {capture.capture_id} ({capture.source_id}) row {number}, "
                f"profile {row.profile_id}, locator {row.source_locator}: {exc}"
            ) from exc
    return tuple(result)
