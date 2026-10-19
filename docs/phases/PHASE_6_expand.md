# PHASE 6 — Broader Coverage and Reproducible MVP

Implementation guide for an autonomous Codex run. Prepared 14 October 2026.

**Outcome:** expand the supported municipality/product coverage through the existing release pipeline, make coverage and limitations inspectable, and make the offline CLI/map MVP reproducible in another environment. Source/schema failures are diagnosed during preparation. Economic behavior, source meaning and module boundaries remain stable as the dataset grows.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), freshly fetched at **ff7fb63424bc3b03f25bddf50b32ed8618293df0**. Public `main` still ends at Phase 4, with no other published branches. The supplied **PHASE_5_map_MVP.md** defines the intended UI contract, but its implementation is **not present in the inspected repository**. This guide therefore distinguishes verified backend interfaces from conditional Phase 5 integration. Do not claim that Phase 5 code was reviewed.

**Intended guide location:** **docs/phases/PHASE_6_expand.md**. Inspect the current implementation checkout; do not reset it to this commit. If completed Phase 5 code is present there, use its actual interfaces and progress evidence. Do not recreate Phase 5 inside this phase. Coverage/reporting/preparation work can proceed independently; full MVP integration requires completed Phase 5.

## 0. Start here

1. Inspect applicable instructions, git status/history and user-owned changes.
2. Read **docs/PROJECT_BRIEF.md**, **docs/IMPLEMENTATION_PLAN.md**, **docs/ARCHITECTURE.md**, **docs/DATA_ACCESS.md**, **docs/DATA_COVERAGE.md**, and Phase 3–5 progress records/guides where supplied. Preserve historical audits; do not recreate missing user-owned files.
3. Inspect the actual release models, builder, normalizer, adapters, storage validator, snapshot reader, market selection/projection, evaluator/export/version modules, CLI, source recipes and shared fixtures.
4. Inspect completed Phase 5 composition, services, cache keys, map joins, controls, download owners and installed launch path if available. Record any departure from its guide before planning changes.
5. Read Sections 3–10, then execute M1–M6 in Section 11 without routine confirmation. Maintain **docs/progress/PHASE_6.md**.
6. Verify A1–A12 in Section 13. Keep Phase 5 integration, observed coverage, browser checks and engineering evidence separate.

Current user instructions and applicable repository instructions take precedence. The brief owns product meaning; the implementation plan owns phase responsibilities; this guide supplies Phase 6 decisions. Resolve ordinary implementation choices autonomously. Ask only when a material ambiguity or blocker cannot be resolved from these sources.

An implementation request authorizes scoped code/documentation changes, local checks and local commits. Do not push, merge, deploy, contact providers or initiate paid/account access. No new AGENTS.md, agent service, execution framework or mandatory approval between milestones.

## 1. Baseline and entry conditions

### 1.1 Verified versus required

| Component | Inspected state | Phase 6 use |
|---|---|---|
| Models/config | Frozen records, explicit periods/segments/locations, safe configuration loading | Preserve contracts; add only necessary reporting/source metadata |
| Finance | Tested savings, reserve, mortgage/cash limits and target diagnostics | Reuse unchanged |
| Ingestion/storage | Reviewed CSV normalization, official geography capture, checksummed immutable releases | Extend through these owners when selected inputs require it |
| Markets | Validated snapshot, exact queries, pure profile selection/projection | Add read-only coverage inspection; preserve lookup/selection behavior |
| Application/CLI | Local/local evaluation, traces, JSON/CSV export and exact replay | Same services over larger releases |
| Phase 5 UI | Specified in the supplied guide; unpublished at inspection | Inspect actual implementation before UI integration |
| Observed markets | Acquisition/use blocked; redistribution unresolved | Resolve only through documented permitted inputs |
| Real geography | Four municipalities verified in the prior handoff; retained bytes are ignored local files | Obtain supplied captures or repeat permitted acquisition; hashes alone are insufficient |

**Preparation verification:** at the recorded commit, `uv sync --locked`, `bash scripts/check.sh` and `uv build` passed: **289 tests**, strict mypy on 38 source files, Ruff format/lint, lock consistency and **nine import contracts**. This verifies the published Phase 4 baseline only. It does not verify Phase 5, expanded data or Phase 6. Re-establish the implementation checkout's own gate and installed/browser evidence.

The existing synthetic pilot has four municipalities, eleven observations and twelve coverage cells. Getafe room is intentionally missing. Both fixture market values and fixture polygons are synthetic. Keep this pilot unchanged as the small regression reference.

### 1.2 Phase 5 integration prerequisite

Before modifying UI behavior, verify its service/composition boundary, all three map metrics, draft/applied state, safe scenario import, existing-owner downloads, session caching and wheel launch. Use actual names and files rather than assuming the suggested Phase 5 file layout was followed exactly.

If Phase 5 is absent or independently broken, record the prerequisite and complete independent coverage/preparation/reporting work. Do not backfill its controls or app in Phase 6, claim its tests passed, or mark the overall phase complete. A small integration repair is in scope once a completed implementation exists; implementing the prior phase is a separate task.

## 2. Scope, targets and completion meaning

### 2.1 Required deliverables

