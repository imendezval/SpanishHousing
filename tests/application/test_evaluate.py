from pathlib import Path

import pytest

from spain_housing.application import evaluate_location, evaluate_scenario
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.market import MarketLookup, MarketMetric, MarketQuery
from spain_housing.models.scenario import GeographicReference, Scenario

MADRID = GeographicReference(level="municipality", code="28079")
BARCELONA = GeographicReference(level="municipality", code="08019")
GETAFE = GeographicReference(level="municipality", code="28065")


class RecordingMarket:
    def __init__(self, repo: SnapshotMarketRepository):
        self.repo = repo
        self.queries: list[MarketQuery] = []

    def get(self, query: MarketQuery) -> MarketLookup:
        self.queries.append(query)
        return self.repo.get(query)


def test_independent_composed_reference(release_dir: Path, scenario: Scenario) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    run = evaluate_scenario(
        scenario, market_data=repo, context=repo.evaluation_context, mapped_locations=(MADRID,)
    )
    result = run.results[0]
    assert result.calculation_status == "available"
    assert result.savings.ending_savings_eur == 9900
    assert result.savings.usable_savings_eur == 4900
    assert len(result.prepared_budgets) == 3 and len(result.market_inputs) == 3
    purchase = result.purchase
    assert purchase.savings_price_limit_eur == pytest.approx(16333.333333333)
    assert purchase.mortgage_price_limit_eur == pytest.approx(225000)
    assert purchase.maximum_price_eur == pytest.approx(16333.333333333)
    assert purchase.binding_constraint == "savings"
    assert purchase.target_price_eur == 240000
    assert purchase.target_loan_eur == 192000
    assert purchase.target_upfront_cash_eur == pytest.approx(72000)
    assert purchase.target_monthly_payment_eur == 640
    assert purchase.target_cash_shortfall_eur == pytest.approx(67100)
    assert purchase.target_payment_shortfall_eur == pytest.approx(40)
    assert result.affordable_area_m2.value == pytest.approx(5.4444444444)
    assert result.target_affordability_ratio.value == pytest.approx(0.06805555555)
    assert "SYNTHETIC" in result.warnings[0]
    assert len(result.warnings) == len(set(result.warnings))
    assert run.evaluation_context.kind == "synthetic"
    assert "sha256-" in run.code_version and run.runtime_evidence.python_version
    assert type(run).model_validate_json(run.model_dump_json()) == run


@pytest.mark.parametrize("variant", ["mortgage", "zero", "unbounded", "above_one"])
def test_capacity_boundaries(release_dir: Path, scenario: Scenario, variant: str) -> None:
    data = scenario.model_dump(mode="json")
    if variant in ("mortgage", "above_one"):
        data["participants"][0]["starting_savings_eur"] = 200000
    if variant == "zero":
        data["retained_reserve_eur"] = 20000
    if variant == "unbounded":
        data["mortgage"]["financed_fraction"] = 1
        data["purchase_costs"]["allowance_fraction"] = 0
    if variant == "above_one":
        data["target_property"]["area_m2"] = 10
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    result = evaluate_location(
        Scenario.model_validate(data),
        saving_location=MADRID,
        buying_location=MADRID,
        market_data=repo,
        context=repo.evaluation_context,
    )
    assert result.calculation_status == "available"
    if variant == "mortgage":
        assert result.purchase.maximum_price_eur == pytest.approx(225000)
        assert result.purchase.binding_constraint == "mortgage"
    elif variant == "zero":
        assert result.savings.viability == "viable"
        assert result.purchase.maximum_price_eur == 0
        assert (
            result.affordable_area_m2.status == "available" and result.affordable_area_m2.value == 0
        )
    elif variant == "unbounded":
        assert result.purchase.savings_price_limit_eur is None
        assert result.purchase.maximum_price_eur == 180000
    else:
        assert result.target_affordability_ratio.value == pytest.approx(7.5)


