# PHASE 3 — Pilot Dataset and Offline Market Access

Implementation guide for an autonomous Codex run. Prepared 7 October 2026.

**Outcome:** a small, traceable market dataset with verified municipal identifiers and polygons, explicit coverage, reproducible immutable releases, and an offline repository implementing the existing MarketData protocol. Acquisition, persistence and querying have separate owners. Financial calculations remain unchanged.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), inspected at **b523385f448c32cd71fd70c80e4b679d3f384102**. The latest checkout includes the completed Phase 2 financial engine as well as Phase 1's contracts/audit. Intended guide location: **docs/phases/PHASE_3_pilot_dataset.md**. Inspect the current worktree; do not reset it to this commit.

## 0. Start here

1. Inspect the checkout, applicable repository instructions, user changes and recent commits.
2. Read **docs/PROJECT_BRIEF.md**, **docs/IMPLEMENTATION_PLAN.md**, **docs/ARCHITECTURE.md**, **docs/DATA_COVERAGE.md**, and both existing progress records.
3. Inspect **models/market.py**, **models/contracts.py**, **models/base.py**, the current CLI/configuration loader, source catalog, audit CSV and quality/import contracts.
4. Read this guide's scope, release format and lookup semantics before designing adapters.
5. Follow M1–M6 in Section 11. Continue autonomously between checkpoints; keep **docs/progress/PHASE_3.md** current.
6. Finish against Section 13's acceptance criteria, distinguishing engineering verification from real-data readiness.

The current user request and applicable repository instructions take precedence. The brief owns product meaning; the implementation plan owns component responsibilities; this guide supplies Phase 3 decisions left open there. Resolve ordinary implementation choices independently and record material decisions. Ask only about a genuine blocker or a change that materially alters the intended project.

Local code, source inspection, permitted data acquisition, checks, documentation and scoped local commits are within scope. No push, merge, publication, deployment, provider contact, paid access or credential setup is authorized by this guide. Do not create AGENTS.md or an agent service for this task; respect existing applicable instructions. A single Codex workflow suffices.

## 1. Current implementation and inherited conditions

### 1.1 Existing components

| Component | Current state | Phase 3 use |
|---|---|---|
| Scenario and geographic references | Independent saving/buying bindings; explicit dates and financial assumptions | Preserve them; do not execute geographic modes |
| MarketObservation | Metric/unit, period, statistic, basis, segment, evidence kind, source and timestamp | Normalize into this existing contract |
| MarketQuery / MarketLookup | Period/segment-aware request; available/missing/unsupported result | Implement their concrete offline behavior |
| MarketData | get(query: MarketQuery) -> MarketLookup | Preserve the protocol |
| Financial engine | Savings, mortgage, proportional costs and fixed-financing capacity implemented | No dependency on data acquisition or storage |
| ingestion and markets | Reserved namespaces | Add concrete implementations in their existing locations |
| Source catalog / coverage audit | Leads and 48 audited area/metric rows | Evidence for source selection; not a ready dataset |
| CLI | validate-scenario only | Preserve it; add only working dataset commands |
| Data directories | Raw, processed and releases excluded from ordinary Git | Retain local artifacts; track small permitted metadata |
| Tooling | uv.lock, Ruff, strict mypy, pytest, seven import contracts | Extend rather than replace |

The checked-in README links a Phase 2 guide that is absent from the tracked tree at the inspected commit. Preserve any supplied/untracked guide in the implementation checkout. Correct relevant documentation links without recreating Phase 2 or treating a missing explanatory document as a reason to replace working code.

### 1.2 Inspection verification

On the recorded commit, locked installation succeeded. The **136 tests**, strict mypy, Ruff lint, seven import contracts and package build passed when run individually.

However, **bash scripts/check.sh stopped at Ruff's formatting check of the README financial Python example**. This is a small inherited documentation-format issue, not a financial-engine failure. M1 must repair it with the locked formatter and re-run the complete gate. Do not repeat the old progress document's all-green claim without current evidence.

No real release, concrete market reader or municipal polygon bundle exists yet. Phase 3 must supply them; synthetic fixtures alone do not satisfy the real-pilot requirement.

## 2. Scope and initial pilot

### 2.1 Required deliverables

- An explicit source/access plan and narrowly scoped acquisition or curated-input adapters.
- Validated observations preserving source meaning, reference periods, provenance and segmentation.
- An official-code location registry and matching versioned municipality polygons.
- One canonical release format, common persistence/validation owner, hashes and immutable publication to local storage.
- Coverage and quality reports, including intentional gaps.
- An offline SnapshotMarketRepository implementing MarketData.
- Thin build/validate/query CLI commands and documented reconstruction from retained inputs.
- Offline tests, a built-wheel smoke, progress evidence and a Phase 4 handoff.

### 2.2 Default geographic scope

Use the audit's municipality-level **Madrid, Barcelona and Jaén** as the core pilot. Include **Getafe** as the preferred additional gap case if its inputs and geometry can be verified without widening research substantially.

| Location | Audit code, to re-verify | Intended metrics |
|---|---|---|
| Madrid | 28079 | Purchase €/m², whole-home rent €/m²/month, room €/month |
| Barcelona | 08019 | Same three metrics |
| Jaén | 23050 | Same three metrics; audit marks its code provisional |
| Getafe, additional case | 28065 | Purchase and whole-home rent; room remains missing unless independently sourced |

