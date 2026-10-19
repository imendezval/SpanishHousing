"""Offline national registry reconciliation and canonical official artifact assembly."""

from collections.abc import Iterator
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urljoin, urlsplit

from pydantic import TypeAdapter

from spain_housing.models.geography import (
    AtlasCollection,
    AtlasFeature,
    GeographyRecipe,
    Municipality,
)
from spain_housing.storage.coverage_geometry import validate_source_coverage
from spain_housing.storage.files import canonical_json, read_capture, sha256, strict_json
from spain_housing.storage.geography import (
    file_record,
    geometry_counts,
    validate_atlas,
    write_geography,
)
from spain_housing.storage.permissions import (
    redistribution_scope,
    validate_capture_permission,
    validate_source_use,
)

from .geography import read_registry


def _request_key(url: str) -> tuple[str, str, tuple[tuple[str, str], ...]]:
    parsed = urlsplit(url)
    query = dict(parse_qsl(parsed.query)) | {"f": "json"}
    return parsed.netloc, parsed.path, tuple(sorted(query.items()))


def retained_features(
    recipe: GeographyRecipe, data_root: Path, ids: tuple[str, ...], level: str
) -> Iterator[dict[str, Any]]:
    """Verify the entire retained next-link chain, counts, levels and unique IDs."""
    captures = {c.capture_id: c for c in recipe.captures}
    total: int | None = None
    received = 0
    seen: set[str] = set()
    expected_url: str | None = None
    for index, capture_id in enumerate(ids):
        capture = captures[capture_id]
        url = str(capture.primary_url)
        if expected_url is not None and _request_key(url) != _request_key(expected_url):
            raise ValueError("missing/reordered geography pagination link")
        page = TypeAdapter(dict[str, Any]).validate_python(
            strict_json(read_capture(data_root, capture))
        )
        features = TypeAdapter(list[dict[str, Any]]).validate_python(page.get("features"))
        if page.get("type") != "FeatureCollection" or page.get("crs") not in (None, "OGC:CRS84"):
            raise ValueError("official pages must use CRS84 FeatureCollections")
        matched = page.get("numberMatched")
        if type(matched) is not int or not features or page.get("numberReturned") != len(features):
            raise ValueError("incomplete geography page/counts")
        if total is None:
            total = matched
        if matched != total:
            raise ValueError("official snapshot changed between geography pages")
        next_links = [link for link in page.get("links", []) if link.get("rel") == "next"]
        if len(next_links) != (1 if index < len(ids) - 1 else 0):
            raise ValueError("incomplete or excessive retained geography pagination")
        if next_links:
            expected_url = urljoin(url, next_links[0]["href"])
        for feature in features:
            identity = str(feature.get("id", ""))
            properties = feature.get("properties", {})
            if not identity or identity in seen:
                raise ValueError("duplicate/unidentified official geography feature")
            if (
                feature.get("type"),
                properties.get("country"),
                properties.get("nationallevelname"),
            ) != ("Feature", "ES", level):
                raise ValueError("geography feature has wrong country/administrative level")
            seen.add(identity)
            received += 1
            yield feature
    if total != received:
        raise ValueError("retained geography pages do not match total source count")


