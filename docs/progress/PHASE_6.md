# Phase 6 progress

Current milestone: M1 baseline/integration verification, 14 October 2026.
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
Registry/full geometry verification passes, 16 multipart geometries, no repair.
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
