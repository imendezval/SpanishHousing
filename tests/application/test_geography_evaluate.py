"""Independent financial reference over geography-backed complete/partial releases."""

from pathlib import Path

import pytest

from fixtures.synthetic.atlas import demo_config
from spain_housing.storage.files import strict_json


def test_hand_calculated_four_month_reference_and_purchase_only_gap(
    atlas_dir: Path, tmp_path: Path, scenario
) -> None:
    from spain_housing.application import evaluate_scenario
    from spain_housing.ingestion.demo import generate_demo
    from spain_housing.ingestion.release import build_release
    from spain_housing.markets.repository import SnapshotMarketRepository
    from spain_housing.models.scenario import Scenario
    from spain_housing.storage.release import parse_recipe

    data = scenario.model_dump(mode="json")
    data["saving_months"] = 4
    data["retained_reserve_eur"] = 1200
    data["target_property"]["area_m2"] = 60
    data["participants"][0]["starting_savings_eur"] = 10000
    data["household_nonhousing_expenses"]["milestones"] = [dict(month_offset=0, amount_eur=600)]
    data["living_stages"][1]["end_month_offset"] = 4
    reference = Scenario.model_validate(data)
    results = []
    for variant in ("complete", "partial"):
        inputs = generate_demo(
            atlas_dir, demo_config(), output_root=tmp_path / variant, variant=variant
        )
        recipe = parse_recipe(strict_json((inputs / "recipe.json").read_bytes()))
        release = build_release(
            recipe,
            data_root=inputs,
            release_root=tmp_path / "releases",
            allow_synthetic=True,
            geography_dir=atlas_dir,
        )
        market = SnapshotMarketRepository.from_release(
            release, allow_synthetic=True, geography_dir=atlas_dir
        )
        run = evaluate_scenario(
            reference,
            market_data=market,
            context=market.evaluation_context,
            mapped_locations=(market.locations[0].location,),
        )
        results.append(run.results[0])
    complete, gap = results
    assert complete.savings.ending_savings_eur == pytest.approx(13200)
    assert complete.savings.usable_savings_eur == pytest.approx(12000)
    purchase = complete.purchase
    assert purchase.savings_price_limit_eur == pytest.approx(40000)
    assert purchase.mortgage_price_limit_eur == pytest.approx(225000)
    assert purchase.maximum_price_eur == pytest.approx(40000)
    assert purchase.target_price_eur == pytest.approx(120000)
    assert purchase.target_cash_shortfall_eur == pytest.approx(24000)
    assert purchase.target_loan_eur == pytest.approx(96000)
    assert purchase.target_monthly_payment_eur == pytest.approx(320)
    assert complete.affordable_area_m2.value == pytest.approx(20)
    assert complete.target_affordability_ratio.value == pytest.approx(1 / 3)
    assert gap.purchase.maximum_price_eur == pytest.approx(40000)
    assert gap.affordable_area_m2.status == "missing"
