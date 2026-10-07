# Phase 2 progress

Current milestone: M6 complete. M1–M6 and A1–A10 are verified; no required checks or repairs remain.

| Milestone | Evidence/status |
|---|---|
| M1 | Locked Phase 1 baseline: 46 tests, seven import contracts, Ruff and strict mypy passed. Result contract checkpoint `65652f5`. |
| M2 | Six-month savings reference, signed paths, reserve, persistent exhaustion, chronology and immutability tests pass. Checkpoint `a85b5b7`. |
| M3 | Zero/positive/small/underflow-rate references, payment/loan grid, total debt and finite-output checks pass. Checkpoint `a85b5b7`; extreme-input checks verified at `60c6ecd`. |
| M4 | Protocol cost components, every capacity table case, non-default assumptions, minimum, near-equal labels, unbounded cash and feasibility tests pass. Checkpoint `60c6ecd`. |
| M5 | Target references, simultaneous/no shortfalls, absent targets, JSON round trips, separate saver/borrower composition and recovered-exhaustion refusal pass. README example executed using the installed wheel. Checkpoint `60c6ecd`. |
| M6 | Full source gate passed (136 tests); sdist/wheel build and isolated wheel CLI/API smoke passed. Ownership review and handoff complete. |

## Acceptance evidence

| ID | Status/evidence |
|---|---|
| A1 | Verified locked baseline at `551cb17`; Phase 1 tooling gaps reconciled with current gate, build and isolated wheel evidence. |
| A2 | Savings references and boundary tests pass, including unchanged negative balances and epsilon semantics. |
| A3 | Literal mortgage references, grid, tiny rates and non-finite derived-output rejection pass. |
| A4 | Proportional policy and distinct-component alternative policy tests pass. |
| A5 | Capacity references and feasibility grid pass, including full financing with zero costs/income. |
| A6 | Both target references and both/no shortfalls pass; target absence and serialization verified. |
| A7 | Invalid scalar/sequence tests and actual recovered-exhausted composition refusal pass. |
| A8 | Independent references, invariants, JSON and separate saver/borrower workflow pass. |
| A9 | Full locked source gate passed with unchanged lock/import contracts; sdist/wheel built and isolated wheel CLI/API smoke passed. |
| A10 | Formula ownership, minimal contracts, callable API, current progress and Phase 3/4 handoff documented. Scoped implementation checkpoints `65652f5`, `a85b5b7`, `60c6ecd`; final documentation checkpoint accompanies this record. |

## Checks and decisions

Last full gate: `bash scripts/check.sh` with `PATH=/tmp/phase2-tools/bin:$PATH` and `UV_CACHE_DIR=/tmp/phase2-uv-cache`: 136 tests passed, Ruff format/lint, strict mypy (19 files), seven import contracts and lock check passed. `uv sync --locked` passed at baseline. The missing `uv` binary was installed under `/tmp/phase2-tools`; no lock/dependency change was needed.

`uv build` passed, producing `dist/spain_housing-0.1.0.tar.gz` and `dist/spain_housing-0.1.0-py3-none-any.whl`. Wheel smoke used fresh `/tmp/spain-housing-wheel.BsoUan`, created with `uv venv /tmp/spain-housing-wheel.BsoUan --python 3.12` and installed with `uv pip install --python /tmp/spain-housing-wheel.BsoUan/bin/python /home/inigo/data/git/repo/SpanishHousing/dist/spain_housing-0.1.0-py3-none-any.whl`.

From working directory `/tmp`, with `env -u PYTHONPATH`, the wheel's `spain-housing --help` and `validate-scenario --defaults /home/inigo/data/git/repo/SpanishHousing/configs/defaults.yaml --scenario /home/inigo/data/git/repo/SpanishHousing/configs/scenarios/room_only.yaml --json` passed. The exact README Python block was piped into that environment's Python: literal €60,000 savings, €200,000 maximum price, savings binding and €15,000 target shortfall assertions passed. Package and finance imports were confirmed under `/tmp/spain-housing-wheel.BsoUan/lib/python3.12/site-packages`, inside that interpreter's `sys.prefix`. This is a wheel install, independently of the editable source gate.

`PurchaseResult.savings_price_limit_eur` is required but nullable solely for an unbounded cash constraint. `target_loan_eur` is explicit and all six target diagnostics are coherent. No persisted target payloads were found; target-free finite payloads remain valid. Scenario schema/defaults and cost protocol are unchanged.

Savings exhaustion uses 1e−8 EUR; binding labels use €0.01 absolute tolerance and preserve the actual minimum. Mortgage annuity factor has one owner and uses `log1p`/`expm1`; public scalars reject booleans/strings/non-finite values and outputs are not rounded. Savings, costs and mortgage remain independent; purchase composes costs/mortgage. The private validation module shares scalar checks only.

Working tree initially contained untracked user `AGENTS.md` and Phase 2 guide; both remain preserved and excluded from task commits. No blockers. No push, merge or deployment.

Next handoff: Phase 3 owns pilot data/reuse/coverage and its existing access limitations. Phase 4 prepares exactly N budgets, resolves rent shares/utilities upstream, selects savers and borrowers separately, samples borrower finances at offset N and translates exhaustion to unviable status, then resolves destination targets and run metadata. Reuse the financial formulas; nonlinear costs and variable financing require deliberate solver extensions. No Phase 2 gaps remain.
