# PHASE 7 — National Municipal Map with Real Geography

Implementation guide for an autonomous Codex run. Prepared 19 October 2026.

**Outcome:** the installed application displays a recognisable map of Spain divided into real municipalities. Its fills come from the existing affordability engine using explicitly synthetic purchase prices and rents. National navigation, municipality selection, unavailable states and financial details work without runtime data collection. Geography can remain visible as economic coverage changes.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), freshly fetched and inspected at **ba3580a1caf1186439d1666219ec4af48c8df5e8**. This revision includes actual Phase 5 and Phase 6 code. The older Phase 6 guide describes a preparation-time checkout that ended at Phase 4; its warning about absent Phase 5 is superseded by the inspected implementation and progress reports. Its recorded observed-market blocker remains applicable.

**Intended location:** `docs/phases/PHASE_7_map_geo.md`. Implement the phase against the current working tree; do not reset to the reviewed commit. This document extends the implementation plan with the national-geography phase agreed after Phase 6. Save-in-A/buy-in-B follows this phase; salary realism and historical reconstruction remain deferred.

## 0. Start here

1. Read applicable `AGENTS.md`, inspect Git status/history and identify user changes before editing. Preserve user-owned work. The inspected instructions require lowercase commit subjects and coherent intermediate commits during long implementations.
2. Read `docs/PROJECT_BRIEF.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/ARCHITECTURE.md`, `docs/DATA_EXPANSION.md`, `docs/DATA_ACCESS.md`, `docs/RUNBOOK.md`, and `docs/progress/PHASE_5.md` and `PHASE_6.md`. The inspected `AGENTS.md` names `docs/SPAIN_HOUSING_PROJECT_BRIEF.md`; the actual brief is `docs/PROJECT_BRIEF.md`. Locate an existing renamed equivalent rather than creating a duplicate.
3. Inspect the owners in Section 3, the current dataset models/storage validator, official adapter, geography verifier, repository/context, evaluator/export/version modules, launcher, map/presentation/session code, import contracts, fixtures and scaling script. Read previous phase guides for context; their old repository snapshots are historical evidence.
4. Read Sections 4–10 before designing the implementation. They settle artifact identity, provenance, backward compatibility, geographic joins, synthetic inputs, rendering and scale.
5. Record the starting revision, baseline checks and a short implementation plan in `docs/progress/PHASE_7.md`. Execute M1–M6 in Section 11 without routine confirmation. Resume using Section 14.
6. Finish against A1–A12 in Section 13. Report national geography, synthetic economics, installed/browser evidence and unresolved observed-market access separately.

Current user instructions and applicable repository instructions take precedence. The brief owns economic meaning; the architecture owns dependency direction; this guide supplies Phase 7's explicit changes. Routine implementation choices belong to the implementing agent. Ask only about a material ambiguity or blocker that cannot be resolved from these sources.

An implementation request authorizes scoped code/documentation changes, permitted official-data acquisition, local verification and local commits. Do not push, merge, deploy, contact providers or initiate paid/account access. Do not add another agent framework, mandatory milestone approvals, or a new `AGENTS.md`.

## 1. Actual starting point and evidence

### 1.1 Implemented foundations

| Owner | Actual implementation | Phase 7 consequence |
|---|---|---|
| Models/config | Frozen validated records, explicit units/dates, safe scenario loading, independent saving/buying bindings | Preserve economic inputs and their validation |
| Finance/application | Monthly budgets, exhaustion/reserve, mortgage/cash limits, all three indicators, exports/replay | Reuse numerical rules; geometry never enters finance |
| Ingestion/storage | Official capture adapter, registry reconciliation, retained-feature selection, immutable checksummed market releases | Extend these owners for independent geography; do not build a second persistence framework |
| Markets | Validated indexed snapshot, exact queries, pure selection/projection and coverage reports | Preserve product/period/proxy/no-fallback semantics |
| Launcher/UI | Packaged `serve`, injected services, coordinated Apply, session memo, map picking, details and downloads | Evolve the composition/map contract without infrastructure imports in UI |
| Geography evidence | Sixteen official INE identities and complete IGN features verified during Phase 6 | Evidence of a working route, not national geography or bytes present in a fresh clone |
| Demo | Four-city regression pilot and generated 16-/250-location inputs | Current market values, registry fixture identities and displayed shapes are synthetic |
| Observed markets | Acquisition/use/redistribution remain blocked for the selected products | Synthetic economic demonstration is the authorized Phase 7 path |

Current `ui/map.py::decorate` requires equal code sets for context locations, results and boundaries. `Services.destinations` includes only economic-release locations. `ui/app.py` labels both shapes and prices synthetic whenever `context.kind == "synthetic"`. These assumptions must evolve deliberately; suppressing their checks or changing only the warning is insufficient.

`storage/release.py::validate_source_use` and `validate_capture_permission` intentionally prohibit real-source decisions/captures inside a schema-1 synthetic release. Phase 7 must distinguish geographic provenance from market provenance without reclassifying official captures as synthetic or allowing synthetic prices into an observed market release.

### 1.2 Preparation-time checks

Checks were executed in an isolated detached review worktree, using the committed lock and Python 3.12.14. `uv sync --locked --extra map` and `uv build` succeeded. Strict mypy passed on 49 package files, and all **10 import contracts** were kept. Lock and formatting checks passed. The aggregate `bash scripts/check.sh` stopped at four Ruff `I001` import-order findings in:

- `tests/data/test_geography.py`
- `tests/data/test_normalize.py`
- `tests/data/test_release.py`
- `tests/data/test_repository.py`

The correctly invoked `uv run --locked --extra map pytest -q --tb=short` passed **329 tests**. M1 must establish the implementation checkout's actual gate and repair any reproducible baseline issues with a minimal change. Do not disable an import rule or exclude tests to manufacture a passing gate.

Phase 6's own progress report records 329 passing tests on Python 3.12/3.13 plus installed/browser checks. Those are historical reported results; they do not verify Phase 7. No national artifact, Phase 7 implementation, new installed-package browser check or newly acquired market data was produced while writing this guide.

## 2. Scope and product decisions

### 2.1 Required outcome

- A pinned, independently versioned official national geography artifact, with municipality identities, canonical geometry and source evidence.
- A reproducible simplified display derivative, separately identified from canonical geography.
- A market-release extension referencing geography independently of synthetic/observed market evidence.
- Deterministic national synthetic purchase, whole-home rent and room inputs, built and queried through the existing pipeline.
- A national municipal choropleth with useful outlines, territorial views, search, picking, details and stable legends.
- Explicit behavior for geographic areas outside economic coverage, missing inputs, unsupported requests and unviable saving paths.
- Measured national-scale loading/evaluation/rendering, with targeted changes where needed.
- Portable artifacts, installed core/map verification, browser proof and a usable runbook.