@pytest.mark.parametrize("variant", ["missing", "stale", "condition", "strict_proxy"])
def test_buying_gap_preserves_capacity(release_dir: Path, scenario: Scenario, variant: str) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    data = scenario.model_dump(mode="json")
    if variant == "condition":
        data["target_property"]["condition"] = "new"
    if variant == "strict_proxy":
        data["living_stages"] = [dict(data["living_stages"][0], end_month_offset=3)]
        data["market_selection"]["allow_pooled_property_proxy"] = False
    context = repo.evaluation_context
    if variant == "stale":
        from datetime import date

        context = context.model_copy(
            update={
                "profiles": tuple(
                    p.model_copy(
                        update={"period_start": date(2024, 9, 1), "period_end": date(2024, 10, 1)}
                    )
                    if p.metric == MarketMetric.PURCHASE_PRICE_PER_M2
                    else p
                    for p in context.profiles
                )
            }
        )

    class Gap:
        def get(self, query: MarketQuery) -> MarketLookup:
            if variant == "missing" and query.metric == MarketMetric.PURCHASE_PRICE_PER_M2:
                return MarketLookup(status="missing", reason="sale cell absent")
            return repo.get(query)

    result = evaluate_location(
        Scenario.model_validate(data),
        saving_location=MADRID,
        buying_location=MADRID,
        market_data=Gap(),
        context=context,
    )
    assert result.calculation_status == "available" and result.purchase.maximum_price_eur > 0
    assert result.purchase.target_price_eur is None
    assert result.affordable_area_m2.status == (
        "missing" if variant in ("missing", "stale") else "unsupported"
    )
    assert len(result.market_inputs) == (1 if variant == "strict_proxy" else 2)


def test_saving_a_buying_b_and_deferred_mode(release_dir: Path, scenario: Scenario) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    market = RecordingMarket(repo)
    result = evaluate_location(
        scenario,
        saving_location=MADRID,
        buying_location=BARCELONA,
        market_data=market,
        context=repo.evaluation_context,
    )
    assert [q.location for q in market.queries] == [MADRID, MADRID, BARCELONA]
    assert result.purchase.target_price_eur == 200000
    assert result.savings.ending_savings_eur == 9900
    assert result.market_inputs[-1].observation.location == BARCELONA
    data = scenario.model_dump(mode="json")
    data["locations"].update(
        mode="fixed_saving", saving_location=dict(kind="explicit", location=MADRID.model_dump())
    )
    market.queries.clear()
    run = evaluate_scenario(
        Scenario.model_validate(data),
        market_data=market,
        context=repo.evaluation_context,
        mapped_locations=(BARCELONA, GETAFE),
    )
    assert not market.queries
    assert all(
        r.calculation_status == "unsupported" and r.saving_location == MADRID for r in run.results
    )


def test_exhaustion_precedes_purchase_and_gaps_ordered(
    release_dir: Path, scenario: Scenario
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    market = RecordingMarket(repo)
    data = scenario.model_dump(mode="json")
    data["participants"][0]["starting_savings_eur"] = 0
    data["participants"][0]["net_annual_income"] = dict(
        interpolation="step",
        milestones=[dict(month_offset=0, amount_eur=0), dict(month_offset=1, amount_eur=120000)],
    )
    run = evaluate_scenario(
        Scenario.model_validate(data),
        market_data=market,
        context=repo.evaluation_context,
        mapped_locations=(MADRID, GETAFE),
    )
    exhausted = run.results[1]
    assert exhausted.calculation_status == "unviable" and exhausted.purchase is None
    assert exhausted.savings.ending_savings_eur > 0 and len(exhausted.savings.monthly_path) == 3
    assert exhausted.affordable_area_m2.status == "unviable"
    assert all(q.metric != MarketMetric.PURCHASE_PRICE_PER_M2 for q in market.queries)
    gap = run.results[0]
    assert gap.buying_location == GETAFE and gap.calculation_status == "missing_input"
    assert gap.savings is None and not gap.prepared_budgets


def test_repeat_order_requests_and_offline(
    release_dir: Path, scenario: Scenario, monkeypatch: pytest.MonkeyPatch
) -> None:
    import socket

    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)

    def prohibited(*args, **kwargs):
        raise AssertionError("network/raw release refresh")

    monkeypatch.setattr(socket, "create_connection", prohibited)
    for file in release_dir.iterdir():
        file.unlink()
    context = repo.evaluation_context
    locations = (
        MADRID,
        BARCELONA,
        GETAFE,
        GeographicReference(level="municipality", code="99999"),
        GeographicReference(level="province", code="28"),
    )
    first = evaluate_scenario(
        scenario, market_data=repo, context=context, mapped_locations=locations
    )
    second = evaluate_scenario(
        scenario, market_data=repo, context=context, mapped_locations=tuple(reversed(locations))
    )
    assert first == second and first.model_dump_json() == second.model_dump_json()
    assert [r.calculation_status for r in first.results] == [
        "available",
        "missing_input",
        "available",
        "missing_input",
        "unsupported",
    ]
    for invalid in [(), (MADRID, MADRID)]:
        with pytest.raises(ValueError, match="nonempty and unique"):
            evaluate_scenario(scenario, market_data=repo, context=context, mapped_locations=invalid)
    data = scenario.model_dump(mode="json")
    data["market_selection"]["profile_ids"] = ["unknown"]
    with pytest.raises(ValueError, match="unknown profile"):
        evaluate_scenario(
            Scenario.model_validate(data),
            market_data=repo,
            context=context,
            mapped_locations=(MADRID,),
        )
