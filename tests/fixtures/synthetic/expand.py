"""Generate retained synthetic inputs; the existing builder remains the only pipeline."""

import argparse
import csv
import io
import json
from copy import deepcopy
from pathlib import Path

from spain_housing.models.dataset import BuildRecipe
from spain_housing.storage.release import canonical_json, sha256

PILOT = Path(__file__).parent / "pilot"
# Engineering identities only. All names, registry and shapes remain synthetic.
EXPANSION = (
    ("46250", "València"),
    ("29067", "Málaga"),
    ("07040", "Palma"),
    ("48020", "Bilbao"),
    ("41091", "Sevilla"),
    ("50297", "Zaragoza"),
    ("47186", "Valladolid"),
    ("37274", "Salamanca"),
    ("44216", "Teruel"),
    ("08015", "Badalona"),
    ("46169", "Mislata"),
    ("41038", "Dos Hermanas"),
)
GAPS = {
    ("28065", "room"): "missing",
    ("08015", "room"): "missing",
    ("46169", "room"): "missing",
    ("44216", "sale"): "missing",
    ("41038", "rent"): "unsupported",
}


def _csv(rows: list[dict[str, object]], fields: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def prepare_fixture(root: Path, count: int = 16, *, segmented: bool = False) -> BuildRecipe:
    """One deterministic input generator shared by tests, runbook and measurements."""
    if count not in (16, 250):
        raise ValueError("generated cases must have 16 or 250 municipalities")
    data = json.loads((PILOT / "recipe.json").read_bytes())
    original_locations = deepcopy(data["locations"])
    additions = list(EXPANSION)
    additions.extend((f"99{i:03d}", f"Stress {i:03d}") for i in range(count - 16))
    features = json.loads((PILOT / "boundaries.geojson").read_bytes())["features"]
    for index, (code, name) in enumerate(additions):
        location = deepcopy(original_locations[0])
        location.update(
            location={"level": "municipality", "code": code},
            official_name=f"Synthetic {name}",
            province_code=code[:2],
            core=False,
            geometry_feature_id=f"fixture-{code}",
            geometry_national_code=f"fixture-{code}",
        )
        for mapping in location["source_mappings"]:
            mapping["label"] = location["official_name"]
        data["locations"].append(location)
        x, y = -8 + (index % 20) * 0.5, 28 + (index // 20) * 0.45
        features.append(
            dict(
                type="Feature",
                id=f"fixture-{code}",
                properties=dict(
                    nationallevelname="Municipio",
                    nationalcode=f"fixture-{code}",
                    nameunit=location["official_name"],
                ),
                geometry=dict(
                    type="Polygon",
                    coordinates=[
                        [
                            [x, y],
                            [x + 0.3, y],
                            [x + 0.3, y + 0.3],
                            [x, y + 0.3],
                            [x, y],
                        ]
                    ],
                ),
            )
        )
    if segmented:
        profile = deepcopy(data["profiles"][0])
        profile.update(profile_id="sale-flat-2", segment={"property_type": "flat", "bedrooms": 2})
        data["profiles"].append(profile)
    fields = list(next(csv.DictReader(io.StringIO((PILOT / "prices.csv").read_text()))))
    tables: dict[str, list[dict[str, object]]] = {"prices": [], "rooms": []}
    # Preserve pilot values exactly; added values are deterministic assumptions.
    originals = {}
    for filename in ("prices.csv", "rooms.csv"):
        for row in csv.DictReader(io.StringIO((PILOT / filename).read_text())):
            originals[(row["source_location"], row["profile_id"])] = row
    for index, location in enumerate(data["locations"]):
        for profile in data["profiles"]:
            code, key = location["location"]["code"], profile["profile_id"]
            if (code, key) in GAPS:
                continue
            row = originals.get((location["official_name"], key))
            if row is None:
                row = dict(
                    profile_id=key,
                    source_location=location["official_name"],
                    geographic_scope="municipality",
                    raw_value=str(
                        1500 + index * 10
                        if key.startswith("sale")
                        else 200 + index
                        if key == "room"
                        else 8
                    ),
                    raw_unit="eur_per_m2"
                    if key.startswith("sale")
                    else "eur_per_month"
                    if key == "room"
                    else "eur_per_m2_month",
                    period_start=profile["period_start"],
                    period_end=profile["period_end"],
                    statistic=profile["statistic"],
                    basis=profile["basis"],
                    source_locator=f"self-authored:{code}:{key}",
                    evidence_kind="synthetic",
                    estimation_method="",
                    quality_notes="Generated synthetic scaling input",
                )
            tables["rooms" if key == "room" else "prices"].append(row)
    data["declared_gaps"] = [
        dict(
            location_code=code,
            profile_id=profile,
            status=status,
            reason="Deliberate synthetic partial-coverage case",
        )
        for (code, profile), status in sorted(GAPS.items())
    ]
    payloads = {
        "prices.csv": _csv(tables["prices"], fields),
        "rooms.csv": _csv(tables["rooms"], fields),
        "registry.csv": _csv(
            [
                dict(
                    CPRO=loc["province_code"],
                    CMUN=loc["location"]["code"][2:],
                    DC=loc["control_digit"],
                    NOMBRE=loc["official_name"],
                )
                for loc in data["locations"]
            ],
            ["CPRO", "CMUN", "DC", "NOMBRE"],
        ),
        "boundaries.geojson": canonical_json(
            dict(type="FeatureCollection", crs="OGC:CRS84", features=features)
        ),
    }
    root.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        path = root / name
        if path.exists() and path.read_bytes() != payload:
            raise ValueError("fixture inputs differ; choose a new directory")
        path.write_bytes(payload)
    for capture in data["captures"]:
        payload = payloads[capture["path"]]
        capture.update(sha256=sha256(payload), byte_size=len(payload))
    data["processing_version"] = "synthetic-expansion-v1"
    recipe = BuildRecipe.model_validate(data)
    payload = canonical_json(recipe.model_dump(mode="json"))
    destination = root / "recipe.json"
    if destination.exists() and destination.read_bytes() != payload:
        raise ValueError("fixture recipe differs; choose a new directory")
    destination.write_bytes(payload)
    return recipe


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--locations", type=int, choices=(16, 250), default=16)
    args = parser.parse_args()
    prepare_fixture(args.output_root, args.locations)
    print(args.output_root / "recipe.json")
