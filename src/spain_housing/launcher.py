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
from spain_housing.markets.geography import embedded_map_geography, open_map_geography
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.dataset import ReleaseManifestV2
from spain_housing.models.geography import MapGeography
from spain_housing.models.scenario import Scenario
from spain_housing.ui.contracts import Services

UPLOAD_LIMIT = 1024 * 1024


@lru_cache(maxsize=4)
def _snapshot(
    path: str,
    manifest_digest: str,
    allow_synthetic: bool,
    geography_path: str | None = None,
    geography_digest: str | None = None,
) -> SnapshotMarketRepository:
    return SnapshotMarketRepository.from_release(
        Path(path),
        allow_synthetic=allow_synthetic,
        geography_dir=Path(geography_path) if geography_path else None,
    )


@lru_cache(maxsize=4)
def _map_geography(
    geography_path: str, geography_digest: str, display_path: str, display_digest: str
) -> MapGeography:
    return open_map_geography(Path(geography_path), Path(display_path))


def _manifest_digest(root: Path) -> str:
    return hashlib.sha256((root / "manifest.json").read_bytes()).hexdigest()


def compose(
    defaults: Path,
    scenario: Path,
    release: Path,
    *,
    allow_synthetic: bool = False,
    reload: bool = False,
    geography_dir: Path | None = None,
    display_geography: Path | None = None,
) -> tuple[Scenario, Services]:
    resolved = load_scenario(defaults, scenario)
    default_values = load_mapping(defaults)
    path = release.resolve()
    if reload:
        _snapshot.cache_clear()
        _map_geography.cache_clear()
    digest = _manifest_digest(path)
    geo_path = geography_dir.resolve() if geography_dir else None
    geo_digest = _manifest_digest(geo_path) if geo_path else None
    repository = (
        _snapshot(str(path), digest, allow_synthetic, str(geo_path), geo_digest)
        if geo_path
        else _snapshot(str(path), digest, allow_synthetic)
    )
    map_geography = None
    boundaries = None
    if isinstance(repository.manifest, ReleaseManifestV2):
        if geo_path is None or geo_digest is None or display_geography is None:
            raise ValueError("schema-2 map requires explicit --geography and --display-geography")
        display_path = display_geography.resolve()
        map_geography = _map_geography(
            str(geo_path), geo_digest, str(display_path), _manifest_digest(display_path)
        )
    else:
        if display_geography is not None:
            raise ValueError("schema-1 map uses embedded geography; omit --display-geography")
        boundaries = repository.boundaries
        map_geography = embedded_map_geography(repository.evaluation_context, boundaries)

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
        boundaries=boundaries,
        map_geography=map_geography,
        model_version=MODEL_VERSION,
        code_version=code_version(),
        runtime=runtime_evidence(),
        coverage=repository.coverage_report,
    )


def serve(
    *,
    defaults: Path,
    scenario: Path,
    release: Path,
    allow_synthetic: bool,
    port: int,
    geography_dir: Path | None = None,
    display_geography: Path | None = None,
) -> int:
    if importlib.util.find_spec("streamlit") is None:
        raise ValueError(
            "Map support is not installed. Install spain-housing[map] or uv sync --extra map."
        )
    if not 1 <= port <= 65535:
        raise ValueError("port must be between 1 and 65535")
    compose(
        defaults,
        scenario,
        release,
        allow_synthetic=allow_synthetic,
        geography_dir=geography_dir,
        display_geography=display_geography,
    )
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
    if geography_dir is not None:
        args.extend(("--geography", str(geography_dir.resolve())))
    if display_geography is not None:
        args.extend(("--display-geography", str(display_geography.resolve())))
    return subprocess.call(args)


def main() -> None:
    import streamlit as st

    from spain_housing.ui.app import render_app

    parser = argparse.ArgumentParser()
    for name in ("defaults", "scenario", "release"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--allow-synthetic", action="store_true")
    parser.add_argument("--geography", type=Path)
    parser.add_argument("--display-geography", type=Path)
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
            geography_dir=args.geography,
            display_geography=args.display_geography,
        )
        render_app(initial, services, reload=reload)
    except (OSError, ValueError) as exc:
        st.error(f"Application could not load or render: {exc}")


if __name__ == "__main__":
    # Streamlit reexecutes its script on reruns. Use the imported module so
    # immutable release resources retain their bounded process-wide cache.
    from spain_housing.launcher import main as run_app

    run_app()
