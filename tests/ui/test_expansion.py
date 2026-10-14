from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from spain_housing.launcher import _snapshot, compose
from spain_housing.markets.repository import SnapshotMarketRepository

ROOT = Path(__file__).resolve().parents[2]


def app(defaults: str, scenario: str, initial: str) -> None:
    from pathlib import Path

    import streamlit as st

    from spain_housing.launcher import compose
    from spain_housing.ui.app import render_app

    selected = st.session_state.get("injected-release", initial)
    scenario, services = compose(
        Path(defaults), Path(scenario), Path(selected), allow_synthetic=True
    )
    render_app(scenario, services)


def test_expanded_report_release_transition_and_selection(expanded_dir, release_dir):
    at = AppTest.from_function(
        app,
        args=(
            str(ROOT / "configs/defaults.yaml"),
            str(ROOT / "configs/scenarios/phase4_room_demo.yaml"),
            str(expanded_dir),
        ),
        default_timeout=15,
    ).run()
    assert not at.exception
    session = at.session_state["housing-session"]
    assert len(session.applied.results) == 16
    assert any("43/48 captured cells" in e.value for e in at.markdown)
    at.selectbox(key="inspection-location").set_value("08015").run()
    assert session.selected_code == "08015"
    previous_draft = session.draft.copy()
    at.session_state["injected-release"] = str(release_dir)
    at.run()
    assert not at.exception
    assert at.session_state["housing-session"].applied is None
    assert not at.session_state["housing-session"].memo
    assert at.session_state["housing-session"].draft == previous_draft
    assert len(at.get("download_button")) == 0
    assert any("11/12 captured cells" in e.value for e in at.markdown)
    next(b for b in at.button if b.label == "Apply scenario").click().run()
    assert not at.exception
    run = at.session_state["housing-session"].applied
    assert len(run.results) == 4 and run.dataset_release_id == release_dir.name
    assert at.session_state["housing-session"].selected_code != "08015"


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
