"""Lossless table/widget representation; models retain all domain validation."""

from copy import deepcopy
from datetime import date
from typing import Any

import streamlit as st

from spain_housing.models.scenario import Scenario

# Any is confined to editable representations returned by the framework.
Draft = dict[str, Any]


def scenario_draft(scenario: Scenario) -> Draft:
    data = scenario.model_dump(mode="json")
    participants: list[Draft] = []
    income: list[Draft] = []
    debt: list[Draft] = []
    for participant in data["participants"]:
        key = participant["participant_id"]
        participants.append(
            dict(
                participant_id=key,
                starting_savings_eur=participant["starting_savings_eur"],
                saver=key in scenario.saver_ids,
                borrower=key in scenario.borrower_ids,
                income_interpolation=participant["net_annual_income"]["interpolation"],
                debt_interpolation=participant["monthly_debt"]["interpolation"],
            )
        )
        for name, rows in (("net_annual_income", income), ("monthly_debt", debt)):
            rows.extend(
                dict(participant_id=key, **point) for point in participant[name]["milestones"]
            )
    return dict(
        base=data,
        participants=participants,
        income=income,
        debt=debt,
        stages=deepcopy(data["living_stages"]),
        expenses=deepcopy(data["household_nonhousing_expenses"]["milestones"]),
    )


def draft_scenario(draft: Draft) -> Scenario:
    data = deepcopy(draft["base"])
    ids = [row.get("participant_id") for row in draft["participants"]]
    for name in ("income", "debt"):
        for index, row in enumerate(draft[name]):
            if row.get("participant_id") not in ids:
                raise ValueError(
                    f"{name} row {index + 1}: unknown participant ID; update the row explicitly"
                )
    participants = []
    for row in draft["participants"]:
        key = row.get("participant_id")
        paths = {}
        for table, field, interpolation in (
            ("income", "net_annual_income", "income_interpolation"),
            ("debt", "monthly_debt", "debt_interpolation"),
        ):
            paths[field] = dict(
                interpolation=row.get(interpolation),
                milestones=[
                    {name: value for name, value in point.items() if name != "participant_id"}
                    for point in draft[table]
                    if point.get("participant_id") == key
                ],
            )
        participants.append(
            dict(participant_id=key, starting_savings_eur=row.get("starting_savings_eur"), **paths)
        )
    data.update(
        participants=participants,
        saver_ids=[r.get("participant_id") for r in draft["participants"] if r.get("saver")],
        borrower_ids=[r.get("participant_id") for r in draft["participants"] if r.get("borrower")],
        living_stages=deepcopy(draft["stages"]),
    )
    data["household_nonhousing_expenses"]["milestones"] = deepcopy(draft["expenses"])
    return Scenario.model_validate(data)


def _percent(label: str, value: float, key: str) -> float:
    displayed = st.number_input(label, value=value * 100, key=key, format="%.8f")
    # Preserve the exact original fraction when its display was not changed.
    return value if displayed == value * 100 else displayed / 100


def _table(label: str, rows: list[Draft], key: str) -> list[Draft]:
    st.markdown(f"**{label}**")
    columns: dict[str, Any] = {
        "participant_id": st.column_config.TextColumn("Participant ID"),
        "month_offset": st.column_config.NumberColumn("Month offset", step=1),
        "amount_eur": st.column_config.NumberColumn("Amount EUR", format="%.8f"),
        "starting_savings_eur": st.column_config.NumberColumn(
            "Starting savings EUR", format="%.8f"
        ),
        "saver": st.column_config.CheckboxColumn("Saver"),
        "borrower": st.column_config.CheckboxColumn("Borrower"),
        "income_interpolation": st.column_config.SelectboxColumn(
            "Income rule", options=["linear", "step"]
        ),
        "debt_interpolation": st.column_config.SelectboxColumn(
            "Debt rule", options=["linear", "step"]
        ),
        "arrangement": st.column_config.SelectboxColumn(
            "Arrangement", options=["room", "flat_alone", "flat_shared"]
        ),
        "start_month_offset": st.column_config.NumberColumn("Start offset", step=1),
        "end_month_offset": st.column_config.NumberColumn("End offset (exclusive)", step=1),
        "rent_share": st.column_config.NumberColumn("Pool rent share (fraction)", format="%.8f"),
        "rental_area_m2": st.column_config.NumberColumn("Rental area m²", format="%.8f"),
        "bedrooms": st.column_config.NumberColumn("Bedrooms (optional)", step=1),
        "rent_includes_utilities": st.column_config.CheckboxColumn(
            "Rent includes utilities (assumed)"
        ),
    }
    # Always supply nullable columns even when absent from every original row.
    if label == "Living stages":
        rows = [
            dict(rental_area_m2=None, bedrooms=None, **row)
            if not any(k in row for k in ("bedrooms", "rental_area_m2"))
            else row
            for row in rows
        ]
    result = st.data_editor(
        rows, num_rows="dynamic", key=key, column_config=columns, width="stretch"
    )
    return list(result)


