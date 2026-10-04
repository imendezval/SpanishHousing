#!/usr/bin/env bash
set -euo pipefail
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src/spain_housing
uv run --locked lint-imports
uv run --locked pytest
