"""Immutable repository context and its agreement with application run evidence."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from spain_housing.config import load_scenario
from spain_housing.markets.repository import SnapshotMarketRepository
from spain_housing.models.results import RunResult

ROOT = Path(__file__).resolve().parents[2]


def test_public_context_is_immutable_and_run_consistent(release_dir: Path) -> None:
    repo = SnapshotMarketRepository.from_release(release_dir, allow_synthetic=True)
    context = repo.evaluation_context
    assert context.kind == "synthetic" and len(context.locations) == 4
    with pytest.raises(ValidationError):
        context.release_id = "other"
    scenario = load_scenario(
        ROOT / "configs/defaults.yaml", ROOT / "configs/scenarios/room_only.yaml"
    )
    with pytest.raises(ValidationError, match="disagree"):
        RunResult(
            schema_version=1,
            resolved_scenario=scenario,
            dataset_release_id="other",
            model_version="test",
            code_version="test",
            results=(),
            evaluation_context=context,
        )