### 2.2 Geographic resolution and extent

**Municipalities are the economic coloured units.** Use official province outlines for orientation or derive them reproducibly from verified territory associations. Autonomous-community outlines are optional. Do not replace municipal economics with province averages.

Target all municipalities in one selected national INE snapshot, reconciled with a compatible boundary snapshot and relevant in-year changes. The exact expected count comes from retained official evidence, not a hard-coded internet count. A contiguous regional subset is an intermediate milestone, not national completion.

Include mainland Spain, Illes Balears, Canarias, Ceuta and Melilla. Recognise jointly administered or other nonmunicipal areas in the chosen official product. They may be neutral geographic context with their own source identifiers; they are not mortgage destinations or fabricated five-digit municipality codes. Record small special-territory exclusions explicitly where the selected product does not represent them. Unexplained inland holes, absent islands or unresolved municipalities block the national-geography criterion.

### 2.3 Required demonstrations

1. **Complete synthetic national market:** all reconciled municipalities have the three selected demo products. A suitable scenario produces visibly differentiated, valid economic results.
2. **Partial-coverage demonstration:** use the same national geography and a declared limited market subset, plus deliberate missing products within that subset. Geography outside market coverage stays visible. Preserve both outside-release coverage and indicator-specific gaps.

The original four-city fixtures and generated 16-/250-location regression cases remain available. Do not overwrite them with official geometry or relabel their fixture records.

### 2.4 Exclusions

No real-price acquisition campaign, save-in-A/buy-in-B implementation, profession/employment model, historical reconstruction, district/neighbourhood/census-section economics, regional tax solver, new mortgage rules, investment model, required-income/time solver, public deployment or account system.

Retain Streamlit/PyDeck. No mandatory tile server, database, geospatial service, frontend rewrite, distributed jobs, Hydra, DVC, or generic provider/plugin registry. A genuinely necessary small preparation dependency is permitted under Section 6; document and lock it. Do not turn national scaling into an unrelated rewrite.

## 3. Ownership and repository structure

### 3.1 Dependency rules

Preserve all current import contracts and sensitivity tests. Geography is a dataset concern with a display projection; it does not justify a new top-level application stack.

| Component | Owns | Boundary |
|---|---|---|
| `models` | Artifact/reference/provenance records, typed map context and optional compact result contracts | No implementation imports |
| `ingestion` | Official acquisition, reconciliation, canonical assembly, display preparation and demo-input generation | No affordability/UI dependencies |
| `storage` | Shared safe parsing, hashes, identity, integrity, atomic publication and version dispatch | Models and narrow tools only; no imports from ingestion/markets/application/UI |
| `markets` | Read-only geographic/market projections and immutable indexes | No acquisition, finance or UI |
| `application` | Existing financial orchestration; optional measured overview/detail service | No storage/ingestion/launcher/UI dependency, including indirect bypasses |
| `launcher` and CLI | Resolve explicit paths, construct concrete readers and inject typed services | No financial or geographic processing rules |
| `ui` | Apply/view/selection state, pure joins, styling, map/table/details presentation | No direct imports of storage, ingestion, markets, finance or config |

The existing `storage.validate_geometry` mixes reusable ring/topology checks with schema-1 identity checks. Extract shared primitives only where both artifact types need them; keep legacy identity validation as a wrapper. Do not copy the validator and then maintain two subtly different versions. Likewise reuse strict JSON, safe paths, hashing, permissions, atomic writes and normalization rather than scattering local equivalents.

### 3.2 Suggested changes

Paths are ownership guidance, not a required file count. Reuse an equivalent current owner before creating a file.

| Path | Responsibility |
|---|---|
| `models/geography.py` | Geography manifest/reference, registry, provenance and display-derivative contracts |
| `models/dataset.py` or small version-specific model modules | Dataset-v2 market recipe/manifest and typed geography reference; legacy records retained |
| `ingestion/geography.py` and existing official adapter | National capture reconciliation, complete paginated input assembly and shared checks |
| `ingestion/map_geometry.py` | Explicit topology-aware display preparation and quality report |
| `ingestion/demo.py` | One deterministic national synthetic market generator, independent of test fixture imports |
| `storage/geography.py` and existing storage helpers | Canonical geography/display readers and writers using common integrity/publication primitives |
| `storage/release.py`, `ingestion/release.py` | Central v1/v2 dispatch and shared market-release pipeline |
| `markets/geography.py`, `markets/repository.py` | Read-only registry/map views and existing market access |
| `application/` | Measured shared overview/detail support only if Section 9 requires it |
| `launcher.py`, `cli.py`, `ui/contracts.py` | Explicit geography/display composition and commands |
| `ui/map.py`, `presentation.py`, `app.py`, `state.py` | Superset map join, navigation, provenance, selection and bounded state |
| `configs/sources/national_geography.yaml` | Pinned source selection and capture/reconciliation policy |
| `configs/demos/national.yaml` | Generator version/seed, synthetic product ranges and coverage variants |
| `data/manifests/` | Small tracked source, reconciliation, artifact and performance references |
| `docs/GEOGRAPHY.md`, existing runbook/architecture/progress | Current geographic decisions, reproduction and evidence |

Do not put runtime functionality under `tests/`, import synthetic helpers from an installed launcher, or make a script the sole owner of a new business/data rule. Scripts may be thin verification wrappers over packaged functions. Keep financial formulas and result serializers with their existing owners.

## 4. Artifact and compatibility contract

### 4.1 Three separately identified objects

| Object | Stable content/identity | Must not contain |
|---|---|---|
| **Canonical geography** | Official registry and complete canonical geometries, source references, effective dates, crosswalks, checksums and processing evidence | Prices, salaries, scenario state or colour bins |
| **Display derivative** | Parent geography ID, simplified geometries, outline/context layers, algorithm/CRS/tolerance, quality report and content hashes | Reclassified official captures, economic calculations or arbitrary jittered coordinates |
| **Market release** | Economic locations/products/periods/observations/gaps, market provenance, referenced canonical geography ID and market processing evidence | A duplicated national display layer, workstation-specific paths or an implicit latest-geography rule |

Use content-addressed identifiers, for example `geography-<sha256>` and `display-<sha256>`. The exact spelling is less important than a single validated format and deterministic identity. Retain existing `pilot-<digest>`/`synthetic-<digest>` market prefixes unless a concrete incompatibility requires a documented change. No name implies observed housing simply because its geometry is official.

Canonical geography identity must not change because a palette, viewport, outline width or display simplification changes. A display derivative records its parent canonical ID; a market release references the canonical ID, not a particular simplification. Source registry/boundary changes intentionally produce a new canonical artifact. Published artifacts are immutable; reject same-ID/different-content writes.

