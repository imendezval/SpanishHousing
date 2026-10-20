"""Composition resources, explicit revalidation and supported server startup."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from spain_housing import launcher
from spain_housing.launcher import _snapshot, compose
from spain_housing.markets.repository import SnapshotMarketRepository

ROOT = Path(__file__).resolve().parents[1]


def test_supported_launch_argv_and_missing_optional_extra(
    release_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    defaults, scenario = (
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
    )
    calls = []
    monkeypatch.setattr(launcher.subprocess, "call", lambda args: calls.append(args) or 0)
    assert (
        launcher.serve(
            defaults=defaults,
            scenario=scenario,
            release=release_dir,
            allow_synthetic=True,
            port=8654,
        )
        == 0
    )
    args = calls[0]
    assert args[:3] == [sys.executable, "-m", "streamlit"] and args[3] == "run"
    assert Path(args[4]).name == "launcher.py" and "--server.address=127.0.0.1" in args
    assert "--server.port=8654" in args and args[-1] == "--allow-synthetic"
    with pytest.raises(ValueError, match="port"):
        launcher.serve(
            defaults=defaults, scenario=scenario, release=release_dir, allow_synthetic=True, port=0
        )
    monkeypatch.setattr(launcher.importlib.util, "find_spec", lambda name: None)
    with pytest.raises(ValueError, match=r"spain-housing\[map\]"):
        launcher.serve(
            defaults=defaults,
            scenario=scenario,
            release=release_dir,
            allow_synthetic=True,
            port=8501,
        )


def test_resource_hit_revalidation_and_digest_change(expanded_dir):
    args = (
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        expanded_dir,
    )
    _snapshot.cache_clear()
    with patch(
        "spain_housing.launcher.SnapshotMarketRepository.from_release",
        wraps=SnapshotMarketRepository.from_release,
    ) as opens:
        compose(*args, allow_synthetic=True)
        compose(*args, allow_synthetic=True)
        assert opens.call_count == 1
        compose(*args, allow_synthetic=True, reload=True)
        assert opens.call_count == 2
        manifest = expanded_dir / "manifest.json"
        manifest.write_bytes(manifest.read_bytes() + b" ")
        compose(*args, allow_synthetic=True)
        assert opens.call_count == 3

    # The loaded immutable resources are bounded, and warm resources cannot
    # bypass the explicit synthetic-data opt-in.
    assert _snapshot.cache_info().maxsize == 4
    assert _snapshot.cache_info().currsize <= 4
    with pytest.raises(ValueError, match="opt-in"):
        compose(*args)
    # Cached reads are intentional. Explicit reload must recheck payload bytes
    # even when the manifest itself has not changed.
    artifact = expanded_dir / "boundaries.geojson"
    artifact.write_bytes(artifact.read_bytes() + b" ")
    compose(*args, allow_synthetic=True)
    with pytest.raises(ValueError, match="hash/size"):
        compose(*args, allow_synthetic=True, reload=True)
