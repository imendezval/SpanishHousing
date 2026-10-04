"""Typed future engine outputs; no calculations live here."""

from typing import Annotated, Literal

from pydantic import StringConstraints, model_validator

from .base import (
    FiniteAmount,
    Money,
    Month,
    PositiveFinite,
    PositiveMoney,
    Ratio,
    Record,
    SchemaVersion,
)
from .market import MarketObservation
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
    savings_price_limit_eur: Money
    mortgage_price_limit_eur: Money
    maximum_price_eur: Money
    binding_constraint: Literal["savings", "mortgage", "both"]
    target_price_eur: PositiveMoney | None = None
    target_upfront_cash_eur: Money | None = None
    target_monthly_payment_eur: Money | None = None
    target_cash_shortfall_eur: Money | None = None
    target_payment_shortfall_eur: Money | None = None


class Indicator(Record):
    status: Literal["available", "missing", "unsupported"]
    value: Ratio | PositiveFinite | None = None
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


class RunResult(Record):
    schema_version: SchemaVersion
    resolved_scenario: Scenario
    dataset_release_id: Annotated[str, StringConstraints(strict=True, min_length=1)]
    model_version: Annotated[str, StringConstraints(strict=True, min_length=1)]
    code_version: Annotated[str, StringConstraints(strict=True, min_length=1)]
    results: tuple[LocationResult, ...]
