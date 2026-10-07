"""Scenario structure and calendar validation; no financial calculation."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field, StrictBool, StringConstraints, model_validator

from .base import (
    Money,
    Month,
    NonNegativeFinite,
    Offset,
    PositiveFinite,
    PositiveInt,
    PositiveRatio,
    Ratio,
    Record,
    SchemaVersion,
    add_months,
)

ParticipantId = Annotated[str, StringConstraints(strict=True, pattern=r"^[a-z][a-z0-9_-]*$")]
LocationCode = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Za-z0-9_-]+$")]


class AmountMilestone(Record):
    month_offset: Offset
    amount_eur: Money


class AmountPath(Record):
    interpolation: Literal["linear", "step"]
    milestones: tuple[AmountMilestone, ...]

    @model_validator(mode="after")
    def ordered(self) -> "AmountPath":
        offsets = [point.month_offset for point in self.milestones]
        if not offsets or offsets[0] != 0 or offsets != sorted(set(offsets)):
            raise ValueError(
                "milestones must start at offset 0 and have strictly increasing offsets"
            )
        return self


class Participant(Record):
    participant_id: ParticipantId
    net_annual_income: AmountPath
    monthly_debt: AmountPath
    starting_savings_eur: Money


class LivingStage(Record):
    arrangement: Literal["room", "flat_alone", "flat_shared"]
    start_month_offset: Offset
    end_month_offset: PositiveInt
    rent_share: PositiveRatio
    rental_area_m2: PositiveFinite | None = None
    bedrooms: PositiveInt | None = None
    rent_includes_utilities: StrictBool

    @model_validator(mode="after")
    def valid_stage(self) -> "LivingStage":
        if self.end_month_offset <= self.start_month_offset:
            raise ValueError("stage end must follow stage start")
        if self.arrangement != "room" and self.rental_area_m2 is None and self.bedrooms is None:
            raise ValueError("flat stage requires rental_area_m2 or bedrooms")
        if self.arrangement == "flat_alone" and self.rent_share != 1:
            raise ValueError("flat_alone requires rent_share of 1")
        return self


class MortgageAssumptions(Record):
    financed_fraction: PositiveRatio
    maximum_debt_ratio: Ratio
    term_years: PositiveInt
    annual_nominal_interest_fraction: NonNegativeFinite


class PurchaseCostAssumptions(Record):
    policy: Literal["proportional"]
    allowance_fraction: NonNegativeFinite


class TargetProperty(Record):
    property_type: Literal["flat", "house"]
    area_m2: PositiveFinite
    condition: Literal["ordinary", "new", "renovation"]


class MarketPolicy(Record):
    kind: Literal["frozen", "growth"]
    base_month: Month
    annual_rent_growth_fraction: Annotated[float, Field(strict=True, allow_inf_nan=False, gt=-1)]
    annual_purchase_growth_fraction: Annotated[
        float, Field(strict=True, allow_inf_nan=False, gt=-1)
    ]

    @model_validator(mode="after")
    def frozen_has_zero_growth(self) -> "MarketPolicy":
        if self.kind == "frozen" and (
            self.annual_rent_growth_fraction != 0 or self.annual_purchase_growth_fraction != 0
        ):
            raise ValueError("frozen market policy requires zero growth fractions")
        return self


class GeographicReference(Record):
    level: Literal["municipality", "province", "autonomous_community"]
    code: LocationCode


class MarketSelectionPolicy(Record):
    strategy: Literal["latest_complete"] = "latest_complete"
    maximum_reference_age_months: Offset = 12
    profile_ids: tuple[Annotated[str, StringConstraints(strict=True, min_length=1)], ...] = ()
    whole_home_rent_source: Literal["per_m2", "per_month"] = "per_m2"
    allow_pooled_property_proxy: StrictBool = False

    @model_validator(mode="after")
    def unique_profiles(self) -> "MarketSelectionPolicy":
        if len(self.profile_ids) != len(set(self.profile_ids)):
            raise ValueError("profile_ids must be unique")
        return self


class LocationBinding(Record):
    kind: Literal["mapped", "explicit"]
    location: GeographicReference | None = None

    @model_validator(mode="after")
    def valid_binding(self) -> "LocationBinding":
        if (self.kind == "explicit") != (self.location is not None):
            raise ValueError("explicit binding requires a location; mapped binding must omit it")
        return self


class LocationPlan(Record):
    mode: Literal["local_local", "fixed_saving"]
    saving_location: LocationBinding
    buying_location: LocationBinding

    @model_validator(mode="after")
    def valid_mode(self) -> "LocationPlan":
        if self.mode == "local_local" and (
            self.saving_location.kind != "mapped" or self.buying_location.kind != "mapped"
        ):
            raise ValueError("local_local requires separate mapped saving and buying bindings")
        if self.mode == "fixed_saving" and (
            self.saving_location.kind != "explicit" or self.buying_location.kind != "mapped"
        ):
            raise ValueError("fixed_saving requires explicit saving and mapped buying bindings")
        return self


class Scenario(Record):
    schema_version: SchemaVersion
    start_month: Month
    saving_months: PositiveInt
    participants: tuple[Participant, ...]
    saver_ids: tuple[ParticipantId, ...]
    borrower_ids: tuple[ParticipantId, ...]
    living_stages: tuple[LivingStage, ...]
    household_nonhousing_expenses: AmountPath
    retained_reserve_eur: Money
    mortgage: MortgageAssumptions
    purchase_costs: PurchaseCostAssumptions
    target_property: TargetProperty
    market_policy: MarketPolicy
    locations: LocationPlan
    market_selection: MarketSelectionPolicy = Field(default_factory=MarketSelectionPolicy)

    @property
    def purchase_month(self) -> date:
        return add_months(self.start_month, self.saving_months)

    @model_validator(mode="after")
    def valid_structure(self) -> "Scenario":
        ids = [participant.participant_id for participant in self.participants]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("participants must contain unique IDs and cannot be empty")
        for label, members in (("saver_ids", self.saver_ids), ("borrower_ids", self.borrower_ids)):
            if not members or len(members) != len(set(members)) or not set(members) <= set(ids):
                raise ValueError(f"{label} must be nonempty, unique, and reference participants")
        offset = 0
        for stage in self.living_stages:
            if stage.start_month_offset != offset:
                raise ValueError("living stages must cover the horizon without gaps or overlaps")
            offset = stage.end_month_offset
        if offset != self.saving_months:
            raise ValueError("living stages must end at saving_months")
        return self
