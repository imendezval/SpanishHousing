"""Import Linter must detect a real forbidden edge, not just parse a config."""

import subprocess
from pathlib import Path


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
