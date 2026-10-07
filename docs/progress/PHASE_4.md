# Phase 4 progress

Status: **engineering verified, observed-data integration blocked**, 7 October
2026. M1–M6 independent engineering is finished. A10 remains unverified because
Phase 3 has no permitted observed market release. Synthetic demonstrations do
not satisfy that criterion or the plan's real-data completion condition.

Latest verified implementation checkpoint: `ee89194`. Final documentation
checkpoint follows it. Reviewed baseline: `3038f00`; locked sync/full baseline
gate passed 227 tests. User-owned untracked `AGENTS.md` and Phase 2–4 execution
guides are preserved and excluded from commits. No push, merge or deployment.

## Milestones and local checkpoints

| Milestone | Result | Checkpoint / evidence |
| --- | --- | --- |
| M1 contracts | Verified | `05427d9`; 238 tests, strict selection/defaults, immutable public context and compatible results |
| M2 selection/projection | Verified | `6697a15`; exact reference intervals, complete/fresh eligibility, series ambiguity and explicit pooled proxies |
| M3 monthly preparation | Verified | `e847cfc`; 255 tests; exactly N budgets, one sampler, saver/borrower separation and effective expenses |
| M4 evaluation/comparison | Verified | `face537`; full gate, independent composed references, partial comparisons and separate A/B locations |
| M5 CLI/export/replay | Verified | `57f9439`; 280 tests; actual builder/repository/CLI integration, deterministic JSON/CSV and replay |
| M6 review/install/handoff | Engineering verified | `ee89194`; 289 tests, build and fresh-wheel workflow; observed integration blocked |

## Acceptance results

| ID | State | Evidence / limitation |
| --- | --- | --- |
| A1 | Verified | Baseline and final locked gate; all original 227 tests retained; old commands/scenarios preserved |
| A2 | Verified | Strict additive settings, immutable context/traces/runtime, defaulted schema-1 results, null/duplicate-ID rules and coherence tests |
| A3 | Verified | Monthly/quarterly exact queries, age/future/ambiguity, source/basis/statistic distinctions, exact-preferred opt-in proxies and no older/cell fallback |
| A4 | Verified | Frozen invariance, reference/base/start bridge, independent growth/decline values, preserved observations and overflow/underflow rejection |
| A5 | Verified | Exact stages/N budgets, linear/step/plateau sampler, one-unit shares, expense milestones, distinct saver/borrower sets, purchase offset N |
| A6 | Verified | Engine calls match independent savings/mortgage limits and target shortfalls; destination-free preparation and reusable buying helper |
| A7 | Verified | Missing saving/buying, unsupported conditions/selectors/geography, exhausted recovery, viable zero capacity, ratio >1, retained provenance |
| A8 | Verified | CLI/Python equality, leading-zero ordered CSV, finite deterministic JSON, safe publication/cleanup, exact replay and evidence/content mismatch rejection |
| A9 | Verified | 289 tests, strict mypy, Ruff, lock check, nine import contracts, sdist/wheel and fresh installed workflow outside checkout |
| A10 | Blocked, unverified | No permitted observed market release for the real core municipalities; synthetic runs are not that evidence |
| A11 | Verified | Financial engine/config loader/lock unchanged; preserved ownership; no new runtime dependencies or speculative framework |
| A12 | Verified | README, architecture, access handoff and this record reflect supported scope, commands and Phase 5 entry point |

## Checks and actual installed evidence

Session executable `/tmp/phase2-tools/bin/uv`; cache `/tmp/phase2-uv-cache`.

```bash
uv sync --locked
bash scripts/check.sh
uv build
git diff --check
```

Final source gate on Python 3.12.3: **289 tests passed**, strict mypy checked 38
source files, nine import contracts kept, Ruff format/lint and lock consistency
passed. Sensitivity checks prove forbidden application/storage and ingestion
edges, the indirect application→markets→storage edge and markets/finance are
detected. Pure selection/projection have their own repository/storage prohibition.
Build produced `dist/spain_housing-0.1.0.tar.gz` and
`dist/spain_housing-0.1.0-py3-none-any.whl`.

Fresh wheel environment: `/tmp/spain-housing-phase4-wheel.8wnATA/venv`, Python
3.12.9. Installed the wheel with `uv pip install --python <venv>/bin/python
<wheel>`; ran `env -u PYTHONPATH <venv>/bin/python /tmp/phase4-wheel-smoke.py` from
`/tmp`. Imports resolved under that environment's `site-packages`. Actual direct
runtime versions: PyYAML 6.0.3, openpyxl 3.1.5, pydantic 2.13.5, shapely 2.2.0.

