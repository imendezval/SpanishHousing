"""Compact views retain exact economics and the existing complete export format."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.application import evaluate_scenario
from spain_housing.application.export import full_run_json, run_json, summary_csv
from spain_housing.application.overview import detail_run, evaluate_overview, project_location
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.results import RunResult
from spain_housing.models.scenario import Scenario


@pytest.mark.parametrize("variant", ["baseline", "zero", "exhausted", "unsupported"])
def test_compact_detail_and_complete_exports_match(
    release_dir: Path, scenario: Scenario, variant: str
) -> None:
    data = scenario.model_dump(mode="json")
    if variant == "zero":
        data["retained_reserve_eur"] = 20000
    if variant == "exhausted":
        data["participants"][0]["net_annual_income"]["milestones"][0]["amount_eur"] = 0
        data["participants"][0]["starting_savings_eur"] = 0
    if variant == "unsupported":
        data["locations"].update(
            mode="fixed_saving",
            saving_location=dict(
                kind="explicit", location=dict(level="municipality", code="28079")
            ),
        )
    scenario = Scenario.model_validate(data)
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    locations = tuple(r.location for r in context.locations)
    arguments = dict(market_data=repo, context=context, mapped_locations=locations)
    full = evaluate_scenario(scenario, **arguments)
    overview = evaluate_overview(scenario, **arguments)
    assert overview.results == tuple(map(project_location, full.results))
    assert summary_csv(overview) == summary_csv(full)
    expected = (
        json.dumps(
            full.model_dump(mode="json"),
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        )
        + "\n"
    )
    assert run_json(full) == expected
    assert full_run_json(overview, market_data=repo, context=context) == expected.encode()
    for result in full.results:
        detail = detail_run(
            overview, result.buying_location.code, market_data=repo, context=context
        )
        assert detail.results == (result,)
    with pytest.raises(ValueError, match="outside"):
        detail_run(overview, "99999", market_data=repo, context=context)
    with pytest.raises(ValueError, match="complete"):
        run_json(overview)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        RunResult.model_validate_json(overview.model_dump_json())
    changed = overview.model_copy(update={"code_version": "changed"})
    with pytest.raises(ValueError, match="evidence changed"):
        full_run_json(changed, market_data=repo, context=context)


def test_membership_index_is_not_serialized_and_follows_copies(release_dir: Path) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    encoded = context.model_dump_json()
    assert context.municipality_codes == frozenset(r.location.code for r in context.locations)
    assert context.model_dump_json() == encoded
    copied = context.model_copy(update={"locations": context.locations[:1]})
    assert copied.municipality_codes == frozenset(r.location.code for r in copied.locations)
