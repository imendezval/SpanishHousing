"""Probe the repository's real import rules with direct and indirect violations."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from fixtures import PROJECT_ROOT

type ImportCheck = Callable[[tuple[tuple[str, str], ...], str], None]


@pytest.fixture
def check_imports(tmp_path: Path) -> ImportCheck:
    # Keep the actual module layout and configuration, but omit implementation
    # imports so each probe isolates the intended forbidden dependency.
    source = PROJECT_ROOT / "src/spain_housing"
    package = tmp_path / "spain_housing"
    for original in source.rglob("*.py"):
        target = package / original.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("")
    config = tmp_path / "pyproject.toml"
    config.write_text((PROJECT_ROOT / "pyproject.toml").read_text())

    def check(edges: tuple[tuple[str, str], ...], contract: str) -> None:
        for origin, destination in edges:
            module = package.joinpath(*origin.split("."))
            path = module / "__init__.py" if module.is_dir() else module.with_suffix(".py")
            assert path.is_file(), f"probe source is not a repository module: {origin}"
            path.write_text(f"import spain_housing.{destination}\n")
        result = subprocess.run(
            ["lint-imports", "--no-cache", "--config", str(config)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 1, result.stdout + result.stderr
        # An unrelated broken contract or a malformed config is not evidence
        # that this particular boundary is enforced.
        assert f"{contract} BROKEN" in result.stdout, result.stdout + result.stderr

    return check


@pytest.mark.parametrize(
    "source,target,contract",
    [
        ("models", "finance", "models do not depend on implementations"),
        ("finance", "storage", "finance has no providers or interface dependencies"),
        ("storage", "ingestion", "storage has only model dependencies"),
        ("application", "storage", "application has no interface or ingestion dependencies"),
        ("application", "ingestion", "application has no interface or ingestion dependencies"),
        ("markets", "finance", "market access has no acquisition or interface dependencies"),
        ("ui", "launcher", "lower layers never import launcher"),
        ("finance", "launcher", "lower layers never import launcher"),
        ("application", "launcher", "lower layers never import launcher"),
    ],
    ids=[
        "models-finance",
        "finance-storage",
        "storage-ingestion",
        "application-storage",
        "application-ingestion",
        "markets-finance",
        "ui-launcher",
        "finance-launcher",
        "application-launcher",
    ],
)
def test_direct_forbidden_imports(
    check_imports: ImportCheck, source: str, target: str, contract: str
) -> None:
    check_imports(((source, target),), contract)


def test_application_indirect_storage_boundary(check_imports: ImportCheck) -> None:
    check_imports(
        (("application", "markets"), ("markets", "storage")),
        "application has no interface or ingestion dependencies",
    )


def test_coverage_indirect_repository_boundary(check_imports: ImportCheck) -> None:
    check_imports(
        (("markets.coverage", "markets.repository"), ("markets.repository", "storage")),
        "pure market rules have no storage dependencies",
    )