The smoke built and validated the fixture release, preserved existing scenario/
market query commands, evaluated both demos over all four municipalities, checked
RunResult/CSV agreement and Python/CLI equality, exported/replayed each run exactly,
refused missing synthetic permission and preserved existing outputs. Saved model,
code and runtime changes failed replay; an actually rebuilt different release
also failed release-ID matching. The real recipe still refused restricted source
use and published no observed release.

Installed calculation code evidence:
`spain-housing-0.1.0/sha256-126d66f723d6f5b2b7a7d2815e31f8038353535159dcb2dba1475c3e53fc36cb`.
Checkout and wheel calculation fingerprints/results were compared using the
**same wheel interpreter and dependency environment**: both demos' economic JSON
was byte-identical. Source gate Python 3.12.3 differs from wheel Python 3.12.9;
exact replay across those different runtimes is intentionally not claimed.

## Demonstration artifacts and reproducible command

Verified release:
`synthetic-aabbe497e620ebfbcd43918d972904e788c0453a6e11153a39d593a247489da5`.
Kind `synthetic`, readiness `synthetic_only`, 11 available of 12 expected cells.
It is under `/tmp/spain-housing-phase4-wheel.8wnATA/releases/`. Both run/export
directories are under that same temporary root, named `phase4_room_demo` and
`phase4_staged_growth_demo`, with separate `-replay` outputs. Temporary test
artifacts are not committed deliverables; rebuild rather than assuming this ID
survives calculation-source changes.

Both runs are ordered Barcelona, Jaén, Getafe, Madrid, with statuses `available`,
`available`, `missing_input`, `available`. Getafe room is a genuine fixture gap;
there are no zero-valued replacement observations. The staged-growth demo has
two savers and one borrower with an explicit expense milestone at offset 3.

```bash
uv run --locked spain-housing build-release \
  --config tests/fixtures/synthetic/pilot/recipe.json \
  --data-root tests/fixtures/synthetic/pilot \
  --release-root data/releases --allow-synthetic
# Set release_dir to the exact path returned above; choose a NEW output directory.
uv run --locked spain-housing evaluate-scenario \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase4_room_demo.yaml \
  --release "$release_dir" --locations 28079 08019 23050 28065 \
  --output-dir outputs/room-demo --allow-synthetic
uv run --locked spain-housing replay-run \
  --run outputs/room-demo/run.json --release "$release_dir" --allow-synthetic
```

## Material decisions and review repairs

- Scenario/result schema stays 1 for defaulted additions. Selection defaults are
  explicit in defaults; existing merge/list/null semantics are unchanged.
- CLI composes the concrete repository. Application gets MarketData and frozen
  context without a repository/storage/ingestion dependency. Geometry stays out
  of economic results. One common fixture builder is in `tests/conftest.py`.
- Selection chooses an eligible profile before querying; no fallback after a
  selected gap. Growth anchors at the last covered month, not offset zero or the
  end boundary; quarterly room evidence remains quarterly. Original observations
  and source labels are retained. Backcasting and fixed-saving runs are deferred.
- Preparation has no buying destination. The combined pool pays one rent share
  and one effective expense budget. Utility flags infer no amounts; milestones
  explicitly change cash spending. Savers enter savings; borrowers enter purchase
  finances at N. Finance alone owns accumulation, exhaustion, capacity and targets.
- Final review repaired early absent-location short-circuiting so all stage
  issues are discovered and unsupported takes precedence over missing. Available
  comparisons require destination purchase evidence. Tests cover nonfinite
  arithmetic/encoding, unbounded CSV flags and actual source changes.
- Economic export has a separate owner from release storage, stages both files,
  refuses existing destinations/cooperative writer locks and cleans only its own
  staging on failure. Replay uses saved resolved inputs and exact evidence;
  no defaults reload, timestamp/random identity or copied saved calculations.

## Remaining blocker and Phase 5 handoff

Only observed integration A10 remains unverified. [Phase 3 progress](PHASE_3.md)
and [data access](../DATA_ACCESS.md) retain the acquisition/use/redistribution
blocker. No provider was contacted and no acquisition was restarted. When a
permitted observed release exists, use the same installed evaluate/export/replay
workflow over the core municipalities and record separate real evidence.

Phase 5 should compose a snapshot and its `evaluation_context` at the launcher,
call `application.evaluate_scenario`, and render typed budgets, savings paths,
borrower finances, limits, shortfalls, indicators and original input traces.
Join separate read-only boundaries by location code/version. Do not recalculate
salary interpolation, rent allocation, market projection or capacity in widgets.
Use explicit synthetic demos while observed readiness is blocked; production
maps must not label fixture values as Spanish market observations.

No independent engineering failures or pending implementation work remain.
On resumption inspect worktree/history and this checkpoint before new work.