### 4.2 Versioning decision

Introduce **dataset schema 2 for newly built market releases that reference external geography**. Preserve schema-1 parsing and embedded-boundary behavior for existing releases. Give geography and display artifacts their own independently versioned schema, initially 1.

Do not broaden the global `models.base.SchemaVersion` from literal 1 to a permissive integer. It is shared by unrelated scenario/run contracts. Use artifact-specific strict version types and dispatch exactly once at the storage boundary. A schema-2 tag must not accidentally validate as a schema-1 record.

Retain the legacy schema-1 model/serialization shape. Adding defaulted fields to old records can change canonical bytes/digest reconstruction; do not invalidate stored releases that way. New version-specific parsing should project to one common immutable internal/read-only market view, reusing normalization, coverage, permissions, identity and index-building rules. This is a versioned data extension, not two financial pipelines.

Keep scenario and economic-run schemas unchanged unless an actual required serialized field cannot fit compatibly. Any necessary result/context addition gets an explicit schema/default/serialization decision and tests. Do not change mortgage/scenario semantics or the financial model version merely for map styling.

Current processing and code fingerprints intentionally depend on actual source. New code can change freshly built release IDs and exact replay evidence. Preserve old on-disk bytes, validate them under their own schema, and distinguish economic equivalence from exact replay under identical code/runtime. Do not edit fingerprints or old runs to force equality.

### 4.3 Registry and geography reference

The canonical registry needs official municipality code/name, province association, control digit, registry effective date/version, source identity/crosswalk and canonical boundary identity/version. Keep leading zeroes. Prefer a focused registry record over requiring market-specific `core` or source-label mappings in the canonical atlas. The market reader may construct the existing `LocationRecord` projection once from verified registry data plus market metadata, preserving application interfaces.

A schema-2 market recipe/manifest pins the canonical geography ID and required registry identity. Source-label mappings, chosen economic locations, core-product requirements and coverage belong to the market component. Economic coverage may be a strict subset of the atlas. Reject duplicate/unknown municipality references, version conflicts and ambiguous joins before serving results.

Paths are runtime inputs. Add an explicit optional `geography_dir`/equivalent at composition and `--geography` to affected CLI commands. It is required for a referenced release and unnecessary for an unchanged embedded schema-1 release. No ancestor-directory search, automatic latest selection, download, or silent use of a different artifact. A shared geography directory may serve several market releases.

### 4.4 Provenance and permissions

Keep **market evidence kind** and **geography origin** distinct. For the new national demo:

- Canonical geographic identity and geometry originate in retained official INE/IGN inputs.
- Display geometry is an explicitly simplified derivative of those inputs.
- Every economic observation is synthetic and retains `evidence_kind="synthetic"`.
- The market context remains synthetic; `--allow-synthetic` remains required.

Apply source/capture permission validation within the correct component. Official geography keeps real URLs, timestamps, licence/attribution evidence and real capture routes. Synthetic market rows keep self-authored generator lineage. Do not introduce a blanket `mixed` evidence escape hatch, relabel official data `synthetic_fixture`, or allow synthetic observations in an observed market component. Legacy schema-1 restrictions remain enforced.

Usage/redistribution of a composed portable bundle cannot exceed its least permissive component. Market coverage inspection continues reporting economic cells; add geographic scope/provenance alongside it without counting polygons as market observations.

### 4.5 Runtime loading and integrity

Reuse safe relative paths, canonical serialization, checksums, bounded parsing and atomic/idempotent publication. Resolve artifact references by expected content identity, not folder names alone. Corruption and wrong versions are errors; they do not become missing prices.

Full official capture parsing, reconciliation and topology validation belong to preparation and `validate-geography`. Economic evaluation needs the verified manifest/registry projection, not full-resolution polygon coordinates. UI composition additionally opens and validates the selected display artifact and its parent reference. Never expose unchecked file bytes, but do not parse millions of unused canonical vertices on every economic run or rerender.

Document validation scope precisely: `validate-release` validates the market component and referenced geography identity/registry needed by it; full canonical geometry verification is the geography command's responsibility. A portable verification workflow executes both. A manifest hash or a previous success marker is not proof that currently supplied payload bytes are intact.

Keep public v1 entry points working. Do not silently replace the v1 repository's `.boundaries` property with an unlabelled derivative. The launcher adapts legacy embedded shapes or the new explicit geography/display pair to one typed map service. Core code must not import Streamlit/PyDeck merely to open registry metadata.

## 5. Official national geography preparation

### 5.1 Source selection

Start with the existing INE registry route and IGN `administrativeunit` collection, whose metadata provides GeoJSON and CRS84. Inspect the installed adapter and live API schema/queryables before issuing requests. Prefer a finite national paginated capture over thousands of repeated per-city requests. The national CNIG product is a documented alternative if the API route is unavailable or unsuitable.

Use one coherent pinned registry/boundary combination. Retain original bytes, actual acquisition times, source URLs, licence/attribution references and any in-year reconciliation evidence. The existing sixteen-city hashes are useful pointers but are not downloadable data by themselves. A fresh clone must be able to follow the new preparation/restoration instructions using actual available bytes.

Acquisition is separate from building. A build consumes retained inputs offline; opening a map never fetches a boundary. Network failures, HTML error pages and source changes are explicit diagnostics.

### 5.2 Pagination and reconciliation

The existing small-capture selector rejects unretained pagination. Preserve its invariant. A national acquisition layer can retain all pages plus an inventory proving completeness, then feed the shared reconciliation owner. Do not delete the pagination check and call a first page complete.

Required checks:

- Follow documented `next` links with loop/duplicate detection, bounded retries/timeouts and a resumable capture inventory.
- Reconcile reported counts where provided, actual feature IDs, unique municipal codes and the pinned registry's expected set.
- Detect repeated/missing pages and duplicate features, including duplicates with conflicting geometry.
- Confirm municipality administrative level and country; do not mix provinces/autonomous regions into economic destinations.
- Reconcile official names/codes with explicit documented crosswalks; no runtime fuzzy matching or guessed identifiers.
- Review relevant registry changes. Every unmatched municipality or boundary needs a resolved explanation before national readiness.

If an API snapshot changes during acquisition, detect inconsistent content/counts and restart the affected capture set coherently. Resume intact retained pages only when the inventory still establishes a consistent selected snapshot. Bound retries: one initial attempt plus at most two retries per transient request, then use the documented official alternative or record a blocker. Do not poll indefinitely.

### 5.3 Geometry invariants

Retain Polygon/MultiPolygon identity, all components and source holes in canonical geometry. Validate finite longitude/latitude, CRS and axis order, closed rings, individual topology, unique IDs and registry joins. Canonical geometry must not be clipped, simplified or silently repaired to pass validation.

