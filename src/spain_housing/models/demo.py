"""Explicit settings for self-authored synthetic economic assumptions."""

from typing import Literal

from pydantic import AwareDatetime, model_validator

from .base import Month, PositiveFinite, Record
from .dataset import CoverageCell, MunicipalCode, Text


class DemoRange(Record):
    minimum: PositiveFinite
    maximum: PositiveFinite

    @model_validator(mode="after")
    def ordered(self) -> "DemoRange":
        if self.maximum < self.minimum:
            raise ValueError("synthetic range maximum must not precede minimum")
        return self


class DemoOverride(Record):
    code: MunicipalCode
    purchase_per_m2: PositiveFinite
    rent_per_m2_month: PositiveFinite
    room_per_month: PositiveFinite


class DemoConfig(Record):
    generator_version: Literal["national-demo-v1"] = "national-demo-v1"
    seed: Text
    logical_timestamp: AwareDatetime
    period_start: Month
    period_end: Month
    purchase_per_m2: DemoRange
    rent_per_m2_month: DemoRange
    room_per_month: DemoRange
    core_codes: tuple[MunicipalCode, ...] = ()
    partial_codes: tuple[MunicipalCode, ...]
    partial_gaps: tuple[CoverageCell, ...]
    overrides: tuple[DemoOverride, ...] = ()

    @model_validator(mode="after")
    def valid_selection(self) -> "DemoConfig":
        if self.period_end <= self.period_start:
            raise ValueError("synthetic period end must follow start")
        for codes in (self.core_codes, self.partial_codes, tuple(o.code for o in self.overrides)):
            if len(codes) != len(set(codes)):
                raise ValueError("duplicate synthetic configuration code")
        if any(
            g.status == "available" or g.location_code not in self.partial_codes
            for g in self.partial_gaps
        ):
            raise ValueError("partial demo gaps must be actual gaps in its declared subset")
        return self
