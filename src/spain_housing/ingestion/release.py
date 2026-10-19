"""Offline assembly from retained captures; storage owns persistence and verification."""

from pathlib import Path

from spain_housing.models.dataset import BuildRecipe, MarketRecipe, ReleasedObservation
from spain_housing.storage.release import (
    canonical_json,
    read_capture,
    sha256,
    validate_geography_reference,
    validate_recipe,
    write_release,
)

from .adapters.curated import read_curated_csv
from .geography import select_boundaries, verify_registry
from .normalize import normalize_rows


def processing_fingerprint() -> str:
    """Fingerprint processing/model source bytes without workstation paths or Git dependency."""
    package = Path(__file__).resolve().parents[1]
    fingerprints = {
        path.relative_to(package).as_posix(): sha256(path.read_bytes())
        for namespace in ("models", "storage", "ingestion")
        for path in sorted((package / namespace).rglob("*.py"))
    }
    return sha256(canonical_json(fingerprints))


def build_release(
    recipe: MarketRecipe,
    *,
    data_root: Path,
    release_root: Path,
    allow_synthetic: bool = False,
    geography_dir: Path | None = None,
) -> Path:
    validate_recipe(recipe, allow_synthetic=allow_synthetic)
    recipe = recipe.model_copy(
        update={
            "producer": recipe.producer.model_copy(
                update={"code_fingerprint": processing_fingerprint()}
            )
        }
    )
    captures = {item.capture_id: item for item in recipe.captures}
    captured_bytes = {key: read_capture(data_root, capture) for key, capture in captures.items()}
    validate_geography_reference(recipe, geography_dir)
    boundaries = None
    if isinstance(recipe, BuildRecipe):
        registry = captures[recipe.geography.registry_capture_id]
        verify_registry(captured_bytes[registry.capture_id], registry.format, recipe.locations)
        boundaries = select_boundaries(recipe, captured_bytes)
    rows: list[ReleasedObservation] = []
    for capture_id in recipe.observation_capture_ids:
        capture = captures[capture_id]
        if capture.format != "csv":
            raise ValueError("selected observation adapter requires a reviewed curated CSV")
        try:
            rows.extend(
                normalize_rows(read_curated_csv(captured_bytes[capture_id]), capture, recipe)
            )
        except ValueError as exc:
            raise ValueError(
                f"capture {capture_id} ({capture.source_id}, {capture.path}): {exc}"
            ) from exc
    return write_release(
        release_root,
        recipe=recipe,
        observations=tuple(rows),
        boundaries=boundaries,
        allow_synthetic=allow_synthetic,
        geography_dir=geography_dir,
    )
