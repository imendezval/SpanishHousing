"""Scenario orchestration over typed inputs, with expected gaps as explicit states."""

from dataclasses import dataclass

from spain_housing.finance import (
    ProportionalPurchaseCostPolicy,
    calculate_fixed_financing_capacity,
    simulate_savings,
)
from spain_housing.markets.projections import project_value
from spain_housing.markets.selection import MarketIssue, resolve_input, validate_selection
from spain_housing.models.contracts import MarketData, PurchaseContext
from spain_housing.models.evaluation import EvaluationContext, MarketInputUse, PurchaseFinances
from spain_housing.models.market import MarketMetric, MarketSegment
from spain_housing.models.results import (
    Indicator,
    LocationResult,
    PurchaseResult,
    RunResult,
    SavingsResult,
)
from spain_housing.models.scenario import GeographicReference, Scenario

from .compare import compare_capacity
from .modes import location_pair, ordered_locations
from .prepare import PreparationIssue, prepare_savings, purchase_finances
from .version import MODEL_VERSION, code_version, runtime_evidence


@dataclass(frozen=True)
class BuyingResult:
    purchase: PurchaseResult
    affordable_area_m2: Indicator
    target_affordability_ratio: Indicator
    market_inputs: tuple[MarketInputUse, ...]
    warnings: tuple[str, ...]
    explanation: str


def evaluate_purchase(
    scenario: Scenario,
    *,
    savings: SavingsResult,
    finances: PurchaseFinances,
    buying_location: GeographicReference,
    market_data: MarketData,
    context: EvaluationContext,
) -> BuyingResult:
    """Reusable destination work from an existing saving result and purchase finances."""
    if scenario.target_property.condition != "ordinary":
        use: MarketInputUse | MarketIssue = MarketIssue(
            "unsupported", "purchase condition has no supported source selector"
        )
    else:
        use = resolve_input(
            scenario,
            context=context,
            market_data=market_data,
            location=buying_location,
            metric=MarketMetric.PURCHASE_PRICE_PER_M2,
            segment=MarketSegment(property_type=scenario.target_property.property_type),
            role="purchase_price",
        )
    price_per_m2 = (
        None
        if isinstance(use, MarketIssue)
        else project_value(use.observation, scenario.market_policy, finances.purchase_month)
    )
    target_price = None if price_per_m2 is None else price_per_m2 * scenario.target_property.area_m2
    purchase = calculate_fixed_financing_capacity(
        savings_result=savings,
        borrower_monthly_net_income_eur=finances.borrower_monthly_net_income_eur,
        borrower_monthly_other_debt_eur=finances.borrower_monthly_other_debt_eur,
        mortgage=scenario.mortgage,
        cost_policy=ProportionalPurchaseCostPolicy(scenario.purchase_costs),
        purchase_context=PurchaseContext(
            buying_location=buying_location,
            purchase_month=finances.purchase_month,
            target_property=scenario.target_property,
        ),
        target_price_eur=target_price,
    )
    if isinstance(use, MarketIssue):
        indicator = Indicator(status=use.status, reason=use.reason)
        return BuyingResult(
            purchase,
            indicator,
            indicator,
            (),
            (),
            f"Financial capacity available; market comparison {use.status}: {use.reason}",
        )
    assert price_per_m2 is not None
    area, ratio = compare_capacity(purchase, price_per_m2, use)
    return BuyingResult(
        purchase,
        area,
        ratio,
        (use,),
        (
            *use.notes,
            "Area and target price are unit-price approximations, not available property quotes.",
            "Financial estimates do not establish bank approval or ownership-cost comfort.",
        ),
        "Financial capacity and approximate ordinary-property market comparison available.",
    )


