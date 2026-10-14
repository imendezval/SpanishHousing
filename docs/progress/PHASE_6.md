# Phase 6 progress

Current milestone: M6 installed/browser/handoff verification, 14 October 2026.
Baseline is local `3972ea3`, with completed Phase 5 code (unpublished code was
absent in the guide's remote inspection). User-owned untracked AGENTS.md and
Phase 2–6 guides are preserved and excluded from commits. No push/merge/deploy.

Plan: verify the actual 310-test/UI baseline; freeze the 16-municipality product
matrix and bounded source decisions; verify official identities/geography;
improve preparation diagnostics; share one immutable coverage report between
snapshot, inspect-release CLI and injected UI; add one generated synthetic helper
for 16-/250-location cases; document/exercise restoration/update/rollback; measure
scaling and caching; verify browser, supported runtimes and installed wheels.

Phase 5 interfaces inspected: launcher.compose → frozen Services; process LRU4
for validated snapshots keyed by manifest bytes/path/permission; session LRU32
identified by complete scenario, destinations, release/model/code/runtime;
strict detached map joins and existing application/config serializers. Public
packaged serve starts the installed launcher; finance remains outside UI.

First gate attempt failed before tests: the earlier /tmp uv installation is gone.
Restoring a temporary toolchain, then rerunning unchanged baseline. Prior temporary
datasets/environments are not assumed available. Actual retained four-city raw
and processed geography directories exist; their bytes still need validation.
Observed markets remain permission-blocked; no observed release is claimed.

Next: finish baseline checks and read/report contracts, bounded current source
review and official registry identity verification. No substantial code edit yet.

M1–M4 checkpoint: restored uv 0.13.0 under /tmp/phase6-tools; unchanged baseline
passed 310 tests, mypy/Ruff/lock and 10 contracts. Actual Phase 5 exists and its
interfaces were verified; no integration prerequisite blocker. Implemented frozen
schema-1 common coverage report/public snapshot property, thin inspect-release,
injected UI coverage panel, strict capture/row/profile diagnostics and shared
16-/250-location synthetic input helper. Original pilot untouched. Current gate:
322 tests, strict mypy 49 files, Ruff/lock and 10 contracts pass.

M2 bounded three-candidate review frozen in docs/DATA_EXPANSION.md. Idealista
terms still restrict copying; SERPAVI is tax-derived 2024 reference (2026 title),
not current asking/room substitute; valuation bulletin is not selected asking
prices. No market captures/provider contact/accounts. Observed build explicitly
refuses restricted Idealista use; A11 remains blocked. All 16 audited codes/control
digits verified against retained official INE XLSX; new INE changes reviewed (none
included). Existing official adapter captured 12 additional complete IGN responses.
Registry/full geometry verification passes, 16 MultiPolygon records, no repair.
Recipe configs/sources/expanded.yaml plus small hash reference, actual ignored
raw/processed expanded-geography bytes retained; geography is not a market release.

Synthetic expanded release: 43/48 available, four missing, one source-declared
unsupported. Dataset unsupported gap is separate from existing exact-query
missing-row behavior; finance/query semantics preserved. Stale scenario tests
use a later base rather than claiming age-zero profiles ending at base are stale.
All diagnostic tests now use actual preserved Spanish raw units; corrupt/html/
column/width/locale/period/profile/unit/nonpositive inputs reject before new output.

Next M5: expanded AppTest/transitions/parity/cache call-count proof, inspect four/
16-/250 performance medians in /tmp/phase6-measurements.json, browser tooling,
runbook/update/backup/rollback reproduction, supported runtimes and fresh wheels.
CI now retains map extra and Python 3.12/3.13 matrix; CI remote execution unrun.

M5 checkpoint: full gates pass **329 tests** on Python 3.12.3 and 3.13.16, strict
mypy 49 source files, Ruff/lock and ten contracts. New coverage indirect-storage
sensitivity passes. Expanded room/staged-growth UI/CLI JSON/CSV and exact replay
pass; source availability versus stale/segment suitability stays distinct. Pure
observed/estimated label counts use explicitly hypothetical unit-test records;
the existing storage guard rejects their publication into synthetic releases.
Actual expanded latest-gap/older-available integration retains no-fallback.
AppTest service transition 16→4 clears old applied run/memo/downloads, preserves
draft, resets retired inspection code after Apply. Resource hits invoke validation
once; reload/digest change invoke it again. No economics moved into UI.

Source Chrome 149.0.7827.53 browser exercised 16-result coverage metadata, all
three metrics, hover/code picking, real room→flat clipboard grid change (Badalona
room missing, flat available), positive capacity with missing Teruel purchase,
no external requests, and explicit reload→Apply. Source first applied display
was ~2.7 s. Final installed/browser pass with Fit and portable reproduction pending.

Measurements: /tmp/phase6-measurements-final.json, three samples/median, Linux
6.8 x86_64, AMD Ryzen 7 7840HS, ~32 GB RAM; Python 3.12.3, same actual package
fingerprint as wheel below. Logical cold validation creates a fresh snapshot each
sample; OS disk-cache coldness is not claimed. Geometry is lightweight synthetic,
not a national complex-polygon performance promise.

| Locations / months | Validate+index ms | Evaluate ms | Report ms | Map preparation ms | Equal memo ms |
|---|---:|---:|---:|---:|---:|
| 4 / 12 | 1.96 | 5.33 | .045 | .033 | .142 |
| 16 / 12 | 3.40 | 6.76 | .085 | .112 | .142 |
| 250 / 84 | 40.62 | 274.52 | .959 | 1.516 | .425 |

Initial evaluation medians ~6/8/306 ms informed targets: <100 ms at 16 locations,
<1 s for 250/84, <5 ms equal memo, <5 s first applied browser display on this
machine. Backend measurements meet them; browser is separately measured. Counts:
11/43/745 observations over three profiles, 30/90/1260 vertices. First Apply calls
evaluator once, equal/presentation adds zero, changed reserve adds one. Two cached
compositions invoke full validation once. No bottleneck warrants optimization;
retain current reader/engine/cache, without workers/database/simplification.

Fresh lock-derived core/map wheels installed in /tmp/phase6-wheel-core and
/tmp/phase6-wheel-map (Python 3.12.9), imports resolve to site-packages and all
commands run from /tmp with PYTHONPATH unset. Both independently restore one
actual synthetic input archive into a/b roots, rebuild identical release bytes,
validate/inspect, evaluate/export room and staged-growth, replay identical JSON/CSV,
reject corruption and roll back to four-city. Evaluation still works after raw
inputs are removed. Core has no Streamlit/PyDeck and serve gives missing-extra
exit 2. Artifacts /tmp/phase6-core-proof and /tmp/phase6-map-proof; JSON evidence
/tmp/phase6-core-proof.json and /tmp/phase6-map-proof.json.

Actual official geography archive exists at
 data/raw/phase6-backups/expanded-geography-20261014.tgz (1,536,830 bytes), SHA-256
8add4ce857d7f38d494d73d693c952e0f74ef766a1654a9e44cd302b3919e788.
Restored into /tmp/phase6-official-restored with recipe/sidecars and verified
through existing geography script; both derived payloads compare byte-identically.
This is a local backup only; off-machine durable transfer was not performed.
Runbook documents separate evaluate-restored-release/rebuild/acquisition/replay
claims, exact explicit commands, synthetic route, backup/update/rollback and errors.

Next: finish installed browser/parity/source-wheel comparisons; final README and
architecture/progress review, final build/diff and local docs commit. Only observed
A11 is blocked; do not claim full Phase 6 complete while that remains unverified.
