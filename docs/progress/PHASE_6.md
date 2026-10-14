# Phase 6 progress

Status: **MVP engineering/browser verified; observed expansion blocked**,
14 October 2026. Independent M1–M6 work is finished. **A11 remains blocked and
unverified; full Phase 6 completion is not claimed.** No other engineering task
or failed check remains. Baseline `3972ea3` contains actual completed Phase 5,
which was absent from the guide's published-repository inspection. Do not reset
to the remote Phase 4 baseline.

Local checkpoints: `60ab273` (coverage/preparation/official geography), `4a26bf5`
(expanded evaluation/cache/scaling/reproduction), followed by final documentation
verification commit. No push, merge, deployment, provider contact or paid/account
access. User-owned untracked AGENTS.md and Phase 2–6 guides remain untouched and
excluded from commits. Original pilot, historical audit, finance, selection/query,
export and scenario schemas/rules are preserved.

## Milestones and acceptance

| Milestone | State | Actual work/evidence |
|---|---|---|
| M1 actual baseline | Verified | 310 unchanged tests; actual Phase 5 launcher/services/cache/map/import/download contracts inspected and exercised |
| M2 bounded source/product decisions | Verified decisions/geography; markets blocked | Sixteen official codes/control digits/full IGN features; three-candidate review frozen; exact products/core/rights/gaps documented |
| M3 preparation/expansion | Engineering verified | Capture/row/profile/locator diagnostics; existing builder with generated 16/250 inputs; drift/corruption fails before publication; observed recipe refuses restricted use |
| M4 coverage/runbook | Verified | Immutable schema-1 report, public snapshot property, offline CLI and injected UI; actual archive restore/rebuild and runbook commands |
| M5 UI/scaling | Verified for synthetic engineering | Expanded/partial parity; real browser, release transitions, measured timings/call counts; no unjustified optimization |
| M6 installation/handoff | Engineering verified | Full two-runtime gate/build, fresh core/map wheels outside checkout, matching source/UI/CLI/replay bytes; A11 blocked |

| Criterion | State | Evidence / limitation |
|---|---|---|
| A1 | Verified | Actual local Phase 5 inspected; baseline gate re-established; prior user files preserved |
| A2 | Verified | Ten contracts including pure coverage/indirect reader sensitivity; original 310 tests retained; no finance/query/export changes or new dependency/framework |
| A3 | Verified scope/decisions | Sixteen authoritative identities; exact September pooled asking purchase/rent and Q2 mean room definitions; usage blockers and all 48 observed gaps explicit |
| A4 | Verified engineering | Nine drift/corruption cases fail before publication; prior release bytes intact; identical retained-byte rebuilds; official geography archive restores exactly |
| A5 | Verified | One frozen schema-1 report; counts/order/evidence agree with validated cells/reader/CLI; source availability stays distinct from scenario suitability |
| A6 | Verified engineering | Expanded older-available/newer-gap has no fallback; exact bedroom variant and mismatch; stale/proxy/status behavior preserved; hypothetical observed/estimated counting test cannot publish mixed inputs |
| A7 | Verified | Real services inject same report; no city list/index bypass; AppTest 16→4 transition clears old run/memo/downloads and preserves draft; reset retired code; expanded UI/CLI parity |
| A8 | Verified for supplied synthetic bytes | Tested installed restore/build→validate→inspect→evaluate/export→replay→serve in clean core/map environments and two independent roots; observed acquisition/reproduction remains blocked |
| A9 | Verified | Four/16/250 medians and evaluator/validation call counts below; no measured bottleneck, justified no-change decision |
| A10 | Verified engineering/browser | 329 tests on Python 3.12.3 and 3.13.16; typing/Ruff/lock/contracts/build; fresh wheels, actual Chrome/WebGL/edits/import/reload/rollback proof; CI config matches local gate |
| A11 | Blocked, unverified | No authorized 12+ municipality observed market release or retained market bundle; official geography and synthetic observations cannot satisfy it |
| A12 | Verified | README, architecture, DATA_EXPANSION, RUNBOOK and this handoff describe actual scope, source decisions, verification and next extension |

## Implementation and material decisions

`models/coverage.py` and pure `markets/coverage.py` aggregate existing validated
cells/observations, not a second coverage generator. The snapshot constructs its
immutable `coverage_report` once. `inspect-release` uses the existing canonical
encoder and performs no network/ingestion/evaluation/output mutation. Frozen
Services carries that same report into a compact UI expander, separately from
applied financial results. No private index or infrastructure access in UI.

Preparation context belongs to existing CSV/normalize/build owners. Schema,
locale, unit, period, profile, source/geometry and capture failures are errors,
not replacement missing prices. Source-declared unsupported coverage is separate
from existing exact-query capability: an absent row of a supported profile still
returns missing. Complete/fresh/exact/proxy/no-fallback policies are unchanged.

