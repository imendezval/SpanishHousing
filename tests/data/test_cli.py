import json
import subprocess
from pathlib import Path

from conftest import FIXTURES

ROOT = Path(__file__).resolve().parents[2]


def command(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["spain-housing", *args], cwd=tmp_path, capture_output=True, text=True, check=False
    )


def test_build_validate_open_query_cli_in_another_directory(tmp_path: Path) -> None:
    args = [
        "build-release",
        "--config",
        str(FIXTURES / "recipe.json"),
        "--data-root",
        str(FIXTURES),
        "--release-root",
        str(tmp_path / "releases"),
    ]
    prohibited = command(tmp_path, *args)
    assert prohibited.returncode == 2 and prohibited.stdout == ""
    assert "opt-in" in prohibited.stderr
    built = command(tmp_path, *args, "--allow-synthetic")
    assert built.returncode == 0 and built.stderr == ""
    summary = json.loads(built.stdout)
    assert summary["kind"] == "synthetic" and summary["readiness"] == "synthetic_only"
    path = summary["path"]
    validated = command(tmp_path, "validate-release", "--release", path, "--allow-synthetic")
    assert validated.returncode == 0 and validated.stderr == ""
    assert json.loads(validated.stdout) == summary
    for query, expected_status in [
        ("query_sale.json", "available"),
        ("query_missing_room.json", "missing"),
    ]:
        result = command(
            tmp_path,
            "query-market",
            "--release",
            path,
            "--query",
            str(FIXTURES / query),
            "--allow-synthetic",
        )
        assert result.returncode == 0 and result.stderr == ""
        assert json.loads(result.stdout)["status"] == expected_status
    unsupported_query = tmp_path / "unsupported.json"
    value = json.loads((FIXTURES / "query_sale.json").read_bytes())
    value["segment"] = {"property_type": "flat"}
    unsupported_query.write_text(json.dumps(value))
    unsupported = command(
        tmp_path,
        "query-market",
        "--release",
        path,
        "--query",
        str(unsupported_query),
        "--allow-synthetic",
    )
    assert unsupported.returncode == 0 and unsupported.stderr == ""
    assert json.loads(unsupported.stdout)["status"] == "unsupported"
    normal = command(tmp_path, "validate-release", "--release", path)
    assert normal.returncode == 2 and normal.stdout == ""
    assert "opt-in" in normal.stderr


def test_invalid_recipe_query_release_and_blocked_real_recipe(
    tmp_path: Path, release_dir: Path
) -> None:
    blocked = command(
        tmp_path,
        "build-release",
        "--config",
        str(ROOT / "configs/sources/pilot.yaml"),
        "--data-root",
        str(tmp_path / "raw"),
        "--release-root",
        str(tmp_path / "blocked"),
    )
    assert blocked.returncode == 2 and blocked.stdout == ""
    assert "restricted" in blocked.stderr
    assert not (tmp_path / "blocked").exists()
    bad_query = tmp_path / "bad.json"
    bad_query.write_text('{"metric":"invalid"}')
    bad = command(
        tmp_path,
        "query-market",
        "--release",
        str(release_dir),
        "--query",
        str(bad_query),
        "--allow-synthetic",
    )
    assert bad.returncode == 2 and bad.stdout == ""
    corrupt = command(
        tmp_path, "validate-release", "--release", str(tmp_path / "absent"), "--allow-synthetic"
    )
    assert corrupt.returncode == 2 and corrupt.stdout == ""
    bad_query.write_text('{"kind":"synthetic","kind":"observed"}')
    invalid = command(
        tmp_path,
        "build-release",
        "--config",
        str(bad_query),
        "--data-root",
        str(FIXTURES),
        "--release-root",
        str(tmp_path / "invalid"),
        "--allow-synthetic",
    )
    assert invalid.returncode == 2 and invalid.stdout == "" and "duplicate" in invalid.stderr