National checks also cover relationships between polygons. Use spatial indexing for adjacency/overlap checks rather than a quadratic all-pairs comparison. Distinguish source-declared shared/nonmunicipal territories from contradictory municipality overlaps. Report real source defects and legal exceptions; do not assign arbitrary ownership or buffer polygons to hide them.

Record separate counts for municipalities, context territories, features, polygon components and vertices. One municipality may have multiple polygon parts. A missing island/part must not be hidden by a correct municipality count.

For the national outline and province context, use the selected compatible official levels or a declared derived union. Document source/derivation and parent IDs. These are orientation layers, not province-level affordability observations.

## 6. Display derivative and geometric quality

### 6.1 Preserve canonical data, prepare the display once

Keep canonical coordinates unchanged. Create a new display artifact through a pure preparation function plus the shared writer. Record parent geography ID, algorithm/version, actual library/GEOS versions, CRS transforms, tolerance, any quantization and quality metrics. Generate it offline and reuse it across scenarios.

Use topology-aware simplification of a verified polygonal coverage, not independent per-municipality simplification that creates shared-edge discrepancies. Shapely is already a dependency; inspect its installed `coverage_is_valid`, `coverage_invalid_edges` and `coverage_simplify` behavior. `coverage_simplify` requires GEOS 3.12 or newer and valid edge-matched coverage. Do not assume individually valid polygons satisfy that precondition.

Municipal/context coverage must account for legitimate shared territories before simplification. If the source does not form the required coverage, diagnose it and use a bounded compatible official alternative or an explicit topology-preserving preparation decision. Do not silently clean source topology, drop exceptional polygons, or repeatedly try tolerances until a broken source happens to pass.

Express simplification in a documented metric CRS appropriate to each disconnected territorial group. Never label a degree tolerance as metres. A small declared dependency such as `pyproj` is acceptable if required for reproducible transforms; lock it and record the decision. Avoid adding GeoPandas/GDAL merely to call existing geometry functions. If code directly imports another library, declare it rather than relying on a transitive dependency.

### 6.2 Bounded tuning and quality gate

Start with a **50 m nominal display tolerance**, then evaluate at most **20, 50 and 100 m** under the chosen metric method. Choose the smallest passing candidate that meets the payload/interaction targets. These values are preparation parameters, not official boundary accuracy claims. Freeze the chosen configuration and evidence before further UI tuning.

For each candidate verify:

- Identical geographic feature/code sets and parent identity; no empty/collapsed municipality.
- Valid individual and coverage topology; no introduced shared-edge cracks/overlaps.
- Retained disconnected components and holes. If a small ring would disappear, reduce tolerance locally through a consistent shared-edge policy or retain it explicitly; never erase it without a documented product decision.
- Per-municipality area change and boundary displacement in the metric QA system. Initial gates: relative area change at most **2%**, and measured symmetric boundary displacement at most **250 m**. Record worst cases and inspect them. A stricter source/local case may require retaining more vertices.
- National, island and province outlines remain consistent with the rendered coverage.

The tolerance parameter is not a mathematical guarantee of maximum displacement; measure the stated QA quantities. If no candidate satisfies fidelity and payload targets, preserve fidelity and record the remaining performance issue. Use a measured additional display level or compact encoding only if necessary; do not weaken thresholds silently.

Ship one proven national display layer first. A second finer derivative is optional if detailed views require it. Select any additional detail level through supported public controls/APIs and cache it by identity. Do not require undocumented PyDeck/Streamlit viewport callbacks or add a custom JavaScript component solely for automatic detail switching.

## 7. Deterministic national synthetic market inputs

### 7.1 One generator feeding the existing pipeline

Implement a packaged generator consuming the validated municipality registry and an explicit small config. It emits synthetic observation captures/rows, market source decisions, a schema-2 recipe and declared gaps for the existing normalizer/builder. It does not generate polygons or modify official registry evidence.

Use the existing three product meanings/units: purchase EUR/m², whole-home rent EUR/m²/month, and room EUR/month. Keep their periods, basis/statistic/segments explicit and compatible with the demo scenarios. Synthetic labels describe assumptions, not provider measurements. No report/audit values become newly observed prices.

Make outputs stable under registry reordering and unrelated municipality additions: derive local variation from a specified hash of generator version, seed and stable municipal code, rather than iteration position or Python's randomized `hash()`. Persist the algorithm/config/seed and canonical registry identity in lineage. Canonical ordering, stable metadata and the same code/inputs reproduce the same economic payloads and release ID. Do not insert wall-clock timestamps into deterministic generated data; distinguish generator creation metadata from actual official capture times.

Simple fixed province/territory variation plus bounded local variation is sufficient. No population, labour-market or learned price model is required. Starting demonstration ranges may be purchase **800–5,000 EUR/m²**, whole-home rent **5–20 EUR/m²/month**, and room **250–850 EUR/month**. They are synthetic test settings only. Keep rent and purchase variation deterministic and reasonably related so the map is legible; do not assign cities an invented real-world ranking.

Do not add random colours, interpolate computed affordability between municipalities or smooth results across boundaries. Every numeric fill is a returned economic indicator from the existing calculation rules.

### 7.2 Complete and partial variants

The complete national variant includes all reconciled municipality codes and all three products. It may produce unviable results under particular user assumptions; complete data does not imply affordable housing.

The partial variant uses the same geography and an explicitly declared economic subset distributed across mainland/island/urban/rural cases. Include at least one municipality lacking room rent, one lacking purchase price and one lacking whole-home rent. Also leave municipalities outside the economic release entirely. Stable declared code lists/rules define these cases; removing rows accidentally is not a coverage policy.

Do not reproduce the old sixteen-city prices by importing a test-only helper. Preserve the old cases as regressions; share only genuinely common low-level generation utilities if needed. Keep source status, query capability, scenario suitability and financial viability separate.

### 7.3 Hand-checkable integration reference

Create a tiny independent verification case using an actual built release and the normal evaluator. Override synthetic inputs/configuration explicitly; this reference is not a statement about a Spanish municipality.

| Input | Value |
|---|---|
| Saving horizon | Four months; purchase at offset 4 |
| Saver/borrower | One, net annual income 24,000 EUR throughout |
| Initial savings / retained reserve | 10,000 / 1,200 EUR |
| Nonhousing expenses / existing monthly debt | 600 / 100 EUR |
| Months 0–1 | One room, 400 EUR/month, rent share 1 |
| Months 2–3 | Whole home, 80 m² × 15 EUR/m²/month × rent share 0.5 |
| Purchase price product / target | 2,000 EUR/m²; target 60 m² |
| Mortgage | Financing 0.8; zero interest; 25 years; total-debt ratio 0.35 |
| Purchase-cost allowance / projection | 0.10; frozen |

