from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


def app(defaults: str, scenario: str, release: str) -> None:
    from dataclasses import replace
    from pathlib import Path

    import streamlit as st

    from spain_housing.launcher import compose
    from spain_housing.ui.app import render_app

    initial, services = compose(Path(defaults), Path(scenario), Path(release), allow_synthetic=True)
    if "evaluation-count" not in st.session_state:
        st.session_state["evaluation-count"] = 0

    def counted(value, destinations):
        st.session_state["evaluation-count"] += 1
        return services.evaluate(value, destinations)

    render_app(initial, replace(services, evaluate=counted))


def test_real_controls_apply_correct_error_and_downloads(release_dir: Path) -> None:
    at = AppTest.from_function(
        app,
        args=(
            str(ROOT / "configs/defaults.yaml"),
            str(ROOT / "configs/scenarios/phase4_room_demo.yaml"),
            str(release_dir),
        ),
        default_timeout=15,
    ).run()
    assert not at.exception
    session = at.session_state["housing-session"]
    assert session.applied.results[-1].purchase.maximum_price_eur == pytest.approx(38000)
    horizon = next(
        widget for widget in at.number_input if widget.label == "Saving horizon (months)"
    )
    horizon.set_value(13)
    next(button for button in at.button if button.label == "Apply scenario").click()
    at.run()
    assert not at.exception and at.error
    session = at.session_state["housing-session"]
    assert session.applied.resolved_scenario.saving_months == 12
    assert session.draft["base"]["saving_months"] == 13
    horizon = next(
        widget for widget in at.number_input if widget.label == "Saving horizon (months)"
    )
    horizon.set_value(12)
    reserve = next(widget for widget in at.number_input if widget.label == "Retained reserve EUR")
    reserve.set_value(6000.0)
    next(button for button in at.button if button.label == "Apply scenario").click()
    at.run()
    assert not at.exception and not at.error
    session = at.session_state["housing-session"]
    assert session.applied.resolved_scenario.retained_reserve_eur == 6000
    assert session.applied.results[-1].purchase.maximum_price_eur == pytest.approx(
        34666.666666666664
    )
    assert len(at.get("download_button")) == 3
    calls = at.session_state["evaluation-count"]
    at.selectbox(key="display-metric").set_value("Affordable area").run()
    assert not at.exception
    at.selectbox(key="inspection-location").set_value("28065").run()
    assert not at.exception
    next(button for button in at.button if button.label == "Fit released areas").click().run()
    assert not at.exception and at.session_state["evaluation-count"] == calls
    assert "Synthetic Getafe" in at.subheader[-1].value
