"""Frozen dataset recipes, provenance and portable release records."""

from datetime import date
from pathlib import PurePosixPath
from typing import Annotated, Literal

from pydantic import (
    AwareDatetime,
    BeforeValidator,
    Field,
    HttpUrl,
    StrictBool,
    StringConstraints,
    field_validator,
    model_validator,
)

from .base import FiniteAmount, Month, Offset, Record, SchemaVersion
from .market import MarketBasis, MarketMetric, MarketObservation, MarketSegment, MarketStatistic
from .scenario import GeographicReference


def _version_two(value: object) -> object:
    if type(value) is not int or value != 2:
        raise ValueError("dataset schema_version must be integer 2")
    return value


DatasetVersionTwo = Annotated[Literal[2], BeforeValidator(_version_two)]

Text = Annotated[str, StringConstraints(strict=True, min_length=1)]
Digest = Annotated[str, StringConstraints(strict=True, pattern=r"^[a-f0-9]{64}$")]
Identifier = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Za-z0-9:_-]+$")]
MunicipalCode = Annotated[str, StringConstraints(strict=True, pattern=r"^\d{5}$")]
UsageScope = Literal["permitted", "restricted", "unresolved"]
FileRole = Literal["observations", "locations", "boundaries", "coverage"]


def relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or path.is_absolute()
        or ".." in path.parts
        or "\\" in value
        or str(path) != value
        or value == "."
        or ":" in value
    ):
        raise ValueError("expected a safe relative POSIX path")
    return value


class SourceDecision(Record):
    source_id: Identifier
    product: Text
    primary_url: HttpUrl | None
    terms_url: HttpUrl | None
    local_use: UsageScope
    redistribution: UsageScope
    evidence_reference: Text
    attribution: Text
    reviewed_on: date
    acquisition_route: Text
    notes: tuple[Text, ...] = ()


class CaptureRecord(Record):
    capture_id: Identifier
    source_id: Identifier
    path: Text
    sha256: Digest
    byte_size: Offset
    primary_url: HttpUrl | None
    resolved_url: HttpUrl | None = None
    captured_at: AwareDatetime
    published_on: date | None = None
    source_release: Text | None = None
    methodology_version: Text | None = None
    route: Literal["provider_download", "curated_extract", "synthetic_fixture"]
    format: Literal["csv", "geojson", "xlsx", "html", "json", "pdf", "xml", "zip"]
    permission_reference: Text
    http_status: Annotated[int, Field(strict=True, ge=100, le=599)] | None = None
    content_type: Text | None = None

    _safe_path = field_validator("path")(relative_path)

    @model_validator(mode="after")
    def download_metadata(self) -> "CaptureRecord":
        if self.route == "provider_download" and (
            self.primary_url is None
            or self.resolved_url is None
            or self.http_status != 200
            or self.content_type is None
        ):
            raise ValueError("provider downloads require successful HTTP metadata and URLs")
        return self


class SourceLocationMapping(Record):
    source_id: Identifier
    label: Text
    scope: Literal["municipality"]


class LocationRecord(Record):
    location: GeographicReference
    official_name: Text
    province_code: Annotated[str, StringConstraints(strict=True, pattern=r"^\d{2}$")]
    control_digit: Annotated[str, StringConstraints(strict=True, pattern=r"^\d$")]
    registry_version: Text
    verification_evidence: Text
    geometry_feature_id: Text
    geometry_national_code: Text
    boundary_version: Text
    core: StrictBool = True
    source_mappings: tuple[SourceLocationMapping, ...]

    @model_validator(mode="after")
    def municipality_identity(self) -> "LocationRecord":
        code = self.location.code
        if (
            self.location.level != "municipality"
            or len(code) != 5
            or not code.isascii()
            or not code.isdigit()
        ):
            raise ValueError("release locations require five-digit municipal codes")
        if self.province_code != code[:2]:
            raise ValueError("province code must agree with the municipal code")
        keys = [(item.source_id, item.label) for item in self.source_mappings]
        if len(keys) != len(set(keys)):
            raise ValueError("duplicate source location mapping")
        return self


class ReferenceProfile(Record):
    profile_id: Identifier
    source_id: Identifier
    metric: MarketMetric
    period_start: Month
    period_end: Month
    segment: MarketSegment
    statistic: MarketStatistic
    basis: MarketBasis

    @model_validator(mode="after")
    def valid_period(self) -> "ReferenceProfile":
        if self.period_end <= self.period_start:
            raise ValueError("profile period_end must follow period_start")
        if (self.metric == MarketMetric.ROOM_RENT_PER_MONTH) != (
            self.segment.property_type == "room"
        ):
            raise ValueError("profile metric and room segment disagree")
        return self


class CoverageCell(Record):
    location_code: MunicipalCode
    profile_id: Identifier
    status: Literal["available", "missing", "unsupported"]
    reason: Text | None = None

    @model_validator(mode="after")
    def coherent_status(self) -> "CoverageCell":
        if (self.status == "available") != (self.reason is None):
            raise ValueError("available coverage has no reason; every gap requires a reason")
        return self


