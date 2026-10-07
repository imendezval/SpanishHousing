# Phase 4 progress

Current milestone: M6. M1 `05427d9`; M2 `6697a15`; M3 `e847cfc`; M4 `face537`. Reviewed baseline `3038f00`. Locked sync and full gate
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

M4 verified: local/local orchestration, reusable destination helper over existing
savings/borrower finances, engine-only capacity/target calculations, explicit
partial indicators and unviability. Independent composed values match the guide,
including cash limit 16333.333…, mortgage limit 225000 and target shortfalls.
Zero capacity, ratio >1, unbounded cash, A/B geography and deferred fixed-saving
with no market calls pass. Actual source fingerprint/runtime are recorded.
Full gate passed 267 tests/37 typed files/eight contracts before adding the pure
market ninth contract and indirect application/storage sensitivity check.
A6/A7 verified; A8/A9/A12 pending; A10 remains blocked.

M5 verified: deterministic economic JSON/CSV, safe two-file staging/publication,
existing-output refusal and owned-only cleanup. Exact replay uses resolved saved
inputs and rejects release/model/code/runtime/content mismatches. Thin CLI
evaluation/replay match Python and run outside cwd with explicit paths. Both new
demos opt into pooled proxies; staged growth has two savers/one borrower and an
explicit utility-spending milestone. Production builder/repository/CLI workflow
passes with Getafe room explicitly missing. Full locked gate: 280 tests, strict
mypy (38 files), Ruff, lock check and nine import contracts. A8 verified; A9
awaits final wheel workflow; A10 remains blocked. README/architecture updated.

Next: final edge review, fresh built-wheel/source fingerprint comparison and
installed evaluation/export/replay evidence; update final acceptance/handoff.
