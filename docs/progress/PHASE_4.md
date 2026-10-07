# Phase 4 progress

Current milestone: M4. M1 checkpoint `05427d9`; M2 `6697a15`. Reviewed baseline `3038f00`. Locked sync and full gate
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

M2 verified: exact profile selection, completed-period freshness, source/basis/
statistic ambiguity, explicit IDs, strict dimensions and opt-in pooled proxies.
Original observations remain unchanged; growth uses last covered month and
positive-finite checks. 27 focused contract/selection/repository tests and strict
mypy (32 files) passed. A3/A4 verified; no snapshot get behavior changed.

M3 verified: single path sampler, exact N budgets, one-unit household rent/share,
effective spending, separate saver/borrower aggregates and finances at offset N.
Incomplete stages return typed issues with no partial financial path. Direct
monthly rent and all-flat Getafe work without a room dependency. Exhausted then
recovered savings retain finance's permanent exhaustion. Full pytest: 255 passed;
Ruff and strict mypy passed. A5 preparation verified.

Next: local/local orchestration, separate buying-side helper, financial calls,
partial comparisons, unviable results and actual deterministic version evidence.