class GeographyMetadata(Record):
    registry_capture_id: Identifier
    boundary_capture_ids: tuple[Identifier, ...]
    registry_version: Text
    registry_effective_on: date
    boundary_version: Text
    source_crs: Literal["OGC:CRS84"]
    target_crs: Literal["OGC:CRS84"]
    attribution: Text
    processing_notes: tuple[Text, ...]


class ProducerEvidence(Record):
    revision: Text
    dirty_fingerprint: Digest | None = None
    code_fingerprint: Digest | None = None


class GeographyReference(Record):
    redistribution: UsageScope
    artifact_id: Annotated[str, StringConstraints(strict=True, pattern=r"^geography-[a-f0-9]{64}$")]
    registry_sha256: Digest
    registry_version: Text
    boundary_version: Text
    attribution: Text


class RecipeFields(Record):
    kind: Literal["observed", "synthetic"]
    processing_version: Text
    producer: ProducerEvidence
    recipe_timestamp: AwareDatetime
    numeric_format: Literal["es", "plain"]
    locations: tuple[LocationRecord, ...]
    profiles: tuple[ReferenceProfile, ...]
    decisions: tuple[SourceDecision, ...]
    captures: tuple[CaptureRecord, ...]
    observation_capture_ids: tuple[Identifier, ...]
    declared_gaps: tuple[CoverageCell, ...] = ()
    limitations: tuple[Text, ...] = ()

    @model_validator(mode="after")
    def unique_recipe_keys(self) -> "RecipeFields":
        for label, keys in (
            ("locations", [item.location.code for item in self.locations]),
            ("profiles", [item.profile_id for item in self.profiles]),
            ("decisions", [item.source_id for item in self.decisions]),
            ("captures", [item.capture_id for item in self.captures]),
        ):
            if not keys or len(keys) != len(set(keys)):
                raise ValueError(f"{label} must be nonempty and unique")
        if len(self.observation_capture_ids) != len(set(self.observation_capture_ids)):
            raise ValueError("duplicate observation capture ID")
        profiles = [
            (item.metric, item.period_start, item.period_end, item.segment)
            for item in self.profiles
        ]
        if len(profiles) != len(set(profiles)):
            raise ValueError(
                "conflicting selected profiles: query has no source/statistic selectors"
            )
        mappings = [
            (item.source_id, item.label)
            for location in self.locations
            for item in location.source_mappings
        ]
        if len(mappings) != len(set(mappings)):
            raise ValueError("ambiguous source label-to-code mapping")
        if not any(location.core for location in self.locations):
            raise ValueError("recipe must declare at least one core location")
        return self


class BuildRecipe(RecipeFields):
    schema_version: SchemaVersion
    geography: GeographyMetadata


class BuildRecipeV2(RecipeFields):
    schema_version: DatasetVersionTwo
    geography: GeographyReference


MarketRecipe = BuildRecipe | BuildRecipeV2


class ReleasedObservation(Record):
    observation: MarketObservation
    capture_id: Identifier
    source_locator: Text


class FileRecord(Record):
    path: Text
    role: FileRole
    sha256: Digest
    byte_size: Offset
    record_count: Offset

    _safe_path = field_validator("path")(relative_path)


class CoverageSummary(Record):
    expected: Offset
    available: Offset
    missing: Offset
    unsupported: Offset


class ManifestFields(Record):
    release_id: Annotated[
        str, StringConstraints(strict=True, pattern=r"^(pilot|synthetic)-[a-f0-9]{64}$")
    ]
    content_digest: Digest
    files: tuple[FileRecord, ...]
    coverage: CoverageSummary
    redistribution: UsageScope
    readiness: Literal["ready", "incomplete", "synthetic_only"]


class ReleaseManifest(ManifestFields):
    schema_version: SchemaVersion
    recipe: BuildRecipe

    @property
    def kind(self) -> Literal["observed", "synthetic"]:
        return self.recipe.kind


class ReleaseManifestV2(ManifestFields):
    schema_version: DatasetVersionTwo
    recipe: BuildRecipeV2

    @property
    def kind(self) -> Literal["observed", "synthetic"]:
        return self.recipe.kind


MarketManifest = ReleaseManifest | ReleaseManifestV2


Position = tuple[FiniteAmount, FiniteAmount]
Ring = tuple[Position, ...]
PolygonCoordinates = tuple[Ring, ...]


class PolygonGeometry(Record):
    type: Literal["Polygon"]
    coordinates: PolygonCoordinates


class MultiPolygonGeometry(Record):
    type: Literal["MultiPolygon"]
    coordinates: tuple[PolygonCoordinates, ...]


class BoundaryProperties(Record):
    location_code: MunicipalCode
    boundary_version: Text


class BoundaryFeature(Record):
    type: Literal["Feature"] = "Feature"
    id: Text
    properties: BoundaryProperties
    geometry: Annotated[PolygonGeometry | MultiPolygonGeometry, Field(discriminator="type")]


class BoundaryCollection(Record):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    crs: Literal["OGC:CRS84"] = "OGC:CRS84"
    features: tuple[BoundaryFeature, ...]
