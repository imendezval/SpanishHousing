# Phase 2 progress

Current milestone: M1. M1 baseline verified; contract refinement in progress. M2–M6 pending.

Working tree at start: untracked `AGENTS.md` and Phase 2 guide, preserved. Baseline at `551cb17`: `uv sync --locked` and `bash scripts/check.sh` passed (46 tests, seven import contracts, Ruff and mypy). `uv` was installed under `/tmp/phase2-tools`; `UV_CACHE_DIR=/tmp/phase2-uv-cache` was used. This re-verifies the old Phase 1 gate claim; wheel verification remains for M6.

Decision: keep `PurchaseResult.savings_price_limit_eur` required but nullable for a mathematically unbounded cash limit. Add target principal and require all target diagnostics together. No Scenario change.

Acceptance: A1 partially verified (wheel pending); A2–A10 pending.

Next: test the contract, implement savings, mortgage, costs and purchase in their owning modules; run focused checks and checkpoint each coherent slice.
