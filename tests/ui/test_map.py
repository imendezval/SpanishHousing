import json
from pathlib import Path

import pytest

from spain_housing.launcher import compose
from spain_housing.models.results import Indicator
from spain_housing.ui.map import LAYER_ID, decorate, render_map, selected_code, viewport
from spain_housing.ui.presentation import (
    PALETTE,
    STYLES,
    DisplayValue,
    Metric,
    colour,
    legend,
    metric_value,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("metric", list(Metric))
def test_bins_zero_edges_and_open_end(metric: Metric) -> None:
    for index, edge in enumerate(STYLES[metric].edges):
        assert colour(DisplayValue("available", edge, None), metric) == PALETTE[index]
        if edge > 0:
            assert (
                colour(DisplayValue("available", edge - 0.00001, None), metric)
                == PALETTE[index - 1]
            )
    assert colour(DisplayValue("available", 1e9, None), metric) == PALETTE[-1]
    assert len(legend(metric)) == 10
    assert (
        len(
            {
                colour(DisplayValue(status, None, "reason"), metric)
                for status in ["missing", "unsupported", "unviable"]
            }
        )
        == 3
    )


def test_join_geometry_originals_and_partial_status(release_dir: Path) -> None:
    scenario, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release_dir,
        allow_synthetic=True,
    )
    run = services.evaluate(scenario, services.destinations)
    before = services.boundaries.model_dump_json()
    for metric in Metric:
        features = decorate(run, services.context, services.boundaries, metric)
        assert len(features) == 4
        assert {f["properties"]["status"] for f in features} == {"available", "missing"}
        for original, detached in zip(services.boundaries.features, features, strict=True):
            assert original.model_dump(mode="json")["geometry"] == detached["geometry"]
        assert 3 <= viewport(features)["zoom"] <= 12
        assert viewport(features[:1])["zoom"] > viewport(features)["zoom"]
    assert services.boundaries.model_dump_json() == before
    features[0]["geometry"]["coordinates"] = []
    assert services.boundaries.model_dump_json() == before
    result = run.results[0]
    assert result.purchase
    partial = result.model_copy(
        update={"affordable_area_m2": Indicator(status="missing", reason="no purchase evidence")}
    )
    assert metric_value(partial, Metric.PRICE).status == "available"
    assert metric_value(partial, Metric.AREA).status == "missing"
    zero = result.model_copy(
        update={"purchase": result.purchase.model_copy(update={"maximum_price_eur": 0.0})}
    )
    assert metric_value(zero, Metric.PRICE).value == 0
    high = result.model_copy(
        update={"target_affordability_ratio": Indicator(status="available", value=1.75)}
    )
    assert metric_value(high, Metric.RATIO).value == 1.75
    for bad_run, bad_context, boundaries in [
        (
            run.model_copy(update={"results": (*run.results, run.results[0])}),
            services.context,
            services.boundaries,
        ),
        (
            run.model_copy(update={"results": run.results[:-1]}),
            services.context,
            services.boundaries,
        ),
        (run, services.context.model_copy(update={"boundary_version": "bad"}), services.boundaries),
        (
            run,
            services.context,
            services.boundaries.model_copy(update={"features": services.boundaries.features[:-1]}),
        ),
    ]:
        with pytest.raises(ValueError, match="join|version"):
            decorate(bad_run, bad_context, boundaries, Metric.PRICE)


def test_picking_code_only_and_invalid_events() -> None:
    event = {"selection": {"objects": {LAYER_ID: [{"properties": {"location_code": "08019"}}]}}}
    assert selected_code(event, {"08019", "28079"}) == "08019"
    assert selected_code(event, {"28079"}) is None
    for invalid in [None, {}, {"selection": None}, {"selection": {"indices": {LAYER_ID: [1]}}}]:
        assert selected_code(invalid, {"08019"}) is None


def test_rendered_spec_disables_remote_basemap_and_uses_plain_tooltips(monkeypatch):
    from spain_housing.ui import map as module

    def capture(deck, **options):
        spec = json.loads(deck.to_json())
        # Streamlit's supported PyDeck no-provider default; None/empty style
        # is instead replaced by remote tiles in Streamlit 1.65.
        assert "mapProvider" not in spec and spec["mapStyle"] == "__MAP_STYLE__"
        assert set(deck._tooltip) == {"text"}
        assert options["key"] == "housing-map"
        return spec

    monkeypatch.setattr(module.st, "markdown", lambda *args, **kwargs: None)
    monkeypatch.setattr(module.st, "pydeck_chart", capture)
    render_map([], Metric.PRICE, dict(longitude=-3.5, latitude=40, zoom=4.5))
