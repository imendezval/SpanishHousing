from datetime import date
from pathlib import Path

import pytest

from spain_housing.markets.projections import project_value
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.markets.selection import (
    MarketIssue,
    resolve_input,
    select_reference,
    validate_selection,
)
from spain_housing.models.market import MarketLookup, MarketMetric, MarketQuery, MarketSegment
from spain_housing.models.scenario import (
    GeographicReference,
    MarketPolicy,
    MarketSelectionPolicy,
    Scenario,
)

SALE = MarketMetric.PURCHASE_PRICE_PER_M2
ROOM = MarketMetric.ROOM_RENT_PER_MONTH
MADRID = GeographicReference(level="municipality", code="28079")


@pytest.mark.parametrize(
    "change", [{"source_id": "synthetic:other"}, {"basis": "valuation"}, {"statistic": "mean"}]
)
def test_incompatible_series_never_selected_by_newer_date(
    release_dir: Path, scenario: Scenario, change: dict
) -> None:
    context = SnapshotMarketRepository.from_release(
        release_dir, allow_synthetic=True
    ).evaluation_context
    latest = next(p for p in context.profiles if p.metric == SALE)
    other = latest.model_copy(
        update={
            "profile_id": "older",
            "period_start": date(2026, 8, 1),
            "period_end": date(2026, 9, 1),
            **change,
        }
    )
    context = context.model_copy(update={"profiles": (*context.profiles, other)})
    result = select_reference(scenario, context, SALE, MarketSegment(property_type="flat"))
    assert isinstance(result, MarketIssue) and result.status == "unsupported"


def test_latest_gap_has_no_older_fallback(release_dir: Path, scenario: Scenario) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    latest = next(p for p in context.profiles if p.metric == SALE)
    older = latest.model_copy(
        update={
            "profile_id": "older",
            "period_start": date(2026, 8, 1),
            "period_end": date(2026, 9, 1),
        }
    )
    context = context.model_copy(update={"profiles": (*context.profiles, older)})
    queries = []

    class Gap:
        def get(self, query: MarketQuery) -> MarketLookup:
            queries.append(query)
            assert query.period_end == latest.period_end
            return MarketLookup(
                status="missing", reason="latest gap; older data would be available"
            )

    result = resolve_input(
        scenario,
        context=context,
        market_data=Gap(),
        location=MADRID,
        metric=SALE,
        segment=MarketSegment(property_type="flat"),
        role="purchase_price",
    )
    assert isinstance(result, MarketIssue) and result.status == "missing" and len(queries) == 1


class RecordingMarket:
    def __init__(self, repo: SnapshotMarketRepository):
        self.repo = repo
        self.queries: list[MarketQuery] = []

    def get(self, query: MarketQuery) -> MarketLookup:
        self.queries.append(query)
        return self.repo.get(query)


def test_exact_periods_proxy_and_growth(release_dir: Path, scenario: Scenario) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    market = RecordingMarket(repo)
    uses = []
    for metric, property_type, role in [
        (SALE, "flat", "purchase_price"),
        (ROOM, "room", "room_rent"),
    ]:
        use = resolve_input(
            scenario,
            context=repo.evaluation_context,
            market_data=market,
            location=MADRID,
            metric=metric,
            segment=MarketSegment(property_type=property_type),
            role=role,
        )
        assert not isinstance(use, MarketIssue)
        uses.append(use)
    assert [(q.period_start, q.period_end) for q in market.queries] == [
        (date(2026, 9, 1), date(2026, 10, 1)),
        (date(2026, 4, 1), date(2026, 7, 1)),
    ]
    assert uses[0].proxy_for_property_type == "flat" and uses[1].reference_anchor_month == date(
        2026, 6, 1
    )
    room = uses[1].observation
    policy = MarketPolicy(
        kind="growth",
        base_month="2026-10-01",
        annual_rent_growth_fraction=0.21,
        annual_purchase_growth_fraction=0.44,
    )
    assert project_value(room, policy, date(2027, 6, 1)) == pytest.approx(363)
    assert project_value(uses[0].observation, policy, date(2027, 9, 1)) == pytest.approx(4320)
    assert project_value(room, scenario.market_policy, date(2030, 1, 1)) == 300
    decline = policy.model_copy(update={"annual_rent_growth_fraction": -0.19})
    assert project_value(room, decline, date(2027, 6, 1)) == pytest.approx(243)
    for rate, year in [(1e308, 2030), (-0.9999999999999999, 2100)]:
        extreme = policy.model_copy(update={"annual_rent_growth_fraction": rate})
        with pytest.raises(ValueError, match="projection"):
            project_value(room, extreme, date(year, 1, 1))