Expected contributions are 900, 900, 700, 700 EUR; ending savings **13,200**, usable savings **12,000**, cash-constrained price **40,000**, mortgage payment allowance **600/month**, mortgage-constrained price **225,000**, and maximum purchase price **40,000 EUR**. Affordable area is **20 m²**, target price **120,000**, and target ratio **1/3**. Target upfront requirement is **36,000**, cash shortfall **24,000**, loan **96,000**, and monthly payment **320 EUR**.

Use independent expected constants/tolerances, not the implementation under test to derive its own expectations. With only the purchase observation removed, maximum capacity remains available while area/ratio become missing. Keep existing exhaustion and zero-capacity semantics; do not change them to make the map more colourful.

## 8. National map and application contract

### 8.1 Typed composition

Extend the injected service boundary with a read-only map-geography context: parent/display IDs, geography provenance/attribution, registry names/territory associations, display features and eligible codes. Do not hand UI a concrete repository, file root or mutable private index. Adapt legacy embedded synthetic geography to that same rendering view at composition.

Keep the economic `EvaluationContext`/release coverage report scoped to market data. The map knows the atlas can be larger. A separate geometry resource cache uses canonical/display manifest content identities; economic session keys still include scenario, explicit evaluated destinations, market release, model/code and runtime. Display-only changes do not require financial recomputation within the same calculation evidence. A new code fingerprint still invalidates exact economic caches as it does today.

Use this join contract:

- `A` = eligible municipality codes in the atlas.
- `M` = municipality codes in the selected market release.
- `E` = explicitly requested economic evaluation destinations; by default `E = M`.
- `R` = returned result codes.

Require `E ⊆ M ⊆ A`, uniqueness and **`R = E`**. Additional geographic context territories are not members of the economic code sets. Reject duplicate/unknown results, missing requested results and incompatible geography identities. Do not weaken those checks to accommodate partial coverage.

Atlas municipalities outside `M` render a geographic-only unavailable state with reason “Outside selected market coverage.” A deliberate evaluation subset `M - E` is “Not evaluated in this run,” never an economic zero. Within `E`, preserve the evaluator's actual per-indicator missing/unsupported/unviable/available state. Do not manufacture a `LocationResult` merely to colour an outside-release polygon.

### 8.2 Required user experience

- Initial national display is recognisable, with mainland/Balearics visible and clear controls to include/view Canarias and Ceuta/Melilla. An all-territories fit is available. Actual geographic coordinates remain unchanged; labelled inset views are optional, not required.
- Default indicator is **Target affordability**. Keep **Affordable area** and **Maximum purchase price** available. Retain fixed numerical bins and existing economic meaning; no per-scenario quantile rescaling that disguises unchanged values.
- Thin restrained municipality boundaries and stronger province orientation outlines. Avoid a one-pixel minimum on every municipal edge that overwhelms national colours. Use supported scale-aware line widths or an explicit detail toggle; preserve useful edges at urban zoom.
- Hover identifies official name/code, current indicator/value/unit, status/reason and the economic evidence label. A stable visible caption identifies official-derived geometry and synthetic market assumptions independently.
- Picking and searchable municipality selection use codes, handle duplicate names and show matching details. Search all atlas municipalities. Selecting a geographic-only municipality shows its identity/coverage explanation, not a neighbouring location's finances or a traceback.
- Province navigation/filtering is a **view/inspection aid**, not a change to salary, economic mode, result population or an implicit province average. Keep the full evaluated map available.
- View presets for mainland/Balearics, Canarias, Ceuta/Melilla and all territories; zoom-to-selected and reset are predictable. Metric/legend/selection controls do not re-evaluate economics.
- Map, table and details share one pure projection of returned indicators. Paginate/filter a large table if needed without changing the underlying evaluated population or exporting only visible rows accidentally.

A persistent label for the national demo should convey: **“Official geographic boundaries, simplified for display · Synthetic housing prices and rents.”** Geographic-only absence, missing economic input and financial unviability need explicit legend/reason semantics. Available numeric zero must retain its numeric colour rather than the missing-data colour.

Uniform maximum-price areas are valid when mortgage income binds. Do not perturb values or invent granular input differences to force a visually varied map. Use the other indicators and a declared demonstration scenario to show price-driven variation.

### 8.3 State, reload and offline behavior

Preserve draft/applied semantics, safe imports and previous-run retention on invalid input. Geometry selection and view state are presentation state; saving/buying bindings remain scenario inputs.

On a market-release change, clear stale economic results/downloads and reconcile selected codes as today. On a compatible display-derivative change, replace geometry/view evidence without mislabelling old data or unnecessarily rerunning finance. An incompatible canonical geography requires explicit composition/revalidation; no remapping silently across registry editions. Reset retired selections and stale picking events safely.

Continue avoiding external basemap tiles, tokens, fonts or provider calls in the normal offline map. Preserve the working no-provider PyDeck behavior. Use actual supported Streamlit selection APIs; browser checks must exercise real WebGL rendering. An HTTP health check or AppTest-only success is not map proof.

## 9. National-scale performance and bounded changes

### 9.1 Measure separate costs

Phase 6's 250-location case used simple synthetic shapes. Establish new measurements using full national display geometry and a representative **84-month** scenario. Record hardware, Python/dependency versions, artifact IDs, municipalities, vertices, serialized display bytes, observation count, runtime/model/code evidence and sample method.

Separate retained-input preparation, canonical validation, display validation/loading, market validation/indexing, financial evaluation, map projection/serialization, browser first display, picking/metric changes, export preparation and peak memory. Report logical cold process/resource state honestly; do not claim OS-cache coldness without evidence.

Use at least three repeated timed samples after one declared warm-up for deterministic backend paths. For browser actions record actual observations and avoid implying a robust distribution from one screenshot. Timings must cover their stated boundary, not exclude the expensive work hidden elsewhere.

Initial engineering targets on the recorded ordinary development machine:

| Operation | Target |
|---|---|
| Uncompressed national display payload | At most 20 MiB, subject to Section 6 fidelity |
| Warm-resource first applied map and national 84-month Apply | At most 15 s each |
| Metric/view-only action | No financial calls; usable within 2 s after processing |
| Selected detail, already available or computed on demand | Usable within 2 s |
| Application memory added by one national session | At most 1 GiB over loaded-resource baseline |

These are project performance goals, not universal package guarantees. A missed goal triggers measurement and a bounded repair attempt. Never relax topology/economic correctness, omit destinations, shorten the horizon or quietly revise a threshold to claim success. If a remaining goal cannot be met safely, report it explicitly and leave its criterion unverified.

### 9.2 Inspect existing scaling risks first

