import sys
from pathlib import Path

import pytest

from spain_housing import launcher

ROOT = Path(__file__).resolve().parents[2]


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