def test_selection_scope_age_and_ambiguity(release_dir: Path, scenario: Scenario) -> None:
    context = SnapshotMarketRepository.from_release(
        release_dir, allow_synthetic=True
    ).evaluation_context
    segment = MarketSegment(property_type="flat")
    strict = scenario.model_copy(update={"market_selection": MarketSelectionPolicy()})
    assert select_reference(strict, context, SALE, segment).status == "unsupported"
    bedroom = select_reference(
        scenario, context, SALE, MarketSegment(property_type="flat", bedrooms=2)
    )
    assert isinstance(bedroom, MarketIssue) and bedroom.status == "unsupported"
    stale = scenario.model_copy(
        update={"market_selection": MarketSelectionPolicy(maximum_reference_age_months=2)}
    )
    assert (
        select_reference(stale, context, ROOM, MarketSegment(property_type="room")).status
        == "missing"
    )
    future = scenario.model_copy(
        update={
            "market_policy": scenario.market_policy.model_copy(
                update={"base_month": date(2026, 6, 1)}
            )
        }
    )
    assert (
        select_reference(future, context, ROOM, MarketSegment(property_type="room")).status
        == "missing"
    )
    original = next(p for p in context.profiles if p.metric == SALE)
    other = original.model_copy(
        update={
            "profile_id": "other",
            "source_id": "synthetic:other",
            "period_end": date(2026, 9, 1),
            "period_start": date(2026, 8, 1),
        }
    )
    ambiguous = context.model_copy(update={"profiles": context.profiles + (other,)})
    assert select_reference(scenario, ambiguous, SALE, segment).status == "unsupported"
    chosen = scenario.model_copy(
        update={
            "market_selection": MarketSelectionPolicy(
                profile_ids=(original.profile_id,), allow_pooled_property_proxy=True
            )
        }
    )
    assert select_reference(chosen, ambiguous, SALE, segment).profile == original
    validate_selection(chosen.market_selection, ambiguous)
    for ids in [("unknown",), (original.profile_id, "other")]:
        with pytest.raises(ValueError):
            validate_selection(MarketSelectionPolicy(profile_ids=ids), ambiguous)
    tied = other.model_copy(
        update={
            "source_id": original.source_id,
            "period_start": original.period_start,
            "period_end": original.period_end,
        }
    )
    assert (
        select_reference(
            scenario,
            context.model_copy(update={"profiles": context.profiles + (tied,)}),
            SALE,
            segment,
        ).status
        == "unsupported"
    )


def test_exact_preferred_no_cell_fallback_and_bad_provider(
    release_dir: Path, scenario: Scenario
) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    original = next(p for p in context.profiles if p.metric == SALE)
    exact = original.model_copy(
        update={"profile_id": "exact", "segment": MarketSegment(property_type="flat")}
    )
    context = context.model_copy(update={"profiles": context.profiles + (exact,)})

    class Gap:
        def get(self, query: MarketQuery) -> MarketLookup:
            assert query.segment.property_type == "flat"
            return MarketLookup(status="missing", reason="selected exact cell missing")

    use = resolve_input(
        scenario,
        context=context,
        market_data=Gap(),
        location=MADRID,
        metric=SALE,
        segment=MarketSegment(property_type="flat"),
        role="purchase_price",
    )
    assert isinstance(use, MarketIssue) and use.status == "missing"

    class Wrong:
        def get(self, query: MarketQuery) -> MarketLookup:
            result = repo.get(query.model_copy(update={"segment": original.segment}))
            assert result.observation
            return result

    with pytest.raises(ValueError, match="disagrees"):
        resolve_input(
            scenario,
            context=context,
            market_data=Wrong(),
            location=MADRID,
            metric=SALE,
            segment=MarketSegment(property_type="flat"),
            role="purchase_price",
        )
