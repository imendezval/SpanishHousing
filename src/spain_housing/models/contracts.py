"""Minimal replaceable data and purchase-cost boundaries."""

from typing import Protocol

from .base import Money, Month, Record
from .market import MarketLookup, MarketQuery
from .scenario import GeographicReference, TargetProperty


class MarketData(Protocol):
    def get(self, query: MarketQuery) -> MarketLookup: ...


class PurchaseContext(Record):
    buying_location: GeographicReference
    purchase_month: Month
    target_property: TargetProperty


class PurchaseCostBreakdown(Record):
    purchase_cost_eur: Money
    mortgage_formalisation_cost_eur: Money


class PurchaseCostPolicy(Protocol):
    def costs(self, price_eur: Money, context: PurchaseContext) -> PurchaseCostBreakdown: ...
