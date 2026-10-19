"""Strict detached geometry joins and rendering-only viewport/selection adapters."""

import math
from collections.abc import Mapping
from typing import Any

import pydeck as pdk  # type: ignore[import-untyped]
import streamlit as st

from spain_housing.models.dataset import BoundaryCollection, BoundaryFeature, GeographyReference
from spain_housing.models.evaluation import EvaluationContext
from spain_housing.models.geography import AtlasFeature, MapGeography
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import GeographicReference

from .presentation import STYLES, DisplayValue, Metric, colour, formatted, legend, metric_value

LAYER_ID = "municipal-affordability"


def decorate(
    run: RunResult | None,
    context: EvaluationContext,
    boundaries: BoundaryCollection | None,
    metric: Metric,
    *,
    geography: MapGeography | None = None,
    market_geography: GeographyReference | None = None,
    destinations: tuple[GeographicReference, ...] | None = None,
) -> list[dict[str, Any]]:
    """Require R=E and E⊆M⊆A; geographic absence never becomes an economic result."""
    source_features: tuple[AtlasFeature | BoundaryFeature, ...]
    legacy_versions = (
        {f.properties.location_code: f.properties.boundary_version for f in boundaries.features}
        if boundaries is not None
        else {}
    )
    market = {r.location.code: r for r in context.locations}
    result_codes = [r.buying_location.code for r in run.results] if run else []
    requested = (
        [r.code for r in destinations]
        if destinations is not None
        else list(market)
        if run is not None
        else []
    )
    if geography is not None:
        atlas = {r.code: r for r in geography.municipalities}
        source_features = geography.boundaries.features
        if geography.geography_id.startswith("embedded:"):
            if geography.geography_id != "embedded:" + context.release_id:
                raise ValueError("embedded map release identity mismatch")
        elif (
            market_geography is None
            or market_geography.artifact_id != geography.geography_id
            or market_geography.boundary_version != geography.boundary_version
        ):
            raise ValueError("market/map geography identity mismatch")
        if geography.boundary_version != context.boundary_version:
            raise ValueError("map boundary versions disagree")
        names = {code: r.official_name for code, r in atlas.items()}
        atlas_codes = set(atlas)
    else:
        if boundaries is None:
            raise ValueError("map requires explicit geography or legacy embedded boundaries")
        source_features = boundaries.features
        atlas_codes = set(market)
        names = {code: r.official_name for code, r in market.items()}
    feature_codes = [
        f.properties.location_code
        for f in source_features
        if f.properties.location_code is not None
    ]
    if (
        len(market) != len(context.locations)
        or len(result_codes) != len(set(result_codes))
        or len(requested) != len(set(requested))
        or len(feature_codes) != len(set(feature_codes))
        or set(result_codes) != set(requested)
        or not set(requested) <= market.keys()
        or not market.keys() <= atlas_codes
        or set(feature_codes) != atlas_codes
    ):
        raise ValueError(
            "map join requires unique atlas/market/destination codes "
            "and exactly one result per requested code"
        )
    if run is not None and (
        run.dataset_release_id != context.release_id
        or run.evaluation_context is None
        or run.evaluation_context.boundary_version != context.boundary_version
    ):
        raise ValueError("run and map boundary versions disagree")
    results = {r.buying_location.code: r for r in run.results} if run else {}
    features = []
    for feature in source_features:
        code = feature.properties.location_code
        detached = feature.model_dump(mode="json")
        if code is None:
            detached["properties"].update(
                display_value=None,
                display_text="Geographic context",
                status="context",
                reason="Nonmunicipal territory; not a financial destination",
                evidence="Official geographic context",
                colour=[225, 225, 225, 230],
            )
            features.append(detached)
            continue
        result = results.get(code)
        if code not in market:
            display = DisplayValue("outside_coverage", None, "Outside selected market coverage")
            badge = "Geography only · no economic observation"
        elif result is None:
            display = DisplayValue("not_evaluated", None, "Not evaluated in this run")
            badge = context.kind + " market coverage · no applied result"
        else:
            location = market[code]
            if (
                location.location.level != "municipality"
                or result.buying_location != location.location
                or location.boundary_version != context.boundary_version
            ):
                raise ValueError(f"map geography/version mismatch for {code}")
            display = metric_value(result, metric)
            kinds = dict.fromkeys(
                [context.kind, *(use.observation.evidence_kind for use in result.market_inputs)]
            )
            badge = " · ".join(kinds) + (
                " · pooled proxy"
                if any(use.proxy_for_property_type for use in result.market_inputs)
                else ""
            )
        if geography is None and legacy_versions.get(code) != context.boundary_version:
            raise ValueError(f"map geography/version mismatch for {code}")
        detached["properties"].update(
            name=names[code],
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


def render_map(
    features: list[dict[str, Any]],
    metric: Metric,
    view: dict[str, float],
    *,
    outlines: list[dict[str, Any]] | None = None,
    chart_key: str = "housing-map",
) -> object:
    geographic = any(
        f["properties"].get("status") in ("outside_coverage", "not_evaluated") for f in features
    )
    for label, rgb in legend(metric, geographic=geographic):
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
                get_line_width=8,
                line_width_units="meters",
                line_width_min_pixels=0,
                line_width_max_pixels=1.2,
                auto_highlight=True,
            )
        ]
        + (
            [
                pdk.Layer(
                    "GeoJsonLayer",
                    id="province-orientation",
                    data=dict(type="FeatureCollection", features=outlines),
                    pickable=False,
                    filled=False,
                    stroked=True,
                    get_line_color=[55, 55, 55, 200],
                    get_line_width=70,
                    line_width_units="meters",
                    line_width_min_pixels=0.6,
                    line_width_max_pixels=2,
                )
            ]
            if outlines
            else []
        ),
        tooltip={
            "text": "{name} ({location_code})\n{display_text}\n{status}: {reason}\n{evidence}"
        },
    )
    return st.pydeck_chart(
        deck,
        key=chart_key,
        on_select="rerun",
        selection_mode="single-object",
        height=480,
        alt=f"Released municipality polygons coloured by {metric.value}; "
        "table below provides all values.",
    )
