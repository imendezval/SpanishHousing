# Phase 7 progress — real national geography, synthetic economics

Updated 20 October 2026. Execution guide:
[PHASE_7_map_geo.md](../phases/PHASE_7_map_geo.md).

## Current state and resume point

The national map is available with **8,132 official municipalities** and explicitly
synthetic housing prices/rents. The user approved the Bellver/Prullans neutral
intersection treatment on resumption; the earlier pending-approval report is
historical (commit `9b54b40`). Canonical geometry is unchanged. No push, merge,
deployment, provider outreach or external artifact upload occurred.

National geometry, display fidelity/size, both supported Python gates and two
independent installed artifact rebuilds pass. **A9 is not fully verified:** initial
confirmed national browser images take 31–41 s using software graphics, above
the 15 s goal. Backend timings do not establish browser paint performance.
National and partial browser exports are byte-identical to installed core CLI
and replay. Actual release/display transitions, missing/outside/unviable states,
all metric tooltips and restored browser behavior pass. A same-session browser
check also verifies prepared full export/download, retention during staging and
invalidation after Apply. All functional checks are complete; A9 remains open.

### Milestones

| Milestone | State |
|---|---|
| M1 | Complete: actual Phase 5/6 baseline, instructions and contracts inspected |
| M2 | Complete: retained national INE/IGN inputs, exact reconciliation, declared source defect |
| M3 | Complete: independent canonical/display contracts, strict dataset-v2 references, selected national display |
| M4 | Complete: deterministic complete/partial synthetic markets, geographic superset joins and actual national UI |
| M5 | Functional/browser/backend checks verified; browser performance goal remains open |
| M6 | Complete local verification: both gates/build/clean core-map installs, two-root rebuild, restored browser, deferred exports and UI/CLI/replay parity; transfer prerequisite remains |

Started at `ba3580a`, 19 October. The supplied phase guide was the only initial
untracked file and was preserved unchanged. Coherent local commits:
`a7b75fc` baseline; `b3fa655` geography/storage; `f204152` v2/demo/UI;
`08f02d0` compact evaluation; `d38378d` camera actions; `1b6b093` AppTest;
`9b54b40` previous evidence; `9336d90` approved neutral policy; `9362166`
shared-edge retention/precision; `b6e36f9` measured encoding/render size;
`665d1a9` Mercator fitting/legible fills. Final docs/index are committed separately
with a lowercase subject; source and wheel fingerprint are frozen at this code.

## Implementation boundaries

- Separate schema-1 canonical/display artifacts and schema-2 market references;
  original dataset-v1 records/bytes/permissions remain supported. No global
  schema widening or mixed-evidence bypass. Geography paths are explicit inputs.
- Shared storage integrity, permissions, geometry primitives and release pipeline.
  All ten import contracts remain. UI imports no ingestion/storage/finance owners.
- All economics are synthetic, built through the existing normalizer/query/
  evaluator. Financial model remains `finance-v1/scenario-v1`; formulas, market
  selection, scenario/run contracts and canonical serializers are unchanged.
- Atlas/market/evaluation/result joins enforce `E ⊆ M ⊆ A`, `R = E`. Outside
  coverage, missing/unsupported, unviable and valid numeric zero remain distinct.
- National overview/detail/export share the existing evaluation loop. Full
  API/CLI/replay is retained; the overview is never labelled a complete run.
  Two overview memo entries and two full selected details bound session caches.
  Full canonical JSON export is explicitly prepared and invalidated on changes.
- Default target indicator, all three metrics, code-labelled search/picking,
  territorial/province views, zoom/reset, attribution and independent geographic/
  market provenance. No external tiles, tokens or runtime provider acquisition.
- Immutable internal coordinates and public PyDeck compact JSON serialization
  remove measured overhead; detached default projections stay equivalent.
  No custom JavaScript or private widget/protocol state manipulation.

## Official source evidence and geography

Recipe: `configs/sources/national_geography.yaml`. Actual retained bytes and
capture/licence records: `data/raw/national-geography/`.

- IGN: 42 municipal pages, **702,058,118 bytes / 8,213 features**; one province
  page, **187,127,244 bytes / 53 source features**. Full pagination retained.
- INE January 2026: **8,132 codes**, exact complete reconciliation, leading zeroes
  and control digits retained; 619 named crosswalks. Reviewed in-year page has
  no creations/removals and 15 renames; January names remain January names.
- All 52 INE provinces and 81 shared/nonmunicipal context areas. Source collective
  province 53 is excluded only from orientation. Mainland, Balearics, Canarias,
  Ceuta and Melilla are represented. Chafarinas/Alhucemas/Vélez and Isla de los
  Faisanes limitations are explicit, without invented municipal identities.
