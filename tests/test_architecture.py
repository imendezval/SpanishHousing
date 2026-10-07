"""Import Linter must detect a real forbidden edge, not just parse a config."""

import subprocess
from pathlib import Path

import pytest


def test_forbidden_import_contract_is_sensitive(tmp_path: Path) -> None:
    package = tmp_path / "spain_housing"
    (package / "models").mkdir(parents=True)
    (package / "finance").mkdir()
    (package / "__init__.py").write_text("")
    (package / "models/__init__.py").write_text("import spain_housing.finance\n")
    (package / "finance/__init__.py").write_text("")
    config = tmp_path / "pyproject.toml"
    config.write_text(
        '[tool.importlinter]\nroot_package = "spain_housing"\n'
        '[[tool.importlinter.contracts]]\nname = "models boundary"\ntype = "forbidden"\n'
        'source_modules = ["spain_housing.models"]\n'
        'forbidden_modules = ["spain_housing.finance"]\n'
    )
    result = subprocess.run(
        ["lint-imports", "--config", str(config)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "models boundary" in result.stdout


@pytest.mark.parametrize(
    "source,target",
    [
        ("finance", "storage"),
        ("storage", "ingestion"),
        ("application", "storage"),
        ("application", "ingestion"),
        ("markets", "finance"),
    ],
)
def test_storage_boundaries_detect_forbidden_edges(
    tmp_path: Path, source: str, target: str
) -> None:
    package = tmp_path / "spain_housing"
    package.mkdir()
    (package / "__init__.py").write_text("")
    for name in (source, target):
        (package / name).mkdir()
        (package / name / "__init__.py").write_text("")
    (package / source / "__init__.py").write_text(f"import spain_housing.{target}\n")
    config = tmp_path / "pyproject.toml"
    config.write_text(
        '[tool.importlinter]\nroot_package = "spain_housing"\n'
        '[[tool.importlinter.contracts]]\nname = "storage boundary"\ntype = "forbidden"\n'
        f'source_modules = ["spain_housing.{source}"]\n'
        f'forbidden_modules = ["spain_housing.{target}"]\n'
    )
    result = subprocess.run(
        ["lint-imports", "--config", str(config)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "storage boundary" in result.stdout


def test_application_indirect_storage_boundary(tmp_path: Path) -> None:
    package = tmp_path / "spain_housing"
    package.mkdir()
    (package / "__init__.py").write_text("")
    for module in ("application", "markets", "storage"):
        (package / module).mkdir()
        (package / module / "__init__.py").write_text("")
    (package / "application/__init__.py").write_text("import spain_housing.markets\n")
    (package / "markets/__init__.py").write_text("import spain_housing.storage\n")
    config = tmp_path / "pyproject.toml"
    config.write_text(
        '[tool.importlinter]\nroot_package = "spain_housing"\n'
        '[[tool.importlinter.contracts]]\nname = "indirect storage"\ntype = "forbidden"\n'
        'source_modules = ["spain_housing.application"]\n'
        'forbidden_modules = ["spain_housing.storage"]\n'
    )
    result = subprocess.run(
        ["lint-imports", "--config", str(config)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0 and "indirect storage" in result.stdout
