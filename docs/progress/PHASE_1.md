# Phase 1 progress

Current milestone: M6 integration review. Earlier engineering gates remain open.

Verified checkpoint commits include `004a7f3` (contracts/configuration), `5f0c25f` (audit/handoff), and `9e47c05` (unit-name cleanup). Focused pytest ran before each. The remaining untracked `AGENTS.md` predates this implementation and is excluded from commits.

| Milestone | Status |
|---|---|
| M1 | in progress: files and lock created; locked sync/build not verified |
| M2 | in progress: scenario tests pass; Import Linter execution pending |
| M3 | in progress: examples and source CLI pass; installed CLI test pending |
| M4 | verified: synthetic market/result contracts and round trips tested |
| M5 | verified: 48 evidence rows, primary report checks and audit invariant test |
| M6 | in progress: non-locked checks pass; locked gate and wheel pending |

Baseline: repository held only `.gitignore`, with supplied docs ignored and `AGENTS.md` untracked. No package, tests, or quality gate existed. The untracked instruction file is preserved.

## Evidence and acceptance

- A1: incomplete. `uv.lock` exists, but locked sync and built-wheel checks were not run after restart. Sandbox DNS cannot resolve `pypi.org`; the temporary `uv` binary from before the interruption is gone. `pip wheel --no-deps --no-build-isolation .` also failed because Hatchling is unavailable.
- A2: reviewed structure against the plan; package namespaces and canonical documents are present. Full dependency graph check is pending.
- A3/A4: 44 targeted pytest cases passed for scenario structure, calendar arithmetic, independent locations, and future fixed-saving representation (with one installed-CLI test deselected).
- A5: examples and deterministic JSON round trips passed; source CLI ran from `/tmp` with explicit absolute paths, and a missing file returned code 2. Installed console script pending.
- A6: synthetic market fixture, missing status, provenance and run metadata tests passed.
- A7: Import Linter contracts and a failure-sensitivity test exist; `lint-imports` is unavailable in the current environment, so detection is unverified.
- A8: 16 areas × 3 metrics audited in `data/manifests/coverage_audit.csv`; report values and methodological caveats recorded in `docs/DATA_COVERAGE.md`.
- A9: Ruff 0.16.0 format/check and `compileall` passed. The focused pytest run passed. Locked Ruff, mypy, Import Linter, full pytest, lock check and package build remain unrun.
- A10: README, architecture, progress and source audit are current. Local checkpoint commits exist; no task changes are intentionally left unstaged.

Last check: `/home/inigo/miniconda3/envs/automl-tab/bin/ruff format --check .` (27 files formatted), the same binary's `check .` (pass), `python3.12 -m compileall -q src tests` (pass), and a Python 3.12 pytest invocation with available external pytest modules and source path (44 passed, one installed-CLI case deselected). A separate source CLI smoke from `/tmp` passed valid JSON and invalid-path cases. This diagnostic run does not prove the package is installed. `bash scripts/check.sh` was attempted and stopped immediately at `uv: command not found`.

Decisions: use Pydantic 2, PyYAML, and a standard src package. Explicit interest appears in every example, not defaults. The room pilot is restricted to cities with public numeric evidence; no inferred room values. Codes not cross-checked against the current INE catalogue are marked provisional in the CSV.

Next action: obtain a Codex session with functional sandbox network or an already-populated `uv` cache, then run `uv sync --locked`, `bash scripts/check.sh`, `uv build`, and an outside-repo wheel install/CLI smoke. Repair any failures before marking A1/A7/A9 complete. Keep `AGENTS.md` untracked unless the user asks otherwise.