The original four-city fixture is untouched. One deterministic helper,
`tests/fixtures/synthetic/expand.py`, prepares independent 16/250 inputs through
real builders/readers. Standard 16: 48 expected, **43 available, 4 missing,
1 source-declared unsupported**. Getafe/Badalona/Mislata lack rooms; Teruel lacks
purchase; Dos Hermanas lacks supported source rent. A test variant provides exact
flat/two-bedroom evidence (59/64 available). Labels/counting branches for observed/
estimated records use hypothetical unit-test inputs only; storage rejects their
publication in a synthetic release. No fake observed release was created.

## Source/geography readiness and backup

Bounded review of three candidates is frozen in [DATA_EXPANSION](../DATA_EXPANSION.md):
Idealista copying remains restricted without permission; SERPAVI 2026 sample
references tax-derived 2024 rentals, not current asking/room data; official
municipal valuations are not selected asking prices. One bounded follow-up for
inaccessible official pages was performed. No market capture, automatic fallback,
provider negotiation or further indefinite search. The observed expanded build
exits 2 for restricted local acquisition/use before publishing any release.

All sixteen shortlisted INE codes/control digits match retained actual 2026 XLSX
bytes. Current INE in-year changes were captured/reviewed; none affect the target.
Existing permitted official adapter captured twelve additional complete IGN
responses. Existing registry/geometry owners verify all sixteen MultiPolygon
records with original parts/holes, no clipping/repair/simplification. Official
València uses explicit selected source label Valencia. Original three-city core
remains unchanged. `expanded.yaml` is an observed **blocked recipe**, not market
readiness; no synthetic rows were inserted into it.

Retained raw: `data/raw/expanded-geography`; derived:
`data/processed/expanded-geography`; small committed references:
`data/manifests/expanded_geography.json`. Actual local archive:
`data/raw/phase6-backups/expanded-geography-20261014.tgz`, 1,536,830 bytes,
SHA-256 `8add4ce857d7f38d494d73d693c952e0f74ef766a1654a9e44cd302b3919e788`.
Archive includes original bytes, sidecars, recipe and reference. Restore into
`/tmp/phase6-official-restored` passes existing geography verification; both
derived files compare byte-identically. This is a local backup, **not off-machine
transfer**. URLs/hashes alone are not retained data. Observed market reproduction
still needs actual permitted bytes and rights.

## Quality and installed verification

Toolchain restored under `/tmp/phase6-tools` (uv 0.13.0), cache
`/tmp/phase6-uv-cache`; old temporary Phase 5 tools/datasets were not assumed to
survive. Initial gate failed for missing uv before any tests; repaired. Ordinary
new test setup/import/expected-status failures and browser selector automation
failures were repaired; no tests were removed/skipped to obtain a passing gate.

Executed:

```bash
uv sync --locked --extra map
bash scripts/check.sh
uv build
git diff --check
```

Final gate **329 passed** on Python **3.12.3** and **3.13.16**; strict mypy on 49
package files, Ruff format/lint, lock consistency and **10 kept contracts**.
Python 3.13 run explicitly used `UV_PYTHON=/tmp/phase6-python/cpython-3.13-linux-x86_64-gnu/bin/python3.13`
and `UV_PROJECT_ENVIRONMENT=/tmp/phase6-check313` so the active conda interpreter
could not silently replace it. CI job now `quality`, Python 3.12/3.13 matrix,
map-enabled sync/full gate/build. **Remote GitHub CI was not executed** (no push).

Fresh environments `/tmp/phase6-wheel-core` and `/tmp/phase6-wheel-map`, Python
**3.12.9**, installed from the built wheel with lock-exported non-dev dependencies.
Every installed command ran from `/tmp` with `PYTHONPATH` unset; imports resolve
to each environment's `lib/python3.12/site-packages/spain_housing/__init__.py`.
Core contains no Streamlit/PyDeck, preserves help/validate/evaluate/replay, and
serve exits 2 with useful missing-extra guidance. Map uses packaged installed
launcher, not checkout apps. Final wheel updated README metadata without changing
any tested package code bytes; fingerprint was checked after installation.

Both restore the actual synthetic archive into independent a/b roots, rebuild
identical release IDs/files, validate/inspect, evaluate/export both room and
staged-growth demos, replay byte-identical JSON/CSV, reject corruption without
altering old releases, and roll back to four-city. Evaluation still works after
raw captures are removed. Installed CLI build/validate/inspect were also exercised
at `/tmp/phase6-cli-restored`. Artifacts/evidence: `/tmp/phase6-core-proof`,
`/tmp/phase6-map-proof`, their adjacent `.json` records, and temporary
`/tmp/phase6-wheel-smoke.py`. Runbook documents the exercised portable steps.

Source/wheel full JSON and CSV compare exactly for both demos under the **same
map-wheel interpreter/dependencies** (`/tmp/phase6-source-reference` and
`/tmp/phase6-wheel-reference`). Browser downloads also exactly match installed
CLI and replay (`/tmp/phase6-browser-cli`, `/tmp/phase6-browser-replay`). No exact
cross-Python-version replay is claimed. Runtime: PyYAML 6.0.3, openpyxl 3.1.5,
pydantic 2.13.5, shapely 2.2.0; model `finance-v1/scenario-v1`; package evidence:
`spain-housing-0.1.0/sha256-3ef29d081932fe1c99796623c7374cabd657d820e77c1e23fbca2755a31969b5`.