Concrete current risks include repeated linear membership scans in `markets/selection.py::resolve_input` and `SnapshotMarketRepository.get`, full `EvaluationContext` reconstruction, retaining every location's monthly budgets/path, serializing downloads on rerenders, repeatedly decorating full geometry, and a per-session memo of up to 32 complete runs.

Use immutable code sets/dictionaries built once where measurements justify them. Pure market modules must remain free of repository/storage imports; inject a prepared lookup/context or use a model-owned immutable projection rather than reading private indexes. Do not cache salary/scenario information in a process-global resource.

Use the existing full evaluator first on a real regional subset and a national sample. If it meets the goals, retain it. If retaining or rendering full national runs fails the goals, introduce a compact application-owned overview and on-demand detail through a shared evaluation loop:

- Per-location numeric work still calls existing preparation/finance/purchase/comparison owners.
- An overview extracts necessary values/statuses/evidence and can discard that location's full trace after projection; it is not a falsely truncated `RunResult`.
- Requested full detail recomputes the same location against pinned scenario/market/code/runtime evidence and must equal the overview numerically and by status.
- Shared iteration/preparation/result projection prevents a copied “fast financial engine.”
- Full export is an explicit on-demand operation using the existing canonical serializers. Refactor common CSV row projection if needed; do not invent a second export format or label an overview as a complete replayable run.

Preserve full API/CLI evaluation and replay. Test overview/detail/full parity, including negative months, exhaustion, reserves, missing purchase inputs and zero capacity. If no compact path is needed, do not scaffold one.

Bound expensive session caches by measured retention cost. For national runs start with the applied result plus at most one previous economic result; keep current small-release behavior only where memory evidence supports it. Cache immutable geometry once per identity; use bounded detail/export caches tied to complete inputs. Metric switching must not regenerate prices, parse captures or execute finance.

Do not add workers, tiling infrastructure or new frameworks after one slow sample. Try shared indexes, bounded retention, display payload preparation and deferred serialization first. Record any remaining architectural limit with evidence.

## 10. Commands, artifacts and reproduction

### 10.1 CLI responsibilities

Add a small coherent command surface, using the existing parser/conventions:

| Command/change | Responsibility |
|---|---|
| `build-geography` | Build immutable canonical geography from retained official inputs/config; no download |
| `validate-geography` | Verify full canonical artifact; optional supplied display artifact is checked against it |
| `build-map-display` | Prepare a deterministic display derivative from a selected canonical artifact/config |
| National demo preparation entry point | Generate labelled market inputs/recipe through packaged code; may be a thin script or one CLI command |
| Existing build/validate/inspect/query/evaluate/replay/serve commands | Accept explicit `--geography` where a schema-2 reference requires it |
| `serve --display-geography` | Select one explicit compatible display artifact; legacy embedded releases remain launchable |

Names may follow a newer established convention in the implementation checkout, but document one canonical spelling and test it. Do not add multiple equivalent wrappers. Keep acquisition explicit through the existing permitted official adapter/thin preparation command; builds and runtime commands remain offline.

Canonical artifact references belong in data/market manifests; local roots/paths stay in CLI/runtime settings. `serve` must propagate new arguments through its subprocess and packaged launcher, with clear missing/wrong-identity errors and core-only missing-map-extra guidance preserved.

### 10.2 Portable data is a deliverable

Provide actual permitted canonical geography, display derivative, demo inputs/recipe and resulting release, or a documented reachable artifact location plus a verified fresh download/restoration procedure. Keep large binaries out of ordinary Git and deliver a compact reproducible bundle using the repository's existing storage/back-up conventions. A local ignored archive, temporary `/tmp` path, source URL list or hashes alone does not prove another machine can run the map.

Record attribution and redistribution conditions for every included official component. Do not publish/upload a dataset externally without the user's authorization; prepare the permitted portable bundle and clear transfer instructions. If no durable artifact destination is authorized/available in the execution environment, report the transfer prerequisite separately instead of claiming off-machine reproduction.

The runbook must support: acquire or restore actual retained inputs → build/validate geography → build/validate display → generate demo → build/validate/inspect market release → evaluate/export/replay → serve. Runtime evaluation/serve must still work after raw acquisition files are removed. Rebuilding canonical data requires the retained raw inputs; document that distinction.

Use the tested dependency lock and explicit paths. Never claim exact output replay across different Python/dependency versions. Fresh current-version runs can establish source/wheel/UI/CLI parity under identical runtime evidence; old code fingerprints remain old evidence.

## 11. Milestones and exit checks

Each milestone ends in a coherent working state and a scoped local commit when appropriate. Build the smallest complete slice before acquiring/rendering national complexity. Milestone dependencies do not require human confirmation.

### M1 — Baseline, compatibility plan and contracts

Re-establish the actual map-enabled gate/build, inspect current versions and repair reproducible baseline issues. Record the specific current join/provenance assumptions. Specify the geography/display/schema-2 contracts, v1 dispatch/serialization behavior, runtime arguments and ownership before editing consumers.

**Exit:** current tests/gates have recorded outcomes; legacy release samples and numeric expectations retained; new contracts and allowed imports tested; progress lists the concrete next action. No global schema-version widening or blanket synthetic permission bypass.

### M2 — Canonical geography, first regional slice, then national completeness

Implement shared retained-input assembly, reconciliation, artifact storage/validation and read-only registry projection. Complete one contiguous regional slice through the real geography builder and reader. Then capture/reconcile the national snapshot including islands, Ceuta/Melilla and classified context territories. Actual market/display composition follows in M3.

**Exit:** canonical artifact with retained provenance, expected code set, complete pagination evidence, topology/exception report and actual reproducible bytes. Preserve legacy geography checks; missing national areas remain explicitly blocked until resolved.

### M3 — Display preparation and separate market composition

Prepare/validate the simplified display artifact and national orientation layers. Implement schema-2 market references through existing normalization/storage/reader owners; adapt legacy and new geometry at composition. Validate independent permission scopes and strict parent IDs.

**Exit:** one compatible real-geography/synthetic-market slice loads end to end; display QA/payload measurements recorded; old v1 releases still build/open/evaluate/serve; incompatible references and corruption fail before results are exposed.

### M4 — National synthetic release and superset map

Implement deterministic generator, complete/partial variants, national evaluated population and typed join contract. Integrate default indicator, provenance captions, coverage states, national territorial navigation, search/picking/table/details. Run the independent reference in Section 7.3.

**Exit:** national official-derived polygons have engine-derived colours; all named territories are reachable; geographic-only selections are safe; metric-specific gaps and zero/unviable states remain correct. No tests-only runtime imports or fabricated observed market evidence.

### M5 — Scale, cache and interaction verification

Measure actual national geometry and 84-month scenarios, then apply only justified changes under Section 9. Exercise small/partial/national release transitions and display transitions. Verify actual browser rendering, meaningful urban/island views, selection and UI/CLI/detail/export parity.

