"""Render injected release evidence without lookups or economic interpretation."""

import streamlit as st

from spain_housing.models.coverage import ReleaseCoverageReport


def render_coverage(report: ReleaseCoverageReport) -> None:
    with st.expander("Dataset coverage and source definitions"):
        counts = report.counts
        st.write(
            f"{len(report.locations)} municipalities; {len(report.profiles)} selected products; "
            f"{counts.available}/{counts.expected} captured cells, "
            f"{counts.missing} missing, {counts.unsupported} unsupported."
        )
        st.caption(
            "Captured availability is not scenario suitability: freshness, segments, "
            "proxy permission and living arrangements are checked when Apply evaluates. "
            "A selected gap never falls back to an older period or another location/source."
        )
        st.write("Available evidence", report.evidence.model_dump(mode="json"))
        st.caption(
            f"Release {report.release_id}; {report.kind}/{report.readiness}; "
            f"redistribution {report.redistribution}. Registry {report.registry_version}; "
            f"boundaries {report.boundary_version}."
        )
        st.dataframe(
            [
                dict(
                    profile=p.profile.profile_id,
                    source=p.profile.source_id,
                    metric=p.profile.metric.value,
                    unit=p.unit.value,
                    start=p.profile.period_start.isoformat(),
                    end_exclusive=p.profile.period_end.isoformat(),
                    statistic=p.profile.statistic,
                    basis=p.profile.basis,
                    segment=p.profile.segment.model_dump(mode="json"),
                    **p.counts.model_dump(mode="json"),
                )
                for p in report.profiles
            ],
            hide_index=True,
        )
        st.dataframe([c.model_dump(mode="json") for c in report.cells], hide_index=True)
        for decision in report.decisions:
            st.write(
                f"{decision.source_id}: {decision.product}; local use {decision.local_use}; "
                f"redistribution {decision.redistribution}. {decision.attribution}"
            )
            st.write(decision.evidence_reference, *decision.notes)
        for limitation in report.limitations:
            st.write(limitation)
        st.caption(report.attribution)
