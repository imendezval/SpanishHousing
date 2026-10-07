"""Reconstruct real official geography independently of blocked market inputs."""

import argparse
from pathlib import Path

from spain_housing.config import load_mapping
from spain_housing.ingestion.geography import select_boundaries, verify_registry
from spain_housing.models.dataset import BuildRecipe
from spain_housing.storage.release import (
    canonical_json,
    read_capture,
    sha256,
    validate_capture_permission,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    recipe = BuildRecipe.model_validate(load_mapping(args.config))
    if recipe.kind != "observed":
        raise ValueError("this verification command is for real official geography only")
    decisions = {decision.source_id: decision for decision in recipe.decisions}
    captures = {capture.capture_id: capture for capture in recipe.captures}
    required = tuple(
        capture.capture_id
        for capture in recipe.captures
        if capture.source_id in ("ine-municipalities", "ign-administrativeunit")
    )
    raw = {}
    for capture_id in required:
        capture = captures[capture_id]
        validate_capture_permission(capture, decisions[capture.source_id], recipe.kind)
        raw[capture_id] = read_capture(args.data_root, capture)
    registry = captures[recipe.geography.registry_capture_id]
    verify_registry(raw[registry.capture_id], registry.format, recipe.locations)
    boundaries = select_boundaries(recipe, raw)
    data = {
        "locations.json": canonical_json(
            [location.model_dump(mode="json") for location in recipe.locations]
        ),
        "boundaries.geojson": canonical_json(boundaries.model_dump(mode="json")),
    }
    reference = {
        "kind": "official_geography_only",
        "not_a_market_release": True,
        "geography": recipe.geography.model_dump(mode="json"),
        "municipal_codes": sorted(location.location.code for location in recipe.locations),
        "files": [
            {"path": name, "sha256": sha256(payload), "byte_size": len(payload)}
            for name, payload in data.items()
        ],
        "capture_ids": list(required),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    for name, payload in data.items():
        destination = args.output_root / name
        if destination.exists():
            if destination.read_bytes() != payload:
                raise ValueError("geography output differs; choose a new output directory")
        else:
            destination.write_bytes(payload)
    print(canonical_json(reference).decode(), end="")


if __name__ == "__main__":
    main()
