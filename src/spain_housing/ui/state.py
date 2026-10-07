"""Session-owned draft/applied transitions and bounded economic result memo."""

import json
from collections import OrderedDict
from dataclasses import dataclass, field

from spain_housing.models.results import RunResult
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
    applied: RunResult | None = None
    error: str | None = None
    pending_import: bool = False
    selected_code: str | None = None
    last_pick: str | None = None
    memo: OrderedDict[str, RunResult] = field(default_factory=OrderedDict)

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
            while len(self.memo) > 32:
                self.memo.popitem(last=False)
        except (ValueError, OSError) as exc:
            self.error = str(exc)
            return False
        self.applied = run
        self.error = None
        self.pending_import = False
        if self.selected_code not in {loc.code for loc in services.destinations}:
            self.selected_code = services.destinations[0].code
        return True
