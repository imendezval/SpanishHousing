"""Packaged local composition, bounded immutable resources and server startup."""

import argparse
import hashlib
import importlib.util
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

from spain_housing.application import evaluate_scenario
from spain_housing.application.version import MODEL_VERSION, code_version, runtime_evidence
from spain_housing.config import (
    load_mapping,
    load_scenario,
    merge_mappings,
    parse_mapping,
    scenario_json,
)
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.scenario import Scenario
from spain_housing.ui.contracts import Services

UPLOAD_LIMIT = 1024 * 1024


@lru_cache(maxsize=4)
def _snapshot(path: str, manifest_digest: str, allow_synthetic: bool) -> SnapshotMarketRepository:
    return SnapshotMarketRepository.from_release(Path(path), allow_synthetic=allow_synthetic)


def compose(
    defaults: Path,
    scenario: Path,
    release: Path,
    *,
    allow_synthetic: bool = False,
    reload: bool = False,
) -> tuple[Scenario, Services]:
    resolved = load_scenario(defaults, scenario)
    default_values = load_mapping(defaults)
    path = release.resolve()
    if reload:
        _snapshot.cache_clear()
    digest = hashlib.sha256((path / "manifest.json").read_bytes()).hexdigest()
    repository = _snapshot(str(path), digest, allow_synthetic)

    def decode(payload: bytes, name: str) -> Scenario:
        if len(payload) > UPLOAD_LIMIT:
            raise ValueError("scenario upload exceeds 1 MiB")
        text = payload.decode("utf-8")
        values = parse_mapping(text, Path(name).suffix)
        return Scenario.model_validate(merge_mappings(default_values, values))

    return resolved, Services(
        evaluate=lambda value, destinations: evaluate_scenario(
            value,
            market_data=repository,
            context=repository.evaluation_context,
            mapped_locations=destinations,
        ),
        decode_scenario=decode,
        encode_scenario=scenario_json,
        context=repository.evaluation_context,
        boundaries=repository.boundaries,
        model_version=MODEL_VERSION,
        code_version=code_version(),
        runtime=runtime_evidence(),
    )


def serve(
    *, defaults: Path, scenario: Path, release: Path, allow_synthetic: bool, port: int
) -> int:
    if importlib.util.find_spec("streamlit") is None:
        raise ValueError(
            "Map support is not installed. Install spain-housing[map] or uv sync --extra map."
        )
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    compose(defaults, scenario, release, allow_synthetic=allow_synthetic)
    args = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(Path(__file__).resolve()),
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--",
        "--defaults",
        str(defaults.resolve()),
        "--scenario",
        str(scenario.resolve()),
        "--release",
        str(release.resolve()),
    ]
    if allow_synthetic:
        args.append("--allow-synthetic")
    return subprocess.call(args)


def main() -> None:
    import streamlit as st

    from spain_housing.ui.app import render_app

    parser = argparse.ArgumentParser()
    for name in ("defaults", "scenario", "release"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--allow-synthetic", action="store_true")
    args = parser.parse_args()
    st.set_page_config(page_title="Spain housing affordability", layout="wide")
    try:
        reload = st.sidebar.button("Reload validated release")
        initial, services = compose(
            args.defaults,
            args.scenario,
            args.release,
            allow_synthetic=args.allow_synthetic,
            reload=reload,
        )
        render_app(initial, services, reload=reload)
    except (OSError, ValueError) as exc:
        st.error(f"Application could not load or render: {exc}")


if __name__ == "__main__":
    main()