**Exit:** recorded performance/memory/call-count evidence, stable identity/state behavior, real browser proof and no hidden data collection. Failed targets or tooling limits remain visible, not silently waived.

### M6 — Installed reproduction, final gate and handoff

Build the final wheel and verify fresh core/map environments outside the checkout. Restore actual portable artifacts in two independent roots, run the documented workflow, confirm deterministic rebuild/current-runtime replay, and run final CI-equivalent checks. Update brief/plan/architecture/runbook/geography/progress accurately.

**Exit:** A1–A12 individually evaluated, actual commands/results/commit references recorded, portable data status clear and observed-market access still correctly described. Finish with remaining blockers and the next feature boundary.

## 12. Verification requirements

### 12.1 Focused automated coverage

Use small deterministic adjacent-polygon fixtures for unit tests, including a shared edge with extra vertices, a hole, multipart/island pieces, a tiny municipality, duplicate names/codes, an axis swap and a legitimate context territory. Synthetic test shapes are never advertised as official samples. Add a small permitted real-world retained subset where rights/size allow; test full national geometry through the explicit artifact workflow rather than downloading it in normal pytest.

| Case | Required evidence |
|---|---|
| Legacy compatibility | Existing schema-1 bundle/recipe validates without rewrite; existing commands/embedded demo still operate |
| Version/reference integrity | Unknown schema, wrong canonical ID, wrong display parent, path traversal and checksum corruption fail clearly |
| Provenance separation | Official geography + synthetic markets succeeds only through correct component rules; synthetic prices cannot become observed |
| Registry/pagination | Missing/duplicate/conflicting features, incomplete pages, wrong levels and unresolved codes are detected |
| Geometry/display | Shared edges consistent, source components/holes retained, valid joins/topology and QA thresholds measured |
| Deterministic demo | Same inputs stable under reordered registry and an unrelated new municipality; seed/version changes are explicit |
| Coverage/join | `R = E`, `E ⊆ M ⊆ A`; unknown/missing result errors; outside-market polygons remain visible without invented results |
| Economic semantics | Section 7.3 constants, purchase-only gaps, room versus flat gaps, exhaustion and numeric zero agree with full evaluator |
| Optional overview/detail | Shared rule use and full/compact/detail parity, with honest export/replay behavior |
| State/cache | Display controls add zero financial calls; correct invalidation and retired-selection behavior on artifact changes |
| Installation | Core import/help/query/evaluate/replay needs no UI; packaged map launch works outside repository |

Tests should verify behavior and independent invariants, not mirror each implementation helper. Preserve full existing finance/selection/export tests. Add sensitivity checks for any new forbidden import edges; do not weaken gates to accommodate the new namespaces.

### 12.2 Actual browser checks

Use a real browser with the installed app and supplied national artifacts. Record browser/runtime, launch command, IDs, applied scenario, actions/outcomes and limited evidence paths. Required checks:

1. National silhouette is recognisable and municipality colours are visible rather than dominated by outlines. Both large rural areas and dense urban municipalities render.
2. Canarias, Balearics, Ceuta/Melilla and multipart/coastal cases are reachable and correctly positioned. Inspect several actual municipalities from different territories by code.
3. All three indicators, legends, map/table values and selected financial details agree with returned results. Numeric zero and a missing purchase product are exercised separately.
4. Complete and partial releases use the same atlas; outside-coverage areas remain visible/selectable with honest explanations.
5. Search, picking, province/view controls, selected zoom and reset work without changing economic inputs. Repeated clicks and duplicate names do not select the wrong location.
6. Scenario changes, staged rent, invalid edits/imports, reload and release/display transitions preserve correct draft/applied/download identity.
7. Downloaded results match installed CLI and replay for the same full resolved inputs/runtime. If exports are deferred, exercise preparation, download and a subsequent scenario change.
8. Offline runtime attempts no external tile/provider requests; record console/page errors and actual interaction timings.

AppTest complements these checks but does not prove polygons appeared. Use supported public APIs; do not mutate private widget/protocol state to pass an interaction test. If browser tooling is unavailable, finish independent engineering and leave browser acceptance unverified.

### 12.3 Final quality and packaging gate

Preserve the current single gate and Python 3.12/3.13 support:

```bash
uv sync --locked --extra map
bash scripts/check.sh
uv build
git diff --check
```

If adding a justified optional preparation extra, update this same gate/CI consistently and retain required extras in every `uv run`; do not let synchronization remove map dependencies mid-check. Keep lock, Ruff format/lint, strict mypy, import contracts/sensitivity and the full test suite. Avoid a second competing quality script.

Run CLI/subprocess tests with `uv run --locked --extra map pytest` or an equivalently activated environment so child commands resolve the installed tools. Merely invoking `.venv/bin/pytest` without the venv on PATH can create environment-only CLI/import-linter failures; diagnose and correct the invocation before attributing failures to the repository.

Fresh wheel verification must unset `PYTHONPATH`, run from an unrelated directory, confirm imports resolve to `site-packages`, and test core-only plus map-enabled installs. Use the final wheel, lock-compatible dependencies and actual restored geographic/display/market bytes. Perform two-root rebuild/validation/evaluation/export/replay and installed launch. Use small fixtures for destructive corruption tests; old valid artifacts remain untouched.

## 13. Acceptance criteria and completion meaning

| ID | Requirement |
|---|---|
| A1 | Actual Phase 6 baseline and repository instructions are inspected, baseline check issues resolved or explicitly isolated, user changes preserved and execution evidence recorded |
| A2 | Existing module/import boundaries and financial/selection semantics preserved; one owner per rule; no duplicate financial, release, validation or UI calculation pipeline |
| A3 | Compatible canonical geography/display/dataset-v2 contracts implemented with strict component provenance and usable schema-1 compatibility |
| A4 | National official registry/boundaries reconciled with complete retained inputs, version/rights evidence, all required territories and explained special cases |
| A5 | Deterministic display derivative preserves IDs/components/holes, shared topology and stated fidelity limits, with measured payload and parent identity |
| A6 | Complete and partial national synthetic inputs are deterministic and pass existing normalization/query/evaluation rules; no synthetic economic value is presented as observed |
| A7 | Superset geographic joins and per-indicator coverage/financial states work, including safe selection outside economic coverage and strict rejection of malformed results |
| A8 | Recognisable national choropleth, default target indicator, all three metrics, navigation/search/picking/details and independently correct provenance are verified in a real browser |
| A9 | National 84-month performance, memory and cache/call-count targets are measured and met; any compact/detail/export changes preserve numerical and evidence parity |
| A10 | Existing exports/replay, draft/applied state, artifact transitions, core-only behavior and packaged installed map workflows work with final code/runtime |
| A11 | Full gate/build and supported-runtime checks pass; actual data/display/demo artifacts and a verified restoration path support two-root installed reproduction |
| A12 | Documentation/progress describe implemented scope, source/geometry decisions, measured limits, portable-data status, remaining observed-market blocker and future extension boundaries |

