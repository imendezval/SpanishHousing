"""Bounded national summaries and pinned on-demand detail, reusing the full evaluator."""

from spain_housing.models.contracts import MarketData
from spain_housing.models.evaluation import EvaluationContext
from spain_housing.models.results import (
    LocationOverview,
    LocationResult,
    RunOverview,
    RunResult,
    SavingsSummary,
)
from spain_housing.models.scenario import GeographicReference, Scenario

from .evaluate import evaluate_scenario, iter_location_results, run_metadata
from .version import MODEL_VERSION, code_version, runtime_evidence


def project_location(result: LocationResult) -> LocationOverview:
    """Project existing results without recomputing money, status or source evidence."""
    savings = result.savings
    return LocationOverview(
        saving_location=result.saving_location,
        buying_location=result.buying_location,
        calculation_status=result.calculation_status,
        savings=SavingsSummary(
            ending_savings_eur=savings.ending_savings_eur,
            usable_savings_eur=savings.usable_savings_eur,
            viability=savings.viability,
        )
        if savings
        else None,
        purchase=result.purchase,
        affordable_area_m2=result.affordable_area_m2,
        target_affordability_ratio=result.target_affordability_ratio,
        explanation=result.explanation,
        market_inputs=result.market_inputs,
        warnings=result.warnings,
    )


def evaluate_overview(
    scenario: Scenario,
    *,
    market_data: MarketData,
    context: EvaluationContext,
    mapped_locations: tuple[GeographicReference, ...],
) -> RunOverview:
    results = tuple(
        project_location(result)
        for result in iter_location_results(
            scenario, market_data=market_data, context=context, mapped_locations=mapped_locations
        )
    )
    return RunOverview.model_validate(run_metadata(scenario, context) | {"results": results})


def validate_overview(overview: RunOverview, context: EvaluationContext) -> None:
    if (
        overview.evaluation_context != context
        or overview.dataset_release_id != context.release_id
        or overview.model_version != MODEL_VERSION
        or overview.code_version != code_version()
        or overview.runtime_evidence != runtime_evidence()
    ):
        raise ValueError("overview calculation evidence changed; apply again before detail/export")


def detail_run(
    overview: RunOverview,
    code: str,
    *,
    market_data: MarketData,
    context: EvaluationContext,
) -> RunResult:
    validate_overview(overview, context)
    selected = next((r for r in overview.results if r.buying_location.code == code), None)
    if selected is None:
        raise ValueError("requested detail is outside the applied evaluated population")
    run = evaluate_scenario(
        overview.resolved_scenario,
        market_data=market_data,
        context=context,
        mapped_locations=(selected.buying_location,),
    )
    if project_location(run.results[0]) != selected:
        raise ValueError("selected detail disagrees with the applied overview")
    return run
