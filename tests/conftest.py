from pathlib import Path

import pytest

from spain_housing.ingestion.release import build_release
from spain_housing.models.dataset import BuildRecipe
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