Synthetic expanded release:
`synthetic-890aef2f82b6631b3c82321da1bfc91216dc802e3662ac2d65f338a19fe59c59`.
Old IDs may change when processing/model source changes; both release and economic
fingerprints are preserved, never edited to force replay.

## Browser proof

Chrome **149.0.7827.53**, temporary Playwright **1.64.0**, headless SwiftShader.
Installed launch from `/tmp` with absolute inputs, loopback 8671, map extra:
`/tmp/phase6-wheel-map/bin/spain-housing serve --defaults <checkout>/configs/defaults.yaml
--scenario <checkout>/configs/scenarios/phase4_room_demo.yaml --release <expanded release>
--allow-synthetic --port 8671`, `PYTHONPATH` unset.

Temporary scripts `/tmp/phase6-browser-proof.py` and
`/tmp/phase6-transition-browser.py`; results
`/tmp/phase6-installed-browser-final.json` and `/tmp/phase6-browser-transition.json`.
Artifacts `/tmp/phase6-browser-evidence` include coverage/three metric screenshots,
Madrid hole/picking, Barcelona multipart after rollback, run/scenario/CSV,
flat run, invalid-edit/import previous runs and rollback run. These are local
verification artifacts, not committed datasets or durable evidence storage.

Actual checks: Fit reveals all sixteen sparse fixture shapes; legends, holes/
multipart and code joins retained; report shows 43/48 independently of suitability;
Teruel retains positive capacity with missing purchase comparison; Badalona room
is missing and a real clipboard stage edit to 80 m² flat-alone becomes available.
All three metrics switch without economic-content changes; Madrid hover/pick code
28079, selector/zoom agree. Invalid horizon and duplicate-key upload retain
byte-identical previous downloads; correction works. Reload removes applied
outputs until Apply. External requests blocked, **zero attempted, zero page errors**.
Public accessible Open buttons/search were used after early selector automation
assumptions failed; no private protocol/widget-state manipulation.

Actual explicit server restart/rollback from sixteen to four clears retired
Badalona selection (08015→08019), shows new context/geometry and four-result
new-release download; Barcelona multipart rendered. AppTest also verifies the
same-session injected service transition: old applied run/memo/downloads cleared,
draft retained, retired inspection code reset on Apply. No UI release picker or
implicit latest selection was introduced; restart is the documented selection path.
Installed first-applied display ~1.4 s (one observation; includes 700 ms settling),
source ~2.7 s; not a national complex-geometry rendering benchmark.

## Scaling and no-change decision

`scripts/measure_scaling.py --work-root <new root>`: three samples, perf_counter
medians. Linux 6.8 x86_64, AMD Ryzen 7 7840HS, ~32 GB RAM, Python 3.12.3.
Logical cold validation means a fresh fully validated snapshot per sample;
OS disk-cache coldness is not claimed. Same package evidence above. Counts:
three profiles, 11/43/745 observations, 30/90/1260 vertices; lightweight synthetic
geometry only. Actual code/release/runtime/geometry bytes are in
`/tmp/phase6-measurements-final.json`.

| Locations / months | Validate+index ms | Evaluate ms | Report ms | Map preparation ms | Equal memo ms |
|---|---:|---:|---:|---:|---:|
| 4 / 12 | 1.96 | 5.33 | .045 | .033 | .142 |
| 16 / 12 | 3.40 | 6.76 | .085 | .112 | .142 |
| 250 / 84 | 40.62 | 274.52 | .959 | 1.516 | .425 |

Initial medians ~6/8/306 ms informed local targets: <100 ms at 16, <1 s at 250/84,
<5 ms equal memo, <5 s first applied browser display. Current measurements meet
these targets. Changed-reserve Apply ~5.93/6.70/399.39 ms. First Apply calls
evaluator once; equal and presentation add zero; changed reserve adds one.
Two cached compositions validate once. No material bottleneck justifies another
optimizer, workers/database, tracing omissions or simplified geometry.

## Remaining inputs and next handoff

Only **A11** remains unverified: documented permitted acquisition/local use and
redistribution (or a compatible approved replacement), actual retained purchase/
whole-home observations across at least twelve municipalities with eight beyond
the original four, and original Madrid/Barcelona/Jaén room core. Then rebuild,
inspect and run this same installed CLI/map/replay workflow with real geometry
and correct source labels. Do not present sixteen synthetic municipalities or
verified official geography as observed market expansion.

Next essential feature: **save in A, buy in B**, preserving independent bindings,
destination-free saving preparation, reusable purchase service and an explicit
purchase-time income assumption. Salary realism and historical reconstruction
remain later work. Use existing modules rather than repairing hidden formulas or
introducing another loader. See [runbook](../RUNBOOK.md),
[data decisions](../DATA_EXPANSION.md) and [architecture](../ARCHITECTURE.md).
