"""Period-aware market observations and explicit lookup states."""

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import HttpUrl, field_validator, model_validator

from .base import Month, PositiveFinite, PositiveInt, Record
from .scenario import GeographicReference

MarketStatistic = Literal["mean", "median", "p10", "p25", "p75", "p90", "weighted_zonal_medians"]
MarketBasis = Literal["asking", "transaction", "valuation", "tax_declared"]


class MarketMetric(StrEnum):
    PURCHASE_PRICE_PER_M2 = "purchase_price_per_m2"
    WHOLE_HOME_RENT_PER_M2_MONTH = "whole_home_rent_per_m2_month"
    WHOLE_HOME_RENT_PER_MONTH = "whole_home_rent_per_month"
    ROOM_RENT_PER_MONTH = "room_rent_per_month"


class MarketUnit(StrEnum):
    EUR_PER_M2 = "eur_per_m2"
    EUR_PER_M2_MONTH = "eur_per_m2_month"
    EUR_PER_MONTH = "eur_per_month"


METRIC_UNITS: dict[MarketMetric, MarketUnit] = {
    MarketMetric.PURCHASE_PRICE_PER_M2: MarketUnit.EUR_PER_M2,
    MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH: MarketUnit.EUR_PER_M2_MONTH,
    MarketMetric.WHOLE_HOME_RENT_PER_MONTH: MarketUnit.EUR_PER_MONTH,
    MarketMetric.ROOM_RENT_PER_MONTH: MarketUnit.EUR_PER_MONTH,
}


class MarketSegment(Record):
    property_type: Literal["flat", "house", "room", "pooled"]
    size_band: str | None = None
    bedrooms: PositiveInt | None = None
    rental_contract_category: Literal["permanent", "seasonal", "mixed"] | None = None


class MarketQuery(Record):
    location: GeographicReference
    period_start: Month
    period_end: Month
    metric: MarketMetric
    segment: MarketSegment | None = None

    @model_validator(mode="after")
    def valid_period(self) -> "MarketQuery":
        if self.period_end <= self.period_start:
            raise ValueError("period_end must follow period_start")
        return self


class MarketObservation(Record):
    location: GeographicReference
    boundary_version: str | None = None
    period_start: Month
    period_end: Month
    retrieved_at: datetime
    source_release: str | None = None
    methodology_version: str | None = None
    metric: MarketMetric
    value: PositiveFinite
    unit: MarketUnit
    statistic: MarketStatistic
    basis: MarketBasis
    segment: MarketSegment
    source_id: str
    source_url: HttpUrl | None = None
    evidence_kind: Literal["observed", "estimated", "synthetic"]
    estimation_method: str | None = None
    sample_count: PositiveInt | None = None
    quality_notes: tuple[str, ...] = ()

    @field_validator("retrieved_at", mode="before")
    @classmethod
    def explicit_timestamp(cls, value: object) -> object:
        if not isinstance(value, (str, datetime)):
            raise ValueError("retrieved_at must be an ISO timestamp")
        return value

    @model_validator(mode="after")
    def consistent_evidence(self) -> "MarketObservation":
        if self.period_end <= self.period_start:
            raise ValueError("period_end must follow period_start")
        if self.retrieved_at.tzinfo is None or self.retrieved_at.utcoffset() is None:
            raise ValueError("retrieved_at must include a timezone")
        if self.unit != METRIC_UNITS[self.metric]:
            raise ValueError(f"{self.metric} requires unit {METRIC_UNITS[self.metric]}")
        if self.metric == MarketMetric.ROOM_RENT_PER_MONTH and self.segment.property_type != "room":
            raise ValueError("room rent requires a room segment")
        if self.metric != MarketMetric.ROOM_RENT_PER_MONTH and self.segment.property_type == "room":
            raise ValueError("whole-home or purchase metrics cannot use a room segment")
        if self.evidence_kind == "synthetic":
            if not self.source_id.startswith("synthetic:"):
                raise ValueError("synthetic observations require a synthetic: source ID")
        elif self.source_id.startswith("synthetic:") or self.source_url is None:
            raise ValueError("observed/estimated observations require a real source URL and ID")
        if self.evidence_kind == "estimated" and not self.estimation_method:
            raise ValueError("estimated observations require estimation_method")
        if self.evidence_kind != "estimated" and self.estimation_method is not None:
            raise ValueError("estimation_method is only valid for estimates")
        return self


class MarketLookup(Record):
    status: Literal["available", "missing", "unsupported"]
    observation: MarketObservation | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def consistent_status(self) -> "MarketLookup":
        if self.status == "available" and self.observation is None:
            raise ValueError("available lookup requires an observation")
        if self.status != "available" and (self.observation is not None or not self.reason):
            raise ValueError("missing/unsupported lookup requires a reason and no observation")
        return self
