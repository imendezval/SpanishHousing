"""Shared strict bytes, safe paths and immutable atomic artifact publication."""

import hashlib
import json
import math
import os
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from spain_housing.models.dataset import CaptureRecord, relative_path


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite JSON number")
    return number


def _invalid_constant(value: str) -> object:
    raise ValueError(f"non-finite JSON token: {value}")


def strict_json(data: bytes) -> object:
    result: object = json.loads(
        data,
        object_pairs_hook=_unique_object,
        parse_float=_finite_float,
        parse_constant=_invalid_constant,
    )
    return result


def contained_path(root: Path, relative: str) -> Path:
    relative_path(relative)
    result = root / relative
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {relative}")
    return result


def read_capture(data_root: Path, capture: CaptureRecord) -> bytes:
    data = contained_path(data_root, capture.path).read_bytes()
    if len(data) != capture.byte_size or sha256(data) != capture.sha256:
        raise ValueError(f"capture hash/size mismatch: {capture.capture_id}")
    if capture.format not in ("html",) and data.lstrip().lower().startswith(
        (b"<!doctype html", b"<html")
    ):
        raise ValueError(f"error/login HTML is not {capture.format}: {capture.capture_id}")
    return data


def publish_artifact(
    root: Path, identity: str, payloads: dict[str, bytes], validate: Callable[[Path], object]
) -> Path:
    """Validate staged bytes and publish once; identical repeat writes are idempotent."""
    relative_path(identity)
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".staging-", dir=root))
    lock = root / f".{identity}.lock"
    owned_lock = False
    try:
        for name, data in payloads.items():
            contained_path(staging, name).write_bytes(data)
        validate(staging)
        lock.mkdir()
        owned_lock = True
        destination = root / identity
        if destination.exists():
            validate(destination)
            if any(
                contained_path(destination, name).read_bytes() != data
                for name, data in payloads.items()
            ):
                raise ValueError("existing artifact ID has different content; refusing overwrite")
        else:
            os.rename(staging, destination)
        return destination
    finally:
        if staging.exists():
            shutil.rmtree(staging)
        if owned_lock:
            lock.rmdir()