The core requires nine actual observations under the selected source profiles. Getafe's absent room rent is an expected coverage gap, not a zero-valued observation. Missing optional Getafe data does not waive the core requirements.

Default reference periods follow the audited leads: September 2026 for headline sale/whole-home rent and Q2 2026 for rooms. Verify these against retained primary evidence. If a period cannot be obtained, select another **explicitly dated** profile and document the change; never replace it silently with whatever the website currently displays.

Do not expand to all 16 audited municipalities, every province or all Spain before this workflow works. A bounded substitution for an unavailable core location needs equivalent metric/code/geometry evidence and a documented reason; do not remove hard cases simply to mark the phase complete.

### 2.3 Deferred work

No scenario preparation, income interpolation, rent sharing, utility allocation, price projection, target-price calculation, affordability indicators, map rendering or financial formulas.

Do not implement salary datasets, historical reconstruction, detailed taxes, variable down payments, DVC, Hydra, DuckDB, scheduled refreshes, provider registries or a general geospatial platform.

Whole-home €/m²/month remains a source measure. Multiplying it by a rental area and applying a household share belongs to Phase 4. Target purchase size is independent of rental size. The repository must not turn pooled prices into a specific 60/100 m² flat or house.

## 3. Ownership and the one shared storage addition

Keep one installable package and the existing src layout. The following additions have concrete responsibilities:

| Path | Owns |
|---|---|
| models/dataset.py | Release, capture, coverage, location and build-configuration records |
| ingestion/adapters/ | Only the chosen source-format/acquisition adapters |
| ingestion/normalize.py | Provider/curation fields -> existing MarketObservation records |
| ingestion/geography.py | Official-code reconciliation, source polygon selection and CRS conversion |
| ingestion/release.py | Assemble a validated bundle, coverage and release recipe |
| storage/release.py | Shared canonical serialization, release loading/validation, hashing and atomic local writes |
| markets/repository.py | Offline selection and MarketLookup behavior |
| markets/geography.py, if needed | Read-only access to released geometries; no duplicate preprocessing |
| cli.py | Parse arguments, load explicit configuration and delegate |
| configs/sources/pilot.yaml | Validated pilot recipe and source selection |
| data/manifests/ | Small permitted source decisions and release references |
| tests/data/ | Ingestion, geometry, storage, query and CLI tests |
| tests/fixtures/synthetic/ | Tiny synthetic capture/release inputs and geometry |
| docs/progress/PHASE_3.md | Current execution evidence and next actions |

**Why storage is added:** both ingestion and markets need the same release format and verification. Existing boundaries prohibit them from importing each other. Putting common persistence into either side would create a forbidden dependency or duplicated parsers. A small shared storage namespace solves an actual current need; it is not a separate service or framework.

### Dependency rules

- models -> standard library and validation library; no implementation imports.
- storage -> models and narrowly needed file/geometry libraries; no ingestion, markets, finance, application, config, CLI or UI.
- ingestion -> models and storage plus chosen source/geographic tools; no markets or finance.
- markets -> models and storage; no ingestion, config, CLI, finance or UI.
- finance stays independent of storage and all data implementations.
- CLI composes config, validated models, ingestion and markets.
- Future application services use markets; they do not bypass selection through storage.

Extend Import Linter for the new namespace: add storage to forbidden dependencies for models, finance, scenario config, application and direct UI imports; add a storage-only-models internal contract. Preserve current contracts. Include sensitivity checks for a forbidden finance -> storage edge and a storage -> implementation edge.

Keep schema validation in models and persisted-bundle verification in storage. Both writer and reader use that verification. Provider adapters translate source-specific representations once. Do not copy JSONL parsers, checksum rules or geometry checks into each adapter/repository.

Use standard-library JSON, CSV, pathlib, hashlib and HTTP tools where sufficient. A small Shapely dependency is justified for polygon validity; add an Excel reader such as openpyxl only if the selected official INE input needs it. Prefer GeoJSON from the official geographic service; add a CRS/driver dependency only when the chosen source actually requires conversion. No pandas/GeoPandas/database stack is required for this pilot.

Keep supported dependency versions in pyproject.toml and the one lockfile. Do not use dynamic imports or broad type ignores to evade dependency/type constraints.

## 4. Source acquisition, rights and bounded decisions

### 4.1 Audit leads are not authorization or captures

The source catalog says redistribution is unestablished. The historical audit's numeric_verified means a reported value was checked, not that it is licensed, stored reproducibly or correctly mapped for this release. Preserve that audit as historical evidence; use a separate current decision record rather than rewriting its unknown reuse fields to assumed permission.

The inspection found a concrete source constraint: Idealista's general terms restrict copying through automated or manual processes without written permission, while its report methodology includes attribution language. Those statements do not by themselves establish the intended dataset acquisition/redistribution route. Record the applicable source-specific permission or license evidence; do not declare that attribution alone resolves the question.

A manually curated CSV is a supported **format**, not a way around source restrictions. Do not scrape listing pages, bypass a wall, invent an API, borrow credentials or contact the provider.

### 4.2 Choose only necessary sources

| Input | First lead | Required distinction |
|---|---|---|
| Sale and whole-home rent | Audited Idealista reports, if the route is permitted | Asking indicators, pooled homes; preserve statistic and methodology |
| Room rent | Audited Q2 press release or another verified permitted source | Room product; actual absolute price and its period |
| Official codes | INE municipality-code operation/current official file | Five-digit municipal code, separate control digit |
| Polygons | IGN/CNIG administrative units and license | Municipality polygons, not administrative boundary lines |

