"""Returned financial/budget/source details, without derived economic calculations."""

import streamlit as st

from spain_housing.models.results import LocationResult, RunResult

from .presentation import formatted


def render_details(result: LocationResult, run: RunResult, names: dict[str, str]) -> None:
    st.subheader(f"Details: {names[result.buying_location.code]} ({result.buying_location.code})")
    st.write(
        f"Saving location: {names.get(result.saving_location.code, result.saving_location.code)}; "
        f"buying location: {names[result.buying_location.code]}"
    )
    st.write(f"Calculation: {result.calculation_status}. {result.explanation or ''}")
    if result.purchase:
        purchase = result.purchase
        cols = st.columns(3)
        cols[0].metric("Maximum purchase price", formatted(purchase.maximum_price_eur))
        cols[1].metric(
            "Cash price limit",
            "No cash constraint"
            if purchase.savings_price_limit_eur is None
            else formatted(purchase.savings_price_limit_eur),
        )
        cols[2].metric("Mortgage price limit", formatted(purchase.mortgage_price_limit_eur))
        st.caption(
            f"Binding constraint: {purchase.binding_constraint}. "
            "Maximum price is the minimum of cash and mortgage limits."
        )
        if purchase.target_price_eur is not None:
            st.dataframe(
                [
                    dict(quantity=key, amount=getattr(purchase, key))
                    for key in (
                        "target_price_eur",
                        "target_loan_eur",
                        "target_upfront_cash_eur",
                        "target_monthly_payment_eur",
                        "target_cash_shortfall_eur",
                        "target_payment_shortfall_eur",
                    )
                ],
                hide_index=True,
            )
        else:
            st.info("Target diagnostics unavailable; financial capacity is still computed.")
    for label, indicator, unit in (
        ("Affordable area", result.affordable_area_m2, "m²"),
        ("Target affordability", result.target_affordability_ratio, "× target price"),
    ):
        st.write(
            f"{label}: {formatted(indicator.value, unit)} · "
            f"{indicator.status} · {indicator.reason or ''}"
        )
    if result.purchase_finances:
        st.write("Purchase finances", result.purchase_finances.model_dump(mode="json"))
    st.caption(
        f"Retained reserve assumption: {formatted(run.resolved_scenario.retained_reserve_eur)}"
    )
    if result.savings:
        st.write(
            f"Ending savings {formatted(result.savings.ending_savings_eur)}; usable "
            f"{formatted(result.savings.usable_savings_eur)}; {result.savings.viability}"
        )
        paths = [
            dict(
                month=p.month.isoformat(),
                closing_savings_eur=p.closing_savings_eur,
                contribution_eur=p.contribution_eur,
            )
            for p in result.savings.monthly_path
        ]
        st.line_chart(paths, x="month", y="closing_savings_eur")
        budgets = []
        for budget, point in zip(result.prepared_budgets, result.savings.monthly_path, strict=True):
            row = budget.model_dump(mode="json")
            row.update(
                contribution_eur=point.contribution_eur,
                closing_savings_eur=point.closing_savings_eur,
            )
            budgets.append(row)
        st.dataframe(budgets, hide_index=True)
    with st.expander("Source periods, projections and limitations"):
        for use in result.market_inputs:
            obs = use.observation
            st.markdown(f"**{use.role} · {obs.evidence_kind}**")
            st.write(
                f"Original {obs.value} {obs.unit.value}; {obs.basis}/{obs.statistic}; "
                f"{obs.period_start} to {obs.period_end} (exclusive); source {obs.source_id}."
            )
            st.write(
                f"Profile {use.profile_id}; anchor {use.reference_anchor_month}; "
                f"base {use.base_month}; base value {use.value_at_base}; "
                f"annual growth fraction {use.annual_growth_fraction}; "
                f"proxy for {use.proxy_for_property_type or 'none'}."
            )
            st.write("Segment", obs.segment.model_dump(mode="json"))
            if obs.source_url:
                st.link_button("Source publication", str(obs.source_url))
        for warning in result.warnings:
            st.write(warning)
    with st.expander("Release and reproducibility evidence"):
        st.write(run.evaluation_context.attribution if run.evaluation_context else "")
        st.write(f"{run.dataset_release_id}; {run.model_version}; {run.code_version}")
        if run.runtime_evidence:
            st.json(run.runtime_evidence.model_dump(mode="json"))