- Canonical: **14,048 components, 173 holes, 4,443,152 vertices**, 186,469,439
  payload bytes. Original geometry remains unchanged, including one known overlap.
- API and independently retained ATOM feed (5,276 bytes) / CNIG GML archive
  (66,245,318 bytes) reproduce Bellver (25051) / Prullans (25179). Exact source
  fingerprints are pinned; new/changed defects still fail. Original canonical
  report correctly retains `source_coverage_valid: false` and historical notes.
- Approved display-only policy extracts the positive-area polygonal intersection,
  subtracts it from both displayed municipalities and publishes one explicit
  `source_conflict` feature with no economic code/owner. Shared line-only contacts
  are not conflict area. Hover/attribution explain the derivative, not ownership.
  Area is **1,440.944794 m² in local EPSG:25831**, **1,446.027048 m² in mainland
  QA EPSG:25830**: the same source intersection under different metric CRSs.

### Selected display

20/50/100 m bounded preparation retained all original components/holes and valid
shared coverage after the approved patch. Full source geometries remain separate.

| Tolerance | Payload bytes | Result |
|---|---:|---|
| 20 m | 30,305,758 | Geography passes; fails 20 MiB size goal |
| 50 m | **20,673,592 (19.72 MiB)** | Selected, smallest passing tolerance |
| 100 m | 20,030,810 | Compatible optional alternative |

Selected 50 m: **1,201,676 vertices**, 14,049 components including the derived
patch, 173 original holes, 81 original context areas. Maximum relative area
change **1.701928%**; symmetric measured displacement/bound **246.139481 m**;
26 retained features. No 2%/250 m threshold was relaxed.

Metric coverage simplification uses seven decimal display coordinates and one
bounded retention pass. A temporary exterior anchors retained interfaces while
simplifying coast/shared edges consistently; it is never published. Nearly
identical matching vertex sequences use a conservative paired-vertex displacement
bound; others use symmetric densified GEOS Hausdorff QA. Algorithm, CRS, versions
and retained IDs are recorded. Lossless `delta-7-v2` row/delta encoding restores
the same typed, validated polygons. Old GeoJSON/delta-v1 displays stay readable.
The original 50 m probe failed Palma at 270.792 m; intermediate oversized and
interrupted probes are diagnostic history, not accepted artifacts.

## Actual current artifacts

| Component | Content identity |
|---|---|
| National canonical | `geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d` |
| Selected national display | `display-179a320c8ce3602b7ccc970503837f206d1b422f8424be1f574b68fa3dc8ca3c` |
| Optional 100 m display | `display-6ec9ea4fbc50973d7e3edf32adeefe7c881021c9a47db3837e7f3049dd3742ce` |
| Complete synthetic market | `synthetic-5b2e10583ed3460cf983a2e3e75a27d36a3e8ba0860ca842c0bb1f8e4b3d4726` |
| Partial synthetic market | `synthetic-eff8fd7cc93fe292f3f66c4acf892fa784cebe09b222ef58864a011fe5796acc` |
| Madrid canonical | `geography-d1dc47df359e230ed58cd438c11712f6b8b1b0a2301c6524313deb8a804066bf` |
| Madrid display | `display-e330cd9cf47c6edc6cbcc60e054d07efa505a2ed5de2957459816e5a43cc498f` |
| Madrid synthetic market | `synthetic-801f31bc010f5ce1606df19fca9b0530bfdd1fc5ec566bdb93e04d137bba89fe` |

Paths: `data/processed/geography/<ID>`, `data/processed/map-display/<ID>`,
`data/releases/<ID>`. Generated inputs: `data/processed/national-demo-inputs/`.
Exact receipts: `{complete,partial,madrid}-demo-built.json` and
`national-display-built.json` in the raw root. Tracked index:
[`national_geography.json`](../../data/manifests/national_geography.json).
Complete market has 24,396 synthetic observations. Partial has 20 municipalities,
57/60 cells: deliberate Getafe room, Badalona purchase and Palma whole-home gaps.
Original four-/16-/250-location fixtures and historical artifacts are preserved.

## Executed verification

Current package code fingerprint:
`spain-housing-0.1.0/sha256-cceecc838ea4996b53e9b6b29dbef1a7e3aecc7b24d8c3daa4a579db52fc59e8`.
Python 3.12.3; Pydantic 2.13.5, PyYAML 6.0.3, Shapely 2.2.0/GEOS 3.14.1,
pyproj 3.8.0, openpyxl 3.1.5. Second gate: Python 3.13.16.

