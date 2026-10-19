# Phase 7 progress

Started 19 October 2026 at `ba3580a`. User-supplied Phase 7 guide was the only
untracked file; its content is preserved. No push, deployment or provider contact
is authorized for this phase.

## Plan and state

- M1 in progress: inspected actual schema-1 storage, normalization, official
  adapter, immutable repository/context, launcher and CLI. Baseline lint, typing
  and ten import contracts pass; **329 passed in 13.13 s**; wheel/sdist build passed. Initial uv failed because
  its default cache is read-only; use `UV_CACHE_DIR=/tmp/phase7-uv-cache` and
  `/tmp/phase6-tools/bin` on PATH. No baseline import-order defect reproduced.
- M2 pending: retain complete official pagination and registry/change evidence,
  reconcile a regional slice then the national set; canonical immutable artifact.
- M3 pending: topology-aware metric display QA and schema-2 references, preserving
  schema-1 serialization and component-specific permission checks.
- M4 pending: packaged deterministic generator; complete/partial releases;
  atlas-superset join, navigation and independent financial reference.
- M5 pending: national 84-month measurements, bounded justified optimizations,
  real installed browser proof and numerical parity.
- M6 pending: final two-runtime gate, wheel/core/map installs, two-root retained
  artifact rebuild/replay, portable bundle and documentation.

## Contract decisions

Canonical geography and display are independently versioned content-addressed
artifacts. New market schema 2 pins canonical geography and registry identity;
old schema 1 retains embedded boundaries and original serialization. Scenario/run
schemas and financial semantics stay unchanged. Common release validation and
normalization remain single owners. Geography permissions use official captures;
synthetic market permissions remain synthetic. Runtime paths are explicit inputs,
never serialized or implicitly discovered. Financial evaluation reads verified
registry metadata, not full-resolution geometry; display composition validates
the explicit derivative and parent. Atlas/market/evaluation/result joins enforce
`E ⊆ M ⊆ A` and `R = E`.

## Acceptance evidence

A1 baseline verified; contract implementation remains in progress. A2–A12 not yet verified. Previous phase results are
historical evidence only. Observed market acquisition remains blocked and does
not block the authorized synthetic Phase 7 economics. Portable off-machine
transfer requires a user-authorized durable destination; prepare actual local
bundle and tested restoration without claiming an external upload.

Next: finish baseline, inspect national IGN pages/queryables and source topology,
then implement independent artifact contracts/shared publication primitives.

Official probe retained in `data/raw/national-geography/probe.json`: collection,
queryables, one-feature municipality response, 2026 INE dictionary and current
in-year-change HTML. IGN reports 8,213 level-Municipio features; this is not yet
the reconciled municipality count. Installed Shapely 2.2.0 / GEOS 3.14.1 supports
coverage operations. No national completeness or topology claim yet.

## M1/M2 checkpoint

Full current gate: **336 passed in 13.35 s**, Ruff/typing (55 files), lock and ten
contracts pass. Shared strict-byte/path/publication/permission/polygon rules are
extracted without changing schema-1 content. Actual retained Phase 6 release
`synthetic-890aef2f82b6631b3c82321da1bfc91216dc802e3662ac2d65f338a19fe59c59`
still validates with unchanged manifest bytes. New strict schema-2 models and
independent atlas/display contracts are present; consumer dispatch is next.

Actual IGN capture: 42 municipality pages (702,058,118 bytes), one province page
(187,127,244 bytes), INE dictionary/changes, service metadata/queryables and
licence bytes, all under `data/raw/national-geography`. Entire INE set **8,132**
matched; **81** explicit 53-series context territories and **619** source-name
crosswalks (exact authoritative code joins; no fuzzy matching). Regional Madrid
179-municipality canonical build passed:
`data/processed/geography/geography-390c77093608da9acc9963f8da8669caf30532fa22b9ac4302e837a47c195d77`.

National API geometry fails edge-matched coverage at Bellver de Cerdanya (25051,
IGN 1171892) and Prullans (25179, 1172000). Intersection area is
1.576066123287909e-7 square degrees; canonical coordinates were **not repaired**.
The national artifact has not been published. A bounded official alternative
is being acquired via IGN's ATOM feed (updated 2026-08-10) and its linked CNIG
GML ZIP. CNIG catalog initially disconnected, then a bounded retry succeeded.
No invented ownership, buffering or dropped municipalities is authorized.

`pyproj` 3.8.0 is added/locked for explicit metric display preparation (no GDAL
or GeoPandas). It is not used by finance. A4/A5 national criteria remain unverified.
Next: inspect the official alternative's geometry before selecting a coherent
canonical source; continue schema-2/display/consumer engineering independently.

Official alternative retained: IGN ATOM feed (5,276 bytes) and linked CNIG GML
ZIP (66,245,318 bytes), `alternative-probe.json` in the raw root. It reproduces
the same Bellver/Prullans overlap; this is not a pagination error. EPSG:25831
measurement: **1,440.944794 m²**. A reviewed prototype subtracting the overlap
from both display polygons and retaining it as neutral context forms valid
coverage, with no arbitrary ownership and unchanged canonical sources. A genuine
source-policy question has been sent asynchronously to the user: approve that
explicit display exception or leave national topology blocked awaiting official
correction. **Do not implement that dependent exception before an answer.**
Independent regional/schema-2/UI/generator work continues.
