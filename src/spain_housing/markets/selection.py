"""Exact profile selection, scope, freshness and retained-response verification."""

from dataclasses import dataclass
from typing import Literal

from spain_housing.models.base import add_months
from spain_housing.models.contracts import MarketData
from spain_housing.models.dataset import ReferenceProfile
from spain_housing.models.evaluation import EvaluationContext, MarketInputUse
from spain_housing.models.market import MarketMetric, MarketQuery, MarketSegment
from spain_housing.models.scenario import GeographicReference, MarketSelectionPolicy, Scenario

from .projections import growth_fraction, month_distance, project_value


@dataclass(frozen=True)
class MarketIssue:
    status: Literal["missing", "unsupported"]
    reason: str


@dataclass(frozen=True)
class SelectedReference:
    profile: ReferenceProfile
    proxy_for_property_type: Literal["flat", "house"] | None = None


def validate_selection(policy: MarketSelectionPolicy, context: EvaluationContext) -> None:
    by_id = {profile.profile_id: profile for profile in context.profiles}
    unknown = set(policy.profile_ids) - by_id.keys()
    if unknown:
        raise ValueError(f"unknown profile IDs: {', '.join(sorted(unknown))}")
    metrics = [by_id[key].metric for key in policy.profile_ids]
    if len(metrics) != len(set(metrics)):
        raise ValueError("explicit profile IDs must select at most one profile per metric")


def _compatible(request: MarketSegment, supplied: MarketSegment, property_type: str) -> bool:
    return supplied.property_type == property_type and all(
        value is None or value == getattr(supplied, name)
        for name, value in (
            ("bedrooms", request.bedrooms),
            ("size_band", request.size_band),
            ("rental_contract_category", request.rental_contract_category),
        )
    )


def select_reference(
    scenario: Scenario, context: EvaluationContext, metric: MarketMetric, segment: MarketSegment
) -> SelectedReference | MarketIssue:
    policy = scenario.market_selection
    profiles = [
        p
        for p in context.profiles
        if p.metric == metric and (not policy.profile_ids or p.profile_id in policy.profile_ids)
    ]
    base = scenario.market_policy.base_month

    def eligible(profile: ReferenceProfile) -> bool:
        return profile.period_end <= base and month_distance(profile.period_end, base) <= (
            policy.maximum_reference_age_months
        )

    exact = [p for p in profiles if _compatible(segment, p.segment, segment.property_type)]
    candidates = [p for p in exact if eligible(p)]
    proxy: Literal["flat", "house"] | None = None
    compatible = exact
    if (
        not candidates
        and segment.property_type in ("flat", "house")
        and (policy.allow_pooled_property_proxy)
    ):
        pooled = [p for p in profiles if _compatible(segment, p.segment, "pooled")]
        compatible = exact + pooled
        candidates = [p for p in pooled if eligible(p)]
        if candidates:
            proxy = segment.property_type
    if not compatible:
        return MarketIssue("unsupported", f"no compatible {metric.value} segment: {segment}")
    if not candidates:
        return MarketIssue(
            "missing",
            f"no complete/fresh {metric.value} reference at {base}; "
            f"maximum age {policy.maximum_reference_age_months} months",
        )
    if len({(p.source_id, p.basis, p.statistic) for p in candidates}) != 1:
        return MarketIssue(
            "unsupported", f"ambiguous {metric.value} source/basis/statistic; select a profile ID"
        )
    latest = max(p.period_end for p in candidates)
    selected = [p for p in candidates if p.period_end == latest]
    if len(selected) != 1:
        return MarketIssue(
            "unsupported", f"ambiguous latest {metric.value} profiles; select a profile ID"
        )
    return SelectedReference(selected[0], proxy)


def resolve_input(
    scenario: Scenario,
    *,
    context: EvaluationContext,
    market_data: MarketData,
    location: GeographicReference,
    metric: MarketMetric,
    segment: MarketSegment,
    role: Literal["room_rent", "whole_home_rent", "purchase_price"],
) -> MarketInputUse | MarketIssue:
    if location.level != "municipality":
        return MarketIssue("unsupported", "only municipality geography is supported")
    selected = select_reference(scenario, context, metric, segment)
    if isinstance(selected, MarketIssue):
        return selected
    if location.code not in context.municipality_codes:
        return MarketIssue("missing", f"municipality {location.code} is outside the release")
    profile = selected.profile
    lookup = market_data.get(
        MarketQuery(
            location=location,
            metric=metric,
            period_start=profile.period_start,
            period_end=profile.period_end,
            segment=profile.segment,
        )
    )
    if lookup.status != "available":
        return MarketIssue(lookup.status, lookup.reason or "market input unavailable")
    observation = lookup.observation
    assert observation is not None
    if observation.location != location or any(
        getattr(observation, name) != getattr(profile, name)
        for name in (
            "metric",
            "period_start",
            "period_end",
            "segment",
            "basis",
            "statistic",
            "source_id",
        )
    ):
        raise ValueError("available provider observation disagrees with selected reference profile")
    if (context.kind == "synthetic") != (observation.evidence_kind == "synthetic"):
        raise ValueError("provider evidence kind disagrees with evaluation context")
    notes = list(observation.quality_notes)
    notes.append(
        "Snapshot counterfactual/projection; reference period is not an as-of availability date."
    )
    if selected.proxy_for_property_type:
        notes.append(
            f"Pooled property proxy for requested {selected.proxy_for_property_type}; "
            "not a segmented quote."
        )
    if scenario.market_policy.kind == "frozen":
        notes.append("Frozen market counterfactual preserves distinct source periods.")
    else:
        notes.append("Effective annual growth anchored at the last covered reference month.")
    return MarketInputUse(
        role=role,
        profile_id=profile.profile_id,
        observation=observation,
        reference_anchor_month=add_months(profile.period_end, -1),
        base_month=scenario.market_policy.base_month,
        value_at_base=project_value(
            observation, scenario.market_policy, scenario.market_policy.base_month
        ),
        annual_growth_fraction=growth_fraction(observation, scenario.market_policy),
        proxy_for_property_type=selected.proxy_for_property_type,
        notes=tuple(notes),
    )
