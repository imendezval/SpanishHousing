# Phase 2 progress

Current milestone: M6. M1–M5 implemented and verified in the source checkout; final build and isolated wheel checks remain.

| Milestone | Evidence/status |
|---|---|
| M1 | Locked Phase 1 baseline: 46 tests, seven import contracts, Ruff and strict mypy passed. Result contract checkpoint `65652f5`. |
| M2 | Six-month savings reference, signed paths, reserve, persistent exhaustion, chronology and immutability tests pass. Checkpoint `a85b5b7`. |
| M3 | Zero/positive/small/underflow-rate references, payment/loan grid, total debt and finite-output checks pass. Checkpoint `a85b5b7`; additional extreme-input checks in next checkpoint. |
| M4 | Protocol cost components, every capacity table case, non-default assumptions, minimum, near-equal labels, unbounded cash and feasibility tests pass. |
| M5 | Target references, simultaneous/no shortfalls, absent targets, JSON round trips, separate saver/borrower composition and recovered-exhaustion refusal pass. Callable README example added; installed execution pending M6. |
| M6 | Full source gate passed (136 tests); build, wheel CLI/API smoke and final handoff pending. |

## Acceptance evidence

| ID | Status/evidence |
|---|---|
| A1 | Verified locked baseline at `551cb17`; Phase 1 tooling gaps reconciled with new evidence. Phase 1 wheel re-verification remains tracked in M6/A9. |
| A2 | Savings references and boundary tests pass, including unchanged negative balances and epsilon semantics. |
| A3 | Literal mortgage references, grid, tiny rates and non-finite derived-output rejection pass. |
| A4 | Proportional policy and distinct-component alternative policy tests pass. |
| A5 | Capacity references and feasibility grid pass, including full financing with zero costs/income. |
| A6 | Both target references and both/no shortfalls pass; target absence and serialization verified. |
| A7 | Invalid scalar/sequence tests and actual recovered-exhausted composition refusal pass. |
| A8 | Independent references, invariants, JSON and separate saver/borrower workflow pass. |
| A9 | Source gate passed with unchanged lock and seven import contracts; package build and isolated wheel pending. |
| A10 | Ownership, contracts, callable API and Phase 3/4 boundaries documented; final evidence/checkpoint pending. |

## Checks and decisions

Last full gate: `bash scripts/check.sh` with `PATH=/tmp/phase2-tools/bin:$PATH` and `UV_CACHE_DIR=/tmp/phase2-uv-cache`: 136 tests passed, Ruff format/lint, strict mypy (19 files), seven import contracts and lock check passed. `uv sync --locked` passed at baseline. The missing `uv` binary was installed under `/tmp/phase2-tools`; no lock/dependency change was needed.

`PurchaseResult.savings_price_limit_eur` is required but nullable solely for an unbounded cash constraint. `target_loan_eur` is explicit and all six target diagnostics are coherent. No persisted target payloads were found; target-free finite payloads remain valid. Scenario schema/defaults and cost protocol are unchanged.

Savings exhaustion uses 1e−8 EUR; binding labels use €0.01 absolute tolerance and preserve the actual minimum. Mortgage annuity factor has one owner and uses `log1p`/`expm1`; public scalars reject booleans/strings/non-finite values and outputs are not rounded. Savings, costs and mortgage remain independent; purchase composes costs/mortgage. The private validation module shares scalar checks only.

Working tree initially contained untracked user `AGENTS.md` and Phase 2 guide; both remain preserved and excluded from task commits. No blockers. No push, merge or deployment.

Next: build; install the wheel into a fresh environment; run CLI validation and the exact README Python example from `/tmp` with no `PYTHONPATH`; verify site-packages origin. Update both progress records with final evidence and checkpoint documentation. Phase 3 owns pilot data/reuse/coverage; Phase 4 prepares exactly N budgets, samples borrower finances at offset N and translates exhaustion to unviable status, then resolves destination targets and run metadata.