- A bounded, source-backed expansion plan using the existing municipality audit.
- Expanded recipes/crosswalks/geography and observations where permitted inputs exist, with explicit gaps elsewhere.
- A reusable read-only release coverage report exposed through CLI and, when Phase 5 exists, its service/UI boundary.
- Strict preparation diagnostics for selected source/schema changes; no runtime data substitution.
- A documented offline source-update, backup, release-selection and rollback workflow.
- Reproducible code/config/environment/release/run instructions and installed-package evidence.
- Measured scaling/caching behavior, with only justified performance changes.
- Focused integration/UI checks proving that larger and partially covered releases use the same pipeline.

### 2.2 Bounded geographic target

Use **data/manifests/coverage_audit.csv** as the starting shortlist: Madrid, Barcelona, Valencia, Málaga, Palma, Bilbao, Sevilla, Zaragoza, Valladolid, Salamanca, Jaén and Teruel; surrounding municipalities Getafe, Badalona, Mislata and Dos Hermanas.

Target **12–16 municipalities**, not all Spain. Preserve the original pilot and aim to add at least eight municipalities beyond its four. Reverify identifiers against actual INE data: the historical audit contains provisional codes and is not the authoritative registry. Exact membership may change for documented coverage/permission reasons; record substitutions once rather than repeatedly expanding the search.

For the observed expansion target, the original three core cities should retain supported purchase, whole-home rent and room inputs. Aim for purchase and whole-home rent on every included expansion municipality. Room and richer segments may be partial; a flat-saving scenario can work where a room-saving scenario cannot. Do not demand universal room coverage or infer it from whole-home rent.

Real expansion remains conditional on permitted captures. More synthetic locations demonstrate engineering scalability, never observed coverage. Another environment must be able to run the documented workflow from supplied code/config/data; a list of source URLs is not a reproducible dataset.

### 2.3 Exclusions

No fixed-saving mode implementation, salary/employment model, historical reconstruction, new tax/financing solver, investment model, gross-to-net conversion, minimum-salary/time solver, national coverage promise, public deployment, provider account negotiation or automatic scheduled refresh.

Do not introduce Hydra, DVC, DuckDB, a database, a REST service, distributed tasks or a generic adapter registry without a demonstrated requirement. The selected scale is already supported by immutable local releases and the existing in-memory reader.

## 3. Ownership and minimal repository changes

### 3.1 Preserve existing boundaries

- **Models:** shared validated records and small additive metadata, without implementation imports.
- **Ingestion:** source-specific acquisition/extraction, geography verification and translation to existing contracts.
- **Storage:** canonical persistence, capture integrity, release validation/identity and atomic publication.
- **Markets:** read-only snapshot access and pure selection/projection/coverage presentation of validated data.
- **Application:** saving preparation, financial orchestration and economic comparison/export/replay.
- **Composition/CLI:** concrete reader/config construction and delegation.
- **UI:** controls and rendering through injected services; no direct infrastructure/finance/config imports.

Preserve every existing import contract and any added in Phase 5. Pure coverage aggregation must not reach repository/storage indirectly. Extend the pure market-rule contract if adding a new pure module. The concrete reader remains at composition; application never imports it. A script does not excuse moving financial or source rules outside their owners.

### 3.2 Suggested responsibilities

