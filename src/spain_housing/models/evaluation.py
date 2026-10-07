"""Immutable public evaluation metadata and economic input traces."""

from typing import Annotated, Literal

from pydantic import Field, model_validator

from .base import Money, Month, PositiveFinite, Record
from .dataset import LocationRecord, ReferenceProfile, Text, UsageScope
from .market import MarketObservation


class EvaluationContext(Record):
    release_id: Text
    kind: Literal["observed", "synthetic"]
    readiness: Literal["ready", "incomplete", "synthetic_only"]
    redistribution: UsageScope
    profiles: tuple[ReferenceProfile, ...]
    locations: tuple[LocationRecord, ...]
    registry_version: Text
    boundary_version: Text
    attribution: Text
    limitations: tuple[Text, ...] = ()

    @model_validator(mode="after")
    def unique_metadata(self) -> "EvaluationContext":
        if len({p.profile_id for p in self.profiles}) != len(self.profiles):
            raise ValueError("context profile IDs must be unique")
        if len({loc.location for loc in self.locations}) != len(self.locations):
            raise ValueError("context locations must be unique")
        if (self.kind == "synthetic") != (self.readiness == "synthetic_only"):
            raise ValueError("context kind and readiness disagree")
        return self


class MarketInputUse(Record):
    role: Literal["room_rent", "whole_home_rent", "purchase_price"]
    profile_id: Text
    observation: MarketObservation
    reference_anchor_month: Month
    base_month: Month
    value_at_base: PositiveFinite
    annual_growth_fraction: Annotated[float, Field(strict=True, allow_inf_nan=False, gt=-1)]
    proxy_for_property_type: Literal["flat", "house"] | None = None
    notes: tuple[Text, ...] = ()


class PurchaseFinances(Record):
    purchase_month: Month
    borrower_monthly_net_income_eur: Money
    borrower_monthly_other_debt_eur: Money


class DependencyVersion(Record):
    name: Text
    version: Text


class RuntimeEvidence(Record):
    python_version: Text
    dependencies: tuple[DependencyVersion, ...]

    @model_validator(mode="after")
    def ordered_dependencies(self) -> "RuntimeEvidence":
        names = [dependency.name for dependency in self.dependencies]
        if names != sorted(set(names)):
            raise ValueError("runtime dependencies must be unique and sorted")
        return self
