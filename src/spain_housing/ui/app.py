"""Session orchestration; financial rules and encoders remain application-owned."""

import streamlit as st

from spain_housing.application.export import run_json, summary_csv
from spain_housing.models.scenario import Scenario

from .contracts import Services
from .controls import render_controls, scenario_draft
from .coverage import render_coverage
from .details import render_details
from .map import decorate, render_map, selected_code, viewport
from .presentation import STYLES, Metric
from .state import Session


def render_app(initial: Scenario, services: Services, *, reload: bool = False) -> None:
    st.title("Spain housing affordability")
    if services.context.kind == "synthetic":
        st.warning(
            "SYNTHETIC demonstration: both market values and boundary shapes are fixtures, "
            "not observed Spanish housing or official geography."
        )
    st.caption(
        f"Release {services.context.release_id} · {services.context.readiness} · "
        f"{len(services.destinations)} released municipalities; sparse coverage only."
    )
    render_coverage(services.coverage)
    if "housing-session" not in st.session_state:
        session = Session(scenario_draft(initial))
        session.apply(session.draft, services)
        st.session_state["housing-session"] = session
    session = st.session_state["housing-session"]
    if session.applied is not None and (
        session.applied.dataset_release_id != services.context.release_id
        or session.applied.code_version != services.code_version
        or session.applied.model_version != services.model_version
        or session.applied.runtime_evidence != services.runtime
    ):
        session.memo.clear()
        session.applied = None
        session.error = (
            "Release or calculation evidence changed. Apply again to calculate a new run."
        )
    if reload:
        session.memo.clear()
        session.applied = None
        session.error = "Release revalidated. Apply the draft to calculate a new run."
    uploaded = st.file_uploader(
        "Import scenario JSON/YAML (UTF-8, maximum 1 MiB)",
        type=["json", "yaml", "yml"],
        max_upload_size=1,
    )
    if st.button("Stage imported scenario", disabled=uploaded is None):
        assert uploaded is not None
        session.stage_import(uploaded.getvalue(), uploaded.name, services)
        st.rerun()
    if session.pending_import:
        st.info("Imported draft awaits Apply. The displayed run is the previous applied scenario.")
    edited, submitted = render_controls(session.draft, session.epoch)
    if submitted:
        session.apply(edited, services)
        st.rerun()
    if session.error:
        st.error(session.error)
        st.info(
            "Inputs were not applied. Displayed results and downloads belong to "
            "the previous successful scenario."
        )
    if session.applied is None:
        return
    run = session.applied
    st.subheader("Last applied scenario")
    st.caption(
        f"Start {run.resolved_scenario.start_month}; purchase "
        f"{run.resolved_scenario.purchase_month}; {run.resolved_scenario.saving_months} "
        "saving months. Unsubmitted form edits do not change these results."
    )
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "Applied scenario.json",
        services.encode_scenario(run.resolved_scenario),
        "scenario.json",
        "application/json",
        key="download-scenario",
        on_click="ignore",
    )
    c2.download_button(
        "Applied run.json",
        run_json(run),
        "run.json",
        "application/json",
        key="download-run",
        on_click="ignore",
    )
    c3.download_button(
        "Applied summary.csv",
        summary_csv(run),
        "summary.csv",
        "text/csv",
        key="download-csv",
        on_click="ignore",
    )
    metric = Metric(st.selectbox("Map metric", [m.value for m in Metric], key="display-metric"))
    features = decorate(run, services.context, services.boundaries, metric)
    if "housing-view" not in st.session_state:
        st.session_state["housing-view"] = dict(longitude=-3.5, latitude=40.0, zoom=4.5)
    if st.button("Fit released areas"):
        st.session_state["housing-view"] = viewport(features)
    event = render_map(features, metric, st.session_state["housing-view"])
    codes = {location.code for location in services.destinations}
    picked = selected_code(event, codes)
    if picked and picked != session.last_pick:
        session.selected_code = picked
        st.session_state["inspection-location"] = picked
    session.last_pick = picked
    names = {loc.location.code: loc.official_name for loc in services.context.locations}
    if st.session_state.get("inspection-location") not in codes:
        st.session_state["inspection-location"] = session.selected_code or sorted(codes)[0]
    session.selected_code = st.selectbox(
        "Inspect municipality",
        sorted(codes),
        format_func=lambda code: f"{names[code]} ({code})",
        key="inspection-location",
    )
    if st.button("Zoom to selected location"):
        selected_features = [
            f for f in features if f["properties"]["location_code"] == session.selected_code
        ]
        st.session_state["housing-view"] = viewport(selected_features)
        st.rerun()
    st.caption(
        f"{STYLES[metric].unit} · no external tiles or tokens required. "
        "Uncovered areas remain uncoloured. " + services.context.attribution
    )
    st.dataframe(
        [
            dict(
                name=f["properties"]["name"],
                code=f["properties"]["location_code"],
                value=f["properties"]["display_value"],
                unit=STYLES[metric].unit,
                status=f["properties"]["status"],
                reason=f["properties"]["reason"],
                evidence=f["properties"]["evidence"],
            )
            for f in features
        ],
        hide_index=True,
    )
    result = next(r for r in run.results if r.buying_location.code == session.selected_code)
    render_details(result, run, names)
