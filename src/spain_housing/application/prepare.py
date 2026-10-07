"""Destination-free preparation of one saving pool's complete monthly inputs."""

import math
from dataclasses import dataclass
from typing import Literal

from spain_housing.markets.projections import project_value
from spain_housing.markets.selection import MarketIssue, resolve_input
from spain_housing.models.base import add_months
from spain_housing.models.contracts import MarketData
from spain_housing.models.evaluation import EvaluationContext, MarketInputUse, PurchaseFinances
from spain_housing.models.market import MarketMetric, MarketSegment
from spain_housing.models.results import PreparedMonthlyBudget
from spain_housing.models.scenario import AmountPath, GeographicReference, Scenario


@dataclass(frozen=True)
class PreparedSavings:
    budgets: tuple[PreparedMonthlyBudget, ...]
    starting_savings_eur: float
    market_inputs: tuple[MarketInputUse, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PreparationIssue:
    issues: tuple[MarketIssue, ...]
    market_inputs: tuple[MarketInputUse, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def status(self) -> Literal["missing_input", "unsupported"]:
        return (
            "unsupported"
            if any(i.status == "unsupported" for i in self.issues)
            else "missing_input"
        )

    @property
    def reason(self) -> str:
        return "; ".join(issue.reason for issue in self.issues)


def sample_amount(path: AmountPath, offset: int) -> float:
    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("amount-path offset must be a nonnegative integer")
    previous = path.milestones[0]
    for following in path.milestones[1:]:
        if offset < following.month_offset:
            if path.interpolation == "step":
                return previous.amount_eur
            fraction = (offset - previous.month_offset) / (
                following.month_offset - previous.month_offset
            )
            return previous.amount_eur + (following.amount_eur - previous.amount_eur) * fraction
        previous = following
    return previous.amount_eur


def _finite_sum(values: list[float]) -> float:
    try:
        total = math.fsum(values)
    except OverflowError as exc:
        raise ValueError("participant aggregate overflow") from exc
    if not math.isfinite(total):
        raise ValueError("participant aggregate must be finite")
    return total


def _participant_amounts(
    scenario: Scenario, ids: tuple[str, ...], offset: int
) -> tuple[float, float]:
    selected = sorted(
        (p for p in scenario.participants if p.participant_id in ids),
        key=lambda p: p.participant_id,
    )
    income = _finite_sum([sample_amount(p.net_annual_income, offset) for p in selected]) / 12
    debt = _finite_sum([sample_amount(p.monthly_debt, offset) for p in selected])
    return income, debt


def purchase_finances(scenario: Scenario) -> PurchaseFinances:
    income, debt = _participant_amounts(scenario, scenario.borrower_ids, scenario.saving_months)
    return PurchaseFinances(
        purchase_month=scenario.purchase_month,
        borrower_monthly_net_income_eur=income,
        borrower_monthly_other_debt_eur=debt,
    )


def prepare_savings(
    scenario: Scenario,
    *,
    saving_location: GeographicReference,
    market_data: MarketData,
    context: EvaluationContext,
) -> PreparedSavings | PreparationIssue:
    if scenario.start_month < scenario.market_policy.base_month:
        return PreparationIssue(
            (MarketIssue("unsupported", "start month precedes base; backcasting is deferred"),)
        )
    if saving_location.level != "municipality":
        return PreparationIssue(
            (MarketIssue("unsupported", "only municipality geography is supported"),)
        )
    if not any(loc.location == saving_location for loc in context.locations):
        return PreparationIssue(
            (MarketIssue("missing", f"municipality {saving_location.code} is outside the release"),)
        )
    warnings = [
        *context.limitations,
        "One stage prices one rental unit; rent_share is the combined saving pool's share.",
        "Non-housing expenses are effective pool spending, including only bills paid outside rent.",
        "Utility inclusion is a user assumption; source bill coverage may be unknown.",
    ]
    if context.kind == "synthetic":
        warnings.insert(0, "SYNTHETIC demonstration; not observed Spanish market evidence.")
    cache: dict[tuple[MarketMetric, MarketSegment], MarketInputUse | MarketIssue] = {}
    stages: list[MarketInputUse] = []
    issues: list[MarketIssue] = []
    for stage in scenario.living_stages:
        if stage.arrangement == "room":
            metric = MarketMetric.ROOM_RENT_PER_MONTH
            if stage.rental_area_m2 is not None or stage.bedrooms is not None:
                issues.append(
                    MarketIssue(
                        "unsupported",
                        f"room selectors unsupported at offset {stage.start_month_offset}",
                    )
                )
                continue
            segment = MarketSegment(property_type="room")
            role: Literal["room_rent", "whole_home_rent"] = "room_rent"
        else:
            metric = (
                MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH
                if scenario.market_selection.whole_home_rent_source == "per_m2"
                else MarketMetric.WHOLE_HOME_RENT_PER_MONTH
            )
            if metric == MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH and stage.rental_area_m2 is None:
                issues.append(
                    MarketIssue(
                        "unsupported",
                        f"per_m2 rent requires area at offset {stage.start_month_offset}",
                    )
                )
                continue
            segment = MarketSegment(property_type="flat", bedrooms=stage.bedrooms)
            role = "whole_home_rent"
        key = metric, segment
        if key not in cache:
            cache[key] = resolve_input(
                scenario,
                context=context,
                market_data=market_data,
                location=saving_location,
                metric=metric,
                segment=segment,
                role=role,
            )
        use = cache[key]
        if isinstance(use, MarketIssue):
            month = add_months(scenario.start_month, stage.start_month_offset)
            issues.append(MarketIssue(use.status, f"stage {month}, {metric.value}: {use.reason}"))
        else:
            stages.append(use)
    traces = tuple(dict.fromkeys(use for use in cache.values() if isinstance(use, MarketInputUse)))
    for use in traces:
        warnings.extend(use.notes)
    warning_tuple = tuple(dict.fromkeys(warnings))
    if issues:
        return PreparationIssue(tuple(issues), traces, warning_tuple)
    budgets = []
    for stage, use in zip(scenario.living_stages, stages, strict=True):
        for offset in range(stage.start_month_offset, stage.end_month_offset):
            month = add_months(scenario.start_month, offset)
            rent = project_value(use.observation, scenario.market_policy, month)
            if use.observation.metric == MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH:
                assert stage.rental_area_m2 is not None
                rent *= stage.rental_area_m2
            income, debt = _participant_amounts(scenario, scenario.saver_ids, offset)
            budgets.append(
                PreparedMonthlyBudget(
                    month=month,
                    net_income_eur=income,
                    rent_eur=rent * stage.rent_share,
                    nonhousing_expenses_eur=sample_amount(
                        scenario.household_nonhousing_expenses, offset
                    ),
                    other_debt_eur=debt,
                )
            )
    starting = _finite_sum(
        [
            p.starting_savings_eur
            for p in sorted(scenario.participants, key=lambda p: p.participant_id)
            if p.participant_id in scenario.saver_ids
        ]
    )
    return PreparedSavings(tuple(budgets), starting, traces, warning_tuple)