| Check | Executed evidence |
|---|---|
| Baseline | 329 tests, inspected actual Phase 5/6 implementation and import boundaries |
| Final Python 3.12 gate | **356 passed in 14.71 s**; lock, Ruff format/lint, mypy 62 files, ten contracts |
| Final Python 3.13 gate | **356 passed in 15.18 s**; same other gates |
| Build | Final wheel/sdist built; wheel SHA-256 `1ff3225678a44bc4b77c9499e0d81c77fb4f8da3a7229a5791fa512ff76e8969` |
| Clean installations | Locked hashed core/map dependencies, final wheel (not editable), unrelated `/tmp` cwd, `PYTHONPATH` unset, imports in `site-packages` |
| Financial parity | Independent four-month 13,200 ending / 12,000 usable / 40,000 capacity / 20 m² / ratio 1/3; shared full/overview/detail/JSON/CSV tests; exhaustion, reserves, zero and gaps |
| Geometry | Synthetic topology/error fixtures plus attributed unmodified real IGN pair; source unchanged, no ownership invented, codec integrity and deterministic outputs |
| Legacy/core | Actual Phase 6 v1 release unchanged, 43 available observations; installed core-only query, no Streamlit; serve exits 2 with actionable map-extra guidance |
| Two-root rebuild | `/tmp/phase7-national-restore-a` and `-b`: **380.382 / 373.447 s**; canonical national/regional, selected national/regional display, all generated inputs/releases have identical IDs and payload bytes |
| Hidden raw runtime | Each restored root hides source and generated inputs, then evaluates/exports/replays partial release; full/overview/CSV equality |

### Final national backend measurement

`data/raw/phase7-evidence/national-backend-final.json`; installed map wheel,
8,132 × 84 months, one warm-up plus three timed samples per deterministic path.
Machine: AMD Ryzen 7 7840HS, 8 cores/16 threads, approximately 31 GiB RAM,
Linux x86_64; ordinary development workload, no OS-cache isolation claim.

| Boundary | Measured median |
|---|---:|
| Cold process composition | 7.397 s (single observation) |
| Changed Apply through actual PyDeck serialization | **7.261 s** (6.085 / 7.261 / 7.308) |
| Metric projection/encoding | **1.139–1.156 s** |
| View bounds | 0.774 s |
| Equal Apply | 0.0257 s |
| Selected details, five territories | 14–22 ms each |
| Full export preparation | 8.945 s; 208,770,585 bytes |

Wire Deck JSON: 37,274,074 bytes (earlier pretty serialization was 168 MB).
Loaded current RSS 612,688 KiB; total peak 938,328 KiB; conservative added peak
upper bound **325,640 KiB**, including full export. Two overview/detail entries;
**zero presentation evaluator calls**. These are backend, not browser timings.

### Actual national browser evidence

Chrome 149.0.7827.53, real installed app, actual national artifacts. Headless
SwiftShader/ANGLE software graphics; no `/dev/dri` device is available. National
and dense Madrid screenshots show recognizable boundaries and visible economic
fills. Earlier strong outlines/underfit camera were repaired and retested using
Mercator layout bounds, detailed-view municipal strokes and lighter provinces.

Successful WebGL tooltip/pick identities: Madrid 28079, Cáceres 10037, Palma
07040, Las Palmas 35016, Santa Cruz 38038, Ceuta 51001, Melilla 52001. Rounded
ratios **1.59, 1.51, 1.45, 0.60, 1.34, 1.33, 1.16** agree with exported CSV.
All three metrics, territorial/province controls and zoom/reset were exercised.
The corrected 50 → 100 → 50 m display transition confirms each display ID in
the actual DOM while economic CSV remains byte-identical. Partial-market reload
clears results, reapplies 20 destinations, safely selects Bellver outside coverage,
and verifies Badalona purchase-only and Getafe room gaps, zero and unviable states.
First confirmed images: **31.143 / 32.349 s**, restored-root **40.940 s**
(limited observations, some concurrent verification). Browser control/server
settle measurements of 0.68–0.86 s do **not** establish GPU frame completion.

The installed restored-root browser uses rebuilt national artifacts with raw
inputs hidden. It selects duplicate names **Arroyomolinos 10023 / 28015**, changes
all three metrics and performs a public mouse drag. Visually inspected before/
after-metric screenshots preserve the panned camera and change the metric fills.
Actual WebGL Madrid tooltips agree with exports for all metrics: **1.59 × target
price, 158,157.34 EUR, 95.11 m²**; repeated picking retains code 28079. Successful
browser passes report **zero page errors and zero external requests**.

