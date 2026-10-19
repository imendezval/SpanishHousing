"""Independent official atlas, display derivative and read-only map contracts."""

from datetime import date
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from .base import Offset, Record, SchemaVersion
from .dataset import (
    CaptureRecord,
    Digest,
    Identifier,
    MultiPolygonGeometry,
    MunicipalCode,
    PolygonGeometry,
    SourceDecision,
    Text,
    UsageScope,
    relative_path,
)
from .dataset import (
    GeographyReference as GeographyReference,
)

GeographyId = Annotated[str, StringConstraints(strict=True, pattern=r"^geography-[a-f0-9]{64}$")]
DisplayId = Annotated[str, StringConstraints(strict=True, pattern=r"^display-[a-f0-9]{64}$")]
ProvinceCode = Annotated[str, StringConstraints(strict=True, pattern=r"^\d{2}$")]


class Municipality(Record):
    code: MunicipalCode
    official_name: Text
    province_code: ProvinceCode
    control_digit: Annotated[str, StringConstraints(strict=True, pattern=r"^\d$")]
    feature_id: Text
    national_code: Text
    source_name: Text

    @model_validator(mode="after")
    def matching_province(self) -> "Municipality":
        if self.code[:2] != self.province_code:
            raise ValueError("municipality/province identity mismatch")
        return self


class AtlasProperties(Record):
    location_code: MunicipalCode | None
    name: Text
    province_code: ProvinceCode | None
    kind: Literal["municipality", "context", "province"]
    source_national_code: Text

    @model_validator(mode="after")
    def economic_identity(self) -> "AtlasProperties":
        if (self.location_code is not None) != (self.kind == "municipality"):
            raise ValueError("only municipalities have economic codes")
        if self.location_code is not None and self.location_code[:2] != self.province_code:
            raise ValueError("atlas feature/province mismatch")
        return self


class AtlasFeature(Record):
    type: Literal["Feature"] = "Feature"
    id: Text
    properties: AtlasProperties
    geometry: Annotated[PolygonGeometry | MultiPolygonGeometry, Field(discriminator="type")]


class AtlasCollection(Record):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    crs: Literal["OGC:CRS84"] = "OGC:CRS84"
    features: tuple[AtlasFeature, ...]


class ContextTerritory(Record):
    feature_id: Text
    reason: Text


class GeographyRecipe(Record):
    schema_version: SchemaVersion = 1
    registry_version: Text
    registry_effective_on: date
    boundary_version: Text
    attribution: Text
    decisions: tuple[SourceDecision, ...]
    captures: tuple[CaptureRecord, ...]
    registry_capture_id: Identifier
    municipal_page_ids: tuple[Identifier, ...]
    province_page_ids: tuple[Identifier, ...]
    support_capture_ids: tuple[Identifier, ...]
    selected_codes: tuple[MunicipalCode, ...] = ()
    context_territories: tuple[ContextTerritory, ...] = ()
    processing_notes: tuple[Text, ...]

    @model_validator(mode="after")
    def unique_references(self) -> "GeographyRecipe":
        for keys in (
            [c.capture_id for c in self.captures],
            [d.source_id for d in self.decisions],
            list(self.selected_codes),
            [c.feature_id for c in self.context_territories],
        ):
            if len(keys) != len(set(keys)):
                raise ValueError("duplicate geography recipe identity")
        required = (
            self.registry_capture_id,
            *self.municipal_page_ids,
            *self.province_page_ids,
            *self.support_capture_ids,
        )
        if not self.municipal_page_ids or not set(required) <= {
            c.capture_id for c in self.captures
        }:
            raise ValueError("geography recipe lacks required retained captures")
        return self


class ArtifactFile(Record):
    path: Text
    sha256: Digest
    byte_size: Offset
    record_count: Offset

    _safe_path = field_validator("path")(relative_path)


class GeographyCounts(Record):
    municipalities: Offset
    context_territories: Offset
    provinces: Offset
    polygon_components: Offset
    holes: Offset
    vertices: Offset


class GeographyManifest(Record):
    schema_version: SchemaVersion = 1
    artifact_id: GeographyId
    content_digest: Digest
    recipe: GeographyRecipe
    registry_sha256: Digest
    files: tuple[ArtifactFile, ...]
    counts: GeographyCounts
    redistribution: UsageScope


class DisplayQuality(Record):
    tolerance_m: Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
    metric_crs: tuple[Text, ...]
    algorithm: Text
    shapely_version: Text
    geos_version: Text
    pyproj_version: Text
    max_relative_area_change: Annotated[float, Field(strict=True, ge=0, le=0.02)]
    max_boundary_displacement_m: Annotated[float, Field(strict=True, ge=0, le=250)]
    worst_area_code: Text
    worst_displacement_code: Text
    original_vertices: Offset
    display_vertices: Offset
    coverage_valid: Literal[True]


class DisplayManifest(Record):
    schema_version: SchemaVersion = 1
    artifact_id: DisplayId
    content_digest: Digest
    parent: GeographyReference
    files: tuple[ArtifactFile, ...]
    quality: DisplayQuality
    counts: GeographyCounts
    attribution: Text
    redistribution: UsageScope


class MapGeography(Record):
    """Injected rendering view; no paths, repositories or market calculations."""

    geography_id: Text
    display_id: Text
    boundary_version: Text
    origin: Literal["official", "synthetic"]
    attribution: Text
    municipalities: tuple[Municipality, ...]
    boundaries: AtlasCollection
    provinces: AtlasCollection