Official alternatives may be examined if the first market source is restricted. Do not silently replace asking prices with valuations, tax-declared rents or transactions. Their basis remains distinct and any revised pilot profile must say what question it supports.

For each selected source record:

- Source ID, product/scope, primary URLs and applicable terms/license URL.
- Allowed acquisition route and evidence/reference for that decision.
- Local-use and redistribution scope separately: permitted, restricted or unresolved.
- Attribution requirements and whether raw captures/derived rows may be committed or shared.
- Review date, selected release/methodology and exact metric/period/segment mapping.
- Restriction or unknown, next action and affected pilot cells.

Do not embed contracts, credentials or private permission correspondence in Git. A reference to retained private evidence can support an authorized local route without committing the document.

### 4.3 Continue independently when a source is blocked

Bound source resolution: inspect the named primary report, applicable terms/metadata and one relevant alternative route. For transient HTTP failures use short timeouts and at most two retries. Record persistent restrictions; do not spend the autonomous run trying more mirrors or unrelated sources indefinitely.

Complete the engine, official geography work, immutable storage, queries and offline fixture verification even when market access is unresolved. Record real-data criteria as blocked. **A synthetic release cannot become an observed release to make the phase green.**

A local-only observed release is acceptable when its local acquisition/use is permitted, even if redistribution is not. Keep its files out of Git and label that scope. If local acquisition/use is itself unresolved, do not create that release through the uncertain route; finish independent engineering and report the concrete decision needed.

No user confirmation is required for routine permitted acquisition, schema choices or checkpoints. Provider contact, payment or new account access would require separate authorization; this phase does not initiate them.

### 4.4 Capture before processing

Preserve immutable inputs under data/raw, identified by SHA-256, with a sidecar capture record. Distinguish provider_download from curated_extract. A curated file's hash fingerprints that file, not an HTML page that was never retained.

Capture metadata includes source ID, primary/resolved URL where relevant, timezone-aware acquisition/review timestamp, published date/release when available, raw file hash/size, route, format and permission reference. HTTP status/content type should be recorded for downloads. Reject an error/login HTML page presented as a CSV, JSON or Excel capture.

For curation keep raw_value, raw_unit, source location label, provider release/period, concise row/page locator and review evidence. Do not preserve entire articles or screenshots merely to store a few values. Where permitted, retained primary bytes are stronger than a mutable URL alone.

Do not invent a precise retrieval time from the audit's date-only accessed_at. Obtain an actual attributable capture/review record. Reprocessing does not change the observation's capture timestamp. Redownloading a revised source creates another capture, even if its reference month is unchanged.

## 5. Normalization and source meaning

Normalize into existing MarketObservation objects, without changing their core schema or the financial result models.

| Metric | Normalized unit | Meaning |
|---|---|---|
| purchase_price_per_m2 | eur_per_m2 | Reported purchase indicator, with its asking/transaction/valuation basis |
| whole_home_rent_per_m2_month | eur_per_m2_month | Unit rent for a complete dwelling, not a monthly household bill |
| whole_home_rent_per_month | eur_per_month | Only when directly supported by a chosen source |
| room_rent_per_month | eur_per_month | Room-level rent, not the whole flat |

The default pilot does not need a monthly-whole-home-rent observation if the source supplies only €/m²/month.

### 5.1 Normalization rules

- Parse locale-specific numeric text with an explicit declared format. Distinguish decimal commas from thousands separators; do not strip every punctuation mark.
- Preserve original value/unit in capture evidence; convert only supported representations. Validate positive finite values through the existing model.
- Treat blank, suppressed, unreported or inaccessible cells as missing, not zero. A percentage change does not supply an absolute price.
- Map source statistics centrally. For the audited whole-home indicators the lead is weighted_zonal_medians; the room release reports mean. Never replace them with a generic median or average silently.
- Set pooled when the source pools homes. Leave unknown size/bedroom/contract dimensions unknown; do not fabricate an ordinary flat, 80 m² or two bedrooms.
- Record utilities/bills uncertainty in quality notes; do not infer it from a scenario's rent_includes_utilities input.
- observed means a reported source observation was captured. Document provider estimation practices. If a particular value is known to be estimated, use estimated with a real method description.
- No new statistical gap filling, nationwide room multiplier, cross-city interpolation or geographic fallback in this phase.

### 5.2 Three separate time concepts

Keep reference interval, publication date and acquisition timestamp distinct.

- A September monthly reference is **[2026-09-01, 2026-10-01)**.
- Q2 is **[2026-04-01, 2026-07-01)**, even if its report was published in August and captured in October.
- A source's rolling sample window/methodology is not the same as its labelled reference month. Preserve any such distinction in methodology/quality metadata.

Do not expand a quarterly value into three fake monthly observations, shift it into September, or interpolate it to a scenario purchase date. A release can contain different periods for different metrics, declared visibly.

Keep source_release and methodology_version where known. Unknown versions remain explicitly unknown, not fabricated version strings. Source revisions for the same reference period remain separate retained captures/releases.

### 5.3 Observation lineage without duplicating domain fields

Use a small release wrapper, for example ReleasedObservation:

- observation: the existing MarketObservation.
- capture_id: a reference to one retained source capture in the manifest.
- source_locator: concise row/page/cell identifier.

