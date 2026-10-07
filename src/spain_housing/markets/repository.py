"""Read-only indexed access to one explicitly selected, fully validated release."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType

from spain_housing.models.dataset import BoundaryCollection, LocationRecord, ReleaseManifest
from spain_housing.models.market import (
    MarketLookup,
    MarketMetric,
    MarketObservation,
    MarketQuery,
    MarketSegment,
)
from spain_housing.storage.release import load_release

IndexKey = tuple[str, MarketMetric, date, date]


def _matches_segment(requested: MarketSegment | None, supplied: MarketSegment) -> bool:
    if requested is None:
        return True
    return requested.property_type == supplied.property_type and all(
        value is None or value == getattr(supplied, name)
        for name, value in (
            ("size_band", requested.size_band),
            ("bedrooms", requested.bedrooms),
            ("rental_contract_category", requested.rental_contract_category),
        )
    )


@dataclass(frozen=True, slots=True)
class SnapshotMarketRepository:
    manifest: ReleaseManifest
    locations: tuple[LocationRecord, ...]
    boundaries: BoundaryCollection
    _index: Mapping[IndexKey, tuple[MarketObservation, ...]]

    @classmethod
    def from_release(
        cls, release_dir: Path, *, allow_synthetic: bool = False
    ) -> "SnapshotMarketRepository":
        bundle = load_release(release_dir, allow_synthetic=allow_synthetic)
        grouped: dict[IndexKey, list[MarketObservation]] = {}
        for row in bundle.observations:
            observation = row.observation
            key = (
                observation.location.code,
                observation.metric,
                observation.period_start,
                observation.period_end,
            )
            grouped.setdefault(key, []).append(observation)
        index = MappingProxyType({key: tuple(values) for key, values in grouped.items()})
        return cls(bundle.manifest, bundle.locations, bundle.boundaries, index)

    def get(self, query: MarketQuery) -> MarketLookup:
        if not isinstance(query, MarketQuery):
            raise ValueError("query must be a validated MarketQuery")
        if query.location.level != "municipality":
            return MarketLookup(
                status="unsupported",
                reason="geographic level is not supported: municipality required",
            )
        profiles = [
            profile for profile in self.manifest.recipe.profiles if profile.metric == query.metric
        ]
        if not profiles:
            return MarketLookup(
                status="unsupported", reason="metric is not supported by this release"
            )
        if not any(_matches_segment(query.segment, profile.segment) for profile in profiles):
            return MarketLookup(
                status="unsupported", reason="requested segment is not supported by this release"
            )
        if not any(location.location == query.location for location in self.locations):
            return MarketLookup(status="missing", reason="municipality is outside this release")
        candidates = [
            observation
            for observation in self._index.get(
                (query.location.code, query.metric, query.period_start, query.period_end), ()
            )
            if _matches_segment(query.segment, observation.segment)
        ]
        if not candidates:
            return MarketLookup(
                status="missing",
                reason="no observation for this municipality, metric, exact interval and segment",
            )
        if len(candidates) != 1:
            return MarketLookup(
                status="unsupported", reason="ambiguous selection: specify the housing segment"
            )
        return MarketLookup(status="available", observation=candidates[0])
