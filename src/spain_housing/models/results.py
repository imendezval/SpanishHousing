"""Typed future engine outputs; no calculations live here."""

from typing import Annotated, Literal

from pydantic import StringConstraints, model_validator

from .base import (
    FiniteAmount,
    Money,
    Month,
    PositiveMoney,
    Record,
    SchemaVersion,
)
from .evaluation import EvaluationContext, MarketInputUse, PurchaseFinances, RuntimeEvidence
from .market import MarketMetric, MarketObservation
from .scenario import GeographicReference, Scenario


class PreparedMonthlyBudget(Record):
    month: Month
    net_income_eur: Money
    rent_eur: Money
    nonhousing_expenses_eur: Money
    other_debt_eur: Money


class MonthlySavingsPoint(Record):
    month: Month
    contribution_eur: FiniteAmount
    closing_savings_eur: FiniteAmount


class SavingsResult(Record):
    monthly_path: tuple[MonthlySavingsPoint, ...]
    ending_savings_eur: FiniteAmount
    usable_savings_eur: Money
    viability: Literal["viable", "funds_exhausted"]


class PurchaseResult(Record):
    savings_price_limit_eur: Money | None
    mortgage_price_limit_eur: Money
    maximum_price_eur: Money
    binding_constraint: Literal["savings", "mortgage", "both"]
    target_price_eur: PositiveMoney | None = None
    target_loan_eur: Money | None = None
    target_upfront_cash_eur: Money | None = None
    target_monthly_payment_eur: Money | None = None
    target_cash_shortfall_eur: Money | None = None
    target_payment_shortfall_eur: Money | None = None

    @model_validator(mode="after")
    def coherent_target(self) -> "PurchaseResult":
        fields = (
            self.target_price_eur,
            self.target_loan_eur,
            self.target_upfront_cash_eur,
            self.target_monthly_payment_eur,
            self.target_cash_shortfall_eur,
            self.target_payment_shortfall_eur,
        )
        if any(value is None for value in fields) and any(value is not None for value in fields):
            raise ValueError("target diagnostics must be all present or all absent")
        return self


class Indicator(Record):
    status: Literal["available", "missing", "unsupported", "unviable"]
    value: Money | None = None
    reason: str | None = None
    observations: tuple[MarketObservation, ...] = ()

    @model_validator(mode="after")
    def consistent_status(self) -> "Indicator":
        if self.status == "available" and self.value is None:
            raise ValueError("available indicator requires a numeric value")
        if self.status != "available" and (self.value is not None or not self.reason):
            raise ValueError("missing/unsupported indicator requires a reason and no value")
        return self


class LocationResult(Record):
    saving_location: GeographicReference
    buying_location: GeographicReference
    calculation_status: Literal["available", "unviable", "missing_input", "unsupported"]
    savings: SavingsResult | None = None
    purchase: PurchaseResult | None = None
    affordable_area_m2: Indicator
    target_affordability_ratio: Indicator
    explanation: str | None = None
    prepared_budgets: tuple[PreparedMonthlyBudget, ...] = ()
    market_inputs: tuple[MarketInputUse, ...] = ()
    purchase_finances: PurchaseFinances | None = None
    warnings: tuple[str, ...] = ()

    @model_validator(mode="after")
    def coherent_calculation(self) -> "LocationResult":
        if self.calculation_status == "available" and (
            self.savings is None or self.purchase is None
        ):
            raise ValueError("available calculation requires savings and purchase capacity")
        if self.purchase is not None and (
            self.savings is None or self.savings.viability != "viable"
        ):
            raise ValueError("purchase requires viable savings")
        if self.calculation_status == "unviable" and (
            self.savings is None
            or self.savings.viability != "funds_exhausted"
            or self.purchase is not None
        ):
            raise ValueError("unviable result requires exhausted savings and no purchase")
        if self.calculation_status in ("missing_input", "unsupported") and (
            self.savings is not None or self.purchase is not None or self.prepared_budgets
        ):
            raise ValueError("incomplete calculation cannot carry completed finances or budgets")
        for indicator in (self.affordable_area_m2, self.target_affordability_ratio):
            if indicator.status == "available" and (
                self.purchase is None
                or not indicator.observations
                or any(
                    observation.metric != MarketMetric.PURCHASE_PRICE_PER_M2
                    or observation.location != self.buying_location
                    for observation in indicator.observations
                )
            ):
                raise ValueError("available comparison requires purchase and buying evidence")
        return self


class RunEvidence(Record):
    schema_version: SchemaVersion
    resolved_scenario: Scenario
    dataset_release_id: Annotated[str, StringConstraints(strict=True, min_length=1)]
    model_version: Annotated[str, StringConstraints(strict=True, min_length=1)]
    code_version: Annotated[str, StringConstraints(strict=True, min_length=1)]
    evaluation_context: EvaluationContext | None = None
    runtime_evidence: RuntimeEvidence | None = None

    @model_validator(mode="after")
    def matching_context(self) -> "RunEvidence":
        if self.evaluation_context is not None and (
            self.dataset_release_id != self.evaluation_context.release_id
        ):
            raise ValueError("dataset release ID and evaluation context disagree")
        return self


class RunResult(RunEvidence):
    results: tuple[LocationResult, ...]


class SavingsSummary(Record):
    ending_savings_eur: FiniteAmount
    usable_savings_eur: Money
    viability: Literal["viable", "funds_exhausted"]


class LocationOverview(Record):
    """Returned aggregates only; no claim to contain a full monthly calculation trace."""

    saving_location: GeographicReference
    buying_location: GeographicReference
    calculation_status: Literal["available", "unviable", "missing_input", "unsupported"]
    savings: SavingsSummary | None
    purchase: PurchaseResult | None
    affordable_area_m2: Indicator
    target_affordability_ratio: Indicator
    explanation: str | None
    market_inputs: tuple[MarketInputUse, ...]
    warnings: tuple[str, ...]


class RunOverview(RunEvidence):
    kind: Literal["overview"] = "overview"
    results: tuple[LocationOverview, ...]
