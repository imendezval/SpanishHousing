> Resumed 20 October 2026: user explicitly approved the neutral intersection
> display treatment. The previous approval blocker below is historical.
> Canonical source artifacts remain unchanged. Implementing opt-in declared
> neutral display patches, then national fidelity/performance/browser/wheel QA.

# Phase 7 progress — national geography, synthetic economics

## Status and next action

**Phase incomplete: national display preparation is blocked by an official-source
boundary overlap and the pending user decision.** Independent implementation,
national synthetic economics, regional browser and available-artifact packaging/
restoration work are complete. Do not infer permission from elapsed time.

Both official IGN API and independently downloaded CNIG GML contain the same
Bellver de Cerdanya (25051) / Prullans (25179) overlap: **1,440.945 m²** in
EPSG:25831. Canonical coordinates stay unchanged. The asynchronous question asks
whether the display should retain the intersection as explicitly neutral
“source boundary conflict”, assigning it to neither municipality, or remain
blocked pending official correction. That display exception is **not implemented**.
The guide §5.3/§6 forbids arbitrary ownership/silent cleaning and requires an
explicit preparation decision. Existing display preparation refuses this source.

**Next:** obtain that decision; if approved, implement only the exact pinned
conflict's declared neutral display treatment, test unchanged canonical identity
and coverage/fidelity, then complete national 20/50/100 m bounded QA, browser and
full-map scale evidence. Otherwise retain the national display blocker. Observed
price acquisition/use remains a separate blocker, not solved by official maps.

## Milestones

| Milestone | Actual state |
|---|---|
| M1 | Complete: brief/plan/architecture/data decisions, Phase 5/6 implementation/instructions inspected; actual baseline verified |
| M2 | Complete retained national identities/source artifact with explicit original topology defect; all registry codes reconciled |
| M3 | Regional display and dataset-v2 composition complete; national display blocked |
| M4 | Complete/partial national synthetic inputs and UI engineering complete; national rendered demonstration blocked |
| M5 | Economic scaling/compact parity and regional installed browser verified; national map/browser targets unverified |
| M6 | Final wheel/core/map, two Python gates and two-root available-artifact reproduction verified; full phase acceptance blocked by national display |

Started at `ba3580a`, 19 October 2026. The supplied phase guide was the only
untracked starting file and was preserved unchanged. No push, merge, deployment,
provider contact or external artifact upload occurred. Local commits:
`a7b75fc` baseline/guide; `b3fa655` geography/storage; `f204152` dataset-v2/demo/UI;
`08f02d0` bounded overview/detail/export; `d38378d` explicit camera actions.
Current implementation checkpoint: `d38378d`; compact Streamlit coverage is
committed separately. Final evidence/docs commit follows these checkpoints.

## Implementation and compatibility

- Independent canonical/display schema-1 artifacts; strict dataset-v2 references.
  Old dataset-v1 fields, embedded geometry and permission restrictions preserved.
- Shared storage bytes/paths/atomic publication, permissions and polygon rules;
  no duplicate persistence or finance pipeline. Explicit runtime geography paths.
- Complete retained pagination, exact INE joins, source/name/context evidence.
  Canonical source validation permits only the two inspected original geometry
  fingerprints; every changed/additional defect still fails. This does not
  approve those polygons for shared-coverage simplification.
- Packaged deterministic code/seed-based synthetic generator feeds the existing
  normalizer/query/evaluator. Logical generator epoch is not a provider timestamp.
- Atlas/market/evaluation/result joins enforce `E ⊆ M ⊆ A`, `R = E`. Context,
  outside coverage, not evaluated, missing, unsupported and unviable are distinct.
  Default target metric, all three indicators, code selection and territory/
  province controls are implemented; geography never enters finance.
- Measured linear membership scans were replaced with an immutable cached index.
  Full national trace retention exceeded 1 GiB additional memory; a distinct
  `RunOverview` projects the same shared result iteration. Two overview memo
  entries, two full selected details and explicit current full export are bounded
  by applied identity. Detail/export checks pinned evidence and numeric parity.
  Canonical full JSON and CSV have one owner; API/CLI full runs/replay remain.
- Explicit camera actions advance chart revision; metric controls keep economic
  identity. Zoom uses a callback before rerender. Small-run behavior remains.
  Pyproj 3.8.0 is declared/locked for metric geometry; financial model remains
  `finance-v1/scenario-v1`, with no formula or selection-policy changes.

## Sources and actual artifacts

Source recipe: `configs/sources/national_geography.yaml`. Raw root:
`data/raw/national-geography/`, with original bytes, capture records, inventories,
registry/changes, licences, service metadata and alternate feed/ZIP.

- 42 municipal pages, 702,058,118 bytes, 8,213 features; one province page,
  187,127,244 bytes, 53 source province features.