Complete (8,132 results) and partial (20) browser JSON and CSV are byte-identical
to installed core CLI evaluation and replay. Full baseline run SHA-256:
`bb723d4ee9b781638c07d74adfc760dbd56d1e76eb6f65fc1492a1445323ab1a`.
Core import/query/evaluate/replay uses no Streamlit and runs outside the checkout.
Evidence root: `data/raw/phase7-evidence/`; actual proofs live in
`national-browser/`, `national-restored-browser/`, `national-metric-browser/`,
`national-cli.json`, `national-backend-final.json` and `national-restore-{a,b}.json`.
`national-deferred-browser/proof.json` verifies a fresh full preparation/download
has that same SHA-256, staging retains it and its economic CSV, then Apply removes
the prepared download and publishes an available zero-capacity national summary.
The check uses a single actual browser session against the installed restored app.

Harness corrections are retained honestly in separate logs: muted selection
highlight is valid; streamed rerenders require waiting for the expected download;
file upload success is HTTP 204. The first `serve` wrapper resolved symlinks once
at startup, so its pointer swaps did **not** prove artifact transitions. Corrected
transition tests use the installed public Streamlit launcher with explicit
symlink arguments; production `serve` stays unchanged and is separately verified
against restored immutable paths. The final display IDs are confirmed in DOM,
and the market transition confirms 20 destinations and cleared/reapplied state.
Earlier failed assertions are diagnostic history, not full passing runs. Browser
proofs aggregate several explicitly identified passes under the same final code/
runtime, rather than pretending all actions occurred in one pass. The 48.048 s
first resource/DOM readiness observation in the continuation receipt excludes a
screenshot and is **not** a confirmed-paint timing.

## Portable availability and handoff

Actual local bundle: `data/raw/phase7-national-portable.tar.gz`, **231,109,766
bytes**, SHA-256
`c9477f3c6d38130611675dbaf70c503ffbefc217606291628966f7506c7f7428`.
Receipt: `data/raw/phase7-national-portable.json`. Contains actual retained official
captures, canonical national/regional atlases, selected/alternate/regional
displays, complete/partial/regional synthetic inputs/releases, final wheel,
configs, lock and hashed requirements. Both new independent rebuilds use it.
Verification sidecars/screenshots are retained separately, avoiding a self-hash
cycle. The previous regional-only archive is historical.

This is an ignored **local archive**, not an off-machine backup or a published
download. A fresh Git clone has no large data. Copy the actual archive plus receipt
to the destination, verify checksum and follow [GEOGRAPHY.md](../GEOGRAPHY.md)
for venv/conda, rebuild, query/evaluate/replay and serve. No durable transfer
destination is authorized; transfer remains a separate prerequisite.

| Acceptance | Current state |
|---|---|
| A1 | Verified: baseline/instructions/user changes and execution evidence |
| A2 | Verified: existing financial/selection rules and module boundaries |
| A3 | Verified: strict artifact/version/provenance and legacy compatibility |
| A4 | Verified with declared original source defect and special territories |
| A5 | Verified: complete deterministic neutral display, topology/fidelity/size |
| A6 | Verified: deterministic explicitly synthetic complete/partial products |
| A7 | Verified: joins/tests/restored evaluation and actual missing/outside/zero/unviable browser states |
| A8 | Verified: actual national rendering, all metric tooltips, territory/code picks, duplicate names, views/pan and financial states |
| A9 | Backend targets verified; initial/interactive browser paint goal **unverified** |
| A10 | Verified: core/legacy, actual artifact transitions, full/partial UI/CLI/replay parity, staged/invalid state and same-session prepared-export invalidation |
| A11 | Verified locally: both gates/build/clean installs/two-root rebuild and restored browser; off-machine transfer unavailable |
| A12 | Verified: docs/progress/index distinguish actual artifacts, performance limits and observed-data readiness |

Do not claim full A1–A12 completion: **A9 remains open**. Final receipts, drivers,
logs, screenshots and downloads are retained under the evidence root; the tracked
index contains the small proof summaries and hashes. The next verification step
is hardware-accelerated browser measurement,
including completed-frame rather than control-acknowledgement timings. No GPU
pass-through is available here. Bounded display, serialization and styling repairs
are complete; no topology, population, horizon or financial limit was weakened.

Next feature remains **save in fixed A, buy in B**, with explicit borrower income
at purchase. Observed housing acquisition/use/redistribution remains blocked and
is separate from this geography demonstration. No salary realism, historical
reconstruction, tax rules or new financial mode was added in Phase 7.
