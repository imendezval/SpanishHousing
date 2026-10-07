from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from spain_housing.config import load_scenario, parse_mapping
from spain_housing.launcher import _snapshot, compose
from spain_housing.ui.controls import draft_scenario, scenario_draft
from spain_housing.ui.state import Session, cache_key

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "name", ["room_only", "phase4_room_demo", "phase4_staged_growth_demo", "joint_saving"]
)
def test_lossless_roundtrip(name: str) -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / f"configs/scenarios/{name}.yaml"
    )
    draft = scenario_draft(scenario)
    assert draft_scenario(draft) == scenario
    original = deepcopy(draft)
    draft_scenario(draft)
    assert draft == original


def test_parser_and_import_atomicity(release_dir: Path) -> None:
    initial, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release_dir,
        allow_synthetic=True,
    )
    session = Session(scenario_draft(initial))
    assert session.apply(session.draft, services)
    applied = session.applied
    before = deepcopy(session.draft)
    for payload, name in [
        (b'{"saving_months":1,"saving_months":2}', "a.json"),
        (b"!!python/object:builtins.object {}", "a.yaml"),
        (b"null", "a.json"),
        (b"[]", "a.json"),
        (b"{}", "a.exe"),
        (b"\xff", "a.yaml"),
        (b'"' * (1024 * 1024 + 1), "a.json"),
        (b'{"market_selection":null}', "a.json"),
    ]:
        assert not session.stage_import(payload, name, services)
        assert session.draft == before and session.applied == applied
    other = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/phase4_staged_growth_demo.yaml"
    )
    assert session.stage_import(
        services.encode_scenario(other).encode(), "../ignored/path.json", services
    )
    assert session.pending_import and session.applied == applied
    assert draft_scenario(session.draft) == other
    assert session.apply(session.draft, services) and not session.pending_import
    assert session.applied.resolved_scenario == other
    with pytest.raises(ValueError):
        parse_mapping('{"a":{"b":1,"b":2}}', ".json")


def test_resource_key_memo_and_failure_preserve_applied(release_dir: Path) -> None:
    initial, services = compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release_dir,
        allow_synthetic=True,
    )
    calls = []

    def counted(scenario, locations):
        calls.append(scenario)
        return services.evaluate(scenario, locations)

    counted_services = replace(services, evaluate=counted)
    session = Session(scenario_draft(initial))
    assert session.apply(session.draft, counted_services)
    assert session.apply(session.draft, counted_services) and len(calls) == 1
    invalid = deepcopy(session.draft)
    invalid["base"]["saving_months"] = 13
    assert not session.apply(invalid, counted_services)
    assert session.applied.resolved_scenario == initial and session.draft == invalid
    original_key = cache_key(initial, services)
    for changed in [
        replace(services, code_version="new"),
        replace(services, model_version="new"),
        replace(services, context=services.context.model_copy(update={"release_id": "new"})),
        replace(services, runtime=services.runtime.model_copy(update={"python_version": "new"})),
        replace(
            services,
            context=services.context.model_copy(
                update={"locations": services.context.locations[:1]}
            ),
        ),
    ]:
        assert cache_key(initial, changed) != original_key
    second = Session(scenario_draft(initial))
    assert second.apply(second.draft, counted_services) and len(calls) == 2
    assert session.memo is not second.memo
    bad_service = replace(services, code_version="contradictory")
    assert not second.apply(second.draft, bad_service)
    assert "identity" in second.error and second.applied.resolved_scenario == initial
    assert _snapshot.cache_info().maxsize == 4
    before = _snapshot.cache_info().hits
    compose(
        ROOT / "configs/defaults.yaml",
        ROOT / "configs/scenarios/phase4_room_demo.yaml",
        release_dir,
        allow_synthetic=True,
    )
    assert _snapshot.cache_info().hits == before + 1
    with pytest.raises(ValueError, match="opt-in"):
        compose(
            ROOT / "configs/defaults.yaml",
            ROOT / "configs/scenarios/phase4_room_demo.yaml",
            release_dir,
        )


def test_participant_removal_and_future_paths_retained() -> None:
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/phase4_staged_growth_demo.yaml"
    )
    draft = scenario_draft(scenario)
    assert any(point["month_offset"] > scenario.saving_months for point in draft["income"])
    draft["participants"].pop()
    with pytest.raises(ValueError, match="unknown participant"):
        draft_scenario(draft)
