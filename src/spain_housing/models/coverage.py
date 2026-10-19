"""Immutable inspection of validated dataset evidence, separate from scenarios."""

from typing import Literal

from .base import Offset, Record, SchemaVersion
from .dataset import (
    CaptureRecord,
    CoverageCell,
    CoverageSummary,
    GeographyReference,
    LocationRecord,
    ReferenceProfile,
    SourceDecision,
    Text,
    UsageScope,
)
from .market import MarketUnit


class EvidenceCounts(Record):
    observed: Offset
    estimated: Offset
    synthetic: Offset


class ProfileCoverage(Record):
    profile: ReferenceProfile
    unit: MarketUnit
    counts: CoverageSummary
    evidence: EvidenceCounts


class ReleaseCoverageReport(Record):
    schema_version: SchemaVersion = 1
    release_id: Text
    geography: GeographyReference | None = None
    kind: Literal["observed", "synthetic"]
    readiness: Literal["ready", "incomplete", "synthetic_only"]
    registry_version: Text
    boundary_version: Text
    attribution: Text
    limitations: tuple[Text, ...]
    redistribution: UsageScope
    decisions: tuple[SourceDecision, ...]
    captures: tuple[CaptureRecord, ...]
    locations: tuple[LocationRecord, ...]
    profiles: tuple[ProfileCoverage, ...]
    cells: tuple[CoverageCell, ...]
    counts: CoverageSummary
    evidence: EvidenceCounts