Package paths below are relative to **src/spain_housing/**; configuration, scripts and documentation paths are relative to the repository root.

| Path | Responsibility |
|---|---|
| configs/sources/expanded.yaml | Explicit selected expansion recipe/products/periods, independently of pilot.yaml |
| data/manifests/ | Small reviewed source/coverage decisions and hash references; actual permission evidence where suitable |
| ingestion/adapters/ | A selected-format adapter only if existing reviewed CSV cannot serve the chosen route |
| ingestion/normalize.py and geography.py | Shared normalization and verified crosswalk/boundary handling |
| models/dataset.py or a small models/coverage.py | New immutable report records, reusing existing coverage/evidence/status semantics |
| markets/coverage.py | Pure deterministic coverage/evidence aggregation over validated inputs |
| markets/repository.py | Public immutable report projection assembled at validated snapshot open |
| cli.py | Thin `inspect-release` command; existing commands retained |
| Actual Phase 5 composition/services/UI | Inject and display coverage; no concrete-reader bypass |
| scripts/ | Thin reproducible verification/measurement entry points, no copied business logic |
| docs/DATA_EXPANSION.md | Current product/source/coverage decisions and remaining blockers |
| docs/RUNBOOK.md | Installation, data restoration/update, launch, reproduction and rollback |
| docs/progress/PHASE_6.md | Execution checkpoint and verified/unverified criteria |

Treat these as ownership guidance, not a file-count requirement. Merge genuinely small helpers with their owner. Inspect newer equivalent paths before creating another one. Never duplicate the release parser, coverage generator, query selector, financial engine or export encoders.

### 3.3 Contract/version discipline

Existing release IDs match `pilot-<digest>` or `synthetic-<digest>`. The `pilot-` prefix does not restrict municipality count. Do not invent an `expanded-` prefix or rename package namespaces merely because coverage grows.

Preserve dataset/scenario/run schema compatibility where additive fields suffice. A required incompatible change needs an explicit schema/migration decision and tests; do not hide it in normalization. Existing scenarios must remain loadable and produce the same economic quantities for the same inputs.

The builder fingerprints actual processing/model/storage source. The economic code fingerprint covers all package Python files, including UI/reporting additions. New code may therefore change exact replay evidence even if mathematics is unchanged. Keep those contracts; use fresh runs and the same code/runtime for parity rather than editing old evidence to force a match.

## 4. Source selection and bounded acquisition

### 4.1 Freeze a product matrix before collecting

For each selected product specify: metric/unit, geographic level, property/contract segment, statistic, asking/transaction/valuation/tax-declared basis, reference interval, source/methodology, freshness assumption and usable rights. Select absolute price levels; a price index or percentage change is not an absolute price input.

Start with the current products: purchase EUR/m², whole-home EUR/m²/month or an explicitly selected monthly whole-home product, and room EUR/month. Select one coherent definition per represented product. Different products may have different periods, but their exact intervals remain visible and the scenario's base/freshness/projection policy must support them.

Do not label pooled residential prices as type-specific flats/houses, room means as medians, valuations as asking prices, tax-declared existing rents as new entrant asking rents, or year-of-publication as year-of-observation. Preserve original source statistics and sample limitations.

### 4.2 Acquisition decision order

1. Prefer already supplied permitted captures/licensed exports satisfying the product matrix.
2. Reuse reviewed routes only within their documented permission and coverage.
3. If blocked, investigate at most **three compatible primary-source candidates**, prioritizing the scarce room product. Record a bounded decision; do not scrape every portal or keep changing sources to manufacture completion.
4. Acquire selected publicly permitted inputs or process authorized supplied files. Preserve original bytes and actual retrieval metadata.
5. If compatible permitted inputs remain unavailable, record affected products/locations and finish independent engineering. Provider contact, contracts and paid access remain user decisions outside this phase's autonomous scope.

Limit candidate re-review to one initial pass and one evidence-driven follow-up per candidate. Do not repeatedly retry inaccessible routes or reopen a documented decision without new evidence.

The repository records Idealista acquisition/use as restricted and redistribution as unresolved. Current general terms also require permission for content copying. A public report, API marketing page, attribution or reviewed manual CSV does not itself overturn that decision.

Official alternatives need semantic review. An official **SERPAVI 2026** publication was found during preparation; its catalogue describes tax-derived rental statistics and a July revision. Its title does not establish 2026 reference periods, current asking rent, room coverage, bulk machine readability or redistribution permission. Treat it as a candidate for a separately labelled product, not an automatic substitute. No new market captures were obtained while preparing this guide.

### 4.3 Required evidence

Reuse `SourceDecision`, `CaptureRecord`, `ReferenceProfile`, `ReleasedObservation` and declared gaps. Record the selected permission evidence, original URL, capture hash/size, actual timezone-aware capture time, publication/reference dates, source/methodology version, source locator and attribution. Separate local use from redistribution.

For reviewed extracts, retain the original evidence as well as the normalized/curated bytes needed for rebuild, with a verifiable row/table locator. Never invent retrieval dates or treat a manually prepared CSV as its own permission grant. Add structured lineage only if a chosen derivation cannot be represented/validated by current records, using the smallest compatible change.

Respect existing synthetic/observed separation: current validation forbids mixing their source decisions/captures. `--allow-synthetic` is an opt-in for fixtures, not permission for restricted sources or an observed release with synthetic holes.

## 5. Geography and segment expansion

### 5.1 Verify every included municipality

Use retained/current reviewed INE registry evidence and complete IGN/CNIG features through existing geography logic. Verify string code, control digit, official name, municipal level, full geometry identity, registry version, boundary version and source label mappings. Municipality/province names must not be conflated.

Review in-year registry changes relevant to included locations. Source labels need explicit crosswalks; do not fuzzy-match, strip accents globally or guess from city names during runtime. Preserve leading zeroes and CRS84 longitude/latitude, polygon holes and multipolygons.

The previous four-city capture hashes are pointers, not available bytes in a fresh clone. Obtain the supplied retained bundle or repeat permitted official capture. Do not claim the real subset was reconstructed from synthetic fixtures or metadata alone.

Acquire geometry only during preparation. Keep complete pagination/selection validation; reject duplicate/missing features and wrong axes/CRS. No implicit clipping, simplification or topology repair to pass a broken source. The map later renders the validated release.

### 5.2 Add only supported segments

Existing `MarketSegment` supports flat/house/room/pooled, size bands, bedrooms and rental contract categories. Prefer this contract when actual source definitions fit. Do not fabricate bedroom prices, infer a room price from a flat multiplier or apply an arbitrary quality premium.

Unknown dimensions are not exact matches. A pooled product remains explicit proxy evidence. The UI must not offer a segment as available simply because the source sells a broadly related product. Ordinary/new/renovation comparisons remain subject to the evaluator's actual support; adding rows alone does not implement a condition model.

If selected data supplies direct monthly whole-home rent, select `per_month` explicitly. It is a different product, not a rescue fallback for a missing unit-rent query. Keep all changes at ingestion/model/selection owners; no source-specific switches in finance or widgets.

## 6. Offline release preparation and quality gate

### 6.1 One existing preparation path

Reuse `build_release`, reviewed CSV parsing, `normalize_rows`, registry/boundary verification and `storage.write_release`. Larger data is input to this pipeline, not a reason to create a second builder.

If a chosen raw format needs a new adapter, confine format parsing to ingestion and feed shared normalized contracts. Use an explicit recipe/format choice with backward-compatible default behavior. Do not guess adapter/source from filename or write a plugin registry for one provider. Keep extraction separate from download and building offline.

### 6.2 Fail before publication

Preparation must reject or clearly diagnose:

- Changed/missing/duplicate columns, malformed row widths or error/login HTML.
- Unparseable numeric locale, unit/metric mismatch, nonpositive prices or nonfinite values.
- Changed period/statistic/basis/segment, unknown profiles and ambiguous query identities.
- Unresolved/nonmunicipal labels, duplicate identities and incorrect boundary versions/geometry.
- Missing/corrupt captures, permission-reference contradictions and coverage/lineage inconsistencies.

Use existing validators; improve diagnostics only at the relevant owner. A parser failure must not be converted to an ordinary missing price. Suppressed/unreported source values can become explicit gaps when that is the source's meaning; they are never zero observations.

Keep release readiness semantics: `ready` reflects required core coverage, not all optional locations or UI support. Choose core flags before collecting, retain the original core intention, and document any legitimate scope change. Do not demote failing core cities merely to obtain a green readiness label.

A permitted partial-product release can be useful, but label its scope explicitly. A flat-only release has no room profile; room queries are unsupported, and `ready` for its selected profiles does not satisfy the original room/flat expansion goal. Do not include a blocked source merely to represent its gaps or silently remove a required product to claim full completion.

### 6.3 Publish immutable releases

Use existing staged, atomic/idempotent publication and content identity. Build into a new content-addressed directory, validate it, inspect coverage, then explicitly select it for evaluation. Preserve old releases and resolved runs. Never edit a released observations/geometry file in place, update a manifest hash to disguise corruption or overwrite an active release on refresh.

Keep recipe capture times/evidence fixed for offline rebuilds; do not insert current time into every build. With the same captures, recipe and processing code/environment, rebuild identity/content should agree. If processing or source data intentionally changes, expect a new release and record why.

## 7. Coverage report and query-policy transparency

### 7.1 One reusable report owner

Add a small immutable report over a **validated release**, exposing:

- Release ID/kind/readiness, registry/boundary versions, attribution, limitations and usage scope.
- Product/profile definitions with exact periods, units, source, statistic, basis and segment.
- Deterministically ordered location × profile cells, statuses and reasons.
- Per-profile and total available/missing/unsupported counts, with observed/estimated/synthetic counts for available evidence.
- Which source definitions, segment limits and time constraints users must understand.

Aggregate existing validated cells/observations; do not regenerate competing coverage rules or infer observations from totals. Pure aggregation belongs in markets; storage remains the owner of release coverage verification. Snapshot construction can project the validated bundle's cells/evidence into a public immutable `coverage_report`. Do not expose `_index`, reread JSON privately from UI or enumerate raw provider files at runtime.

Keep reporting separate from the economic RunResult. A report is dataset evidence, not a second Scenario/LocationResult schema. Add its typed service metadata to actual Phase 5 composition instead of forcing application to import the repository.

Give this new standalone report an explicit schema version, initially 1. It derives from the validated release and is not another persisted release format or alternative coverage source of truth.

### 7.2 Required CLI inspection

Add **`spain-housing inspect-release --release <path> [--allow-synthetic]`**. Default to stable machine-readable JSON using existing CLI serialization conventions; print expected errors to stderr with nonzero status. It opens/validates the selected release and emits the common report, without network, ingestion, evaluation or output-directory mutation.

The report must distinguish **captured availability** from **scenario suitability**. A cell can be available yet too old, of the wrong segment or otherwise unsupported for a particular scenario. Do not advertise a count of available rows as a guarantee that every living mode works there.

### 7.3 Explicit policy, not automatic rescue

Document and preserve the current policy:

- Select complete/fresh profiles according to the resolved scenario.
- Exact queries preserve source intervals/dimensions; quarterly data stays quarterly.
- Once a profile is selected, a missing city does not trigger an older period, neighbouring city, province or another source.
- Pooled proxies require existing explicit permission and retain warnings.
- Publisher-estimated inputs retain their evidence label/method; no new automatic imputation model is introduced.

Recipes cannot include competing source/statistic variants with identical query keys because `MarketQuery` has no source/statistic selector. Use an explicitly selected release/product or the existing profile-ID policy where representable; do not silently choose an arbitrary row. Adding more periods/bases is not a reason to weaken ambiguity detection.

Separate missing evidence, unsupported query/mode, estimated/proxy evidence and exhausted saving paths. Available zero financial capacity remains a legitimate calculation; zero market price remains invalid. All expanded-map indicators retain their own statuses.

## 8. Source updates, storage and reproducible operation

### 8.1 Document one complete runbook

Write **docs/RUNBOOK.md** for someone starting in a clean environment. Reference existing technical docs instead of repeating their full rules. Include:

1. Supported Python version, checkout revision, package installation and locked optional map extra.
2. Required inputs: defaults, resolved/saved scenario, explicit release path and synthetic permission when applicable.
3. Two separate data routes: restore an existing validated release for evaluation, or restore permitted original captures/recipe and rebuild offline.
4. Exact tested build, validate, inspect, evaluate, export, replay and map-launch commands.
5. Release/source periods, restrictions, original hashes and backup location/restore procedure.
6. How to select a new release, restart/reload safely and return to an old release.
7. Common preparation/startup/replay errors, with the relevant owner and corrective action.

Use commands exercised during implementation, with actual documented paths/variables. Do not assume a temporary directory from a previous session still exists. Preserve a simple labelled synthetic route that needs no market account, and a separate observed route requiring the actual permitted bundle.

### 8.2 Three distinct reproduction claims

| Claim | Inputs and evidence |
|---|---|
| Reproduce acquisition | Provider route, terms, URL/version and capture metadata; a mutable endpoint may now return different bytes |
| Rebuild a dataset release | Original retained bytes, fixed recipe/crosswalk/decisions and compatible processing environment; verify content identity and files |
| Reproduce an economic run | Exact validated release, resolved Scenario, ordered destinations and matching model/code/runtime; existing replay proves content agreement |

Do not promise that redownloading a live source reproduces an old release. Publication date, actual capture time and observation interval remain distinct. UI-only changes can change the existing whole-package economic code fingerprint; explain a replay refusal rather than bypassing it.

Keep deterministic sorting and identifiers independent of workstation roots, wall-clock evaluation time, cache order or map selection. UI/table rounding does not change exports. Geometries remain separate from economic runs.

### 8.3 Local immutable data plus real backups

Keep source code, schemas, configuration, small decisions and documentation in Git. Retain raw captures, complete releases, optional processed artifacts and user run outputs in their existing ignored locations. Back up irreplaceable original bytes together with recipe/capture sidecars; a URL/hash is not a backup.

Document portable relative capture paths and explicit runtime roots. Do not embed a personal machine path or credential in economic configuration. A second environment receives actual data bytes through a permitted transfer route; local-only licensed data must not be committed or publicly distributed to make a demo convenient.

DVC is not required for this phase. Content-addressed releases, Git-versioned recipes/decisions and ordinary verified backups already provide the needed provenance. If a later storage/collaboration need justifies DVC or remote object storage, add it around these artifacts without changing evaluator/query contracts.

### 8.4 Manual update and rollback

Keep updates explicit:

- Check only the selected source products at their actual publication cadence; monthly prices and quarterly room products need not update together.
- Capture new permitted bytes and review methodology/schema/period/coverage changes.
- Create a new recipe with the correct captures/versions/gaps; do not modify the recipe inside an old release.
- Build, validate and inspect the new release; run a small scenario/CLI-map comparison before selecting it.
- Restart the app or use its verified explicit reload path, replacing context/geometry/result caches coherently.
- Roll back by selecting the previous intact release. Saved scenarios remain explicit; do not silently change their base/profile policy to accept new data.

Failure during acquisition, extraction, validation or publication leaves the previous release and applied UI run intact. No ingestion on startup/rerun, implicit latest-release lookup, automatic provider fallback or scheduled refresh service in this phase.

## 9. Performance and scaling, measured first

### 9.1 Reproducible measurements

Before optimizing, measure:

- Cold full release validation/index construction, including geometry size.
- First evaluation of a resolved scenario over all selected municipalities.
- Repeated identical scenario reuse, and changing an actual economic assumption.
- Coverage report generation and detached map preparation.
- Browser response/rendering on a supported larger release.

Record code/release/runtime identifiers, environment/hardware, municipality/profile/observation counts, saving horizon, geometry vertices/bytes, method and measured times. Use `time.perf_counter`, several repeated samples and medians; separate cold and warm work. Do not conflate network downloads with evaluation time or invent a national performance result from a four-city run.

Keep a thin measurement script if useful; it calls public owners and reports observations, not a copied evaluator. Performance timings are engineering metadata and do not go into RunResult or its deterministic identity.

### 9.2 Bounded scaling cases

Required cases are the unchanged four-city regression pilot and a **16-location expanded synthetic case**, produced through the real builder/reader with controlled gaps. If permitted observed inputs exist, measure their actual 12–16-location release separately.

Add a generated **250-location, 84-month synthetic stress case** to exercise query/index/evaluation scaling. Generate it from one small shared test/measurement helper with unique identities and explicit synthetic metadata; do not commit hundreds of copied fixture files or display it as observed Spanish coverage. Geometry can be lightweight fixture geometry; record that it does not establish performance for equally many real complex polygons.

These cases must finish through the same interfaces and preserve results/coverage. A warm equal-run or presentation-only rerun must call the evaluator **zero additional times**. Loading an already cached immutable release must not repeat full validation unnecessarily. Test these call-count boundaries directly; avoid flaky wall-time assertions in ordinary CI.

Set and record a practical latency target after the first baseline measurement. If interaction is slow, profile and fix the dominant work, then rerun the same case and prove numerical equality. If no material bottleneck exists at the selected scale, report measurements and retain the simple implementation; optimization is not a quota.

### 9.3 Safe changes only

Potential improvements include removing repeated parsing/serialization, computing dataset summaries once, retaining the existing immutable index and fixing cache-key/session boundaries. Do not drop budgets/source traces, round intermediate money, substitute vectorized formulas with different semantics, parallelize ambiguous source lookups or bypass release validation for speed.

No database, background workers, spatial interpolation or geometry simplification merely to satisfy a benchmark. Preserve complete holes/multipolygons. Existing resource/result cache identity must include the actual release, Scenario, ordered locations and model/code/runtime. Never share personal drafts/results globally.

## 10. Integration with completed Phase 5

This section applies only after inspecting the actual Phase 5 implementation. Adapt its existing composition/services rather than rebuilding the app around a guessed interface.

### 10.1 Coverage-aware rendering

Inject the shared report as immutable service metadata. Add a compact coverage/source panel showing released locations/products, periods, counts, missing/unsupported reasons and evidence/usage limitations. Keep the main financial workflow readable; lengthy product definitions belong in an expander/table.

Derive selectors/names from release metadata, never a four-city list. Preserve default evaluation across the intended released destinations and code-based inspection selection. A location supported for flat saving may be missing for room saving; allow that scenario to reveal typed gaps without substituting rent.

Keep Phase 5's three metrics, stable legends and indicator-specific states. Financial capacity can remain available when a purchase comparison is missing; absent saving rent prevents a completed financial result. The price ceiling remains the existing minimum of cash and mortgage limits. Source availability, estimated/proxy evidence and saving unviability are separate dimensions.

Join matching municipality codes/levels/boundary versions, rejecting corrupt joins. Preserve actual polygons and the selector/table fallback. Label synthetic markets and synthetic geography, including any new generated fixtures. Additional data must not trigger live boundary/source requests.

### 10.2 Release transitions and output consistency

Selecting/reloading a release must replace services, context, geometry and applicable caches together. Preserve or explicitly reset the inspection code if it is absent in the new release. Do not show an old run under a new release title, mix old geometry with new prices or silently change a loaded Scenario.

Use the existing Apply workflow. Metric/city/coverage-table changes are presentation only. Run/scenario/CSV downloads continue to use the same applied records and existing encoders. The report may have its own download if useful, but must not become another economic export format.

Verify UI/CLI parity in the same interpreter/environment over both expanded and partial releases. No hard-coded currency values, room multipliers, growth calculations or salary interpolation in widgets. Preserve separate saving/buying labels and bindings for the next essential feature.

## 11. Autonomous work loop and milestones

### 11.1 Persistent execution record

Create/update **docs/progress/PHASE_6.md** before substantial edits. Keep one compact record with baseline/worktree state, current milestone, completed behavior, next action, decisions/deviations, source/Phase 5 blockers and actual verification evidence.

At each coherent milestone: implement, run relevant checks, repair failures, record evidence and make a scoped local commit when allowed. Do not stage unrelated/user-owned files, generated datasets or user outputs. Keep source-of-truth definitions in their existing owners; do not copy this entire guide into progress notes.

After a restart/context loss, read progress, git status/history and current affected code. Resume the next incomplete action. A remembered successful test does not cover later edits. Preserve source investigation decisions so a new context does not reopen the same unavailable providers indefinitely.

When a genuine blocker affects one path, finish independent authorized work. Mark only evidenced criteria verified. Do not remove failing tests, replace observed checks with fixtures or convert unpublished Phase 5 into a fictional completed baseline. Long-session reliability comes from incremental checks and recoverable decisions, without a new harness.

### 11.2 M1 — Establish actual baseline and integration contract

Inspect the current checkout, verify its gate and separate backend/Phase 5/data readiness. Read the actual Phase 5 code if available and record its service/cache/launch interfaces. Settle the minimal report contract and preserve import boundaries.

**Exit evidence:** actual baseline checks and source/version evidence, known UI prerequisites, a scoped file plan and initial progress record. If Phase 5 is absent, its integration portion remains blocked while independent M2–M4 work proceeds.

### 11.3 M2 — Freeze coverage/product decisions and permitted routes

Select the 12–16-location shortlist and product definitions. Review permitted captures or the bounded candidates, document source/period/segment/permission decisions, and verify obtainable geographic identities. Define gaps before building rather than hiding them after evaluation.

**Exit evidence:** explicit expansion matrix/recipe direction and captured inputs where authorized, or precise unresolved cells/routes. No invented data, permission or automatic alternative product. Preserve the historical audit independently.

### 11.4 M3 — Expand preparation and strict source diagnostics

Prepare selected inputs through existing CSV/geography/normalization/storage owners. Add only a necessary source adapter/metadata refinement. Build/validate expanded immutable releases where inputs permit; add the separate 16-location synthetic integration case.

**Exit evidence:** controlled source drift/corruption fails before publication; deterministic rebuilds agree; gaps and provenance survive the reader; prior releases remain intact. Observed build may remain blocked without preventing synthetic engineering checks.

### 11.5 M4 — Common coverage inspection and update runbook

Implement the immutable report, public snapshot projection and thin `inspect-release` CLI. Verify counts/order/evidence and maintain one aggregation owner. Write/exercise restoration, rebuild, release selection, replay and rollback instructions.

**Exit evidence:** real builder/reader/report agreement on complete/partial fixtures; offline inspection errors are explicit; a clean-environment user has actual input/backup steps instead of only URLs.

### 11.6 M5 — Expanded map integration and measured scaling

When completed Phase 5 is available, integrate the report/metadata and exercise larger/partial releases through its controls, map and downloads. Measure four-/16-/250-location cases, fix only demonstrated bottlenecks and preserve numerical equality. Verify browser behavior separately from simulated UI tests.

**Exit evidence:** no hard-coded city list, stale release state or data fallback; UI/CLI parity; cache-call-count/scaling measurements; actual browser proof. Without Phase 5, finish independent measurements and record UI/browser integration as blocked.

### 11.7 M6 — Full verification and reproducible handoff

Run the final gate/build, fresh installed-wheel core/map workflows and the documented end-to-end reproduction in a clean environment. Verify observed expansion if authorized data exists; otherwise preserve the exact blocker. Review duplicates/dependencies and update README/architecture/runbook/progress.

**Exit evidence:** A1–A12 states with actual commands/results, portable data/run instructions, remaining blockers and next-feature boundaries. Do not mark full MVP reproduction complete without the installed Phase 5 application and its browser evidence.

## 12. Meaningful verification

### 12.1 Functional and data cases

Reuse the shared builder/repository fixtures in **tests/conftest.py** and existing Phase 4 demo scenarios. Add one deterministic expanded fixture helper, keeping generated data explicitly synthetic. Expected coverage/counts come from a declared independent test matrix, not the aggregation function being tested.

| Case | Required assertion |
|---|---|
| Existing four-city release | Prior economic quantities and Getafe's missing room behavior remain unchanged |
| Expanded 16-location release | Expected location × profile cells, evidence totals, code order and geometry/result joins agree |
| Missing room with whole-home rent | Room saving is unavailable while a supported flat-saving scenario remains evaluable |
| Missing purchase with valid saving rent | Financial capacity/path survive; area/target comparison are unavailable |
| Richer supported segment | Exact bedroom/type/product works; unknown/mismatched dimensions do not masquerade as exact evidence |
| Newer selected profile with a gap | No fallback to an older available observation or another source |
| Available source versus unsuitable scenario | Coverage stays available while freshness/segment/query support is reported separately |
| Unsupported, estimated/proxy, unviable and zero | Correct independent labels and numeric behavior are retained |
| Schema/locale/period/source drift | Preparation fails with capture/row/profile context instead of publishing missing replacement values |
| Capture/release/geometry corruption | Validation fails; previous published release remains untouched |
| Offline rebuild and restore | Same retained inputs/code reproduce identity/content; reader/evaluation require no source download |
| Release/cache/selection transition | No old context/geometry/run under new identity; selection remains code-based |

Where richer segment or estimated evidence is absent from authorized inputs, exercise the relevant contract branch with clearly identified test data; do not advertise production support that has no source evidence. Unknown dimensions and multiple plausible series still require explicit selection or an unsupported result.

Test the common report against the builder/validated reader: total expected equals locations × selected profiles, status counts agree, and evidence counts sum to available cells. Keep `CoverageSummary` distinct from per-scenario available results. CLI inspection and UI metadata must use the same report, with stable ordering and no private-index access.

### 12.2 End-to-end economic consistency

For both room and staged-growth demos, use a real built release and the existing evaluator/CLI. Compare complete canonical JSON and summary CSV under identical resolved Scenario, destination order, release, code and runtime. Reuse the existing replay path; do not reload current defaults for a saved run.

Check that source/schema errors occur during release preparation/open, not during a silent UI refresh. Evaluation of a released bundle must work without raw captures or live provider access. Rebuilding it requires the retained input bytes. These are different tests.

Use AppTest for supported widget/state operations when Phase 5 exists. Use pure conversion tests and a real browser for unsupported data-editor interactions; do not invent private AppTest APIs. A passing simulated test does not prove WebGL rendering.

### 12.3 Full gate and CI

Preserve the current gate owners and any Phase 5 additions. With the completed map extra present:

```bash
uv sync --locked --extra map
bash scripts/check.sh
uv build
git diff --check
```

Every `uv run` inside the full gate must retain `--extra map`; otherwise synchronization can remove UI dependencies. Keep lock consistency, Ruff format/lint, strict mypy, import contracts/sensitivity and full pytest. Do not skip UI tests to report a passing development gate.

Update **.github/workflows/check.yml** to use the same complete gate and build; its inspected job is still named `phase1`. A small Python 3.12/3.13 compatibility matrix is appropriate for the declared support. Avoid a parallel collection of partially overlapping check scripts. CI tests are deterministic/offline and need no private/observed provider credentials.

If Phase 5 is absent, execute/report the available backend gate and keep full map/CI integration unverified; do not add a placeholder map extra or app just to satisfy the commands above. Distinguish a blocked prerequisite from a source/test failure.

### 12.4 Fresh environment and browser proof

Build a wheel, create a new environment outside the repository and install it with the tested map dependencies. Use the documented pinned runtime/lock-derived versions when comparing exact replay; a compatible but different dependency version is not identical runtime evidence.

Unset `PYTHONPATH`, confirm `site-packages` import origins and run installed commands from an unrelated working directory with explicit input paths. The installed app must use the packaged launch path, not a checkout-only `apps/` script. Verify core-only wheel import/help/validation/evaluation/replay separately from a fresh map-enabled installation.

Exercise the runbook's synthetic restore/build → validate → inspect → evaluate/export → replay → serve workflow. Run twice from independently prepared data/output roots, verify stable content and refuse corrupt inputs without damaging old outputs. Archive/transfer actual permitted bytes when proving observed reproduction; hashes/URLs and synthetic reruns do not satisfy that evidence.

When Phase 5 exists, a real browser must verify:

1. Larger sparse coverage renders correct polygons/legend and retains holes/multipolygons.
2. Room/flat changes reveal the intended different gaps rather than imputation.
3. All three metrics, source badges, coverage panel and location details agree with applied results.
4. Picking, selector and zoom work by code across more locations and after a release transition.
5. Invalid edits/imports retain a clearly previous applied run; downloads agree with current applied records.
6. Default operation without external tiles and presentation-only reruns remain usable.

Record the actual browser, command, release/scenario and observed outcome. HTTP health, a blank-map screenshot or unexecuted checklist is not browser proof. If tooling/Phase 5 is unavailable, keep the browser criterion unverified and finish independent work.

## 13. Acceptance criteria and honest completion

| ID | Requirement |
|---|---|
| A1 | Actual baseline and completed Phase 5 integration contract are inspected/verified; prerequisites and user changes are preserved |
| A2 | Module/import boundaries, existing finance/query/export behavior and compatible schemas remain intact; no duplicate pipeline/framework is introduced |
| A3 | Bounded 12–16-location/product expansion decisions identify verified codes, exact semantics, usable rights and explicit unsupported/missing coverage |
| A4 | Selected inputs use existing preparation owners; drift/corruption fails before publication; immutable rebuild/restore and source lineage are verified |
| A5 | Common immutable coverage report, public snapshot projection and offline `inspect-release` agree with validated cells/evidence and separate source availability from scenario suitability |
| A6 | Existing complete/fresh/exact selection, explicit proxy and no-fallback policies survive expansion; partial evidence does not become fabricated prices/results |
| A7 | Actual Phase 5 uses expanded metadata/coverage without hard-coded cities, infrastructure bypass or stale release/cache/selection state; UI/CLI/download parity is verified |
| A8 | Runbook documents actual environment/input/backup/update/rollback/reproduction steps; another clean environment runs the installed core/map workflow with supplied bytes |
| A9 | Four-/16-/250-location measurements and cache call counts are recorded; any optimization is measured and economically equivalent, or a justified no-change decision is documented |
| A10 | Full quality gate, supported runtime checks, CI/build, fresh core/map wheel tests and actual expanded-map browser verification pass with real evidence |
| A11 | Authorized observed expansion achieves at least 12 municipalities, including eight beyond the original four, purchase/whole-home coverage and the original three-city room core; retained bytes reproduce the observed workflow |
| A12 | README, architecture, data decisions, runbook and progress accurately state supported scope, source/Phase 5 blockers, checks and next essential extension |

**Known preparation limits:** A1's Phase 5 integration is unverified because published code is absent; its dependent A7/A8/A10 map portions cannot be claimed from this checkout. A11 remains blocked by observed source access. Twelve or more synthetic municipalities do not satisfy observed expansion.

Report criteria individually. Examples of honest final states are **independent backend/coverage engineering verified; Phase 5 integration and observed expansion blocked**, or, once the actual UI exists, **MVP engineering/browser verified; observed expansion blocked**. Declare full Phase 6 complete only when every criterion is actually verified. Do not alter acceptance counts/core/product meaning solely to remove a blocker.

Finish with implemented behavior, milestone/local commit references, executed checks, A1–A12 states, measured performance, unresolved inputs and the next concrete action. Never describe an unrun command as successful or assume a temporary dataset still exists after resumption.

## 14. Future implementations

The pipeline must remain modular enough that these features fit **without substantial repository restructuring**. Preserve the boundaries now; implementation is deferred.

| Order/feature | Boundary to retain |
|---|---|
| **Next essential extension: save in A, buy in B** | Independent bindings; destination-free saving preparation; reusable purchase evaluation; explicit purchase-time income assumption and separate inspection location |
| **Salary realism by profession and place** | Separate salary/employment data service and versioned observations; user-assumed income remains an explicit economic input; availability evidence does not become an invented hiring probability |
| **Historical paths/maps, including 2010 — latest major extension** | True reference/publication/capture dates, retained releases, versioned geography and explicit selection/projection policies; no claim that a date slider reconstructs the past |
| Regional purchase costs/variable financing | Existing cost/purchase owner and solver boundary, without tax arithmetic in application/UI |
| Gross-to-net, savings returns and ownership costs | Explicit conversion/budget/finance assumptions feeding the same scenario contracts |
| More detailed property segments/required-income or time solvers | Validated product definitions and separate application services over existing financial rules |
| Provider APIs, DVC, database or Hydra if justified later | Acquisition/storage/batch composition around current contracts, without coupling the evaluator to a framework |

For fixed-saving, moving destination must not silently change salary or retain it by accident. For salary realism, source population/profession/time definitions matter. Historical modeling must separate a historical path, frozen comparison and as-of forecast and audit historical room coverage before promising it.

Handoff: working release inspection/update/reproduction paths, immutable data references and actual backups, performance observations, supported product matrix, remaining observed/UI blockers and verified extension boundaries. The next phase should add its feature rather than first repairing hidden formulas, duplicated loaders or a hard-coded pilot.

## 15. Research basis

Primary sources informed the workflow and data distinctions. The decisions above are the phase contract; inspect installed APIs and current source evidence before implementation.

- [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) — persistent scope, milestones and check/repair loops, applied through M1–M6 and the progress record.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — incremental verified work, recoverable state and end-to-end proof rather than premature completion.
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) — navigable repository knowledge and enforced ownership, applied through existing docs/import contracts.
- [INE municipality registry and changes](https://www.ine.es/daco/daco42/codmun/codmun_anual.htm) and [IGN administrative-unit collection](https://api-features.ign.es/collections/administrativeunit?f=json) — official geography/identity routes; selected captures still need retention and verification.
- [Idealista general terms](https://www.idealista.com/ayuda/articulos/terminos-y-condiciones-generales-de-idealista/) — current copying restrictions, alongside the repository's recorded source decisions.
- [Official SERPAVI 2026 publication catalogue](https://publicaciones.transportes.gob.es/serpavi-2026-sistema-estatal-de-referencia-del-precio-del-alquiler-de-vivienda) — a tax-statistics candidate, without implying room/current-asking coverage or a reviewed bulk-data licence.
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) — supported UI simulation; browser rendering remains separate evidence as specified by Phase 5.

Backend contracts and readiness were inspected from the recorded repository. The supplied Phase 5 guide was read separately. No unpublished Phase 5 implementation, newly acquired market release or newly granted permission is asserted here.