def render_controls(draft: Draft, epoch: int) -> tuple[Draft, bool]:
    edited = deepcopy(draft)
    data = edited["base"]
    prefix = f"draft-{epoch}-"
    with st.form("scenario-form"):
        st.subheader("Scenario inputs")
        st.caption(
            "Net annual income is EUR/year; debt and expenses are EUR/month. "
            "Apply submits all edits together."
        )
        c1, c2 = st.columns(2)
        with c1:
            data["start_month"] = (
                st.date_input(
                    "Start month",
                    value=date.fromisoformat(data["start_month"]),
                    key=prefix + "start",
                )
                .replace(day=1)
                .isoformat()
            )
        with c2:
            data["saving_months"] = st.number_input(
                "Saving horizon (months)",
                value=data["saving_months"],
                step=1,
                key=prefix + "horizon",
            )
        with st.expander("Participants and income/debt paths", expanded=False):
            st.caption(
                "Savers contribute cash; borrowers supply purchase-time income/debt. "
                "Future milestones are preserved."
            )
            edited["participants"] = _table(
                "Participants", edited["participants"], prefix + "participants"
            )
            edited["income"] = _table(
                "Net annual income milestones", edited["income"], prefix + "income"
            )
            edited["debt"] = _table(
                "Monthly other debt milestones", edited["debt"], prefix + "debt"
            )
        with st.expander("Living stages and effective spending"):
            st.caption(
                "One stage prices one unit. Rent share belongs to the combined saving pool. "
                "Expenses include only bills outside rent; change milestones explicitly."
            )
            edited["stages"] = _table("Living stages", edited["stages"], prefix + "stages")
            edited["expenses"] = _table(
                "Monthly non-housing expense milestones", edited["expenses"], prefix + "expenses"
            )
            path = data["household_nonhousing_expenses"]
            path["interpolation"] = st.selectbox(
                "Expense interpolation",
                ["step", "linear"],
                index=["step", "linear"].index(path["interpolation"]),
                key=prefix + "expenses-rule",
            )
            data["retained_reserve_eur"] = st.number_input(
                "Retained reserve EUR",
                value=float(data["retained_reserve_eur"]),
                key=prefix + "reserve",
                format="%.8f",
            )
        with st.expander("Mortgage, purchase allowance and target"):
            mortgage = data["mortgage"]
            for field, label in (
                ("financed_fraction", "Financed price (%)"),
                ("maximum_debt_ratio", "Maximum total debt / net income (%)"),
                ("annual_nominal_interest_fraction", "Annual nominal mortgage interest (%)"),
            ):
                mortgage[field] = _percent(label, mortgage[field], prefix + field)
            mortgage["term_years"] = st.number_input(
                "Mortgage term (years)", value=mortgage["term_years"], step=1, key=prefix + "term"
            )
            costs = data["purchase_costs"]
            costs["allowance_fraction"] = _percent(
                "Proportional purchase-cost allowance (%)",
                costs["allowance_fraction"],
                prefix + "costs",
            )
            target = data["target_property"]
            for field, label, options in (
                ("property_type", "Target property", ["flat", "house"]),
                ("condition", "Target condition", ["ordinary", "new", "renovation"]),
            ):
                target[field] = st.selectbox(
                    label, options, index=options.index(target[field]), key=prefix + field
                )
            target["area_m2"] = st.number_input(
                "Target area m²",
                value=float(target["area_m2"]),
                key=prefix + "target-area",
                format="%.8f",
            )
        with st.expander("Market policy and geography"):
            policy = data["market_policy"]
            policy["kind"] = st.selectbox(
                "Market policy",
                ["frozen", "growth"],
                index=["frozen", "growth"].index(policy["kind"]),
                key=prefix + "policy",
            )
            policy["base_month"] = (
                st.date_input(
                    "Market base month",
                    value=date.fromisoformat(policy["base_month"]),
                    key=prefix + "base",
                )
                .replace(day=1)
                .isoformat()
            )
            for field, label in (
                ("annual_rent_growth_fraction", "Effective annual rent growth (%)"),
                ("annual_purchase_growth_fraction", "Effective annual purchase growth (%)"),
            ):
                policy[field] = _percent(label, policy[field], prefix + field)
            selection = data["market_selection"]
            selection["maximum_reference_age_months"] = st.number_input(
                "Maximum reference age (months)",
                value=selection["maximum_reference_age_months"],
                step=1,
                key=prefix + "age",
            )
            text = st.text_input(
                "Explicit profile IDs (comma separated)",
                value=", ".join(selection["profile_ids"]),
                key=prefix + "profiles",
            )
            selection["profile_ids"] = [part.strip() for part in text.split(",")] if text else []
            selection["whole_home_rent_source"] = st.selectbox(
                "Whole-home rent source",
                ["per_m2", "per_month"],
                index=["per_m2", "per_month"].index(selection["whole_home_rent_source"]),
                key=prefix + "rent-source",
            )
            selection["allow_pooled_property_proxy"] = st.checkbox(
                "Allow labelled pooled property proxy",
                value=selection["allow_pooled_property_proxy"],
                key=prefix + "proxy",
            )
            st.caption(
                f"Geographic mode: {data['locations']['mode']}. Local/local is supported; "
                "fixed saving is deferred. Imported independent bindings are preserved."
            )
        submitted = st.form_submit_button("Apply scenario")
    return edited, submitted
