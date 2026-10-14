from copy import deepcopy
from pathlib import Path

import pytest

from fixtures.synthetic.expand import prepare_fixture
from spain_housing.ingestion.release import build_release
from spain_housing.models.dataset import BuildRecipe
from spain_housing.storage.release import sha256


@pytest.mark.parametrize(
    "change", ["column", "width", "locale", "period", "profile", "unit", "html", "zero", "capture"]
)
def test_selected_source_drift_fails_before_publication(tmp_path: Path, change: str):
    inputs = tmp_path / "inputs"
    recipe = prepare_fixture(inputs)
    destination = tmp_path / "releases"
    old = build_release(recipe, data_root=inputs, release_root=destination, allow_synthetic=True)
    before = {p.name: p.read_bytes() for p in old.iterdir()}
    file = inputs / "rooms.csv"
    data = file.read_text()
    if change == "column":
        data = data.replace("raw_value", "changed_value", 1)
    if change == "width":
        header, rows = data.split("\n", 1)
        data = header + "\n" + rows.replace("\n", ",extra\n", 1)
    if change == "locale":
        data = data.replace("300,€/mes", "3.00,€/mes", 1)
    if change == "period":
        data = data.replace("2026-04-01", "2026-05-01", 1)
    if change == "profile":
        data = data.replace("\nroom,", "\nunknown,", 1)
    if change == "unit":
        data = data.replace("€/mes", "eur_per_m2", 1)
    if change == "zero":
        data = data.replace("300,€/mes", "0,€/mes", 1)
    if change == "html":
        data = "<html>Login required</html>"
    file.write_text(data if change != "capture" else data + " ")
    payload = deepcopy(recipe.model_dump(mode="json"))
    if change != "capture":
        c = next(c for c in payload["captures"] if c["capture_id"] == "rooms")
        c.update(sha256=sha256(file.read_bytes()), byte_size=file.stat().st_size)
    changed = BuildRecipe.model_validate(payload)
    with pytest.raises(ValueError) as error:
        build_release(changed, data_root=inputs, release_root=destination, allow_synthetic=True)
    if change != "capture":
        assert "rooms" in str(error.value)
    if change in ("locale", "period", "profile", "unit", "zero"):
        assert "row 2" in str(error.value) and "profile" in str(error.value)
    assert list(destination.iterdir()) == [old]
    assert before == {p.name: p.read_bytes() for p in old.iterdir()}
