"""Territorial view and inspection controls; they never change evaluated destinations."""

from typing import Any

import streamlit as st

from spain_housing.models.geography import MapGeography

from .map import viewport


def render_navigation(
    features: list[dict[str, Any]], geography: MapGeography | None
) -> tuple[dict[str, float], str | None]:
    if "housing-view" not in st.session_state:
        st.session_state["housing-view"] = dict(longitude=-3.5, latitude=40.0, zoom=4.5)
    if st.button("Fit released areas"):
        st.session_state["housing-view"] = viewport(features)
    province_filter = None
    if geography is not None and geography.origin == "official":
        view = st.selectbox(
            "Territorial view",
            ("Mainland and Balearics", "Canarias", "Ceuta and Melilla", "All territories"),
        )
        if st.button("Go to territorial view"):

            def included(feature: dict[str, Any]) -> bool:
                province = feature["properties"].get("province_code")
                return (
                    True
                    if view == "All territories"
                    else province in ("35", "38")
                    if view == "Canarias"
                    else province in ("51", "52")
                    if view == "Ceuta and Melilla"
                    else province not in ("35", "38", "51", "52")
                )

            selected = [f for f in features if included(f)]
            if selected:
                st.session_state["housing-view"] = viewport(selected)
            else:
                st.info("The selected atlas has no features in this territorial view.")
        provinces = {
            f.properties.province_code: f.properties.name for f in geography.provinces.features
        }
        choices = ["All provinces", *sorted(code for code in provinces if code is not None)]
        chosen = st.selectbox(
            "Province inspection filter",
            choices,
            format_func=lambda code: (
                code if code == "All provinces" else f"{provinces[code]} ({code})"
            ),
        )
        if chosen != "All provinces":
            province_filter = chosen
        if st.button("View selected province") and province_filter:
            selected = [
                f for f in features if f["properties"].get("province_code") == province_filter
            ]
            if selected:
                st.session_state["housing-view"] = viewport(selected)
        if st.button("Reset national view"):
            mainland = [
                f
                for f in features
                if f["properties"].get("province_code") not in ("35", "38", "51", "52")
            ]
            st.session_state["housing-view"] = viewport(mainland or features)
        st.caption(
            "Territorial/province controls change the view and table only; "
            "economic inputs and evaluated destinations stay fixed."
        )
    return st.session_state["housing-view"], province_filter
