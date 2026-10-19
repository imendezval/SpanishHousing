"""Capture explicitly permitted official inputs; no acquisition occurs while building."""

from datetime import UTC, date, datetime
from pathlib import Path
from time import sleep
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from pydantic import HttpUrl, TypeAdapter

from spain_housing.models.dataset import CaptureRecord, SourceDecision
from spain_housing.storage.release import canonical_json, read_capture, sha256, strict_json


def download_official_capture(
    url: str,
    *,
    decision: SourceDecision,
    data_root: Path,
    format: Literal["xlsx", "geojson", "html", "json", "pdf", "xml", "zip"],
    source_release: str | None = None,
    published_on: date | None = None,
) -> CaptureRecord:
    if decision.local_use != "permitted" or decision.source_id not in (
        "ine-municipalities",
        "ign-administrativeunit",
    ):
        raise ValueError("official capture requires the reviewed permitted INE/IGN source decision")
    allowed_hosts = (
        ("www.ine.es",)
        if decision.source_id == "ine-municipalities"
        else ("api-features.ign.es", "www.ign.es", "centrodedescargas.cnig.es")
    )
    from urllib.parse import urlsplit

    if urlsplit(url).scheme != "https" or urlsplit(url).hostname not in allowed_hosts:
        raise ValueError("capture URL is outside the selected official source")
    with urlopen(
        Request(url, headers={"User-Agent": "SpanishHousing-pilot/0.1"}), timeout=20
    ) as response:
        status = response.status
        resolved = response.url
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if status != 200 or urlsplit(resolved).hostname not in allowed_hosts or not data:
        raise ValueError("invalid official capture response")
    if format != "html" and (
        "text/html" in content_type
        or data.lstrip().lower().startswith((b"<html", b"<!doctype html"))
    ):
        raise ValueError("error/login HTML is not the requested official input")
    if format in ("json", "geojson"):
        strict_json(data)
    if format in ("xlsx", "zip") and not data.startswith(b"PK"):
        raise ValueError("official archive response is not ZIP/XLSX")
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


def capture_official_pages(
    url: str, *, decision: SourceDecision, data_root: Path, inventory: Path
) -> tuple[CaptureRecord, ...]:
    """Retain a bounded, resumable IGN chain; never treat a first page as complete."""
    initial_url = url
    records: list[CaptureRecord] = []
    if inventory.exists():
        saved = strict_json(inventory.read_bytes())
        if not isinstance(saved, dict) or saved.get("initial_url") != url:
            raise ValueError("pagination inventory belongs to another request")
        records = list(TypeAdapter(tuple[CaptureRecord, ...]).validate_python(saved["captures"]))
    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    matched: int | None = None
    index = 0
    while True:
        if url in seen_urls or index >= 1000:
            raise ValueError("geography pagination loop or page bound exceeded")
        seen_urls.add(url)
        if index < len(records):
            record = records[index]
            if str(record.primary_url) != url:
                raise ValueError("pagination inventory does not match retained next links")
            data = read_capture(data_root, record)
        else:
            for attempt in range(3):
                try:
                    record = download_official_capture(
                        url, decision=decision, data_root=data_root, format="geojson"
                    )
                    break
                except (HTTPError, URLError, TimeoutError):
                    if attempt == 2:
                        raise
                    sleep(attempt + 1)
            records.append(record)
            data = read_capture(data_root, record)
        page = strict_json(data)
        if not isinstance(page, dict) or page.get("type") != "FeatureCollection":
            raise ValueError("geography page is not a FeatureCollection")
        features = page.get("features")
        count = page.get("numberMatched")
        if not isinstance(features, list) or not features or type(count) is not int:
            raise ValueError("geography page lacks features/matched count")
        if matched is None:
            matched = count
        if count != matched or page.get("numberReturned") != len(features):
            raise ValueError("geography snapshot counts changed or page is incomplete")
        for feature in features:
            if not isinstance(feature, dict) or "id" not in feature:
                raise ValueError("geography page contains an unidentified feature")
            identity = str(feature["id"])
            if identity in seen_ids:
                raise ValueError("duplicate geographic feature across pages")
            seen_ids.add(identity)
        links = page.get("links", [])
        if not isinstance(links, list):
            raise ValueError("invalid geography links")
        next_links = [
            link for link in links if isinstance(link, dict) and link.get("rel") == "next"
        ]
        if len(next_links) > 1:
            raise ValueError("ambiguous geography pagination")
        complete = not next_links
        inventory.parent.mkdir(parents=True, exist_ok=True)
        inventory.write_bytes(
            canonical_json(
                dict(
                    initial_url=initial_url,
                    captures=[r.model_dump(mode="json") for r in records],
                    matched=matched,
                    received=len(seen_ids),
                    complete=complete,
                )
            )
        )
        index += 1
        if complete:
            if len(seen_ids) != matched or index != len(records):
                raise ValueError("incomplete geography pagination inventory")
            return tuple(records)
        target = urlsplit(urljoin(url, str(next_links[0]["href"])))
        if target.scheme != "https" or target.hostname != "api-features.ign.es":
            raise ValueError("pagination link leaves the official source")
        query = dict(parse_qsl(target.query)) | {"f": "json"}
        url = urlunsplit((target.scheme, target.netloc, target.path, urlencode(query), ""))
