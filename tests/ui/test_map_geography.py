"""Independent atlas/market joins and real Streamlit state over small synthetic test shapes."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from fixtures.synthetic.atlas import demo_config
from spain_housing.ingestion.demo import generate_demo
from spain_housing.ingestion.map_geometry import prepare_display
from spain_housing.ingestion.release import build_release
from spain_housing.launcher import compose
from spain_housing.storage.files import strict_json
from spain_housing.storage.release import parse_recipe
from spain_housing.ui.map import decorate
from spain_housing.ui.presentation import Metric

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def composed(tmp_path: Path, atlas_dir: Path) -> tuple[Path, Path, Path]:
    geo = atlas_dir
    display = prepare_display(geo, artifact_root=tmp_path / "displays")
    config = demo_config()
    inputs = generate_demo(geo, config, output_root=tmp_path / "inputs", variant="partial")
    release = build_release(
        parse_recipe(strict_json((inputs / "recipe.json").read_bytes())),
        data_root=inputs,
        release_root=tmp_path / "releases",
        allow_synthetic=True,
        geography_dir=geo,
    )
    return geo, display, release


def test_superset_join_distinguishes_outside_coverage_gap_and_unevaluated(composed) -> None:
    geo, display, release = composed
    scenario, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release,
        allow_synthetic=True,
        geography_dir=geo,
        display_geography=display,
    )
    run = services.evaluate(scenario, services.destinations)

    def features(value=run, metric=Metric.AREA, **changes):
        return decorate(
            value,
            services.context,
            services.boundaries,
            metric,
            geography=services.map_geography,
            market_geography=services.coverage.geography,
            destinations=services.destinations if value else (),
            **changes,
        )

    rows = {f["properties"]["location_code"]: f["properties"] for f in features()}
    assert rows["28001"]["status"] == "missing"  # Only the purchase product is missing.
    assert rows["28002"]["status"] == "outside_coverage"
    assert rows["28002"]["reason"] == "Outside selected market coverage"
    assert features(metric=Metric.PRICE)[0]["properties"]["status"] == "available"
    unevaluated = {f["properties"]["location_code"]: f["properties"] for f in features(None)}
    assert unevaluated["28001"]["status"] == "not_evaluated"
    assert unevaluated["28002"]["status"] == "outside_coverage"
    with pytest.raises(ValueError, match="join"):
        features(run.model_copy(update={"results": ()}))
    with pytest.raises(ValueError, match="join"):
        features(run.model_copy(update={"results": (run.results[0], run.results[0])}))
    with pytest.raises(ValueError, match="identity"):
        decorate(
            run,
            services.context,
            None,
            Metric.AREA,
            geography=services.map_geography.model_copy(
                update={"geography_id": "geography-" + "a" * 64}
            ),
            market_geography=services.coverage.geography,
        )


def _app(
    defaults: str, scenario: str, release: str, geo: str, display: str, compact: bool = False
) -> None:
    import dataclasses
    from pathlib import Path

    import streamlit as st

    from spain_housing.application.overview import project_location
    from spain_housing.launcher import compose
    from spain_housing.models.results import RunOverview
    from spain_housing.ui.app import render_app

    initial, services = compose(
        Path(defaults),
        Path(scenario),
        Path(release),
        allow_synthetic=True,
        geography_dir=Path(geo),
        display_geography=Path(st.session_state.get("injected-display", display)),
    )
    st.session_state.setdefault("evaluation-count", 0)

    def counted(value, destinations):
        st.session_state["evaluation-count"] += 1
        run = services.evaluate(value, destinations)
        if compact:
            return RunOverview.model_validate(
                run.model_dump(exclude={"results"})
                | {"results": tuple(project_location(row) for row in run.results)}
            )
        return run

    def detail(run, code):
        st.session_state["detail-count"] = st.session_state.get("detail-count", 0) + 1
        return services.detail(run, code)

    def export(run):
        st.session_state["export-count"] = st.session_state.get("export-count", 0) + 1
        return services.full_export(run)

    render_app(
        initial, dataclasses.replace(services, evaluate=counted, detail=detail, full_export=export)
    )


def test_geographic_only_selection_and_display_changes_never_evaluate(
    composed, tmp_path: Path
) -> None:
    geo, display, release = composed
    at = AppTest.from_function(
        _app,
        args=(
            str(ROOT / "configs/defaults.yaml"),
            str(ROOT / "configs/scenarios/phase4_room_demo.yaml"),
            str(release),
            str(geo),
            str(display),
        ),
        default_timeout=15,
    ).run()
    assert not at.exception
    assert at.selectbox(key="display-metric").value == Metric.RATIO.value
    assert any("Official geographic boundaries" in caption.value for caption in at.caption)
    initial = at.session_state["housing-session"].applied
    revision = at.session_state["housing-view-revision"]
    at.selectbox(key="inspection-location").set_value("28002").run()
    assert not at.exception
    assert any("Outside selected market coverage" in info.value for info in at.info)
    assert at.subheader[-1].value == "Same name (28002)"
    at.selectbox(key="display-metric").set_value(Metric.PRICE.value).run()
    assert at.session_state["housing-view-revision"] == revision
    next(button for button in at.button if button.label == "Reset national view").click().run()
    assert at.session_state["housing-view-revision"] == revision + 1
    next(button for button in at.button if button.label == "Reset national view").click().run()
    assert at.session_state["housing-view-revision"] == revision + 2
    next(
        button for button in at.button if button.label == "Zoom to selected location"
    ).click().run()
    assert at.session_state["housing-view-revision"] == revision + 3
    assert at.session_state["evaluation-count"] == 1
    assert not at.exception and at.session_state["evaluation-count"] == 1
    assert at.session_state["housing-session"].applied == initial
    # A compatible display identity changes, while economic memo identity stays fixed.
    second = prepare_display(geo, artifact_root=tmp_path / "other-displays", tolerance_m=20.0)
    _, first_services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release,
        allow_synthetic=True,
        geography_dir=geo,
        display_geography=display,
    )
    _, second_services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release,
        allow_synthetic=True,
        geography_dir=geo,
        display_geography=second,
    )
    from spain_housing.ui.state import cache_key

    assert first_services.map_geography.display_id != second_services.map_geography.display_id
    assert cache_key(initial.resolved_scenario, first_services) == cache_key(
        initial.resolved_scenario, second_services
    )
    at.session_state["injected-display"] = str(second)
    at.run()
    assert not at.exception
    assert at.session_state["housing-display"] == second_services.map_geography.display_id
    assert at.session_state["housing-session"].applied == initial
    assert at.session_state["evaluation-count"] == 1


def test_compact_app_defers_complete_export_and_reuses_selected_details(composed) -> None:
    from spain_housing.models.results import RunResult

    geo, display, release = composed
    at = AppTest.from_function(
        _app,
        args=tuple(
            map(
                str,
                (
                    ROOT / "configs/defaults.yaml",
                    ROOT / "configs/scenarios/phase4_room_demo.yaml",
                    release,
                    geo,
                    display,
                ),
            )
        )
        + (True,),
        default_timeout=15,
    ).run()
    assert not at.exception
    assert at.session_state["detail-count"] == 1
    assert not any(b.label == "Applied run.json" for b in at.get("download_button"))
    at.selectbox(key="display-metric").set_value(Metric.PRICE.value).run()
    assert at.session_state["evaluation-count"] == at.session_state["detail-count"] == 1
    next(b for b in at.button if b.label == "Prepare full run.json").click().run()
    assert not at.exception and at.session_state["export-count"] == 1
    session = at.session_state["housing-session"]
    prepared_export = session.full_export
    full = RunResult.model_validate_json(prepared_export)
    assert len(full.results) == 1 and full.results[0].prepared_budgets
    at.selectbox(key="inspection-location").set_value("28002").run()
    assert not at.exception and at.session_state["detail-count"] == 1
    assert any("Outside selected market coverage" in info.value for info in at.info)
    assert at.session_state["housing-session"].full_export == prepared_export
    assert at.session_state["export-count"] == 1
