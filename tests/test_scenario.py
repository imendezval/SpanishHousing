"""Structural and extension-readiness behaviour at the scenario boundary."""

from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.config import load_scenario
from spain_housing.models.scenario import Scenario

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / "configs/defaults.yaml"
EXAMPLES = ROOT / "configs/scenarios"


def example(name: str = "room_only") -> dict:
    scenario = load_scenario(DEFAULTS, EXAMPLES / f"{name}.yaml")
    return scenario.model_dump(mode="json")


def test_separate_savers_borrowers_and_locations() -> None:
    joint = Scenario.model_validate(example("joint_saving"))
    assert joint.saver_ids == ("buyer", "partner")
    assert joint.borrower_ids == ("buyer",)
    assert joint.locations.saving_location.location.code == "28079"
    assert joint.locations.buying_location.kind == "mapped"
    assert joint.purchase_month == date(2033, 10, 1)


@pytest.mark.parametrize(
    "start,months,expected",
    [("2026-11-01", 2, date(2027, 1, 1)), ("2010-01-01", 84, date(2017, 1, 1))],
)
def test_calendar_months_and_historical_start(start: str, months: int, expected: date) -> None:
    data = example()
    data["start_month"] = start
    data["saving_months"] = months
    data["living_stages"][0]["end_month_offset"] = months
    assert Scenario.model_validate(data).purchase_month == expected


@pytest.mark.parametrize(
    "edit",
    [
        lambda d: d["living_stages"][0].update(end_month_offset=83),
        lambda d: d["living_stages"].append({**d["living_stages"][0], "start_month_offset": 10}),
        lambda d: d.update(saving_months=0),
        lambda d: d.update(unexpected=1),
        lambda d: d["participants"].append(deepcopy(d["participants"][0])),
        lambda d: d.update(borrower_ids=["stranger"]),
        lambda d: d.update(schema_version=True),
        lambda d: d["mortgage"].update(financed_fraction=1.2),
        lambda d: d["mortgage"].update(maximum_debt_ratio=-0.1),
        lambda d: d["living_stages"][0].update(rent_share=0),
        lambda d: d["participants"][0].update(participant_id=123),
        lambda d: d["participants"][0]["net_annual_income"]["milestones"].append(
            {"month_offset": 0, "amount_eur": 1}
        ),
    ],
)
def test_malformed_scenario_rejected(edit) -> None:
    data = example()
    edit(data)
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


@pytest.mark.parametrize(
    "field,value",
    [
        ("retained_reserve_eur", True),
        ("retained_reserve_eur", "1000"),
        ("retained_reserve_eur", float("inf")),
        ("saving_months", True),
        ("saving_months", "84"),
    ],
)
def test_numeric_coercion_rejected(field: str, value: object) -> None:
    data = example()
    data[field] = value
    with pytest.raises(ValidationError):
        Scenario.model_validate(data)


def test_zero_income_interest_and_later_income_target_accepted() -> None:
    data = example()
    data["participants"][0]["net_annual_income"]["milestones"] = [
        {"month_offset": 0, "amount_eur": 0},
        {"month_offset": 100, "amount_eur": 30000},
    ]
    data["mortgage"]["annual_nominal_interest_fraction"] = 0
    assert (
        Scenario.model_validate(data).participants[0].net_annual_income.milestones[-1].month_offset
        == 100
    )


def test_rent_sharing_does_not_add_a_borrower() -> None:
    data = example("staged_living")
    assert data["living_stages"][-1]["rent_share"] == 0.5
    assert data["borrower_ids"] == ["buyer"]
