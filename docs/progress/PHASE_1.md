# Phase 1 progress

Current milestone: M6 verified in the Phase 2 checkout on 7 October 2026. Original tooling gaps have been resolved with executed checks.

Phase 2 re-verification: `uv sync --locked` and `bash scripts/check.sh` passed on the unchanged Phase 1 baseline (`551cb17`): 46 tests, seven import contracts, Ruff formatting/lint, and strict mypy. The integrated package's build and wheel CLI/API checks also passed in Phase 2 M6. Data coverage limitations still belong to Phase 3.

Verified checkpoint commits include `004a7f3` (contracts/configuration), `5f0c25f` (audit/handoff), and `9e47c05` (unit-name cleanup). Focused pytest ran before each. The remaining untracked `AGENTS.md` predates this implementation and is excluded from commits.

| Milestone | Status |
|---|---|
| M1 | verified: locked sync, lock check, build and wheel installation passed |
| M2 | verified: scenario tests, strict mypy and all seven import contracts passed |
| M3 | verified: examples, source and installed CLI tests passed |
| M4 | verified: synthetic market/result contracts and round trips tested |
| M5 | verified: 48 evidence rows, primary report checks and audit invariant test |
| M6 | verified: full locked gate and outside-repository wheel smoke passed |

Baseline: repository held only `.gitignore`, with supplied docs ignored and `AGENTS.md` untracked. No package, tests, or quality gate existed. The untracked instruction file is preserved.

## Evidence and acceptance

- A1: verified. Locked sync/check, build and separate wheel installation passed. The old missing-tool/network limitation no longer blocks the current checkout.
- A2: verified. Structure reviewed against the plan; package namespaces/canonical documents and full dependency graph passed.
- A3/A4: verified. The full 46-case baseline suite passed with no deselections, covering scenario structure, calendar arithmetic, independent locations and fixed-saving representation.
- A5: verified. Examples, deterministic JSON round trips and error cases passed. Wheel console help and scenario JSON validation ran from `/tmp` with absolute paths.
- A6: synthetic market fixture, missing status, provenance and run metadata tests passed.
- A7: verified. Seven Import Linter contracts and the failure-sensitivity test passed.
- A8: 16 areas × 3 metrics audited in `data/manifests/coverage_audit.csv`; report values and methodological caveats recorded in `docs/DATA_COVERAGE.md`.
- A9: verified. Locked Ruff, strict mypy, Import Linter, full pytest, lock check, package build and outside-repository wheel smoke passed.
- A10: README, architecture, progress and source audit are current. Local checkpoint commits exist; no task changes are intentionally left unstaged.

Latest executed checks: baseline `uv sync --locked` and `bash scripts/check.sh` (46 tests); integrated `bash scripts/check.sh` (136 tests); `uv build`; fresh wheel installation in `/tmp/spain-housing-wheel.BsoUan`, with CLI and financial API executed from `/tmp` without `PYTHONPATH`. Imports were confirmed inside that environment's site-packages. Exact evidence and commands are in [Phase 2 progress](PHASE_2.md). `uv` and its cache were placed under `/tmp`; no dependency lock changes were needed.

Historical context: the original Phase 1 session could run only partial source checks because `uv`, Hatchling and network access were unavailable. Its incomplete engineering statuses above have been updated solely after current verification; the old source-only checks were not treated as installed-wheel evidence.

Decisions: use Pydantic 2, PyYAML, and a standard src package. Explicit interest appears in every example, not defaults. The room pilot is restricted to cities with public numeric evidence; no inferred room values. Codes not cross-checked against the current INE catalogue are marked provisional in the CSV.

Next handoff: Phase 3 must address the documented source access, reuse, segmentation and provisional geographic identifier limitations. Phase 2's financial engine is verified independently of these data gaps. Keep the user instruction file untracked unless requested otherwise.
