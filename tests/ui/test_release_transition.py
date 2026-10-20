"""Streamlit release transitions clear economic results and retire selections."""

from copy import deepcopy
from pathlib import Path

from streamlit.testing.v1 import AppTest

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
    previous_draft = deepcopy(session.draft)
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
