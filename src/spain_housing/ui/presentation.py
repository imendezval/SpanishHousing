"""One returned-result projection feeds map, table and tooltip; no economics."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from spain_housing.models.results import LocationResult


class Metric(StrEnum):
    PRICE = "Maximum purchase price"
    AREA = "Affordable area"
    RATIO = "Target affordability"


@dataclass(frozen=True)
class MetricStyle:
    unit: str
    edges: tuple[float, ...]


STYLES = {
    Metric.PRICE: MetricStyle("EUR", (0, 50000, 100000, 150000, 200000, 300000, 500000)),
    Metric.AREA: MetricStyle("m²", (0, 20, 40, 60, 80, 100, 150)),
    Metric.RATIO: MetricStyle("× target price", (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5)),
}
PALETTE = (
    (68, 1, 84),
    (68, 57, 131),
    (49, 104, 142),
    (33, 145, 140),
    (53, 183, 121),
    (144, 215, 67),
    (253, 231, 37),
)
STATUS_COLOURS = {
    "missing": (145, 145, 145),
    "unsupported": (230, 126, 34),
    "unviable": (190, 90, 160),
    "outside_coverage": (210, 210, 210),
    "not_evaluated": (195, 195, 210),
}


@dataclass(frozen=True)
class DisplayValue:
    status: Literal[
        "available", "missing", "unsupported", "unviable", "outside_coverage", "not_evaluated"
    ]
    value: float | None
    reason: str | None


def metric_value(result: LocationResult, metric: Metric) -> DisplayValue:
    if metric == Metric.PRICE:
        if result.calculation_status == "available" and result.purchase is not None:
            return DisplayValue("available", result.purchase.maximum_price_eur, None)
        status = (
            "missing" if result.calculation_status == "missing_input" else result.calculation_status
        )
        if status == "available":
            raise ValueError("available financial result is missing capacity")
        return DisplayValue(status, None, result.explanation)
    indicator = (
        result.affordable_area_m2 if metric == Metric.AREA else result.target_affordability_ratio
    )
    return DisplayValue(indicator.status, indicator.value, indicator.reason)


def colour(display: DisplayValue, metric: Metric) -> tuple[int, int, int]:
    if display.status != "available":
        return STATUS_COLOURS[display.status]
    assert display.value is not None
    index = max(i for i, edge in enumerate(STYLES[metric].edges) if display.value >= edge)
    return PALETTE[index]


def formatted(value: float | None, unit: str = "EUR") -> str:
    return "Unavailable" if value is None else f"{value:,.2f} {unit}"


def legend(
    metric: Metric, *, geographic: bool = False
) -> tuple[tuple[str, tuple[int, int, int]], ...]:
    edges = STYLES[metric].edges
    rows = []
    for i, edge in enumerate(edges):
        label = f"[{edge:g}, {edges[i + 1]:g})" if i + 1 < len(edges) else f"[{edge:g}, ∞)"
        rows.append((f"{label} {STYLES[metric].unit}", PALETTE[i]))
    return tuple(rows) + tuple(
        (status.replace("_", " ").title(), rgb)
        for status, rgb in STATUS_COLOURS.items()
        if geographic or status not in ("outside_coverage", "not_evaluated")
    )
