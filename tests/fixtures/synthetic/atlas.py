"""Self-authored topology/registry fixtures; never official geographic evidence."""

from pathlib import Path

from spain_housing.models.dataset import CaptureRecord, SourceDecision
from spain_housing.models.geography import GeographyRecipe
from spain_housing.storage.files import canonical_json, sha256


def atlas_inputs(root: Path, *, defect: str | None = None) -> GeographyRecipe:
    root.mkdir()
    decisions = tuple(
        SourceDecision(
            source_id=source,
            product="Self-authored geographic test fixture, not official data",
            primary_url="https://www.ine.es/fixture"
            if source.startswith("ine")
            else "https://api-features.ign.es/fixture",
            terms_url="https://example.org/self-authored",
            local_use="permitted",
            redistribution="permitted",
            evidence_reference="Self-authored test bytes only",
            attribution="Synthetic test geometry",
            reviewed_on="2026-10-19",
            acquisition_route="curated test fixture",
        )
        for source in ("ine-municipalities", "ign-administrativeunit")
    )
    registry = b"CPRO,CMUN,DC,NOMBRE\n28,001,0,Same name\n28,002,1,Same name\n"
    first = [[[-4.0, 40.0], [-3.5, 40.0], [-3.5, 40.5], [-3.5, 41.0], [-4.0, 41.0], [-4.0, 40.0]]]
    second = [[[-3.5, 40.0], [-3.0, 40.0], [-3.0, 41.0], [-3.5, 41.0], [-3.5, 40.5], [-3.5, 40.0]]]
    if defect == "overlap":
        for position in second[0]:
            if position[0] == -3.5:
                position[0] = -3.6
    if defect == "edge":
        second[0].pop(-2)
    features = []
    for identity, code, coordinates in (("one", "28001", first), ("two", "28002", second)):
        features.append(
            dict(
                type="Feature",
                id=identity,
                properties=dict(
                    country="ES",
                    nationallevelname="Municipio",
                    nationalcode="341328" + code,
                    nameunit="Same name",
                ),
                geometry=dict(type="Polygon", coordinates=coordinates),
            )
        )
    if defect == "duplicate":
        features[-1] = features[0]
    if defect == "axis":
        features[0]["geometry"]["coordinates"][0][0] = [40.0, -4.0]
    if defect == "level":
        features[0]["properties"]["nationallevelname"] = "Provincia"
    page = dict(
        type="FeatureCollection", features=features, numberMatched=2, numberReturned=2, links=[]
    )
    if defect == "pagination":
        page["links"] = [dict(rel="next", href="https://api-features.ign.es/missing")]
    province = dict(
        type="Feature",
        id="province",
        properties=dict(
            country="ES",
            nationallevelname="Provincia",
            nationalcode="34132800000",
            nameunit="Fixture province",
        ),
        geometry=dict(
            type="Polygon",
            coordinates=[[[-4.0, 40.0], [-3.0, 40.0], [-3.0, 41.0], [-4.0, 41.0], [-4.0, 40.0]]],
        ),
    )
    contents = (
        ("registry_csv", registry, "csv", decisions[0]),
        ("municipal_json", canonical_json(page), "geojson", decisions[1]),
        (
            "province_json",
            canonical_json(
                dict(
                    type="FeatureCollection",
                    features=[province],
                    numberMatched=1,
                    numberReturned=1,
                    links=[],
                )
            ),
            "geojson",
            decisions[1],
        ),
    )
    captures = []
    for name, data, fmt, decision in contents:
        (root / name).write_bytes(data)
        captures.append(
            CaptureRecord(
                capture_id=name,
                source_id=decision.source_id,
                path=name,
                sha256=sha256(data),
                byte_size=len(data),
                primary_url="https://api-features.ign.es/" + name,
                captured_at="2026-10-19T00:00:00Z",
                route="curated_extract",
                format=fmt,
                permission_reference=decision.evidence_reference,
            )
        )
    return GeographyRecipe(
        registry_version="Self-authored fixture",
        registry_effective_on="2026-01-01",
        boundary_version="fixture-boundary",
        attribution="Synthetic test geometry",
        decisions=decisions,
        captures=tuple(captures),
        registry_capture_id="registry_csv",
        municipal_page_ids=("municipal_json",),
        province_page_ids=("province_json",),
        support_capture_ids=(),
        processing_notes=("Self-authored shapes, not official geography",),
    )


def demo_config():
    from spain_housing.models.demo import DemoConfig

    return DemoConfig.model_validate(
        dict(
            seed="independent-test",
            logical_timestamp="2026-10-19T00:00:00Z",
            period_start="2026-09-01",
            period_end="2026-10-01",
            purchase_per_m2=dict(minimum=800, maximum=5000),
            rent_per_m2_month=dict(minimum=5, maximum=20),
            room_per_month=dict(minimum=250, maximum=850),
            partial_codes=["28001"],
            partial_gaps=[
                dict(
                    location_code="28001",
                    profile_id="sale",
                    status="missing",
                    reason="Deliberate purchase-only gap",
                )
            ],
            overrides=[
                dict(code="28001", purchase_per_m2=2000, rent_per_m2_month=15, room_per_month=400)
            ],
        )
    )
