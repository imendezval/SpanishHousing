"""Pure market projection from the last covered month, never a new observation."""

import math
from datetime import date

from spain_housing.models.base import add_months
from spain_housing.models.market import MarketMetric, MarketObservation
from spain_housing.models.scenario import MarketPolicy


def month_distance(start: date, end: date) -> int:
    return (end.year - start.year) * 12 + end.month - start.month


def growth_fraction(observation: MarketObservation, policy: MarketPolicy) -> float:
    return (
        policy.annual_purchase_growth_fraction
        if observation.metric == MarketMetric.PURCHASE_PRICE_PER_M2
        else policy.annual_rent_growth_fraction
    )


def project_value(observation: MarketObservation, policy: MarketPolicy, month: date) -> float:
    """Compound effective annual growth once from the reference anchor."""
    rate = growth_fraction(observation, policy)
    if policy.kind == "frozen" or rate == 0:
        return observation.value
    anchor = add_months(observation.period_end, -1)
    try:
        value = observation.value * math.exp(month_distance(anchor, month) / 12 * math.log1p(rate))
    except OverflowError as exc:
        raise ValueError("market projection overflow") from exc
    if not math.isfinite(value) or value <= 0:
        raise ValueError("market projection must remain positive and finite")
    return value
