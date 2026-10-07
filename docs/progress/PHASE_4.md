# Phase 4 progress

Current milestone: M2. Reviewed baseline `3038f00`. Locked sync and full gate
passed: 227 tests, strict mypy (29 files), Ruff, eight import contracts and lock
check. User-owned untracked instructions and Phase 2–4 guides are preserved.

M1 verified: defaulted selection policy, immutable public context, trace/runtime
records and coherent backward-compatible result additions. Full gate passed 238
tests, strict mypy (30 files), Ruff and eight contracts. Sensitivity checks cover
application/storage, application/ingestion and markets/finance. Shared fixture
builder moved to tests/conftest.py. M2–M6 pending. A1/A2 verified;
A3–A9/A11/A12 pending; A10 blocked by Phase 3 market permissions.
No observed release exists. Continue engineering with explicit synthetic opt-in.

Decisions: retain schema version 1 for defaulted settings/results. CLI composes
the concrete repository; application receives MarketData and immutable context,
preserving its indirect storage prohibition. Finance remains unchanged.

Next: verify contracts/defaults and import sensitivity; checkpoint M1, then
implement exact reference selection and pure projections.
