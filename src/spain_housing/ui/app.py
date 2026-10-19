"""Session orchestration; financial rules and encoders remain application-owned."""

import streamlit as st

from spain_housing.application.export import run_json, summary_csv
from spain_housing.models.results import RunOverview
from spain_housing.models.scenario import Scenario

from .contracts import Services
from .controls import render_controls, scenario_draft
from .coverage import render_coverage
from .details import render_details
from .map import decorate, render_map, selected_code, viewport
from .navigation import render_navigation
from .presentation import STYLES, Metric
from .state import Session


def render_app(initial: Scenario, services: Services, *, reload: bool = False) -> None:
    st.title("Spain housing affordability")
    geography = services.map_geography
    if (
        services.context.kind == "synthetic"
        and geography is not None
        and geography.origin == "official"
    ):
        st.warning(
            "SYNTHETIC housing prices and rents; financial results are illustrative, "
            "not observed Spanish affordability."
        )
        st.caption(
            "Official geographic boundaries, simplified for display · "
            "Synthetic housing prices and rents."
        )
    elif services.context.kind == "synthetic":
        st.warning(
            "SYNTHETIC demonstration: both market values and boundary shapes are fixtures, "
            "not observed Spanish housing or official geography."
        )
    st.caption(
        f"Release {services.context.release_id} · {services.context.readiness} · "
        f"{len(services.destinations)} economic municipalities; "
        f"{len(services.inspection_codes)} mapped municipalities."
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
        session.clear_results()
        session.error = (
            "Release or calculation evidence changed. Apply again to calculate a new run."
        )
    if reload:
        session.clear_results()
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
    run = session.applied
    if run is not None:
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
        if isinstance(run, RunOverview):
            if c2.button("Prepare full run.json"):
                with st.spinner("Preparing complete monthly results"):
                    try:
                        session.prepare_export(services)
                    except (ValueError, OSError) as exc:
                        st.error(str(exc))
            if session.full_export is not None:
                c2.download_button(
                    "Applied run.json",
                    session.full_export,
                    "run.json",
                    "application/json",
                    key="download-run",
                    on_click="ignore",
                )
        else:
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
    metric = Metric(
        st.selectbox(
            "Map metric",
            [Metric.RATIO.value, Metric.AREA.value, Metric.PRICE.value],
            key="display-metric",
        )
    )
    features = decorate(
        run,
        services.context,
        services.boundaries,
        metric,
        geography=geography,
        market_geography=services.coverage.geography,
        destinations=services.destinations if run is not None else (),
    )
    display_id = (
        geography.display_id if geography is not None else services.context.boundary_version
    )
    if st.session_state.get("housing-display") != display_id:
        st.session_state["housing-display"] = display_id
        st.session_state["housing-view"] = dict(longitude=-3.5, latitude=40.0, zoom=4.5)
        session.last_pick = None
    view, province_filter = render_navigation(features, geography)
    outlines = (
        [f.model_dump(mode="json") for f in geography.provinces.features] if geography else None
    )
    event = render_map(
        features, metric, view, outlines=outlines, chart_key="housing-map-" + display_id
    )
    codes = set(services.inspection_codes)
    picked = selected_code(event, codes)
    if picked and picked != session.last_pick:
        session.selected_code = picked
        st.session_state["inspection-location"] = picked
    session.last_pick = picked
    names = (
        {loc.code: loc.official_name for loc in geography.municipalities}
        if geography
        else {loc.location.code: loc.official_name for loc in services.context.locations}
    )
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
        "Neutral context is not a financial destination. "
        + (geography.attribution if geography else services.context.attribution)
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
            if f["properties"]["location_code"] is not None
            and (province_filter is None or f["properties"].get("province_code") == province_filter)
        ],
        hide_index=True,
    )
    result = (
        next((r for r in run.results if r.buying_location.code == session.selected_code), None)
        if run
        else None
    )
    if result is None:
        reason = (
            "Outside selected market coverage"
            if session.selected_code not in {loc.code for loc in services.destinations}
            else "Not evaluated in this run"
        )
        st.subheader(f"{names[session.selected_code]} ({session.selected_code})")
        st.info(reason + ". Geography is available; no financial result is substituted.")
    else:
        assert run is not None
        if isinstance(run, RunOverview):
            detail = session.detail(services, session.selected_code)
            render_details(detail.results[0], detail, names)
        else:
            render_details(result, run, names)
