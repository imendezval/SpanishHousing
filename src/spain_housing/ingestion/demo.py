"""Deterministic synthetic prices over a validated atlas, feeding the existing builder."""

import csv
import io
from pathlib import Path
from typing import Literal

from spain_housing.models.dataset import (
    BuildRecipeV2,
    CaptureRecord,
    LocationRecord,
    ProducerEvidence,
    ReferenceProfile,
    SourceDecision,
    SourceLocationMapping,
)
from spain_housing.models.demo import DemoConfig, DemoRange
from spain_housing.models.market import METRIC_UNITS, MarketMetric, MarketSegment
from spain_housing.models.scenario import GeographicReference
from spain_housing.storage.files import canonical_json, publish_artifact, read_capture, sha256
from spain_housing.storage.geography import geography_reference, load_geography
from spain_housing.storage.release import parse_recipe, strict_json, validate_recipe

from .adapters.curated import CuratedRow


def synthetic_factor(config: DemoConfig, code: str) -> float:
    """Code-local variation is independent of registry order, size and Python hash seed."""

    def fraction(key: str) -> float:
        digest = sha256(canonical_json([config.generator_version, config.seed, key]))
        return int(digest[:16], 16) / (2**64 - 1)

    return 0.35 * fraction("province:" + code[:2]) + 0.65 * fraction("municipality:" + code)


def _amount(bounds: DemoRange, factor: float) -> str:
    return f"{bounds.minimum + factor * (bounds.maximum - bounds.minimum):.2f}"


def generate_demo(
    geography_dir: Path,
    config: DemoConfig,
    *,
    output_root: Path,
    variant: Literal["complete", "partial"] = "complete",
) -> Path:
    geography = load_geography(geography_dir, full=False)
    reference = geography_reference(geography.manifest)
    by_code = {m.code: m for m in geography.registry}
    selected = set(by_code) if variant == "complete" else set(config.partial_codes)
    if not selected or not selected <= by_code.keys():
        raise ValueError("synthetic subset contains unknown/empty municipality selection")
    if not {o.code for o in config.overrides} <= by_code.keys():
        raise ValueError("synthetic override references an unknown municipality")
    source_id = "synthetic:" + config.generator_version
    decision = SourceDecision(
        source_id=source_id,
        product="Self-authored synthetic flat/room assumptions",
        primary_url=None,
        terms_url=None,
        local_use="permitted",
        redistribution="permitted",
        evidence_reference="Self-authored deterministic demonstration; no provider prices",
        attribution="Synthetic market assumptions; not observed housing prices or rents",
        reviewed_on=config.logical_timestamp.date(),
        acquisition_route="Packaged deterministic generator",
        notes=(
            "Logical timestamp is a configured deterministic epoch, not provider retrieval time.",
        ),
    )
    profiles = tuple(
        ReferenceProfile(
            profile_id=key,
            source_id=source_id,
            metric=metric,
            period_start=config.period_start,
            period_end=config.period_end,
            segment=MarketSegment(property_type="room" if key == "room" else "flat"),
            statistic="mean",
            basis="asking",
        )
        for key, metric in (
            ("sale", MarketMetric.PURCHASE_PRICE_PER_M2),
            ("rent", MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH),
            ("room", MarketMetric.ROOM_RENT_PER_MONTH),
        )
    )
    locations = tuple(
        LocationRecord(
            location=GeographicReference(level="municipality", code=code),
            official_name=by_code[code].official_name,
            province_code=by_code[code].province_code,
            control_digit=by_code[code].control_digit,
            registry_version=reference.registry_version,
            verification_evidence="Pinned canonical geography " + reference.artifact_id,
            geometry_feature_id=by_code[code].feature_id,
            geometry_national_code=by_code[code].national_code,
            boundary_version=reference.boundary_version,
            core=not config.core_codes or code in config.core_codes,
            source_mappings=(
                SourceLocationMapping(source_id=source_id, label=code, scope="municipality"),
            ),
        )
        for code in sorted(selected)
    )
    gaps = config.partial_gaps if variant == "partial" else ()
    gap_keys = {(g.location_code, g.profile_id) for g in gaps}
    overrides = {o.code: o for o in config.overrides}
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        csv_buffer, fieldnames=list(CuratedRow.model_fields), lineterminator="\n"
    )
    writer.writeheader()
    for code in sorted(selected):
        factor = synthetic_factor(config, code)
        override = overrides.get(code)
        values = {
            "sale": str(override.purchase_per_m2)
            if override
            else _amount(config.purchase_per_m2, factor),
            "rent": str(override.rent_per_m2_month)
            if override
            else _amount(config.rent_per_m2_month, factor),
            "room": str(override.room_per_month)
            if override
            else _amount(config.room_per_month, factor),
        }
        for profile in profiles:
            if (code, profile.profile_id) in gap_keys:
                continue
            writer.writerow(
                dict(
                    profile_id=profile.profile_id,
                    source_location=code,
                    geographic_scope="municipality",
                    raw_value=values[profile.profile_id],
                    raw_unit=METRIC_UNITS[profile.metric].value,
                    period_start=config.period_start.isoformat(),
                    period_end=config.period_end.isoformat(),
                    statistic=profile.statistic,
                    basis=profile.basis,
                    source_locator=f"generator/{config.generator_version}/{code}/{profile.profile_id}",
                    evidence_kind="synthetic",
                    estimation_method="",
                    quality_notes="SYNTHETIC assumptions; no real-world city ranking",
                )
            )
    csv_data = csv_buffer.getvalue().encode("utf-8")
    lineage = canonical_json(
        dict(
            config=config.model_dump(mode="json"),
            geography=reference.model_dump(mode="json"),
            variant=variant,
        )
    )
    payloads: dict[str, bytes] = {}
    captures = []
    for label, data, fmt in (("observations", csv_data, "csv"), ("generator", lineage, "json")):
        digest = sha256(data)
        path = f"captures/{digest}.{fmt}"
        payloads[path] = data
        captures.append(
            CaptureRecord.model_validate(
                dict(
                    capture_id=label + "-" + digest,
                    source_id=source_id,
                    path=path,
                    sha256=digest,
                    byte_size=len(data),
                    primary_url=None,
                    captured_at=config.logical_timestamp,
                    source_release=config.generator_version,
                    methodology_version=config.generator_version,
                    route="synthetic_fixture",
                    format=fmt,
                    permission_reference=decision.evidence_reference,
                )
            )
        )
    recipe = BuildRecipeV2(
        schema_version=2,
        kind="synthetic",
        processing_version=config.generator_version,
        producer=ProducerEvidence(revision=config.generator_version),
        recipe_timestamp=config.logical_timestamp,
        numeric_format="plain",
        locations=locations,
        profiles=profiles,
        decisions=(decision,),
        captures=tuple(captures),
        observation_capture_ids=(captures[0].capture_id,),
        geography=reference,
        declared_gaps=gaps,
        limitations=(
            "All housing prices/rents are synthetic assumptions, not observations.",
            "Official geography does not make the economic inputs observed.",
        ),
    )
    payloads["recipe.json"] = canonical_json(recipe.model_dump(mode="json"))
    identity = "inputs-" + sha256(payloads["recipe.json"])

    def validate(path: Path) -> None:
        supplied = parse_recipe(strict_json((path / "recipe.json").read_bytes()))
        validate_recipe(supplied, allow_synthetic=True)
        for capture in supplied.captures:
            read_capture(path, capture)

    return publish_artifact(output_root, identity, payloads, validate)
