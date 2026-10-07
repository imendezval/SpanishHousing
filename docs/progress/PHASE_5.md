# Phase 5 progress

Status: **engineering and browser verified; observed-data integration blocked**,
8 October 2026. Independent M1–M6 work is complete. A11 remains blocked and
unverified; synthetic releases do not satisfy observed-data readiness.
Baseline `ff7fb63` passed 289 tests. Local implementation commits: `3c7a26f`
(foundation/controls/map/details), `bd21cbd` (browser repairs/lifecycle/parity),
`4d07c42` (evidence badges/import reruns), followed by the final
verification/documentation commit. No push, merge or
deployment was performed. User-owned untracked AGENTS.md and Phase 2–5 guides
remain untouched and excluded from commits.

## Milestones and decisions

| Milestone | State | Evidence |
|---|---|---|
| M1 baseline/composition | Verified | Optional locked map extra; packaged `serve`; ten import contracts, including launcher bypass edges |
| M2 controls/parser/state | Verified | Complete lossless controls; shared safe parser; atomic import and widget epoch reset; invalid drafts retained |
| M3 applied/cache/downloads | Verified | Personal LRU32; immutable resource LRU4; actual manifest-byte/permission keys; identity validation and existing encoders |
| M4 joins/map/selection | Verified | Strict detached code/level/version join; holes/multipart preserved; three fixed legends; plain tooltip/code picking and selector fallback |
| M5 details/browser | Verified for synthetic demonstrations | Returned limits/budgets/signed paths/source traces; AppTest and real Chrome edits, imports, statuses and selection |
| M6 gate/wheels/handoff | Engineering verified | 310 tests, build, fresh core/map wheels outside checkout and exact source/UI/CLI/replay comparisons; A11 blocked |

Composition uses explicit defaults/scenario/release paths and the active Python
interpreter. The Streamlit script calls the imported launcher module, preserving
its bounded shared immutable cache across reruns. Reload revalidates artifacts
and clears the requesting session's applied run/memo. Salaries, drafts, selections
and run memo remain session-local. Memo identity includes the entire scenario,
ordered destinations, release, model, actual code fingerprint and runtime.

UI performs representation, validation orchestration and presentation only.
Existing evaluator/configuration/serializers own economic and persistence rules.
Imported independent bindings, future milestones, optional selectors and growth
assumptions are retained; fixed saving remains deferred. Changes to the horizon
do not adjust stages silently. Downloads use `on_click="ignore"` and identify
the last applied scenario. Imports require Apply; invalid submissions retain
explicitly previous results and downloads.

Browser testing found that passing an explicit None/empty PyDeck style causes
Streamlit to supply remote CARTO tiles. Keeping the public no-provider default
avoids that fallback; actual requests were blocked during verification, with
zero external requests attempted. Resource-cache lifetime across script reruns
was also repaired. Early browser automation attempts failed on grid focus and
numeric editor events; final proof uses real keyboard/clipboard grid interaction,
without private widget-state manipulation. A reference-check assertion was
corrected to the existing calculation status `missing_input`; no status/domain
rules were changed.

## Acceptance evidence

| Criterion | State | Actual evidence |
|---|---|---|
| A1 | Verified | Original commands/scenarios and all 289 baseline tests retained; architecture sensitivity tests and ten contracts pass |
| A2 | Verified | Streamlit 1.65.0/PyDeck 0.9.3 locked in map extra; installed public module launch; fresh core has neither dependency |
| A3 | Verified | Four original scenario roundtrips; complete participant/path/stage/policy controls; future paths and independent bindings retained |
| A4 | Verified | AppTest edit/apply/error correction and staged import reset; real browser invalid coverage retains previous applied download, import repairs draft |
| A5 | Verified | Session isolation/memo hits/evidence invalidation/LRU32 eviction; resource max4, manifest/permission identity; explicit reload catches same-manifest artifact corruption; presentation causes no evaluator calls |
| A6 | Verified | All three metric bins/edges/zero/open-end/ratio >1; detached geometry and rejected malformed joins; browser hole/multipart, picking, selector and zoom |
| A7 | Verified | Returned purchase limits/shortfalls, budgets, purchase finances, signed paths, source intervals/anchors/growth/proxies; browser negative path and unbounded cash caption |
| A8 | Verified | Safe JSON/YAML/UTF-8/1 MiB import failure tests; room/growth UI-applied JSON/CSV equal ordered CLI; installed browser bytes equal installed CLI and replay exactly |
| A9 | Verified | Locked full gate, build, diff check; fresh core and map environments outside checkout; exact source/wheel economic output under identical interpreter/dependencies |
| A10 | Verified | Chrome 149.0.7827.53 real WebGL rendering, hover/code picking, selector/zoom, metrics/statuses, dynamic path/stage rows, changed assumptions, invalid Apply and import recovery; external requests blocked |
| A11 | Blocked, unverified | No authorized observed market release; inherited acquisition/local-use/redistribution blocker, despite retained official pilot geography |
| A12 | Verified | README launch/controls/limitations; architecture/service/cache boundaries; this evidence and Phase 6 handoff |

Final full gate: `bash scripts/check.sh` with `/tmp/phase2-tools/bin` on PATH and
`UV_CACHE_DIR=/tmp/phase2-uv-cache`: **310 passed**, strict mypy on 46 source
files, Ruff format/lint, lock consistency and **10 kept import contracts**.
`uv build` produced sdist and wheel; `git diff --check` passed.

