from pathlib import Path

import pytest

from spain_housing.config import load_scenario
from spain_housing.ingestion.release import build_release
from spain_housing.models.dataset import BuildRecipe
from spain_housing.models.scenario import Scenario
from spain_housing.storage.release import strict_json

FIXTURES = Path(__file__).resolve().parent / "fixtures/synthetic/pilot"


@pytest.fixture
def recipe() -> BuildRecipe:
    return BuildRecipe.model_validate(strict_json((FIXTURES / "recipe.json").read_bytes()))


@pytest.fixture
def release_dir(tmp_path: Path, recipe: BuildRecipe) -> Path:
    return build_release(
        recipe, data_root=FIXTURES, release_root=tmp_path / "releases", allow_synthetic=True
    )


@pytest.fixture
def scenario() -> Scenario:
    root = Path(__file__).resolve().parents[1]
    data = load_scenario(
        root / "configs/defaults.yaml", root / "configs/scenarios/room_only.yaml"
    ).model_dump(mode="json")
    data["saving_months"] = 3
    data["participants"][0]["net_annual_income"]["milestones"] = [
        {"month_offset": 0, "amount_eur": 24000}
    ]
    data["participants"][0]["monthly_debt"]["milestones"] = [{"month_offset": 0, "amount_eur": 100}]
    data["mortgage"]["annual_nominal_interest_fraction"] = 0
    data["market_selection"]["allow_pooled_property_proxy"] = True
    data["living_stages"] = [
        dict(
            arrangement="room",
            start_month_offset=0,
            end_month_offset=2,
            rent_share=1,
            rent_includes_utilities=True,
        ),
        dict(
            arrangement="flat_shared",
            start_month_offset=2,
            end_month_offset=3,
            rent_share=0.5,
            rental_area_m2=80,
            rent_includes_utilities=False,
        ),
    ]
    return Scenario.model_validate(data)


@pytest.fixture
def expanded_dir(tmp_path: Path) -> Path:
    from fixtures.synthetic.expand import prepare_fixture

    data_root = tmp_path / "expanded-inputs"
    expanded = prepare_fixture(data_root)
    return build_release(
        expanded,
        data_root=data_root,
        release_root=tmp_path / "expanded-releases",
        allow_synthetic=True,
    )
