from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from conftest import FIXTURES
from pydantic import ValidationError

from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.contracts import MarketData
from spain_housing.models.market import MarketQuery, MarketSegment
from spain_housing.storage.release import load_release, strict_json, write_release


def sale_query(**changes: object) -> MarketQuery:
    original = strict_json((FIXTURES / "query_sale.json").read_bytes())
    return MarketQuery.model_validate(original | changes)


@pytest.mark.parametrize(
    "change,status,reason",
    [
        ({}, "available", None),
        ({"period_start": "2026-08-01"}, "missing", "exact interval"),
        ({"period_end": "2026-11-01"}, "missing", "exact interval"),
        ({"location": {"level": "municipality", "code": "99999"}}, "missing", "outside"),
        ({"location": {"level": "province", "code": "28"}}, "unsupported", "geographic level"),
        ({"metric": "whole_home_rent_per_month"}, "unsupported", "metric"),
        ({"segment": {"property_type": "flat"}}, "unsupported", "segment"),
        ({"segment": {"property_type": "house"}}, "unsupported", "segment"),
        ({"segment": {"property_type": "pooled", "bedrooms": 2}}, "unsupported", "segment"),
        ({"segment": {"property_type": "pooled", "size_band": "80-100"}}, "unsupported", "segment"),
        (
            {"segment": {"property_type": "pooled", "rental_contract_category": "permanent"}},
            "unsupported",
            "segment",
        ),
        ({"segment": None}, "available", None),
    ],
)
def test_exact_period_segment_and_capability_statuses(
    release_dir: Path, change: dict, status: str, reason: str | None
) -> None:
    repository: MarketData = SnapshotMarketRepository.from_release(
        release_dir, allow_synthetic=True
    )
    lookup = repository.get(sale_query(**change))
    assert lookup.status == status
    if reason is not None:
        assert reason in lookup.reason
        assert lookup.observation is None
    else:
        assert lookup.observation.value == 3_000
        assert lookup.observation.evidence_kind == "synthetic"


def test_room_quarter_is_never_reinterpreted_as_september(release_dir: Path) -> None:
    repository = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    query = MarketQuery.model_validate(
        strict_json((FIXTURES / "query_missing_room.json").read_bytes())
    )
    missing = repository.get(query)
    assert missing.status == "missing"
    madrid = query.model_copy(update={"location": sale_query().location})
    available = repository.get(madrid)
    assert available.status == "available"
    assert available.observation.value == 300
    september = MarketQuery.model_validate(
        madrid.model_dump() | {"period_start": "2026-09-01", "period_end": "2026-10-01"}
    )
    assert repository.get(september).status == "missing"
    month_in_quarter = MarketQuery.model_validate(
        madrid.model_dump() | {"period_end": "2026-05-01"}
    )
    assert repository.get(month_in_quarter).status == "missing"


def test_repository_is_offline_immutable_and_needs_no_query_time_files(
    release_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_network(*args: object, **kwargs: object) -> None:
        pytest.fail("repository must not access the network")

    monkeypatch.setattr("socket.create_connection", no_network)
    monkeypatch.setattr("urllib.request.urlopen", no_network)
    repository = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    expected = next(
        row.observation
        for row in load_release(release_dir, allow_synthetic=True).observations
        if row.observation.location.code == "28079"
        and row.observation.metric == "purchase_price_per_m2"
    )
    for path in release_dir.iterdir():
        path.unlink()
    lookup = repository.get(sale_query())
    assert lookup.observation == expected
    with pytest.raises(ValidationError, match="frozen"):
        lookup.observation.value = 1
    with pytest.raises(FrozenInstanceError):
        repository.manifest = None
    assert repository.get(sale_query()).observation == expected


def test_underspecified_query_is_ambiguous_not_arbitrary(release_dir: Path, tmp_path: Path) -> None:
    bundle = load_release(release_dir, allow_synthetic=True)
    selected = next(
        row
        for row in bundle.observations
        if row.observation.location.code == "28079"
        and row.observation.metric == "purchase_price_per_m2"
    )
    segment = MarketSegment(property_type="pooled", size_band="large")
    alternate = selected.model_copy(
        update={
            "observation": selected.observation.model_copy(
                update={"segment": segment, "value": 3_100.0}
            )
        }
    )
    profile = next(p for p in bundle.manifest.recipe.profiles if p.profile_id == "sale").model_copy(
        update={"profile_id": "sale-large", "segment": segment}
    )
    recipe = bundle.manifest.recipe.model_copy(
        update={"profiles": bundle.manifest.recipe.profiles + (profile,)}
    )
    path = write_release(
        tmp_path / "ambiguous",
        recipe=recipe,
        observations=bundle.observations + (alternate,),
        boundaries=bundle.boundaries,
        allow_synthetic=True,
    )
    repository = SnapshotMarketRepository.from_release(path, allow_synthetic=True)
    result = repository.get(sale_query(segment=None))
    assert result.status == "unsupported" and "ambiguous" in result.reason
    explicit = repository.get(sale_query(segment={"property_type": "pooled", "size_band": "large"}))
    assert explicit.observation.value == 3_100


def test_corrupt_release_refused_before_query_and_synthetic_opt_in_required(
    release_dir: Path,
) -> None:
    with pytest.raises(ValueError, match="opt-in"):
        SnapshotMarketRepository.from_release(release_dir)
    (release_dir / "boundaries.geojson").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash/size"):
        SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
