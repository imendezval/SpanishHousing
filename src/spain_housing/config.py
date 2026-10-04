"""Safe scenario file loading and deterministic default resolution."""

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from spain_housing.models.scenario import Scenario


class _UniqueKeysLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(loader: _UniqueKeysLoader, node: yaml.MappingNode) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str):
            raise ValueError("YAML mapping keys must be strings")
        if key in result:
            raise ValueError(f"duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


_UniqueKeysLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)


def _json_mapping(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML/JSON object, rejecting duplicate keys at every depth."""
    content = path.read_text(encoding="utf-8")
    try:
        if path.suffix.lower() == ".json":
            value = json.loads(content, object_pairs_hook=_json_mapping)
        elif path.suffix.lower() in {".yaml", ".yml"}:
            value = yaml.load(content, Loader=_UniqueKeysLoader)
        else:
            raise ValueError(f"unsupported configuration extension: {path.suffix}")
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"invalid configuration {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a top-level mapping in {path}")
    return value


def merge_mappings(defaults: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge mappings; lists and explicit nulls replace defaults."""
    merged = deepcopy(defaults)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_mappings(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def load_scenario(defaults_path: Path, scenario_path: Path) -> Scenario:
    """Resolve explicit defaults and a saved scenario into a fresh validated record."""
    defaults = load_mapping(defaults_path)
    saved = load_mapping(scenario_path)
    try:
        return Scenario.model_validate(merge_mappings(defaults, saved))
    except ValidationError as exc:
        raise ValueError(f"invalid scenario {scenario_path}: {exc}") from exc


def scenario_json(scenario: Scenario) -> str:
    """Produce stable JSON that can be passed back to the scenario loader."""
    return json.dumps(scenario.model_dump(mode="json"), sort_keys=True, indent=2) + "\n"