Report criteria individually with evidence. Regional-only polygons, a national outline without municipal detail, random colours, all-grey absence caused by missing demo inputs, or unverifiable temporary artifacts do not satisfy the requested national demonstration. A mathematically uniform maximum-price layer is valid when other verified indicators and the declared demo establish the expected behavior.

Blocked observed-price acquisition does **not** block Phase 7 completion, because synthetic markets are explicitly authorized. Missing official national geography, failed fidelity/scale targets, unverified actual rendering or unavailable reproducible artifacts do affect Phase 7's relevant criteria. Finish independent work when a blocker is genuinely external; do not mark unchecked requirements verified or substitute invented official data.

## 14. Long-session execution and recovery

Maintain one concise `docs/progress/PHASE_7.md`, not several competing task journals. Record starting/current revision, M1–M6 state, decisions with reasons/owners, artifact IDs and actual available paths, executed checks and results, remaining A1–A12 evidence, blockers, and one concrete next command/action. Keep references to stable repo files rather than relying on this chat or terminal history.

Work in small vertical increments: change one contract/owner, exercise the corresponding real path, repair failures, then commit a coherent state. Commit subjects begin lowercase. A commit must remain understandable and usable independently; do not split producer and required consumer changes into knowingly broken intermediate commits. Stage only owned changes and inspect the staged diff. Do not overwrite user changes or reset history.

On resumption: inspect instructions/status/log, read progress and referenced decisions, verify artifacts/tooling still exist, run the smallest recorded smoke check, then continue the next incomplete milestone. Temporary caches, captures and browser tools may have disappeared. Reacquire/restore through recorded permitted routes; a progress claim or hash is not the missing file.

When a check fails, classify source/data/implementation/environment failure, reproduce narrowly and repair at the responsible owner. Repeat the relevant checks after changes. After a final complete gate passes, broaden/repeat only for a new change or unresolved concern. Do not repeatedly reinstall or run the entire suite instead of diagnosing a known failure.

After two attempts at the same failing acquisition/tool approach, change the approach using evidence or record the dependency. Do not loop indefinitely, relax schemas, silently change product policy, or replace official geography with a synthetic outline. Ask only for genuinely missing authorized inputs, an unresolved material product decision, or an external action requiring authorization. Continue independent work while documenting what is blocked.

Milestones and progress records are implementation aids. They do not require new agent services, subagents, external task systems or routine user approval. Continue through the authorized phase until complete or a genuine blocker leaves no useful dependent work.

Final implementation report: concise behavior changes, local commit references, A1–A12 states, commands/results, geography/display/market IDs and portable-artifact availability, national performance/browser evidence, remaining limits and next action. Distinguish executed checks from historical/reported evidence.

## 15. Future implementations and handoff

The pipeline must remain modular enough that later features fit without substantial repository restructuring. Prepare only the extension points used here.

| Future feature | Boundary preserved by Phase 7 |
|---|---|
| **Save in A, buy in B — next economic feature** | Independent bindings and reusable saving/purchase services; geographic inspection is separate from saving origin and borrower-income assumptions |
| **Real housing observations** | Replace synthetic market releases without regenerating canonical geometry; retain exact product periods/segments and permission checks |
| **Salary realism by profession/place** | Separate versioned salary/employment context; user-assumed income remains explicit, and no geography heuristic becomes a salary model |
| **Historical scenarios, e.g. 2010 — latest major extension** | Versioned registry/canonical geography and explicit market references; current boundaries are never silently reused as historical truth |
| **Submunicipal geography** | Typed geographic identity and clear map/economic code join, without implementing new levels or manufacturing neighbourhood prices now |
| **More display levels or tiles if measured later** | Display derivative independent of economic release and financial engine; stable geographic IDs and numeric meaning |
| **Regional costs, financing, returns and other finance refinements** | Existing finance/purchase-policy owners, not map widgets or geometry preparation |

Update the implementation plan with Phase 7's actual scope and the reordered immediate next feature. Preserve the previous phases as history, including their honest observed-data blockers. Hand off supported artifact schemas/commands, reconciliation/fidelity decisions, portable inputs, parity/performance evidence and remaining prerequisites.

## 16. Research basis

The following primary sources informed the workflow and technical constraints. The explicit requirements above are the phase contract; inspect current installed APIs and source metadata during implementation.

- [OpenAI — Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex): applied here through a persistent phase plan and explicit milestone verification.
- [OpenAI — Harness engineering](https://openai.com/index/harness-engineering/): applied through navigable repository decisions and mechanically preserved dependency boundaries.
- [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): applied through recoverable progress, coherent increments and actual end-to-end checks.
- [INE — Municipality-code operation](https://www.ine.es/dyngs/INEbase/operacion.htm?c=Estadistica_C&cid=1254736177031&idp=1254734710990) and [methodology](https://www.ine.es/daco/daco42/codmun/codmun00i.htm): official identifiers, snapshot dates and in-year changes.
- [IGN — Administrative-unit collection](https://api-features.ign.es/collections/administrativeunit?f=json), [service/licence](https://api-features.ign.es/?f=html), and [CNIG boundary downloads](https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos): official polygon route and alternative national product.
- [IGN — Territorial organisation](https://educativo.ign.es/atlas-didactico/organizacion-territorial-bach/estructuracin_interna.html): shared/nonmunicipal territorial context.
- [Shapely — coverage simplification](https://shapely.readthedocs.io/en/stable/reference/shapely.coverage_simplify.html): coverage preconditions and GEOS requirement; fidelity thresholds in this guide are project decisions, not guarantees from that API.
- [Streamlit — PyDeck chart](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart): supported rendering/selection surface; exact installed behavior remains subject to verification.

### Preparation-evidence note

Repository inspection and checks were performed at the revision in the introduction. No repository implementation files were edited to prepare this guide. The initial direct `.venv/bin/pytest` invocation lacked the venv executables on PATH for subprocess tests; that environment-only result is superseded by the correctly invoked `uv run --locked --extra map pytest` result recorded below. The full aggregate gate remains distinct from individual checks because its Ruff import findings were not repaired during document preparation.

**Correctly invoked pytest result:** `uv run --locked --extra map pytest -q --tb=short` — **329 passed in 17.29 s**. Independent strict mypy, ten import contracts and build passed. The aggregate gate stopped at the four Ruff findings listed in Section 1.2. Browser and installed-wheel behavior were not re-executed during guide preparation; their verification belongs to this implementation phase.