def _unsupported(
    saving: GeographicReference,
    buying: GeographicReference,
    reason: str,
    context: EvaluationContext,
) -> LocationResult:
    indicator = Indicator(status="unsupported", reason=reason)
    warnings = context.limitations
    if context.kind == "synthetic":
        warnings = ("SYNTHETIC demonstration; not observed Spanish market evidence.", *warnings)
    return LocationResult(
        saving_location=saving,
        buying_location=buying,
        calculation_status="unsupported",
        affordable_area_m2=indicator,
        target_affordability_ratio=indicator,
        explanation=reason,
        warnings=warnings,
    )


def evaluate_location(
    scenario: Scenario,
    *,
    saving_location: GeographicReference,
    buying_location: GeographicReference,
    market_data: MarketData,
    context: EvaluationContext,
) -> LocationResult:
    if saving_location.level != "municipality" or buying_location.level != "municipality":
        return _unsupported(
            saving_location, buying_location, "only municipality geography is supported", context
        )
    prepared = prepare_savings(
        scenario, saving_location=saving_location, market_data=market_data, context=context
    )
    if isinstance(prepared, PreparationIssue):
        indicator = Indicator(
            status="unsupported" if prepared.status == "unsupported" else "missing",
            reason=prepared.reason,
        )
        return LocationResult(
            saving_location=saving_location,
            buying_location=buying_location,
            calculation_status=prepared.status,
            affordable_area_m2=indicator,
            target_affordability_ratio=indicator,
            explanation=prepared.reason,
            market_inputs=prepared.market_inputs,
            warnings=prepared.warnings,
        )
    savings = simulate_savings(
        prepared.budgets,
        starting_savings_eur=prepared.starting_savings_eur,
        retained_reserve_eur=scenario.retained_reserve_eur,
    )
    finances = purchase_finances(scenario)
    if savings.viability == "funds_exhausted":
        reason = "Saving cash was exhausted; later recovery does not make the path viable."
        indicator = Indicator(status="unviable", reason=reason)
        return LocationResult(
            saving_location=saving_location,
            buying_location=buying_location,
            savings=savings,
            prepared_budgets=prepared.budgets,
            purchase_finances=finances,
            calculation_status="unviable",
            affordable_area_m2=indicator,
            target_affordability_ratio=indicator,
            explanation=reason,
            market_inputs=prepared.market_inputs,
            warnings=prepared.warnings,
        )
    buying = evaluate_purchase(
        scenario,
        savings=savings,
        finances=finances,
        buying_location=buying_location,
        market_data=market_data,
        context=context,
    )
    return LocationResult(
        saving_location=saving_location,
        buying_location=buying_location,
        savings=savings,
        prepared_budgets=prepared.budgets,
        purchase_finances=finances,
        calculation_status="available",
        purchase=buying.purchase,
        affordable_area_m2=buying.affordable_area_m2,
        target_affordability_ratio=buying.target_affordability_ratio,
        explanation=buying.explanation,
        market_inputs=tuple(dict.fromkeys((*prepared.market_inputs, *buying.market_inputs))),
        warnings=tuple(dict.fromkeys((*prepared.warnings, *buying.warnings))),
    )


def evaluate_scenario(
    scenario: Scenario,
    *,
    market_data: MarketData,
    context: EvaluationContext,
    mapped_locations: tuple[GeographicReference, ...],
) -> RunResult:
    validate_selection(scenario.market_selection, context)
    results = []
    for mapped in ordered_locations(mapped_locations):
        saving, buying = location_pair(scenario, mapped)
        if scenario.locations.mode != "local_local":
            results.append(
                _unsupported(saving, buying, "fixed_saving geographic mode is deferred", context)
            )
        else:
            results.append(
                evaluate_location(
                    scenario,
                    saving_location=saving,
                    buying_location=buying,
                    market_data=market_data,
                    context=context,
                )
            )
    return RunResult(
        schema_version=1,
        resolved_scenario=scenario,
        dataset_release_id=context.release_id,
        evaluation_context=context,
        model_version=MODEL_VERSION,
        code_version=code_version(),
        runtime_evidence=runtime_evidence(),
        results=tuple(results),
    )
