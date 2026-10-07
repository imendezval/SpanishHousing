#!/usr/bin/env bash
set -euo pipefail
uv lock --check
uv run --locked --extra map ruff format --check .
uv run --locked --extra map ruff check .
uv run --locked --extra map mypy src/spain_housing
uv run --locked --extra map lint-imports
uv run --locked --extra map pytest