JSONL contains these wrapper records; repository.get returns the contained MarketObservation, preserving MarketData. The wrapper avoids forcing dataset-specific capture fields into every existing domain record.

Validate that each observation's source ID, URL/release and retrieved_at agree with the referenced capture. Do not duplicate a second editable value, unit, period or location alongside observation. Every observed/estimated row must have real lineage; synthetic IDs remain confined to explicit fixtures/releases.

## 6. Official identifiers and geometry

### 6.1 Registry and crosswalk

Obtain the current official INE reference and applicable in-year changes. Preserve its version, capture hash and effective date. The official municipal code consists of two province digits plus three municipality digits; the separate control digit is not part of the five-digit join key.

Released codes are strings, including Barcelona's leading zero. If the official spreadsheet splits numeric columns, normalize with their documented widths; do not pad arbitrary provider identifiers based on guesses.

For each selected municipality retain:

- GeographicReference, official name and province/code.
- Registry version and verification evidence.
- Explicit source-label -> official-code mapping, with source geographic scope.
- Geometry feature identifier and boundary version.

Names may help establish the crosswalk but are not runtime join keys. A city label must mean the municipality, not its province or metropolitan area. Jaén's provisional audit status is resolved by official evidence, not by copying its existing code.

Reject unresolved names/codes, duplicate mappings and a province row assigned to a city. Support accents and official spelling changes without changing identity opportunistically.

### 6.2 Boundary source

Prefer the official IGN API-Features **administrativeunit** collection's GeoJSON route for a small selection; metadata identifies its schema, items and license. Inspect the actual schema/queryables and identifiers before writing filters. Do not hard-code an unverified property name or assume service nationalcode equals the INE string.

Use administrative polygons, not the similarly named administrativeboundary line collection. If the API route is unavailable, use a permitted official CNIG file and only the driver/conversion needed for that format. Do not require a national download when a verified subset route works.

For API retrieval, follow required pagination and verify each requested municipality is fully represented. A bounding-box response can contain unrelated features; filter/join by verified identifiers. Do not accept the first page as the full pilot or choose features only by their names.

Retain the raw response/file and service/dataset version where available. When a live service has no named release, identify the frozen boundary snapshot honestly by capture time and content hash; do not invent an official edition.

### 6.3 Released geometry requirements

- GeoJSON FeatureCollection in **OGC:CRS84 longitude/latitude**. Do not merely relabel projected or latitude/longitude data.
- Nonempty, valid Polygon/MultiPolygon geometry; finite coordinates and closed rings.
- Exactly one released feature per selected municipal code. Preserve complete multipart territories and holes; combine parts only through an explicit, validated operation.
- Unique feature IDs/codes, registry join integrity and observation boundary_version agreement.
- No substituted points, rectangles or simplified fake municipal boundaries.
- No simplification, clipping or automatic geometry repair by default. If actual source defects require repair, retain the original, record the operation/tool and verify the result rather than silently applying buffer(0).

Use one shared geometry validation routine in persisted-bundle verification; ingestion uses it before a release is accepted and the offline reader/validator uses the same rules. Keep Shapely objects out of financial/scenario contracts.

Store source/target CRS, attribution, source version and processing decisions. Geometry without market observations may remain present so future maps can show gaps; market observations without their selected municipality geometry fail validation.

IGN/CNIG's license requires source recognition, including derived-data attribution where applicable. Preserve attribution in the manifest and pass it to the later map layer; do not render a map now.

## 7. Release contract and common storage

### 7.1 Minimal physical format

Use small transparent formats, not a database:

~~~text
data/releases/<release_id>/
    manifest.json
    observations.jsonl
    locations.json
    boundaries.geojson
    coverage.json
~~~

Raw captures and temporary/processed artifacts remain outside that directory. A complete release is portable: readers need no raw source path, network connection or live configuration. Raw captures remain necessary for rebuilding and verifying acquisition provenance, not for normal queries.

### 7.2 Manifest fields

Define frozen records in models/dataset.py with strict finite values, forbidden unknown fields and explicit schema_version=1 for this new dataset format. Do not alter Scenario's version alias. Group related fields; do not create a class for every scalar.

| Group | Required information |
|---|---|
| Identity | Dataset schema version, release ID, observed/synthetic kind, full content digest |
| Build recipe | Processing version, producer code revision/dirty-state evidence, normalized build configuration or its retained digest, fixed recipe timestamp |
| Scope | Selected registry locations, reference profiles by metric/segment, known limitations |
| Sources | Capture IDs, hashes, source/release/methodology, timestamp/publication metadata and lineage references |
| Usage | Per-source local/redistribution decision and attribution; overall release scope |
| Files | Safe relative path, role, SHA-256, byte size and relevant record counts for each payload |
| Geography | Registry version, boundary version/source/CRS and processing evidence |
| Coverage | Expected/available/gap counts and the coverage artifact reference |

The manifest must not contain absolute workstation paths, credentials, copied permission correspondence or implicit latest-source settings.

Build-time elapsed/log timestamps are not identity inputs. To produce byte-identical outputs from the same recipe, keep the recipe timestamp explicit and fixed; do not insert datetime.now into observations or the manifest on every rebuild. Record actual executions in progress/log output.

### 7.3 Coverage and profile rules

coverage.json contains one result per expected location/metric/profile in the recipe:

- available with a matching released observation.
- missing for a supported profile whose value is absent, such as Getafe room rent.
- unsupported for a requested product/shape the source/release cannot represent.

Include a concise reason for every gap, capture/source evidence where relevant and counts that reconcile to observations. Coverage is generated from validated inputs, not separately hand-edited to make the release complete.

A source-access block must be visible in readiness/coverage. Do not write an available cell with an empty value, or an observed release containing synthetic replacements.

The recipe selects one source/basis/statistic per queryable profile. The current MarketQuery lacks source/basis/statistic selectors; therefore conflicting alternative series cannot be silently bundled under the same query key. Select one explicitly or reject an ambiguous build. Keep alternative raw inputs for a future selection-policy extension.

### 7.4 One verification owner

storage.release verifies:

- Strict JSON/JSONL parsing, including duplicate object keys and non-finite numeric tokens.
- Manifest/schema, file roles, hashes, sizes and counts.
- Positive/compatible observations via existing models.
- Source-capture references, selected-profile consistency and evidence-kind separation.
- Semantic duplicate query keys, not only identical lines.
- Registry/code/geometry relationships and shared polygon validity.
- Coverage reconciliation and attribution/usage metadata.
- For an observed release, permitted local use for every included source with an evidence reference. Overall redistribution scope must not be more permissive than any included source; unresolved scope cannot become permission.

A duplicate key includes location level/code, reference interval, metric and full segment. Different values or sources under the same selected key are a conflict; reject instead of first/last-row-wins. Exact repeated rows also fail, exposing source/parser mistakes.

Do not turn release corruption, invalid rows or a missing payload file into MarketLookup(status=missing). These are release validation errors and must prevent opening the repository.

Payload paths must resolve inside the release directory. Reject absolute paths, traversal and symlinks escaping it. Hash verification is integrity checking, not a claim that a manifest is signed or trusted.

## 8. Reproducible build and immutable local publication

### 8.1 Recipe and acquisition separation

configs/sources/pilot.yaml describes locations, source/capture references, reference profiles, normalization settings and expected coverage. Runtime roots are explicit CLI parameters, not economic scenario fields.

The CLI can reuse config.load_mapping for safe YAML/JSON parsing, then validate a dataset-specific build record. Pass validated configuration and explicit paths to ingestion; do not import config.py into ingestion or storage.

The required builder consumes retained local inputs and is **offline**. Network acquisition is a separate source-adapter operation. If an acquire command is added, it must be narrowly working and respect source decisions; do not advertise a collector that returns fake/empty rows.

### 8.2 Deterministic bytes and identity

- Sort observations, locations, features and coverage by documented semantic keys.
- Use stable UTF-8 serialization, key ordering, line endings and JSONL record layout.
- Preserve capture timestamps and normalized input metadata.
- Derive the content digest from canonical manifest metadata excluding its own ID/digest plus payload digests. Do not hash a manifest containing a digest of itself.
- Use a safe content-addressed ID such as pilot-<full_sha256>, with a different explicit prefix for synthetic releases.
- Keep absolute output roots, fresh execution timestamps and temporary paths out of the identity.

Same captured inputs, configuration, processing version and code evidence must produce the same release ID and bytes. A changed value, source capture, profile, geometry or processing version must change identity. Document the exact rule once in storage; do not implement independent ID recipes in ingestion and CLI.

If the working producer tree is dirty, record evidence of its relevant diff/content fingerprint; do not claim a commit hash fully describes uncommitted processing code.

### 8.3 Atomic write behavior

Build into a task-owned temporary directory under the destination filesystem. Write all payloads, compute metadata, run the common validator, then atomically publish the directory.

If the final ID already exists, verify it and return the existing release only when content/metadata agree. Never overwrite, merge files into it or offer a force replacement. A failure leaves no directory that looks like a complete release. Clean up only task-owned staging files.

A source correction or new observation creates a new release. Existing released directories are never updated in place.

### 8.4 Retention and Git

Retain immutable raw inputs and real releases locally with documented backup/transfer instructions. A hash or URL cannot recreate lost bytes, and a provider may revise/remove its source.

Git stores code, build configuration, tests, synthetic fixtures and small permitted manifest/reference metadata. Real provider data stays out of Git unless its exact intended redistribution is permitted and deliberately chosen. Do not commit national geometry downloads or a large release merely because the raw folder is ignored.

Do not require DVC for this small pilot. Add it later if artifact size/multi-machine coordination justifies it. A synthetic release fixture can be built in a temporary test directory; it must never masquerade as the retained real pilot.

## 9. Offline market repository and exact selection

### 9.1 Public behavior

Implement a small concrete repository, for example:

~~~text
SnapshotMarketRepository.from_release(release_dir, *, allow_synthetic=False)
    -> SnapshotMarketRepository

repository.get(query: MarketQuery) -> MarketLookup
repository.manifest -> validated immutable release metadata
~~~

Load and validate one explicitly selected local release once. Keep a small in-memory index; no query-time disk scan, acquisition, cache refresh or network call. Do not auto-select the newest directory.

Expose released location/geometry metadata through a small read-only API when needed. Return records/copies that cannot mutate the indexed dataset or later query results.

Normal observed use rejects synthetic releases unless the caller explicitly opts in for tests/demos. The kind remains synthetic in every output/metadata path; allow_synthetic is not a relabelling operation.

### 9.2 Period contract

**get uses exact reference-interval equality**: both start and end must match the selected observation. It does not select the nearest, latest, enclosing quarter or overlapping interval.

