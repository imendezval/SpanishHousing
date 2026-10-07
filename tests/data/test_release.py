import json
import shutil
from pathlib import Path

import pytest
from conftest import FIXTURES

from spain_housing.ingestion.release import build_release
from spain_housing.models.dataset import BuildRecipe
from spain_housing.storage.release import (
    canonical_json,
    content_identity,
    load_release,
    sha256,
    strict_json,
    write_release,
)


def reseal(release_dir: Path, filename: str, payload: bytes) -> None:
    """Keep byte integrity valid to test the independent semantic verifier."""
    (release_dir / filename).write_bytes(payload)
    manifest = json.loads((release_dir / "manifest.json").read_bytes())
    for record in manifest["files"]:
        if record["path"] == filename:
            record.update(sha256=sha256(payload), byte_size=len(payload))
    metadata = {
        key: value for key, value in manifest.items() if key not in ("release_id", "content_digest")
    }
    identity, digest = content_identity(metadata)
    manifest.update(release_id=identity, content_digest=digest)
    (release_dir / "manifest.json").write_bytes(canonical_json(manifest))


def test_deterministic_build_identity_relocation_and_input_immutability(
    recipe: BuildRecipe, release_dir: Path, tmp_path: Path
) -> None:
    original = recipe.model_dump_json()
    again = build_release(
        recipe, data_root=FIXTURES, release_root=release_dir.parent, allow_synthetic=True
    )
    other = build_release(
        recipe, data_root=FIXTURES, release_root=tmp_path / "another-root", allow_synthetic=True
    )
    assert again == release_dir
    assert other.name == release_dir.name
    assert {p.name: p.read_bytes() for p in release_dir.iterdir()} == {
        p.name: p.read_bytes() for p in other.iterdir()
    }
    moved = tmp_path / "portable-renamed-directory"
    shutil.copytree(release_dir, moved)
    bundle = load_release(moved, allow_synthetic=True)
    assert bundle.manifest.coverage.expected == 12
    assert bundle.manifest.coverage.available == 11
    assert bundle.manifest.coverage.missing == 1
    assert bundle.manifest.readiness == "synthetic_only"
    assert bundle.manifest.recipe.producer.code_fingerprint is not None
    assert recipe.model_dump_json() == original


def test_changed_recipe_capture_value_and_geometry_change_identity(
    recipe: BuildRecipe, release_dir: Path, tmp_path: Path
) -> None:
    changed_version = recipe.model_copy(update={"processing_version": "pilot-v2"})
    changed = build_release(
        changed_version,
        data_root=FIXTURES,
        release_root=tmp_path / "releases",
        allow_synthetic=True,
    )
    assert changed.name != release_dir.name
    raw = tmp_path / "retained"
    shutil.copytree(FIXTURES, raw)
    for capture_id, old, new in [
        ("prices", b"3.000", b"3.001"),
        ("boundaries", b"-3.8,40.2", b"-3.81,40.2"),
    ]:
        capture = next(c for c in recipe.captures if c.capture_id == capture_id)
        payload = (raw / capture.path).read_bytes().replace(old, new)
        (raw / capture.path).write_bytes(payload)
        captures = tuple(
            c.model_copy(update={"sha256": sha256(payload), "byte_size": len(payload)})
            if c.capture_id == capture_id
            else c
            for c in recipe.captures
        )
        changed = build_release(
            recipe.model_copy(update={"captures": captures}),
            data_root=raw,
            release_root=tmp_path / capture_id,
            allow_synthetic=True,
        )
        assert changed.name != release_dir.name
        (raw / capture.path).write_bytes((FIXTURES / capture.path).read_bytes())


@pytest.mark.parametrize(
    "payload", [b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'{"a":1e999}']
)
def test_strict_json_rejects_ambiguous_or_nonfinite_tokens(payload: bytes) -> None:
    with pytest.raises(ValueError):
        strict_json(payload)


@pytest.mark.parametrize(
    "defect",
    [
        "hash",
        "count",
        "missing",
        "lineage",
        "duplicate",
        "json_key",
        "coverage",
        "usage",
        "kind",
        "identity",
        "profile",
    ],
)
def test_corruption_is_an_error_not_a_lookup_gap(release_dir: Path, defect: str) -> None:
    path = release_dir / "observations.jsonl"
    lines = path.read_bytes().splitlines()
    if defect == "hash":
        path.write_bytes(path.read_bytes() + b" ")
    elif defect == "missing":
        path.unlink()
    elif defect in ("lineage", "duplicate", "json_key", "kind", "profile"):
        row = json.loads(lines[0])
        if defect == "lineage":
            row["capture_id"] = "nonexistent"
        elif defect == "kind":
            row["observation"].update(
                evidence_kind="observed",
                source_id="real-source",
                source_url="https://example.org/report",
            )
        elif defect == "profile":
            row["observation"]["statistic"] = "median"
        elif defect == "duplicate":
            row = json.loads(lines[1])
        lines[0] = canonical_json(row).rstrip(b"\n")
        if defect == "json_key":
            lines[0] = lines[0].replace(b'"capture_id":', b'"capture_id":"other","capture_id":', 1)
        reseal(release_dir, "observations.jsonl", b"\n".join(lines) + b"\n")
    elif defect == "coverage":
        coverage = json.loads((release_dir / "coverage.json").read_bytes())
        coverage[0].update(status="missing", reason="invented gap")
        reseal(release_dir, "coverage.json", canonical_json(coverage))
    else:
        manifest = json.loads((release_dir / "manifest.json").read_bytes())
        if defect == "count":
            manifest["files"][0]["record_count"] += 1
        elif defect == "usage":
            manifest["recipe"]["decisions"][0]["local_use"] = "unresolved"
        else:
            manifest["content_digest"] = "a" * 64
        (release_dir / "manifest.json").write_bytes(canonical_json(manifest))
    with pytest.raises((ValueError, OSError)):
        load_release(release_dir, allow_synthetic=True)


def test_existing_corrupt_release_is_not_overwritten(
    recipe: BuildRecipe, release_dir: Path
) -> None:
    path = release_dir / "coverage.json"
    path.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash/size"):
        build_release(
            recipe, data_root=FIXTURES, release_root=release_dir.parent, allow_synthetic=True
        )
    assert path.read_bytes() == b"corrupt"
    assert not list(release_dir.parent.glob(".staging-*"))
    assert not list(release_dir.parent.glob("*.lock"))


def test_failed_semantic_build_leaves_no_published_directory(
    release_dir: Path, tmp_path: Path
) -> None:
    bundle = load_release(release_dir, allow_synthetic=True)
    destination = tmp_path / "failed"
    with pytest.raises(ValueError, match="duplicate"):
        write_release(
            destination,
            recipe=bundle.manifest.recipe,
            observations=bundle.observations + bundle.observations[:1],
            boundaries=bundle.boundaries,
            allow_synthetic=True,
        )
    assert list(destination.iterdir()) == []


def test_escape_symlink_and_synthetic_opt_in(release_dir: Path, tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="opt-in"):
        load_release(release_dir)
    original = (release_dir / "locations.json").read_bytes()
    outside = tmp_path / "external.json"
    outside.write_bytes(original)
    (release_dir / "locations.json").unlink()
    (release_dir / "locations.json").symlink_to(outside)
    with pytest.raises(ValueError, match="escapes"):
        load_release(release_dir, allow_synthetic=True)
