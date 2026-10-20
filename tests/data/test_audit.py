"""Guard the distinction between audit evidence and missing market data."""

import csv
from collections import Counter

from fixtures import PROJECT_ROOT


def test_audit_has_every_area_metric_and_no_invented_missing_values() -> None:
    path = PROJECT_ROOT / "data/manifests/coverage_audit.csv"
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 48
    assert Counter(row["location_name"] for row in rows) == {
        name: 3 for name in {row["location_name"] for row in rows}
    }
    assert {row["metric"] for row in rows} == {
        "purchase_price_per_m2",
        "whole_home_rent_per_m2_month",
        "room_rent_per_month",
    }
    for row in rows:
        assert row["source_url"].startswith("https://www.idealista.com/")
        assert (row["value"] != "") == (row["verification_status"] == "numeric_verified")
        assert row["reuse_status"] == "unknown"
        if row["verification_status"] == "numeric_verified":
            assert float(row["value"]) > 0
            assert row["observation_period"]
            assert row["evidence_scope"] in {
                "city_row",
                "municipality_row",
                "press_release_city_prose",
            }