- INE January 2026: **8,132 municipalities**, all matched, 619 retained name
  crosswalks; current change page reviewed: no creations/removals, 15 name changes.
  January labels remain explicitly January labels, including October renames.
- **81 neutral shared/nonmunicipal areas**; all **52 INE provinces** retained.
  Collective source province code 53 is excluded from orientation, not from
  underlying neutral context. Mainland, Balearics, Canarias, Ceuta/Melilla present.
  Chafarinas/Alhucemas/Vélez and special Isla de los Faisanes limitations are
  explicit; no false municipal identities are created.
- Canonical: 14,048 components / 173 holes / 4,443,152 vertices;
  186,469,439 payload bytes. Known original overlap remains; coverage is false.
- Alternate retained ATOM feed 5,276 bytes / GML ZIP 66,245,318 bytes independently
  reproduce the same defect. No alternate-feature patch was substituted.

| Artifact | Final content identity |
|---|---|
| National canonical | `geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d` |
| Madrid canonical (179 municipalities) | `geography-d1dc47df359e230ed58cd438c11712f6b8b1b0a2301c6524313deb8a804066bf` |
| Madrid display | `display-3018daeaf69b898617c881a5a725395c52d2c2478328a45b5625c62548ad9497` |
| Complete synthetic release (24,396 observations) | `synthetic-56ef26321a2cec83299334af7b6d9ea9b8fa37e2e0db92d74c4fce95ebf007d6` |
| Partial synthetic release (20 municipalities; 57/60 cells) | `synthetic-5cd6638621c6bdb07c99666af101f8e8b2660fe8a66d4b13afa6664847c973c6` |
| Madrid synthetic release | `synthetic-d4c90f6afb5bcb790c8e498b1a9ee5aaae9a85c25421d3c629960224cc78e3ea` |

Canonical artifacts: `data/processed/geography/<ID>`; display:
`data/processed/map-display/<ID>`; releases: `data/releases/<ID>`. Generated
inputs are under `data/processed/national-demo-inputs/`; exact paths and IDs are
in `{complete,partial,madrid}-demo-built.json` in the raw root and the tracked
[`national_geography.json`](../../data/manifests/national_geography.json).
Madrid display: 50 m, 946,036 bytes, 22,629 vertices, worst area 0.1682%, measured
symmetric densified Hausdorff displacement 126.001 m, retained parts/holes.
No national display/payload/fidelity claim is made.

## Executed final verification

Evidence: `data/raw/phase7-evidence/`; final economic measurements also in raw
root `compact-national-final.json`. Package fingerprint:
`spain-housing-0.1.0/sha256-15d55b0302e7fd3a4c3e6d52f62342a4a9d1ecd440eb44b682ad8995d0304080`.
Python/runtime: 3.12.3, pydantic 2.13.5, PyYAML 6.0.3, Shapely 2.2.0,
openpyxl 3.1.5, pyproj 3.8.0. Second gate Python 3.13.16.

| Check | Executed evidence |
|---|---|
| Baseline | 329 passed in 13.13 s; lock/Ruff/mypy/ten contracts/build passed |
| Final single gate, Python 3.12.3 | `bash scripts/check.sh`: **349 passed in 14.86 s**, Ruff format/lint, lock, mypy 62 files, ten contracts |
| Final single gate, Python 3.13.16 | Same gate: **349 passed in 13.47 s**, all other gates passed |
| Packaging | `uv build` wheel/sdist; clean core/map installs with locked hashes, `PYTHONPATH` unset, unrelated `/tmp` cwd, imports confirmed in `site-packages` |
| Numeric/contracts | Independent four-month 13,200 ending / 12,000 usable / 40,000 capacity / 20 m² / ratio 1/3; full/overview/detail/JSON/CSV parity; exhaustion, zero/reserve, unsupported and product gaps |
| State/UI | AppTest full and compact paths, deferred export, cached detail, geographic-only selection, repeated reset/zoom, display identity, invalid/staged input and zero extra presentation evaluations |
| Legacy | Actual retained Phase 6 v1 release opens (43 observations), unchanged manifest; all original tests/fixtures preserved; core-only serve gives actionable missing-map diagnostic |
| National economic scale | 8,132 × 84 months, warm-up + 3 samples **4.272 / 4.342 / 4.238 s**, median **4.272 s**; selected detail **10.4 / 10.8 / 11.8 ms** |
| Economic memory | Peak **383,276 KiB**, loaded-resource peak 335,108 KiB, increment **48,168 KiB** with two overviews; excludes display/browser/full export |
| Actual restored browser | Chrome **149.0.7827.53**, installed map using root B rebuilt artifacts, 179 official municipalities × 84 months; first display **4.017 s**; metric actions **1.089 / 0.994 / 1.042 s** including driver wait |
| Browser behavior | Visible official polygons and WebGL pick 28079; all metrics/details, staged/invalid imports, reload, unchanged downloads; **0 page errors / 0 external requests** |
| UI/CLI/replay | Restored-root regional run/CSV byte-identical to installed core CLI and replay; run SHA-256 `0754f66195e79906cd06f961d1e4c04b5777698f7e5f5ca602e96f39a7c4183e` |
| Two-root restoration | Independently extracted `/tmp/phase7-restore-a` and `-b`: national/regional canonical, regional display, all generated inputs/releases rebuilt with identical IDs/payload bytes (64.710 / 61.197 s); evaluation/export/replay succeeds with raw inputs hidden |
| Full CLI geography validation | National reports `source_coverage_valid: false` with explicit pinned conflict; paired regional display validates; commands run from installed core outside checkout |