Independent fixture reference confirmed in actual browser download: Madrid
usable savings EUR 11,400 / max EUR 38,000 / area approximately 12.6667 m²;
Barcelona EUR 10,800 / EUR 36,000 / 14.4 m²; Jaén EUR 13,200 / EUR 44,000 /
44 m². Mortgage limit EUR 225,000; Getafe calculation `missing_input` and map
missing room state. Float comparisons use tolerance without altering values.

## Installed and browser reproduction

Release built with the actual synthetic builder and validated reader:
`/tmp/phase5-releases/synthetic-aabbe497e620ebfbcd43918d972904e788c0453a6e11153a39d593a247489da5`.
Its readiness is `synthetic_only`: 11/12 expected cells, explicit missing Getafe
room. Both market observations and geometry are fixtures, not real evidence.

Final wheel environments: `/tmp/phase5-final-core`, `/tmp/phase5-final-map`,
Python **3.12.9**. Both imports resolve to their own
`lib/python3.12/site-packages/spain_housing/__init__.py`. Commands executed from
`/tmp`, with `PYTHONPATH` unset, using absolute explicit inputs. Core help,
scenario validation, evaluation and replay pass; Streamlit/PyDeck are absent;
serve exits 2 with a useful missing-extra instruction. Installed release
validation also passed. Map extra starts the packaged launcher on loopback:

```bash
env -u PYTHONPATH /tmp/phase5-final-map/bin/spain-housing serve \
  --defaults /home/inigo/data/git/repo/SpanishHousing/configs/defaults.yaml \
  --scenario /home/inigo/data/git/repo/SpanishHousing/configs/scenarios/phase4_room_demo.yaml \
  --release /tmp/phase5-releases/synthetic-aabbe497e620ebfbcd43918d972904e788c0453a6e11153a39d593a247489da5 \
  --allow-synthetic --port 8661
```

Chrome ran headless with SwiftShader through temporary Playwright 1.63.0 in
`/tmp/phase5-browser-env`. Verification scripts:
`/tmp/phase5-map-proof.py`, `/tmp/phase5-paste-proof.py`,
`/tmp/phase5-status-browser.py` and `/tmp/phase5-case-browser.py`, run with
`PHASE5_PORT=8661`. Final isolated status checks use `PHASE5_CASE=growth`,
`unsupported`, `unviable` or `unbounded`. Automated waits for exact uploaded
filename text failed; final isolated checks awaited the enabled staging button
and passed with no browser errors or external requests.
Artifacts/downloads are in `/tmp/phase5-browser-proof` (temporary local evidence):
`tile-free-picked-map.png`, `selected-missing-zoom.png`, metric/status screenshots,
`pasted-income.json`, `deleted-income.json`, `pasted-stages.json`,
`invalid-stages-previous.json`, `repaired-stages.json`, `run.json`, `summary.csv`.

Actual dynamic edits: income 24,000 → 30,000, future offset-24 income 42,000
added and deleted; living stages split into room offsets 0–6 and shared-flat
6–12 with 80 m²/50% pool share. Deleting the latter causes a coverage error and
preserves the previous applied download. Reimport/Apply restores the room draft.
All three metrics were switched; reserve-induced zero remains available,
1 m² target produces ratio >1, new condition gives unsupported indicators with
available capacity, high expenses exhaust savings and preserve negative path,
100% financing/zero costs displays **No cash constraint**. Staged growth import
uses two savers/one borrower and all original stages/growth assumptions.

Source/wheel and installed browser/CLI/replay JSON and CSV matched byte for byte.
Explicit destination order: **08019, 23050, 28065, 28079**. CLI outputs:
`/tmp/phase5-final-map-cli`, replay `/tmp/phase5-final-map-replay`;
core `/tmp/phase5-final-core-run` and `/tmp/phase5-final-core-replay`.
The installed browser's applied growth JSON also exactly matches
`/tmp/phase5-final-map-growth-cli/run.json`.
Source/wheel comparison used the final map interpreter/dependencies with source
path enabled only for the separate source reference. Final package fingerprint:
`spain-housing-0.1.0/sha256-c5133a3daf254a627ecb7302df0b87506abfaf6911904087750938ece92c5ada`.
Actual economic runtime: PyYAML 6.0.3, openpyxl 3.1.5, pydantic 2.13.5,
shapely 2.2.0; model `finance-v1/scenario-v1`.

## Remaining blocker and Phase 6 handoff

No independent engineering task remains. A11 requires documented acquisition,
local-use and redistribution permission (or an explicitly permitted replacement
source), the real core market cells and a validated observed release. Then run
this same installed UI/CLI workflow against real official geometry and inspect
source labels/coverage. See [Phase 3](PHASE_3.md), [Phase 4](PHASE_4.md),
[access requirements](../DATA_ACCESS.md) and retained source decisions.

Phase 6 is broader coverage and a reproducible MVP: expand locations/segments
from permitted observed coverage, document source updates and any fallback rules,
measure performance before optimizing, and verify operation in another environment
with partial-coverage UI/integration checks. Diagnose source/schema failures at
release preparation. Extend presentation through current evaluator/service/result
boundaries; keep financial rules, acquisition, serializers and immutable geometry
in their existing modules. Fixed-saving mode, promised national coverage,
historical reconstruction and new financing/tax models remain deferred. Continue
explicit synthetic demonstrations while observed readiness is blocked; do not
describe the pilot as production observed-data integration.