A Q2 room observation is available for a Q2 query. A September room query is missing unless that interval is actually present. This deliberate strict rule avoids treating a quarterly benchmark as September data.

Phase 4 may implement an explicit base-observation/as-of/freshness policy using the manifest profiles and then call get with that selected observation interval. Any older-period use must retain and display its original period. Do not implement projections or stale-data fallback inside get now.

### 9.3 Segment contract

- An explicit property_type must match exactly. pooled is not flat or house; no automatic proxy conversion.
- Each supplied size_band, bedrooms or contract category must be fulfilled by the source segment. Unknown source detail cannot satisfy a specific request.
- None for an optional query dimension means no requested restriction in that dimension, not a fabricated source value.
- query.segment=None means no segment restriction. Return available only for a unique selected observation.
- Multiple matching candidates are unsupported with an explicit ambiguity reason, not an arbitrary winner. The builder already rejects duplicate selected keys; ambiguity from an underspecified query is a separate possible case.

Do not add financial/rental-area logic to this matching function. Later explicit pooled-to-flat approximations belong in a selection/preparation policy and must remain labelled estimates.

### 9.4 Status classification

| Situation | Result |
|---|---|
| One exact period/location/metric match satisfying requested segment | available with unchanged observation and provenance |
| Municipality outside the release, absent supported metric for that location, or absent requested interval | missing with a useful reason |
| Non-municipal query level unsupported by this pilot; direct monthly-home metric absent from its capabilities; unavailable detailed segment | unsupported with a useful reason |
| Query lacks selectors needed to choose among multiple candidates | unsupported: ambiguous selection |
| Corrupt/invalid release or missing required file | Raise a validation/load error; do not return a lookup gap |

Classify against declared release capabilities before searching values. Getafe room rent remains missing because the room profile is supported elsewhere; a flat-specific query against a pooled-only release is unsupported. Keep reason conventions stable and tested.

MarketLookup's existing status/reason/observation contract suffices. Do not change it into numeric sentinels or introduce a second incompatible market-result type.

## 10. CLI and callable workflows

Keep validate-scenario unchanged. Add thin commands with explicit paths:

~~~bash
spain-housing build-release --config configs/sources/pilot.yaml \
    --data-root /absolute/data --release-root /absolute/releases

spain-housing validate-release --release /absolute/releases/RELEASE_ID

spain-housing query-market --release /absolute/releases/RELEASE_ID \
    --query /absolute/query.json
~~~

For synthetic tests/demos require an explicit --allow-synthetic flag on relevant commands. Keep fixture input profiles separate from the real pilot recipe.

build-release delegates to the offline builder and common storage owner; output includes the actual release ID/path and readiness/kind. validate-release delegates to the same full validator and returns a machine-readable summary. query-market validates MarketQuery and serializes MarketLookup.

Valid missing/unsupported lookups are successful queries, exit 0. Invalid arguments, malformed configuration/release and prohibited build inputs exit 2 with concise stderr and no misleading result JSON. Do not swallow errors into zero observations. Preserve stdout for results and progress/error text for stderr.

The commands must work from another working directory with explicit absolute input paths. No global data root, implicit source download or dataset hidden inside a Scenario. Do not add an affordability/evaluate command before Phase 4.

## 11. Autonomous execution and milestones

### 11.1 Persistent evidence

docs/progress/PHASE_3.md is the single current execution record:

- M1–M6 status and acceptance IDs with evidence.
- Exact checks/results, last verified checkpoint and current next action.
- Material schema, access, query, identity and geometry decisions.
- Source blockers, affected cells and whether engineering or real-data readiness is incomplete.

Keep source/capture facts in their manifests and current access decision record, not duplicated across several progress files. Do not paste entire logs or append speculative plans indefinitely.

Each slice follows inspect -> implement -> focused verification -> repair -> diff review -> scoped local checkpoint -> update state -> continue. No confirmation is needed between milestones. Run failing checks after repairs before advancing.

On restart/compaction inspect worktree/history, read progress and verify the claimed last checkpoint. Preserve existing user work. Do not reset, auto-stash, stage unrelated files or invent Git identity. If commits are unavailable, leave reviewable changes and record that limitation.

Tool/network failures do not justify weakening schema/import rules or labelling a fixture as real. Continue independent engineering and report remaining real-data acceptance items honestly.

### 11.2 M1 — Verify baseline and establish contracts

**Implement:** repair the README format issue; rerun the current gate; create Phase 3 progress; settle pilot profiles and minimal release/capture records; add the shared storage namespace and import rules.

**Verify:** all existing tests and the complete locked gate pass; new model round trips and dependency sensitivity work; Scenario/finance/MarketData remain compatible.

**Checkpoint:** a verified foundation, concrete format and scoped source plan. Do not scaffold unused future modules.

### 11.3 M2 — Source decisions and observation inputs

**Implement:** applicable access/reuse evidence, bounded source selection, permitted immutable capture/curation inputs, chosen adapters and normalization.

**Verify:** raw hashes/locators/periods, parsing of localized values, source meanings, missing cells, lineage and rejection of source changes/errors. Compare a small real sample against retained primary evidence when permitted.

**Checkpoint:** actual normalized core rows, or clearly blocked real inputs plus working synthetic adapter verification. Continue later engineering if market acquisition remains blocked.

### 11.4 M3 — Registry and official polygon subset

