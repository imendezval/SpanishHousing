"""Strict detached geometry joins and rendering-only viewport/selection adapters."""

import math
from collections.abc import Mapping
from typing import Any

import pydeck as pdk  # type: ignore[import-untyped]
import streamlit as st

from spain_housing.models.dataset import BoundaryCollection
from spain_housing.models.evaluation import EvaluationContext
from spain_housing.models.results import RunResult

from .presentation import STYLES, Metric, colour, formatted, legend, metric_value

LAYER_ID = "municipal-affordability"


def decorate(
    run: RunResult, context: EvaluationContext, boundaries: BoundaryCollection, metric: Metric
) -> list[dict[str, Any]]:
    codes = [r.location.code for r in context.locations]
    result_codes = [r.buying_location.code for r in run.results]
    feature_codes = [f.properties.location_code for f in boundaries.features]
    if (
        len(codes) != len(set(codes))
        or len(result_codes) != len(set(result_codes))
        or len(feature_codes) != len(set(feature_codes))
        or set(codes) != set(result_codes)
        or set(codes) != set(feature_codes)
    ):
        raise ValueError("map join requires one result, location and boundary per released code")
    if (
        run.evaluation_context is None
        or run.evaluation_context.boundary_version != context.boundary_version
    ):
        raise ValueError("run and map boundary versions disagree")
    locations = {r.location.code: r for r in context.locations}
    results = {r.buying_location.code: r for r in run.results}
    features = []
    for feature in boundaries.features:
        code = feature.properties.location_code
        location, result = locations[code], results[code]
        if (
            location.location.level != "municipality"
            or result.buying_location != location.location
            or location.boundary_version != context.boundary_version
            or feature.properties.boundary_version != context.boundary_version
        ):
            raise ValueError(f"map geography/version mismatch for {code}")
        display = metric_value(result, metric)
        detached = feature.model_dump(mode="json")
        badge = context.kind + (
            " · pooled proxy"
            if any(use.proxy_for_property_type for use in result.market_inputs)
            else ""
        )
        detached["properties"].update(
            name=location.official_name,
            display_value=display.value,
            display_text=formatted(display.value, STYLES[metric].unit),
            status=display.status,
            reason=display.reason or "",
            evidence=badge,
            colour=[*colour(display, metric), 220],
        )
        features.append(detached)
    return features


def selected_code(event: object, valid_codes: set[str]) -> str | None:
    if not isinstance(event, Mapping):
        return None
    selection = event.get("selection", {})
    objects = selection.get("objects", {}) if isinstance(selection, Mapping) else {}
    picked = objects.get(LAYER_ID, []) if isinstance(objects, Mapping) else []
    if not isinstance(picked, list) or not picked or not isinstance(picked[0], Mapping):
        return None
    properties = picked[0].get("properties", {})
    code = properties.get("location_code") if isinstance(properties, Mapping) else None
    return code if isinstance(code, str) and code in valid_codes else None


def viewport(features: list[dict[str, Any]]) -> dict[str, float]:
    points = []

    def visit(value: Any) -> None:
        if (
            isinstance(value, (list, tuple))
            and len(value) == 2
            and all(isinstance(v, (float, int)) for v in value)
        ):
            points.append(value)
        elif isinstance(value, (list, tuple)):
            for child in value:
                visit(child)

    for feature in features:
        visit(feature["geometry"]["coordinates"])
    if not points:
        raise ValueError("map has no geometry coordinates")
    west, east = min(p[0] for p in points), max(p[0] for p in points)
    south, north = min(p[1] for p in points), max(p[1] for p in points)
    span = max(east - west, (north - south) * 1.5, 0.01)
    return dict(
        longitude=(west + east) / 2,
        latitude=(south + north) / 2,
        zoom=max(3.0, min(12.0, math.log2(360 / span) - 1.5)),
    )


def render_map(features: list[dict[str, Any]], metric: Metric, view: dict[str, float]) -> object:
    for label, rgb in legend(metric):
        # Only fixed palette/bin labels enter HTML; all source text stays plain text.
        st.markdown(f'<span style="color:rgb{rgb}">■</span> {label}', unsafe_allow_html=True)
    if metric == Metric.RATIO:
        st.caption(
            "1 × target price means capacity covers the estimated target; "
            "this is not a probability."
        )
    deck = pdk.Deck(
        # Keep PyDeck's default style sentinel with no provider. Passing an
        # explicit None/empty style makes Streamlit supply remote themed tiles.
        map_provider=None,
        initial_view_state=pdk.ViewState(**view),
        layers=[
            pdk.Layer(
                "GeoJsonLayer",
                id=LAYER_ID,
                data=dict(type="FeatureCollection", features=features),
                pickable=True,
                filled=True,
                stroked=True,
                get_fill_color="properties.colour",
                get_line_color=[240, 240, 240],
                line_width_min_pixels=1,
                auto_highlight=True,
            )
        ],
        tooltip={
            "text": "{name} ({location_code})\n{display_text}\n{status}: {reason}\n{evidence}"
        },
    )
    return st.pydeck_chart(
        deck,
        key="housing-map",
        on_select="rerun",
        selection_mode="single-object",
        height=480,
        alt=f"Released municipality polygons coloured by {metric.value}; "
        "table below provides all values.",
    )
