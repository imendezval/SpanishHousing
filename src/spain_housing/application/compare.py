"""Capacity-to-market indicators; finance owns capacity and shortfalls."""

from spain_housing.models.evaluation import MarketInputUse
from spain_housing.models.results import Indicator, PurchaseResult


def compare_capacity(
    purchase: PurchaseResult, price_per_m2: float, use: MarketInputUse
) -> tuple[Indicator, Indicator]:
    assert purchase.target_price_eur is not None
    return (
        Indicator(
            status="available",
            value=purchase.maximum_price_eur / price_per_m2,
            observations=(use.observation,),
        ),
        Indicator(
            status="available",
            value=purchase.maximum_price_eur / purchase.target_price_eur,
            observations=(use.observation,),
        ),
    )