**Implement:** official INE reconciliation, provider/code crosswalk and retained IGN/CNIG geometry subset with version/CRS/attribution.

**Verify:** every selected code, leading-zero preservation, municipality/province distinction, full multipart geometry, topology and one-to-one joins. Source identifiers/property names are inspected rather than guessed.

**Checkpoint:** real official geography independently ready, or exact access defects recorded. Synthetic rectangles remain tests only.

### 11.5 M4 — Release persistence and deterministic build

**Implement:** shared verification, canonical files, coverage/profile reconciliation, content identity and atomic idempotent writes; generate a real release only from permitted verified inputs.

**Verify:** byte-identical rebuild from fixed captures/recipe, new identity on changed inputs, no overwrite, failed-write cleanup, hash/path/duplicate/lineage/geometry corruption rejection, relocated offline opening.

**Checkpoint:** a working synthetic release through the actual builder and, where inputs permit, the immutable observed pilot.

### 11.6 M5 — Repository and dataset CLI

**Implement:** offline indexed MarketData implementation and thin build/validate/query commands.

**Verify:** all availability/period/segment/gap/ambiguity cases, no query-time network, explicit synthetic opt-in, source/config independence and CLI behavior from another directory.

**Checkpoint:** a real or explicitly synthetic release can be built, validated and queried through the same installed interfaces.

### 11.7 M6 — Real-pilot review, full gate and handoff

**Implement:** remaining fixes, current coverage/access notes, README/architecture links and reproducible commands. Review module ownership and duplicate rules.

**Verify:** full gate, package build, fresh-wheel CLI/repository smoke, core real-data criteria, retained capture reconstruction and exact limitations.

**Checkpoint:** complete only when all required criteria pass. Otherwise report engineering verified/data blocked with specific IDs and a reviewable completed implementation, rather than claiming complete or abandoning independent work.

## 12. Tests and installation gate

### 12.1 Offline tests

Use tiny self-authored synthetic captures, a small registry and labelled polygon fixtures. Build temporary releases through the real builder. Do not require provider websites, large downloads or access-controlled datasets during pytest.

| Area | Meaningful checks |
|---|---|
| Normalization | Locale parsing, wrong units, percent-only prices, blank/suppressed values, invalid/nonfinite amounts, source period/statistic/basis/segment preservation |
| Provenance | Capture references/locators, timestamp stability, missing lineage, synthetic/observed mixing, unknown usage decisions |
| Geography | Leading zero, control-digit distinction, province/city mismatch, duplicate/missing codes, invalid/self-intersecting/empty polygons, CRS/axis errors, multipart preservation |
| Release integrity | Duplicate JSON keys/semantic rows, wrong hash/count, missing file, bad lineage, coverage contradictions, traversal/escaped symlink |
| Identity/writes | Identical rebuild, changed-input identity, existing-ID refusal/verification, failed build not published, location of release changed without breaking it |
| Queries | Exact interval, quarter versus month, unknown municipality, missing room, pooled versus flat, requested bedrooms unknown, unsupported metric/level, ambiguity and unchanged provenance |
| Interfaces | MarketData typing, immutable/copy-safe access, no network during open/get, explicit synthetic opt-in |
| CLI | Existing validation preserved; build/validate/query, machine-readable stdout, useful stderr/exit codes, outside-repo paths |

Use hand-written expected normalized values and statuses. Do not prove normalization by calling the same parser to generate its expected answer, or prove identity only by checking that an ID exists.

At least one integration test must build -> validate -> open -> query the same fixture through actual components, including an available metric and a missing one. Add a recorded real-pilot smoke outside the ordinary suite when real inputs are permitted; its success is not inferred from the fixture.

### 12.2 Reuse the existing gate

~~~bash
uv sync --locked
bash scripts/check.sh
uv build
~~~

After intentional dependency changes, regenerate the one lockfile, review the change and use locked commands. Do not bypass Markdown formatting, deselect installed-CLI tests, remove finance tests or ignore new data modules in mypy.

Focused runs may use uv run --locked pytest tests/data. The final gate runs the entire suite and all updated import contracts. Re-run after final source/doc edits.

### 12.3 Built-wheel verification

Install the built wheel into a fresh Python 3.12 environment. Work outside the repository without PYTHONPATH:

- Existing console help and validate-scenario still work.
- Build a synthetic release from explicit fixture paths with opt-in.
- Validate and query it using the wheel's CLI.
- Import the wheel's repository, query one known value and one missing/unsupported case, and verify metadata.
- When available, separately open/validate/query the retained real pilot.

Confirm package imports resolve inside the wheel environment. Do not depend on bundled workstation data, current directory or an editable source install. Missing real data blocks its smoke, not the synthetic installation evidence; report the difference.

## 13. Acceptance criteria and completion report

IDs below belong to Phase 3.