def build_geography(recipe: GeographyRecipe, *, data_root: Path, artifact_root: Path) -> Path:
    decisions = {d.source_id: d for d in recipe.decisions}
    for decision in recipe.decisions:
        validate_source_use(decision, "observed")
    for capture in recipe.captures:
        capture_decision = decisions.get(capture.source_id)
        if capture_decision is None:
            raise ValueError("geography capture references unknown permission")
        validate_capture_permission(capture, capture_decision, "observed")
        read_capture(data_root, capture)
    captures = {c.capture_id: c for c in recipe.captures}
    capture = captures[recipe.registry_capture_id]
    official = read_registry(read_capture(data_root, capture), capture.format)
    expected = set(recipe.selected_codes) if recipe.selected_codes else set(official)
    if not expected or not expected <= official.keys():
        raise ValueError("selected geography codes are absent from the official registry")
    selected_provinces = {code[:2] for code in expected}
    known_context = {c.feature_id: c.reason for c in recipe.context_territories}
    rows: list[Municipality] = []
    features: list[AtlasFeature] = []
    names = []
    used_context: set[str] = set()
    national_codes: set[str] = set()
    for raw in retained_features(recipe, data_root, recipe.municipal_page_ids, "Municipio"):
        props = raw["properties"]
        national_code = str(props["nationalcode"])
        if len(national_code) != 11 or not national_code.isascii() or not national_code.isdigit():
            raise ValueError("invalid official full national code")
        if national_code in national_codes:
            raise ValueError("duplicate national geographic code")
        national_codes.add(national_code)
        source_code = national_code[-5:]
        source_province = national_code[4:6]
        identity = str(raw["id"])
        if source_code in official:
            if source_code not in expected:
                continue
            if source_province != source_code[:2]:
                raise ValueError("IGN province disagrees with official municipality code")
            name, control = official[source_code]
            record = Municipality(
                code=source_code,
                official_name=name,
                province_code=source_province,
                control_digit=control,
                feature_id=identity,
                national_code=national_code,
                source_name=props["nameunit"],
            )
            rows.append(record)
            if record.source_name != name:
                names.append(
                    dict(
                        code=source_code,
                        registry_name=name,
                        source_name=record.source_name,
                        rule="Exact authoritative national-code join; retain both official labels",
                    )
                )
            code: str | None = source_code
            kind = "municipality"
        else:
            if identity not in known_context:
                raise ValueError(
                    f"unresolved nonmunicipal territory {identity}: {props['nameunit']}"
                )
            used_context.add(identity)
            if source_province not in selected_provinces:
                continue
            code = None
            name = props["nameunit"]
            kind = "context"
        features.append(
            AtlasFeature.model_validate(
                dict(
                    id=identity,
                    properties=dict(
                        location_code=code,
                        name=name,
                        province_code=source_province,
                        kind=kind,
                        source_national_code=national_code,
                    ),
                    geometry=raw["geometry"],
                )
            )
        )
    if set(known_context) != used_context:
        raise ValueError("declared context territory was not found in retained official pages")
    registry = tuple(sorted(rows, key=lambda m: m.code))
    if {m.code for m in registry} != expected:
        raise ValueError(
            f"unresolved registry municipalities: {sorted(expected - {m.code for m in registry})}"
        )
    boundaries = AtlasCollection(features=tuple(sorted(features, key=lambda f: f.id)))
    validate_atlas(boundaries, registry)
    valid_coverage = validate_source_coverage(boundaries, recipe.source_conflicts)
    province_features = []
    for raw in retained_features(recipe, data_root, recipe.province_page_ids, "Provincia"):
        national = str(raw["properties"]["nationalcode"])
        province = national[4:6]
        if province not in selected_provinces:
            continue
        province_features.append(
            AtlasFeature.model_validate(
                dict(
                    id=str(raw["id"]),
                    properties=dict(
                        location_code=None,
                        name=raw["properties"]["nameunit"],
                        province_code=province,
                        kind="province",
                        source_national_code=national,
                    ),
                    geometry=raw["geometry"],
                )
            )
        )
    provinces = AtlasCollection(features=tuple(sorted(province_features, key=lambda f: f.id)))
    if {f.properties.province_code for f in provinces.features} != selected_provinces:
        raise ValueError("province orientation coverage does not match selected registry")
    report = dict(
        expected_municipalities=len(expected),
        full_registry_count=len(official),
        municipal_pages=len(recipe.municipal_page_ids),
        province_pages=len(recipe.province_page_ids),
        coverage_valid=valid_coverage,
        source_conflicts=[conflict.model_dump(mode="json") for conflict in recipe.source_conflicts],
        source_name_crosswalks=names,
        context_territories=[c.model_dump(mode="json") for c in recipe.context_territories],
        scope="selected registry subset"
        if recipe.selected_codes
        else "entire retained INE registry",
        limitations=recipe.processing_notes,
    )
    payloads = {
        "registry.json": canonical_json([r.model_dump(mode="json") for r in registry]),
        "canonical.geojson": canonical_json(boundaries.model_dump(mode="json")),
        "provinces.geojson": canonical_json(provinces.model_dump(mode="json")),
        "report.json": canonical_json(report),
    }
    counts = geometry_counts(boundaries, len(provinces.features))
    numbers = (len(registry), len(boundaries.features), len(provinces.features), 1)
    metadata = dict(
        schema_version=1,
        recipe=recipe.model_dump(mode="json"),
        registry_sha256=sha256(payloads["registry.json"]),
        files=[
            file_record(name, data, number).model_dump(mode="json")
            for (name, data), number in zip(payloads.items(), numbers, strict=True)
        ],
        counts=counts.model_dump(mode="json"),
        redistribution=redistribution_scope(recipe.decisions),
    )
    return write_geography(artifact_root, metadata, payloads)
