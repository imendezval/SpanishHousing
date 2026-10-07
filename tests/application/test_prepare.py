from datetime import date
from pathlib import Path

import pytest

from spain_housing.application.prepare import (
    PreparationIssue,
    PreparedSavings,
    prepare_savings,
    purchase_finances,
    sample_amount,
)
from spain_housing.finance import simulate_savings
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.scenario import AmountPath, GeographicReference, Scenario

MADRID = GeographicReference(level="municipality", code="28079")


@pytest.mark.parametrize("code", ["28065", "99999"])
def test_all_discovered_issues_unsupported_precedes_missing(
    release_dir: Path, scenario: Scenario, code: str
) -> None:
    data = scenario.model_dump(mode="json")
    data["living_stages"][1].update(rental_area_m2=None, bedrooms=2)
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    issue = prepare_savings(
        Scenario.model_validate(data),
        saving_location=GeographicReference(level="municipality", code=code),
        market_data=repo,
        context=repo.evaluation_context,
    )
    assert isinstance(issue, PreparationIssue) and issue.status == "unsupported"
    assert {part.status for part in issue.issues} == {"missing", "unsupported"}
    assert len(issue.issues) == 2


@pytest.mark.parametrize(
    "kind,expected",
    [("linear", [100, 150, 200, 150, 100, 100]), ("step", [100, 100, 200, 200, 100, 100])],
)
def test_sampler_milestones_plateau(kind: str, expected: list[float]) -> None:
    path = AmountPath.model_validate(
        dict(
            interpolation=kind,
            milestones=[
                dict(month_offset=0, amount_eur=100),
                dict(month_offset=2, amount_eur=200),
                dict(month_offset=4, amount_eur=100),
            ],
        )
    )
    assert [sample_amount(path, t) for t in range(6)] == expected
    for offset in [-1, True, 0.5]:
        with pytest.raises(ValueError):
            sample_amount(path, offset)


def test_prepared_composed_case(release_dir: Path, scenario: Scenario) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    result = prepare_savings(
        scenario, saving_location=MADRID, market_data=repo, context=repo.evaluation_context
    )
    assert isinstance(result, PreparedSavings)
    assert [b.month for b in result.budgets] == [
        date(2026, 10, 1),
        date(2026, 11, 1),
        date(2026, 12, 1),
    ]
    assert [b.rent_eur for b in result.budgets] == [300, 300, 500]
    assert len(result.market_inputs) == 2
    saved = simulate_savings(
        result.budgets,
        starting_savings_eur=result.starting_savings_eur,
        retained_reserve_eur=scenario.retained_reserve_eur,
    )
    assert [point.contribution_eur for point in saved.monthly_path] == [700, 700, 500]
    assert saved.ending_savings_eur == 9900 and saved.usable_savings_eur == 4900
    finances = purchase_finances(scenario)
    assert finances.purchase_month == date(2027, 1, 1)
    assert finances.borrower_monthly_net_income_eur == 2000


def test_participant_sets_and_expense_milestone(release_dir: Path, scenario: Scenario) -> None:
    data = scenario.model_dump(mode="json")
    saver = dict(data["participants"][0], participant_id="saver", starting_savings_eur=1000)
    borrower = dict(data["participants"][0], participant_id="borrower", starting_savings_eur=1e6)
    data["participants"] += [saver, borrower]
    data["saver_ids"] = ["buyer", "saver"]
    data["borrower_ids"] = ["borrower"]
    data["household_nonhousing_expenses"]["milestones"] += [dict(month_offset=2, amount_eur=1000)]
    updated = Scenario.model_validate(data)
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    result = prepare_savings(
        updated, saving_location=MADRID, market_data=repo, context=repo.evaluation_context
    )
    assert isinstance(result, PreparedSavings)
    assert result.starting_savings_eur == 9000
    assert [b.net_income_eur for b in result.budgets] == [4000] * 3
    assert [b.rent_eur for b in result.budgets] == [300, 300, 500]
    assert [b.nonhousing_expenses_eur for b in result.budgets] == [900, 900, 1000]
    assert result.budgets[0].other_debt_eur == 200
    assert purchase_finances(updated).borrower_monthly_net_income_eur == 2000
    assert purchase_finances(updated).borrower_monthly_other_debt_eur == 100


def test_income_after_purchase_and_debt_at_purchase(scenario: Scenario) -> None:
    data = scenario.model_dump(mode="json")
    data["saving_months"] = 12
    data["living_stages"] = [dict(data["living_stages"][0], end_month_offset=12)]
    data["participants"][0]["net_annual_income"]["milestones"] += [
        dict(month_offset=24, amount_eur=36000)
    ]
    data["participants"][0]["monthly_debt"]["milestones"] += [dict(month_offset=12, amount_eur=0)]
    result = purchase_finances(Scenario.model_validate(data))
    assert result.borrower_monthly_net_income_eur == 2500
    assert result.borrower_monthly_other_debt_eur == 0