| ID | Complete when |
|---|---|
| A1 | Current baseline/full gate is verified; inherited README formatting is repaired; existing financial/configuration behavior remains intact |
| A2 | Selected source acquisition and intended local/redistribution scope have evidence; unresolved restrictions are not treated as permission |
| A3 | Core pilot has actual permitted observations for all three headline metrics per location, with traceable capture/locator and correct source meaning |
| A4 | Official municipal IDs and matching complete valid polygons are verified, versioned and attributed; provisional joins are resolved |
| A5 | Canonical release records/files and common verification preserve units, periods, lineage, selected profiles and honest coverage |
| A6 | Retained inputs/recipe rebuild deterministically; release identity, atomicity, idempotence, corruption checks and relocation work |
| A7 | Offline MarketData implementation obeys exact period/segment semantics and distinguishes valid gaps from invalid releases |
| A8 | Dataset CLI works through the same components, preserves validate-scenario and requires explicit synthetic use |
| A9 | Offline unit/integration tests, full locked gate, updated boundary checks, build and fresh-wheel dataset/CLI smoke pass |
| A10 | Observed pilot's coverage/readiness is demonstrated by real queries; local artifacts and reconstruction/backup instructions exist; real-data smoke limitations are explicit |
| A11 | Repository structure and one-owner rules are preserved; no scenario/map/financial duplication or speculative frameworks enter the phase |
| A12 | README, architecture, access/coverage notes and progress are current; checkpoints and the Phase 4 handoff are reviewable |

**Complete** means all required criteria have evidence. **Engineering verified, real data blocked** means the code/fixture checks pass while named A2/A3/A4/A10 requirements remain unresolved. These are different outcomes; the latter is useful progress but not full Phase 3 completion.

Unsupported detailed housing segments and Getafe room absence are legitimate declared limitations. Unknown permission, unverified core values or fake polygons are not equivalent limitations that can be waved through as a complete real pilot.

Final report should be concise: status/incomplete IDs, actual release ID/kind/scope, locations/metrics/periods and gaps, executed checks, retained artifact/rebuild instructions, checkpoint commits and the next concrete dependency decision. Do not claim that the interactive map or affordability evaluator exists.

## 14. Future extensions and Phase 4 handoff

**The pipeline must remain modular enough that these additions can extend schemas/adapters/selection/orchestration without substantial repository restructuring.**

| Future work | Boundary preserved now |
|---|---|
| Save in one place, buy elsewhere | Queries explicitly name locations; releases contain no saving/buying mode. Application reuses one savings result and queries destination prices independently |
| Profession/location salary realism | Add employment observations/adapters/context separately; household market prices and the financial engine are not repurposed as wage/hiring datasets |
| Historical modelling and evolving maps — last major extension | Reference/publication/capture dates, retained revisions and boundary versions remain explicit. Add historical adapters and an as-of selection policy without changing strict get semantics |
| Better property/room segmentation | Add actual segments/sources and explicit selectors; no pooled-to-flat rule is hidden in ingestion/repository |
| More municipalities/provider exports | Extend source adapters, registry/profile coverage and release size; preserve one normalized format and offline querying |
| DVC/database/batch tooling | Add around acquisition/storage only when scale justifies it; keep MarketData and financial contracts stable |

Phase 4 receives:

- An explicit release ID/path and read-only market repository.
- Metric reference profiles, segments, basis/statistic and known gaps.
- Released municipality registry/geometries with versions and attribution.
- Stable missing/unsupported reasons and retained provenance.
- Reconstruction/integrity evidence and any access limitations.

Phase 4 owns choosing a base observation under an explicit temporal/freshness policy, using a pooled indicator as a labelled approximation if allowed, converting unit rents to household amounts, applying sharing/utilities/growth and preparing financial inputs. It must not query a quarterly room average as though it were a September observation.

For historical work distinguish the date measured from when a value/version became available. Retaining today's revised historical series does not prove what an as-of forecast could have known. A future historical release may need period-appropriate boundaries and consistent cross-year geography.

## 15. Research basis and primary source pointers

The operating rules apply the previous agent-workflow research to a data pipeline: small verified milestones, one persistent state record, mechanically enforced boundaries and honest blocked criteria. They do not require a web-app harness or multiple agents.

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents): incremental work, recoverable progress and verification.
- [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex): scoped milestone/repair loops and inspectable execution state.
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/): repository knowledge and enforced architectural constraints.
- [Idealista report methodology](https://st3.idealista.com/cms/archivos/static/price-indicator/es-metodologia-informes-de-precios-vivienda-2026.pdf): asking indicators, source aggregation and estimation practices.
- [Idealista general terms](https://www.idealista.com/ayuda/articulos/terminos-y-condiciones-generales-de-idealista/): actual access/copying restrictions to evaluate alongside product-specific permission.
- [Audited Q2 room publication](https://www.idealista.com/sala-de-prensa/notas-de-prensa/2026/08/24/266632-la-oferta-de-habitaciones-se-dispara-un-12-y-el-precio-se-queda-casi-plano): a room benchmark has its own period/product scope.
- [INE municipality-code operation](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177031&idp=1254734710990&menu=ultiDatos) and [in-year changes](https://www.ine.es/daco/daco42/codmun/codmun_anual.htm): official registry/version/coding reference.
- [IGN administrative-unit collection metadata](https://api-features.ign.es/collections/administrativeunit?f=json) and [API documentation](https://api-features.ign.es/openapi?f=html): metadata advertises GeoJSON, schema and queryables. Actual item filters/response fields must still be inspected.
- [CNIG boundary catalogue](https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos) and [IGN geographic-data license](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf): source data, versions and attribution requirements.
- [Shapely validity documentation](https://shapely.readthedocs.io/en/stable/manual.html#object.is_valid): topology validation; automatic repair is a separate operation.

Source URLs and current availability can change. The recorded metadata checks establish plausible routes, not a claim that all files, query filters, source permissions or pilot data were downloaded and validated during this guide's preparation.
