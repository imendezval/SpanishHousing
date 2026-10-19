"""Small immutable injected boundary; no concrete provider or server paths."""

from collections.abc import Callable
from dataclasses import dataclass

from spain_housing.models.coverage import ReleaseCoverageReport
from spain_housing.models.dataset import BoundaryCollection
from spain_housing.models.evaluation import EvaluationContext, RuntimeEvidence
from spain_housing.models.geography import MapGeography
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import GeographicReference, Scenario


@dataclass(frozen=True)
class Services:
    evaluate: Callable[[Scenario, tuple[GeographicReference, ...]], RunResult]
    decode_scenario: Callable[[bytes, str], Scenario]
    encode_scenario: Callable[[Scenario], str]
    context: EvaluationContext
    boundaries: BoundaryCollection | None
    model_version: str
    code_version: str
    runtime: RuntimeEvidence
    coverage: ReleaseCoverageReport
    map_geography: MapGeography | None = None

    @property
    def destinations(self) -> tuple[GeographicReference, ...]:
        return tuple(
            sorted((r.location for r in self.context.locations), key=lambda r: (r.level, r.code))
        )

    @property
    def inspection_codes(self) -> tuple[str, ...]:
        return (
            tuple(sorted(m.code for m in self.map_geography.municipalities))
            if self.map_geography
            else tuple(loc.code for loc in self.destinations)
        )