@pytest.mark.parametrize(
    "change", ["missing_later", "area", "room_selector", "bedroom", "per_month", "earlier"]
)
def test_incomplete_inputs_no_budgets(release_dir: Path, scenario: Scenario, change: str) -> None:
    data = scenario.model_dump(mode="json")
    if change == "missing_later":
        data["living_stages"].reverse()
        data["living_stages"][0].update(start_month_offset=0, end_month_offset=1)
        data["living_stages"][1].update(start_month_offset=1, end_month_offset=3)
    elif change == "area":
        data["living_stages"][1].update(rental_area_m2=None, bedrooms=2)
    elif change == "room_selector":
        data["living_stages"][0]["bedrooms"] = 1
    elif change == "bedroom":
        data["living_stages"][1]["bedrooms"] = 2
    elif change == "per_month":
        data["market_selection"]["whole_home_rent_source"] = "per_month"
    else:
        data["start_month"] = "2026-09-01"
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    location = (
        GeographicReference(level="municipality", code="28065")
        if change == "missing_later"
        else MADRID
    )
    result = prepare_savings(
        Scenario.model_validate(data),
        saving_location=location,
        market_data=repo,
        context=repo.evaluation_context,
    )
    assert isinstance(result, PreparationIssue)
    assert not hasattr(result, "budgets")
    assert result.status == ("missing_input" if change == "missing_later" else "unsupported")


def test_exhausted_then_recovered_is_retained(release_dir: Path, scenario: Scenario) -> None:
    data = scenario.model_dump(mode="json")
    data["participants"][0]["starting_savings_eur"] = 0
    data["participants"][0]["net_annual_income"] = dict(
        interpolation="step",
        milestones=[dict(month_offset=0, amount_eur=0), dict(month_offset=1, amount_eur=120000)],
    )
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    result = prepare_savings(
        Scenario.model_validate(data),
        saving_location=MADRID,
        market_data=repo,
        context=repo.evaluation_context,
    )
    assert isinstance(result, PreparedSavings)
    saved = simulate_savings(
        result.budgets, starting_savings_eur=result.starting_savings_eur, retained_reserve_eur=5000
    )
    assert saved.viability == "funds_exhausted" and saved.ending_savings_eur > 0


def test_later_start_projects_from_reference_not_offset(
    release_dir: Path, scenario: Scenario
) -> None:
    data = scenario.model_dump(mode="json")
    data["start_month"] = "2027-06-01"
    data["market_policy"].update(kind="growth", annual_rent_growth_fraction=0.21)
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    result = prepare_savings(
        Scenario.model_validate(data),
        saving_location=MADRID,
        market_data=repo,
        context=repo.evaluation_context,
    )
    assert isinstance(result, PreparedSavings)
    assert result.budgets[0].rent_eur == pytest.approx(363)
    assert result.market_inputs[0].value_at_base == pytest.approx(300 * 1.21 ** (4 / 12))
    assert result.budgets[0].net_income_eur == 2000


def test_direct_monthly_rent_and_all_flat_no_room_dependency(
    release_dir: Path, scenario: Scenario
) -> None:
    from spain_housing.models.market import MarketLookup, MarketMetric, MarketQuery, MarketUnit

    data = scenario.model_dump(mode="json")
    data["living_stages"] = [
        dict(data["living_stages"][1], start_month_offset=0, end_month_offset=3)
    ]
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    getafe = GeographicReference(level="municipality", code="28065")
    all_flat = Scenario.model_validate(data)
    result = prepare_savings(
        all_flat, saving_location=getafe, market_data=repo, context=repo.evaluation_context
    )
    assert isinstance(result, PreparedSavings)
    assert result.budgets[0].rent_eur == pytest.approx(8.3 * 80 * 0.5)
    data["market_selection"]["whole_home_rent_source"] = "per_month"
    direct = Scenario.model_validate(data)
    original = next(
        p
        for p in repo.evaluation_context.profiles
        if p.metric == MarketMetric.WHOLE_HOME_RENT_PER_M2_MONTH
    )
    profile = original.model_copy(update={"metric": MarketMetric.WHOLE_HOME_RENT_PER_MONTH})
    context = repo.evaluation_context.model_copy(update={"profiles": (profile,)})

    class Monthly:
        def get(self, query: MarketQuery) -> MarketLookup:
            assert query.metric == MarketMetric.WHOLE_HOME_RENT_PER_MONTH
            observation = repo.get(query.model_copy(update={"metric": original.metric})).observation
            assert observation
            return MarketLookup(
                status="available",
                observation=observation.model_copy(
                    update={
                        "metric": profile.metric,
                        "unit": MarketUnit.EUR_PER_MONTH,
                        "value": 980.0,
                    }
                ),
            )

    result = prepare_savings(direct, saving_location=getafe, market_data=Monthly(), context=context)
    assert isinstance(result, PreparedSavings)
    assert [b.rent_eur for b in result.budgets] == [490] * 3