Use `UV_CACHE_DIR=/tmp/phase7-uv-cache`, `/tmp/phase6-tools/bin` on PATH here.
The Python 3.13 gate additionally needs explicit
`UV_PYTHON=/tmp/phase6-python/cpython-3.13-linux-x86_64-gnu/bin/python3.13` and
`UV_PROJECT_ENVIRONMENT=/tmp/phase7-check313`; sync alone was initially reset to
3.12 by project selection. That failed invocation is not counted as 3.13 proof.

Repairs/evidence limits: first restoration correctly exposed an intermediate
Madrid recipe/report-default identity mismatch; regenerated paired artifacts
above fix it without rewriting old artifacts. Browser camera actions were made
explicit and retested. An additional optional drag experiment did not establish
manual pan behavior and is **not** counted as camera-retention proof; its note is
retained. National territorial/province/transition/browser checks remain blocked,
not replaced by AppTest or a regional screenshot. CLI/full-export memory and
national display/browser timing are not included in the economic-only benchmark.

## Portable availability and acceptance

Actual archive: `data/raw/phase7-portable.tar.gz`, **213,738,215 bytes**;
SHA-256 `810223185b3652c852c5970d6825b4925c64231bf2e2d918babf436f2775132c`.
Receipt: `data/raw/phase7-portable.json`. Includes actual retained official bytes,
canonical artifacts, regional derivative, complete/partial/regional synthetic
inputs/releases, final wheel/configs/lock/locked requirements and geography
instructions. Both restorations above used this archive. Wheel SHA-256:
`8fcded08bd34c071e95169c029cbe005badc7ec8a05a33ec55bd24ed75986dc6`.
This is an ignored **local** archive, not an off-machine backup or download URL.
No durable transfer destination is authorized. A fresh clone alone lacks data;
copy/archive/receipt are required. Final verification receipts/screenshots/drivers
are retained separately in the evidence root. See [GEOGRAPHY.md](../GEOGRAPHY.md)
for actual paths and commands, including conda/venv.

| Criterion | Final state |
|---|---|
| A1 | Verified: actual baseline/instructions, starting user changes preserved |
| A2 | Verified: financial/selection rules unchanged, shared owners, all contracts/tests |
| A3 | Verified: strict version/reference/permission separation and v1 compatibility |
| A4 | Qualified: complete official registry/extent/provenance; retained source overlap explicitly reported, not valid simplifier input |
| A5 | Regional verified; national blocked, unverified |
| A6 | Verified: deterministic complete/partial national synthetic pipeline, no observed-price claim |
| A7 | Verified through joins/tests/partial restored evaluation; geographic-only handling and strict errors |
| A8 | Regional installed browser verified; required national browser unverified |
| A9 | Economic targets/parity verified; national full-map/memory/interaction target unverified |
| A10 | Existing tests/core/legacy and installed regional UI/CLI/replay verified; national deferred-export/browser transitions unverified |
| A11 | Full gates/build/core/map and two-root available-artifact reproduction verified; national display unavailable, no off-machine copy |
| A12 | Verified: docs/progress/manifest/runbook describe actual availability and blockers |

No all-A1–A12 or full-phase completion claim. Resolve the display policy before
resuming dependent work; preserve source bytes and all financial behavior.

## Resumed display checkpoint (20 October)

User approval covers retaining the exact positive-area intersection as a neutral
source-conflict display feature, with no economic code or owner. Implementation
is explicit `build-map-display --neutral-source-conflicts`; canonical inputs and
all market/finance rules remain unchanged. The display manifest records source
feature IDs, policy, metric CRS and measured patch area; hover and attribution
identify the derived treatment. Shared line-only contacts are excluded from the
positive-area intersection. Old display manifests still validate by original
serialized metadata rather than newly defaulted fields.

Current full gate: **350 passed in 15.98 s**, Ruff/typing/lock and ten contracts.
Tests verify opt-in, original canonical bytes unchanged, neutral no-code identity,
no overlapping display interiors, municipal counts and deterministic publication.
National 50 m candidate correctly fails Palma (07040) boundary displacement
**270.792 m**, above the unchanged 250 m limit (area change 0.05968%). The bounded
20 m candidate is running full national QA. No geometry threshold is waived.
