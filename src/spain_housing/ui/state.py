"""Session-owned draft/applied transitions and bounded economic result memo."""

import json
from collections import OrderedDict
from dataclasses import dataclass, field

from spain_housing.models.results import RunOverview, RunResult
from spain_housing.models.scenario import Scenario

from .contracts import Services
from .controls import Draft, draft_scenario, scenario_draft


def cache_key(scenario: Scenario, services: Services) -> str:
    return json.dumps(
        dict(
            scenario=scenario.model_dump(mode="json"),
            destinations=[loc.model_dump(mode="json") for loc in services.destinations],
            release=services.context.release_id,
            model=services.model_version,
            code=services.code_version,
            runtime=services.runtime.model_dump(mode="json"),
        ),
        sort_keys=True,
        allow_nan=False,
    )


@dataclass
class Session:
    draft: Draft
    epoch: int = 0
    applied: RunResult | RunOverview | None = None
    error: str | None = None
    pending_import: bool = False
    selected_code: str | None = None
    last_pick: str | None = None
    memo: OrderedDict[str, RunResult | RunOverview] = field(default_factory=OrderedDict)

    details: OrderedDict[str, RunResult] = field(default_factory=OrderedDict)
    full_export: bytes | None = None

    def clear_results(self) -> None:
        self.applied = None
        self.memo.clear()
        self.details.clear()
        self.full_export = None

    def detail(self, services: Services, code: str) -> RunResult:
        if not isinstance(self.applied, RunOverview) or services.detail is None:
            raise ValueError("overview detail service is unavailable")
        if code not in self.details:
            self.details[code] = services.detail(self.applied, code)
        self.details.move_to_end(code)
        while len(self.details) > 2:
            self.details.popitem(last=False)
        return self.details[code]

    def prepare_export(self, services: Services) -> None:
        if not isinstance(self.applied, RunOverview) or services.full_export is None:
            raise ValueError("overview export service is unavailable")
        if self.full_export is None:
            self.full_export = services.full_export(self.applied)

    def stage_import(self, payload: bytes, name: str, services: Services) -> bool:
        try:
            scenario = services.decode_scenario(payload, name)
        except (ValueError, UnicodeError) as exc:
            self.error = str(exc)
            return False
        self.draft = scenario_draft(scenario)
        self.epoch += 1
        self.pending_import = True
        self.error = None
        return True

    def apply(self, draft: Draft, services: Services) -> bool:
        self.draft = draft
        self.epoch += 1
        try:
            scenario = draft_scenario(draft)
            key = cache_key(scenario, services)
            run = self.memo.get(key)
            if run is None:
                run = services.evaluate(scenario, services.destinations)
            if (
                run.dataset_release_id != services.context.release_id
                or run.model_version != services.model_version
                or run.code_version != services.code_version
                or run.runtime_evidence != services.runtime
                or run.resolved_scenario != scenario
                or tuple(r.buying_location for r in run.results) != services.destinations
            ):
                raise ValueError("evaluation service identity does not agree with requested inputs")
            self.memo[key] = run
            self.memo.move_to_end(key)
            while len(self.memo) > (2 if len(services.destinations) > 250 else 32):
                self.memo.popitem(last=False)
        except (ValueError, OSError) as exc:
            self.error = str(exc)
            return False
        if self.applied is not run:
            self.details.clear()
            self.full_export = None
        self.applied = run
        self.error = None
        self.pending_import = False
        if self.selected_code not in services.inspection_codes:
            self.selected_code = services.destinations[0].code
        return True
