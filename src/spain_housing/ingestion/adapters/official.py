"""Capture explicitly permitted official inputs; no acquisition occurs while building."""

from datetime import UTC, date, datetime
from pathlib import Path
from typing import Literal
from urllib.request import Request, urlopen

from pydantic import HttpUrl

from spain_housing.models.dataset import CaptureRecord, SourceDecision
from spain_housing.storage.release import canonical_json, sha256, strict_json


def download_official_capture(
    url: str,
    *,
    decision: SourceDecision,
    data_root: Path,
    format: Literal["xlsx", "geojson", "html", "json", "pdf"],
    source_release: str | None = None,
    published_on: date | None = None,
) -> CaptureRecord:
    if decision.local_use != "permitted" or decision.source_id not in (
        "ine-municipalities",
        "ign-administrativeunit",
    ):
        raise ValueError("official capture requires the reviewed permitted INE/IGN source decision")
    allowed_host = (
        "www.ine.es" if decision.source_id == "ine-municipalities" else "api-features.ign.es"
    )
    from urllib.parse import urlsplit

    if urlsplit(url).scheme != "https" or urlsplit(url).hostname != allowed_host:
        raise ValueError("capture URL is outside the selected official source")
    with urlopen(
        Request(url, headers={"User-Agent": "SpanishHousing-pilot/0.1"}), timeout=20
    ) as response:
        status = response.status
        resolved = response.url
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if status != 200 or urlsplit(resolved).hostname != allowed_host or not data:
        raise ValueError("invalid official capture response")
    if format != "html" and (
        "text/html" in content_type
        or data.lstrip().lower().startswith((b"<html", b"<!doctype html"))
    ):
        raise ValueError("error/login HTML is not the requested official input")
    if format in ("json", "geojson"):
        strict_json(data)
    if format == "xlsx" and not data.startswith(b"PK"):
        raise ValueError("official registry response is not XLSX")
    timestamp = datetime.now(UTC)
    digest = sha256(data)
    capture_id = "capture-" + sha256(f"{url}|{timestamp.isoformat()}|{digest}".encode())
    relative = f"captures/{digest}.{format}"
    destination = data_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.read_bytes() != data:
            raise ValueError("existing capture content differs; refusing overwrite")
    else:
        with destination.open("xb") as stream:
            stream.write(data)
    record = CaptureRecord(
        capture_id=capture_id,
        source_id=decision.source_id,
        path=relative,
        sha256=digest,
        byte_size=len(data),
        primary_url=HttpUrl(url),
        resolved_url=HttpUrl(resolved),
        captured_at=timestamp,
        published_on=published_on,
        source_release=source_release,
        route="provider_download",
        format=format,
        permission_reference=decision.evidence_reference,
        http_status=status,
        content_type=content_type,
    )
    with (destination.parent / f"{capture_id}.json").open("xb") as stream:
        stream.write(canonical_json(record.model_dump(mode="json")))
    return record
