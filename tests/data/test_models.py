from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from spain_housing.models.dataset import CaptureRecord, SourceDecision


def test_capture_and_usage_round_trip() -> None:
    decision = SourceDecision(
        source_id="synthetic:test",
        product="self-authored fixture",
        primary_url=None,
        terms_url=None,
        local_use="permitted",
        redistribution="permitted",
        evidence_reference="self-authored",
        attribution="synthetic fixture",
        reviewed_on="2026-10-07",
        acquisition_route="synthetic_fixture",
    )
    capture = CaptureRecord(
        capture_id="fixture",
        source_id=decision.source_id,
        path="fixture.csv",
        sha256="a" * 64,
        byte_size=10,
        primary_url=None,
        captured_at=datetime(2026, 10, 7, tzinfo=UTC),
        route="synthetic_fixture",
        format="csv",
        permission_reference=decision.evidence_reference,
    )
    assert CaptureRecord.model_validate_json(capture.model_dump_json()) == capture
    assert SourceDecision.model_validate_json(decision.model_dump_json()) == decision
    with pytest.raises(ValidationError):
        CaptureRecord.model_validate(capture.model_dump() | {"captured_at": "2026-10-07T00:00:00"})
    with pytest.raises(ValidationError):
        CaptureRecord.model_validate(capture.model_dump() | {"route": "provider_download"})


@pytest.mark.parametrize("path", ["/tmp/data", "../data", "a/../data", "a\\data", "C:/data", "."])
def test_capture_paths_cannot_escape(path: str) -> None:
    with pytest.raises(ValidationError, match="relative"):
        CaptureRecord(
            capture_id="fixture",
            source_id="synthetic:test",
            path=path,
            sha256="a" * 64,
            byte_size=1,
            primary_url=None,
            captured_at="2026-10-07T00:00:00Z",
            route="synthetic_fixture",
            format="csv",
            permission_reference="self-authored",
        )
