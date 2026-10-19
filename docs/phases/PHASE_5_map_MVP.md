# PHASE 5 — Interactive Map MVP

Implementation guide for an autonomous Codex run. Prepared 8 October 2026.

**Outcome:** a local Streamlit application lets a user edit a complete housing scenario, apply it across the released pilot municipalities, inspect three affordability map layers and their financial/source explanations, and download reproducible inputs and results. The UI and CLI use the same evaluator. Interactive use never collects market data.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), inspected at **ff7fb63424bc3b03f25bddf50b32ed8618293df0**, including the completed Phase 4 evaluator, CLI, exports and replay. Intended guide location: **docs/phases/PHASE_5_map_MVP.md**. Inspect the implementation checkout; do not reset it to this commit.

## 0. Start here

1. Inspect applicable repository instructions, the working tree, recent commits and user changes before editing.
2. Read **docs/PROJECT_BRIEF.md**, **docs/IMPLEMENTATION_PLAN.md**, **docs/ARCHITECTURE.md**, **docs/DATA_ACCESS.md**, and **docs/progress/PHASE_3.md** and **PHASE_4.md**. Read supplied phase guides where present; do not recreate missing user-owned guides.
3. Inspect the actual scenario/result/evaluation models, **application/evaluate.py**, **application/export.py**, **application/version.py**, **markets/repository.py**, **config.py**, **cli.py**, the import contracts, demo scenarios and shared test fixtures.
4. Read Sections 3–10 before adding UI code. They settle composition, controls, state, caching, map semantics and downloads.
5. Execute M1–M6 in Section 11, continuing without routine confirmation. Maintain **docs/progress/PHASE_5.md** as the implementation checkpoint.
6. Finish against A1–A12 in Section 13. Report engineering, browser verification and observed-data readiness separately.

Current user instructions and applicable repository instructions take precedence. The project brief owns product meaning; the implementation plan owns phase responsibilities; this guide resolves Phase 5 implementation choices. Resolve routine details autonomously. Ask only when a material ambiguity or blocker cannot be resolved from those sources.

The implementation request authorizes code changes, local execution, verification, documentation and scoped local commits. Do not push, merge, deploy, contact providers or initiate paid/account access. Preserve user-owned files. Do not introduce a new AGENTS.md, an agent service or a parallel execution framework.

## 1. Verified baseline and inherited readiness

### 1.1 Existing implementation

| Component | Actual state | Phase 5 responsibility |
|---|---|---|
| Models/config | Frozen typed scenarios/results; safe YAML/JSON loading, explicit defaults and deterministic scenario JSON | Convert controls to existing records; share configuration parsing for uploads |
| Finance | Savings paths, exhaustion, reserve, mortgage/cash limits and target shortfalls | Render returned quantities; preserve numerical behavior |
| Offline releases | Validated immutable bundles, indexed reader, public context and separate boundaries | Load one explicit release at composition; cache it safely |
| Application | Local/local evaluation, monthly budgets, market traces, borrower finances, partial indicators | Call the existing service from the UI |
| Exports/replay | Canonical run JSON, ordered summary CSV, exact replay with version evidence | Reuse existing encoders for browser downloads |
| CLI | Validation, release build/query, evaluation and replay | Preserve commands; add a packaged local app launch path |
| UI | Reserved namespace | Implement controls, session orchestration, presentation and map |
| Observed markets | Acquisition/use blocked; redistribution unresolved | Preserve the blocker and use explicitly permitted demos |

**Checks performed while preparing this guide:** `uv sync --locked`, `bash scripts/check.sh`, and `uv build` passed at the recorded commit: **289 tests**, strict mypy on 38 source files, Ruff formatting/lint, lock consistency and **nine import contracts**. These checks validate the baseline, not a Phase 5 implementation. Phase 4's progress record contains separate installed-wheel evidence; establish new Phase 5 evidence in M6.

### 1.2 The pilot is an engineering dataset

The synthetic pilot has eleven observations across twelve expected cells. Madrid **28079**, Barcelona **08019** and Jaén **23050** have fixture sale, whole-home rent and room values. Getafe **28065** intentionally lacks a room observation. Preserve leading zeroes in all codes.

Both its market values **and its boundary shapes are synthetic**. The fixture includes a polygon with a hole and a multipolygon, useful for rendering tests. Official municipal geography is independently verified elsewhere, but that does not make these fixture shapes official. Label the whole demonstration accordingly.

There is no permitted observed market release at this baseline. Audit URLs, coverage notes and verified geography are not such a release. Complete independent map engineering using the real release builder/reader with explicit synthetic permission. Do not copy audit values into observations, reopen acquisition indefinitely or imply nationwide market coverage. If an authorized observed release becomes available, run the same application against it and record separate evidence.

## 2. Scope and required product behavior

### 2.1 Deliverables

- A launchable, installable Streamlit/PyDeck app using a selected offline release.
- Editable participants, income/debt milestones, living stages, expenses, mortgage/cost assumptions, target property and market/selection policy.
- A coordinated **Apply scenario** action that evaluates all pilot destinations.
- Municipality polygons coloured by maximum purchase price, affordable area or target affordability ratio.
- Selection by map and a reliable location selector; a table remains usable independently of the map.
- Financial details, signed savings path, prepared budgets, source periods and visible limitations.
- Safe scenario import and resolved-scenario/run/CSV download.
- Explicit session state, bounded caching, UI/CLI parity tests, browser verification and installed-package checks.

The initial geographic mode remains **live and buy locally**: each municipality supplies both the saving-period rent and destination purchase evidence. Keep the two location bindings separate in models and orchestration.

### 2.2 Exclusions

Do not implement fixed-saving evaluation, profession/salary datasets, employment likelihood, historical reconstruction, a minimum-salary or time-to-deposit solver, new acquisition, nationwide coverage, regional tax rules, investment returns, a gross-to-net converter or additional ownership costs. Do not add Hydra, DVC, a database, API server, login system, custom frontend framework or deployment infrastructure.

These later features must fit the existing boundaries, but speculative abstractions are not a deliverable. `fixed_saving` and unsupported property/segment choices remain valid inputs where the existing contracts permit them; present their actual unsupported results rather than silently changing the scenario.

## 3. Architecture, dependencies and ownership

### 3.1 Preserve the existing dependency direction

The launcher composes configuration, concrete release access and application services. UI code consumes validated models and injected services; application code remains independent of UI and infrastructure.

The current UI import contract forbids **direct** imports of `finance`, `markets`, `storage`, `ingestion`, `config` and `cli`; indirect application-mediated imports are allowed. The application/storage prohibition covers indirect imports. Therefore:

- Do not instantiate `SnapshotMarketRepository` inside `ui` or pass its concrete type into UI annotations.
- Do not import `config` into controls merely to read an upload.
- Do not move the repository into application to make UI construction easier.
- Do not call CLI commands from widgets to obtain economic results.
- Do not weaken any existing import contract. Extend lower-layer/UI prohibitions to the new launcher so it cannot become a bypass. Add sensitivity checks for those edges.

### 3.2 Suggested file responsibilities

| Path | Owns |
|---|---|
| src/spain_housing/launcher.py | Packaged composition, startup arguments, release resource cache and local server launch helpers |
| apps/streamlit_app.py | Tiny repository convenience entry point delegating to packaged composition |
| ui/contracts.py | Small typed service bundle/metadata needed by rendering |
| ui/app.py | Render order, form submission and application-service coordination |
| ui/controls.py | Widgets and draft-to-Scenario representation conversion |
| ui/state.py | Session transitions, selected location and bounded result memoization |
| ui/presentation.py | Pure indicator/status/formatting and table projections |
| ui/map.py | Detached GeoJSON decoration, colour bins, PyDeck layers and selection adaptation |
| ui/details.py | Returned financial/source details and savings/budget views |
| config.py | One safe text/file parser, merge semantics and scenario serialization |
| cli.py | Thin `serve` command and existing commands |
| tests/ui/ and launch/config tests | Pure mappings, session behavior, integration and entry-point coverage |
| docs/progress/PHASE_5.md | Milestones, evidence, blockers and restart instructions |

These are responsibility boundaries, not a target file count. Merge tiny helpers with their owner. Split files when their responsibilities become difficult to read. No miscellaneous utils module, generic service registry, parallel result schema or duplicate table/export pipeline.

### 3.3 Stack and optional installation

Use **Streamlit and PyDeck**, as the implementation plan specifies. During preparation the official package pages list Streamlit **1.65.0** and PyDeck **0.9.3**. A reasonable starting range is `streamlit>=1.65,<2` and `pydeck>=0.9.3,<1`; resolve and lock versions compatible with Python 3.12/3.13 and verify the APIs actually installed.

Put these dependencies in a named optional extra, **`map`**. Core validation/evaluation/replay must work without it. Import optional frameworks only on the app path; importing the package or asking for CLI help must not require Streamlit.

If UI code imports pandas directly for editable tables, declare it in that extra with a compatible range rather than relying on Streamlit's transitive dependency. Keep DataFrames in presentation; domain/economic records remain typed models. Prefer supported list/record inputs when they simplify typing.

Keep strict mypy. Confine unavoidable third-party `Any` or narrowly justified ignores to the rendering adapter, not business logic or an entire package. Never solve missing stubs by disabling typing globally.

## 4. Packaged composition and application service

### 4.1 Actual interfaces to reuse

The existing public evaluator is:

```python
def evaluate_scenario(
    scenario: Scenario,
    *,
    market_data: MarketData,
    context: EvaluationContext,
    mapped_locations: tuple[GeographicReference, ...],
) -> RunResult: ...
```

`SnapshotMarketRepository.from_release(path, allow_synthetic=...)` already validates/indexes the release. Its public `evaluation_context`, `locations` and `boundaries` supply everything composition needs. UI downloads reuse `application.export.run_json` and `summary_csv`. Scenario downloads reuse the config owner's `scenario_json` through an injected callback.

Create a small frozen service bundle using ordinary typed callables. It supplies:

- Evaluation of a `Scenario` over an ordered tuple of destination references, closed over the validated snapshot/context.
- Safe uploaded-scenario decoding and deterministic scenario encoding, implemented by the config owner.
- Immutable context, location records and boundaries, plus actual model/code/runtime identifiers for caching.

Do not expose snapshot private indexes, filesystem paths or provider formats to widgets. Do not build an inheritance framework. The callable boundary must also be easy to inject in tests.

### 4.2 Startup and wheel behavior

Add a documented **`spain-housing serve`** command with explicit `--defaults`, `--scenario`, `--release` and `--allow-synthetic` arguments. Use the supported public `python -m streamlit run` command to run the **packaged** launcher script, passing economic arguments after `--`. Default the local server to loopback; permit a documented port override. Do not depend on Streamlit's private Python CLI internals or construct a shell command from input strings.

Keep `apps/streamlit_app.py` minimal. Hatch currently packages `src/spain_housing`, not `apps`; an installed wheel therefore needs its own script/composition path. Use the active interpreter and a resolved installed package path, with no repository-root guessing, `PYTHONPATH` injection or implicit cwd data search.

Fail clearly when the optional extra is absent or a startup input is invalid. Preserve existing CLI exit behavior. Do not launch a partially initialized app with fabricated defaults after a release/config error.

Composition loads the defaults and startup scenario through existing semantics and opens one explicit release. All released locations are evaluated in a deterministic code order; selecting a city for inspection does not restrict evaluation. There is no browser field accepting arbitrary server file paths. Changing releases is an explicit startup/reload operation, never an automatic switch to whichever release appears newest.

### 4.3 Runtime data boundaries

The app reads the selected validated bundle and package metadata. It performs no ingestion, source scraping, release build or market API request while interacting. Release IDs, readiness, attribution and limitations come from actual metadata.

An optional external basemap is a presentation dependency, not market acquisition. The default map must also function without external tiles or API tokens; see Section 7. Preserve the repository's data-use restrictions. Local launch does not authorize public hosting or redistribution of a restricted release.

## 5. Scenario controls without duplicated rules

### 5.1 Required editable inputs

Group the form into compact sections; detailed tables/policies can sit in expanders. Every economically relevant supported field must be editable or preserved faithfully during import/edit/export.

| Group | Controls and units |
|---|---|
| Time | Start month, positive saving horizon in months; show derived purchase month from Scenario |
| Participants | Stable participant ID, starting savings EUR, membership of saving pool and borrower set |
| Income paths | Participant, month offset, **net annual income EUR**, linear/step interpolation |
| Debt paths | Participant, month offset, other **monthly debt EUR**, interpolation |
| Living stages | Half-open start/end offsets, room/flat-alone/flat-shared, rental area/bedrooms, combined rent share, utilities inclusion flag |
| Non-housing budget | Household effective monthly expense milestones, interpolation and retained purchase reserve EUR |
| Mortgage | Financed percentage, maximum total debt percentage, term years, annual nominal interest percentage |
| Purchase/target | Proportional cost allowance percentage, flat/house, area m² and condition |
| Market assumptions | Frozen/growth, base month, annual rent and purchase growth percentages |
| Selection | Freshness months, optional profile IDs, per-m²/per-month whole-home rent source, explicit pooled-property proxy permission |
| Geography | Clearly identified local/local mode; preserve imported independent location bindings |

Use dynamic editable tables for participant paths and living stages, with explicit numeric/text/boolean column configuration. Income in ten or twenty years is simply another milestone; keep milestones beyond the saving horizon because interpolation can depend on them. A basic current/target convenience control may populate the same path, but must not create a competing salary model.

Use stable participant IDs and row keys. Removing/renaming participants must produce either an explicit coordinated update or actionable validation errors; never silently delete unrelated path data or change borrower membership. Retain nullable selectors, interpolation choices and input precision.

### 5.2 Display conversions and validation

Percent controls convert to model fractions at one representation boundary. Dates become first-of-month values. Offsets are integer months. Labels distinguish net annual income, monthly cash amounts, nominal annual interest and the saving pool's share of one rental unit.

Pydantic/models own domain validation; application owns supported economic queries. UI owns only table shape/type conversion and user-friendly presentation of errors. Show field/row paths and retain invalid drafts for correction. Do not duplicate stage coverage, participant uniqueness or financial formulas in widget validators.

An unchanged draft must reconstruct an equal Scenario, including fractional precision. Do not round money/percentages for persistence or replace explicit nulls with defaults. Preserve fields not actively edited by basing changes on the resolved Scenario; do not recreate a partial Scenario from whichever widgets happen to be visible.

Changing the horizon must not silently stretch, erase or duplicate stages. Make any convenience adjustment an explicit user action; otherwise let validation explain the uncovered/overlapping offsets. Switching frozen/growth must not silently discard saved growth assumptions. If nonzero growth remains under frozen policy, expose the conflict for correction.

### 5.3 Explain inherited household semantics once

Include concise help next to the relevant controls:

- Saver IDs contribute income, debt and starting savings during saving. Borrower IDs determine purchase-time income/debt. The sets can differ.
- `rent_share` is the **combined saving pool's share of one unit**. Two savers renting one whole flat together normally use 100%, not 50% and not two full rents. A room query already prices a room; the app must not multiply it by participant count.
- The non-housing path is the effective household cash budget, charged once. Utilities inclusion does not supply a utility amount; users express changed expenses through milestones.
- Flat-alone requires a whole-unit share. The current per-m² rent policy needs area; bedroom-only or segmented requests may be unsupported by this pilot.
- Proxy permission is explicit. Pooled asking-price statistics do not become observed flat/house transactions because a target type was selected.

Initialize from resolved configuration rather than adding UI financial defaults. The project's indicative 80% financing, 10% cost allowance, 35% debt ratio and 25-year term remain configurable assumptions, not newly verified Spanish bank rules.

## 6. Submission, session state and caching

### 6.1 One coherent submission

Use one `st.form` with **Apply scenario**. Coordinated economic changes become one evaluation. Metric selection, city selection, table sorting and viewport controls remain outside the form and do not recompute economics.

Unsubmitted form edits remain browser-side. Label results as the last applied scenario; do not pretend the server can detect every pending edit before submission.

Respect the installed form API: no nested forms; normal buttons/download buttons are outside; only the submit button has a form callback. Dynamic data editors can add/delete rows without illegal buttons inside the form. Consume the editor's returned table; its widget state contains edit operations, not a replacement domain record.

Keep session-local draft values, last successfully applied Scenario/RunResult, a visible draft/error state, selected location code and display metric. Initialize once. Use a widget epoch or an equivalent deliberate reset to load an imported scenario before its widgets are created; do not reset keys on every rerun.

| Event | Required transition |
|---|---|
| Initial load | Resolve startup scenario; evaluate once and show explicit dataset identity |
| Edit | Keep draft separate from the displayed applied result |
| Valid submit | Validate, evaluate/cache, then replace the applied Scenario and RunResult together |
| Invalid submit | Retain draft/errors and last valid run; label it as the previous applied result |
| Expected missing/unsupported/unviable result | Apply the new run with its actual statuses |
| Evaluation failure | Show failure; never attach the new draft label to an old run |
| Metric/city change | Update presentation only |
| Valid import | Replace the draft coherently; require Apply to evaluate it |

On first-load failure there is no fabricated result. After a failed submission, downloads must clearly refer to the last applied run or be disabled until a successful apply; choose one consistent behavior. The main panel must make draft/applied distinction obvious without showing implementation jargon.

### 6.2 Cache loaded releases at composition

Use `st.cache_resource` or an equivalent explicit resource cache for the immutable snapshot. It contains a `MappingProxyType` index and is not a suitable `cache_data` pickle payload. A global resource is acceptable only while all shared objects are read-only and thread-safe.

Bound the cache, initially four releases. Key by resolved release path, actual manifest-byte digest and synthetic permission. Full release validation still happens on a cache miss; reuse the reader rather than parsing a second manifest/release format. A validated reload must clear that resource entry and the session result cache. No session-owned drafts, salaries, selections or mutable rendering properties go into the global resource.

Treat releases as immutable while the app runs. Do not poll/download sources to refresh a chart. If explicit reload finds corruption, report it instead of continuing under a newly claimed identity. Startup identifiers come from the validated snapshot, not a directory name.

### 6.3 Cache results per session using all true inputs

Use one bounded session-local result memo, initially 32 entries. An ordinary mapping/LRU in session state is sufficient; current Streamlit also supports session-scoped `cache_data`. Pick one owner, not both. Do not globally persist personal scenarios or results.

The key includes:

- Canonical complete resolved Scenario, including market selection and independent location bindings.
- Ordered full destination references, including geographic level and string code.
- Actual release ID, model version, calculation-code fingerprint and runtime evidence.

The service must agree with those identifiers before serving the cached result. If a callback is excluded from framework hashing, the complete identity still has to be explicit and checked. Never key only by salary, city count, scenario label or release path. Metric, selected city and presentation rounding are not economic inputs and stay out of the key.

Refresh calculation/runtime identifiers when composition runs after a code reload, or explicitly clear/restart the affected session. Do not capture an old code fingerprint permanently in a cached resource and then reuse results after source changes.

The existing `application.version.code_version()` hashes **all package Python files**, including future UI/launcher code. Adding Phase 5 therefore changes its code evidence. Preserve this contract; do not narrow the hash or rewrite saved Phase 4 runs to make old replay pass. Generate new runs for parity/replay tests, using the same interpreter and dependency environment for exact comparisons.

## 7. Honest municipality map and selection

### 7.1 Geometry join and layers

Use a PyDeck **GeoJsonLayer choropleth**: one released municipality, one result value/status. Do not use a kernel heatmap, spatial interpolation or coloured provinces to suggest coverage between pilot municipalities.

Join validated boundary features and location/result records by **string location code**, with matching municipality level and boundary version. Reject duplicate codes, unexpected results, missing evaluated geometry or version mismatch with an actionable integration error. Do not turn broken joins into ordinary missing-market colours. Preserve Polygon/MultiPolygon coordinates and holes exactly.

Create detached rendering dictionaries from validated records, then add display value, status, label and colour. Never mutate cached boundary objects or economic results. Names come from release location records. Geography remains separate from RunResult and its downloads.

Required layer choices:

| Layer | Returned source | Meaning |
|---|---|---|
| Maximum purchase price, EUR | `purchase.maximum_price_eur` when financial calculation is available | Price ceiling from both financial constraints |
| Affordable area, m² | `affordable_area_m2` indicator | Capacity compared with destination unit price |
| Target affordability | `target_affordability_ratio` indicator | Capacity relative to the selected target's projected price; 1 means enough capacity |

Map maximum-price status from `calculation_status`: available with a purchase record is numeric; `missing_input`, `unsupported` and `unviable` remain distinct. Area/ratio each use their own indicator status. Valid financial capacity can remain coloured when purchase-price evidence is missing and area/ratio are unavailable.

### 7.2 Stable colours and explicit nonnumeric states

Use fixed, documented bins so the same value has the same colour across scenarios. Recommended initial lower edges, with a final open-ended bin:

| Metric | Lower edges |
|---|---|
| EUR | 0; 50,000; 100,000; 150,000; 200,000; 300,000; 500,000 |
| m² | 0; 20; 40; 60; 80; 100; 150 |
| Ratio | 0; 0.25; 0.5; 0.75; 1; 1.25; 1.5 |

Intervals are lower-inclusive/upper-exclusive. Choose an accessible sequential palette; distinguish the ratio's 1 threshold in its legend. Colour and text must agree. Do not normalize each run to its own min/max, classify null as zero, cap ratio at one or display the ratio as a success probability.

**Available zero** belongs in the first numeric bin. Missing data, unsupported requests and unviable saving paths have separate nonnumeric styles and text labels. Observed/estimated/synthetic evidence and explicit proxies are separate badges, not replacements for those statuses. Unsupported means the request cannot be represented by the supplied model/data; missing means required evidence is absent; unviable means the saving path exhausts funds.

Show units, bin bounds and nonnumeric legend entries. Handle all-zero, one-location, constant-value and all-unavailable runs without division errors or an invented colour scale. Uncovered areas of Spain remain uncoloured.

### 7.3 Picking, viewport and map fallback

Use a stable unique layer ID, `pickable=True`, a stable chart key and the installed `st.pydeck_chart` single-object selection API. Current selection events expose selected objects per layer. Extract the object's **location code**, validate it against the active release, and update the session's selected code. Do not use a feature/list index as identity or write to the chart's read-only event state.

Provide a location selector and table even when picking is unavailable. A stale selection after applying a scenario must not select a different municipality or cause a rerun loop. Presentation selection never becomes an evaluator location filter.

Provide useful initial Spain/pilot context, a **Fit released areas** action and a selected-location view. Compute bounds only for viewport presentation; do not simplify or fabricate geometry. Actual municipal footprints are small at a national zoom, so city selection must offer a practical way to zoom. Preserve synthetic shapes as fixtures rather than replacing them with real outlines fetched during interaction.

Default to a PyDeck map without an external basemap (`map_provider=None` on the supported version). Allow an explicitly selected optional basemap if useful; it must not require an account/token for the core workflow. Missing tile access must leave polygons, selection fallback and table usable. Make sparse pilot coverage and synthetic geography visible even when no coast outline is available.

Use plain-text tooltips with name/code, formatted value and units, status/reason and a concise evidence/proxy label. Avoid rendering untrusted source text as HTML. Add a meaningful chart alternative description and visible attribution/coverage text.

## 8. Financial breakdown, budgets and provenance

### 8.1 Explain the two constraints using returned results

For a selected available location, show:

- Maximum purchase price, savings-based limit, mortgage-based limit and binding constraint.
- Ending and usable savings, retained reserve assumption, purchase month and borrower monthly net income/other debt at purchase.
- Target price, target loan, upfront cash, monthly payment, cash shortfall and payment shortfall when the complete target diagnostics exist.
- Affordable area and target ratio with their independent status/reason.

The model's relationship is **P_max = min(P_savings, P_mortgage)**. It is not the maximum of the two limits. UI explains this relationship; finance remains its only implementation owner. A `None` cash limit means **no cash constraint**, not missing data or a displayed infinite currency amount. A zero capacity/shortfall is legitimate. Missing target diagnostics must not be reconstructed in widgets.

Show both saving and buying location labels, even when equal in local/local. Avoid rendering a single generic location that later makes fixed-saving difficult to add.

### 8.2 Monthly trace

Plot the returned `SavingsResult.monthly_path` using its actual months and signed closing balances; negative contributions/balances must remain visible. Show the prepared monthly budget columns alongside contribution/balance and stage labels where useful. Associating a returned month with a stage for display is permitted; resampling income, multiplying rent or recalculating contributions is not.

Show the full exhaustion path for an unviable run, its reason and any returned traces. Do not replace it with a zero-priced purchase or hide recovery after the first exhausted month. For missing/unsupported preparation, show explanations and supporting evidence actually returned, not a partial invented budget.

Use display rounding only. Tables/downloads must not substitute rounded values for the underlying RunResult. Keep annual net income input separate from monthly borrower/budget amounts.

### 8.3 Source information

Render `market_inputs`, context attribution, warnings and limitations. For each distinct input use, show its role, original observation value/unit, source, basis/statistic, segment, evidence kind, reference interval, selected profile, reference/base timing, growth assumption and any property proxy. Explain projected values without relabelling their original observations.

Quarterly room evidence remains quarterly; growth does not manufacture a later observation. Pooled asking-price data remains an approximation when used for a flat/house target. Estimated and synthetic values require visible badges. Do not duplicate one source row for every budget month.

Source hyperlinks may use validated public URLs; render them as links rather than raw HTML. Release kind/readiness and fixture geography labels remain visible in the main page, map and exported run context. Keep lengthy technical version details in an expander while making release identity discoverable.

## 9. Safe scenario import and reproducible downloads

### 9.1 One configuration parser

Add a small in-memory parsing entry point to **config.py** and make the file loader delegate to it. Preserve duplicate-key rejection at every depth, safe YAML, top-level mapping checks, recursive dictionary merge, list replacement and explicit-null override. This is a parser extraction, not a new config system.

Composition injects an upload decoder that parses text, resolves against the startup defaults and validates a fresh Scenario. UI does not import the config module or implement its own JSON/YAML/default rules. Complete resolved exports must load without losing economic fields.

Accept UTF-8 JSON/YAML/YML scenario uploads, with a documented initial size bound of **1 MiB**. Treat the uploaded name only as a format hint; do not write to a supplied path. Reject invalid encoding, unexpected extensions, duplicate keys, unsafe YAML constructs and invalid model data with actionable errors. Never deserialize pickle or trust uploaded calculations as a newly evaluated result.

Validate before replacing the draft. A failed import preserves current draft/applied state. A valid import stages the whole scenario and visibly waits for Apply. Existing valid but deferred modes stay intact and can produce an unsupported run; never coerce them to local/local. Saved-run import/replay inside the UI is not required; existing CLI replay remains the supported verification path.

### 9.2 Downloads share existing owners

Provide separate downloads for:

1. **Applied resolved scenario JSON**, encoded by `config.scenario_json` through the service boundary.
2. **Applied run.json**, encoded by `application.export.run_json`.
3. **Applied summary.csv**, encoded by `application.export.summary_csv`.

All three refer to the same applied Scenario/RunResult, release and versions. Do not encode RunResult with a second UI schema, reformat the existing economic CSV or include map colours/geometry in run.json. Downloads are outside the form, use stable filenames/content types, and do not trigger economic evaluation. The browser owns the save destination; the app does not write an output directory on every rerun.

Verify downloaded JSON/CSV bytes against the existing encoders and the equivalent CLI run in the same environment. Display-only selection and formatting must not alter them.

## 10. Failure behavior and clean-code constraints

Distinguish three failure classes:

| Class | Behavior |
|---|---|
| Invalid scenario/import | Field-oriented message; preserve draft and clearly identified previous applied run |
| Expected economic/data condition | Apply typed missing/unsupported/unviable statuses; other locations/indicators stay usable |
| Startup, corrupted release, geometry join or unexpected execution failure | Clear integration error; no fabricated result or silent fallback |

Handle expected exceptions at the interface boundary. Do not catch every exception and turn it into a missing municipality. Unexpected failures should retain useful diagnostic evidence without presenting personal salary data in logs or swallowing the cause. No retry loop for invalid inputs or unavailable market captures.

Application/result models already provide the required diagnostics. If inspection reveals a genuinely missing reusable quantity, add it minimally at its proper application/model owner with a focused test; do not invent a UI implementation or use this as a reason to refactor the financial engine. Preserve numerical behavior, schema compatibility and replay contracts.

Keep production functions small, typed and explicit. Avoid duplicated widget groups, status switches, threshold definitions, parsers and serialization rules. One metric projection feeds map/table/tooltips; one colour definition feeds polygon colours and legends. Keep presentation rules separate from economic rules. Do not add a framework because only one mode/strategy exists.

## 11. Autonomous work loop and milestones

### 11.1 Persistent checkpoint and resumption

Before substantial edits, create/update **docs/progress/PHASE_5.md** with baseline commit, worktree state, intended milestones and known blockers. Maintain one compact checkpoint containing:

- Current milestone, completed behavior and the next concrete action.
- Material decisions, affected paths and deviations with reasons.
- Exact verification commands/results and failing or unverified criteria.
- Local launch/rebuild instructions and transient artifact locations when needed.
- Separate engineering, browser and observed-data readiness.

After context loss or a restart, inspect this file, git status/history and current code before acting. Resume the next incomplete step; do not restart the project or assume an earlier successful check still covers later changes. Keep source-of-truth rules in their owning modules/docs rather than repeatedly copying this guide into progress notes.

At each milestone: implement a coherent slice, run relevant checks, fix failures, update the checkpoint and make a scoped local commit when allowed. Do not wait for routine approval between milestones. Preserve unrelated/user-owned changes; stage deliberately. Avoid committing generated releases, exports, screenshots containing personal data or temporary browser environments. Do not rewrite earlier commits to hide a failure.

If one criterion is blocked, finish independent work and record the exact blocker. No endless investigation of restricted sources, test skipping, placeholder feature or invented green status. Long-session reliability comes from small verified increments and recoverable evidence, not a larger agent harness.

### 11.2 M1 — Baseline, composition and dependency contracts

Re-establish the actual current baseline and inspect Phase 4 interfaces. Add the map extra, lock it, preserve the core-only import/CLI path and introduce packaged composition plus a tiny repository entry point. Define the typed service boundary and extend/sensitivity-test import contracts.

**Exit evidence:** startup errors are clear; a valid release can be loaded through the installed composition path; a no-map installation can still import/help/validate; dependency checks pass. Document the chosen versions and cache/service shape before building widgets.

### 11.3 M2 — Complete controls, parsing and draft state

Extract the shared safe in-memory config parser. Implement complete participant/path/stage inputs and advanced policy controls, lossless round-trip conversion and atomic import/draft transitions. Use one form and actionable validation. Preserve all scenario fields and deferred modes.

**Exit evidence:** untouched room and staged-growth demos reconstruct equal Scenarios; multi-participant and future-milestone edits survive reruns; invalid stage/participant/null/upload cases preserve state without evaluation.

### 11.4 M3 — Applied runs, cache and downloads

Connect valid submission to the existing evaluator for all released locations. Implement the resource cache and bounded session memo with true identities. Keep presentation reruns independent of economics. Add downloads using existing encoders and verify UI/CLI agreement.

**Exit evidence:** one valid submission produces one coherent applied run; invalid/failing submissions cannot relabel it; changing a real assumption invalidates the correct cache; metric/city/download interactions do not reevaluate; two sessions keep personal state separate.

### 11.5 M4 — Map joins, statuses and selection

Implement detached GeoJSON, fixed bins/legend and all three metrics. Preserve holes/multipolygons, numeric zero and partial indicator states. Add map picking, selector fallback, viewport actions and default operation without tiles. Label synthetic markets and geometry.

**Exit evidence:** pure join/bin/status tests pass; corrupt joins fail explicitly; all pilot features appear with correct values/statuses; selection uses code and changes only presentation.

### 11.6 M5 — Details and interactive verification

Render financial limits, target diagnostics, signed savings/budget paths and source traces. Finish import/export usability. Exercise complete workflows with AppTest and a real browser; repair state/picking/rendering issues revealed by those checks.

**Exit evidence:** details agree with RunResult and downloaded output; invalid edits/imports do not produce stale labels; browser evidence shows actual polygons, tooltips, picking/selection and a changed applied scenario. Health checks alone do not satisfy this milestone's visual evidence.

### 11.7 M6 — Full gate, installed package and handoff

Run the final complete quality gate/build, verify a fresh wheel with and without the map extra outside the checkout, and repeat the synthetic end-to-end workflow using the installed app. Use the same interpreter/runtime for exact CLI/UI/source/wheel economic comparisons. Review for duplicate rules and unnecessary dependencies.

Update README, architecture and progress with real launch commands, supported assumptions, verification and blockers. Evaluate an authorized observed release if available; otherwise retain the inherited observed-data blocker. Finish with A1–A12 states and the next-phase handoff.

## 12. Meaningful tests and required verification

### 12.1 Independent pilot reference

Use the real synthetic builder and repository fixture from **tests/conftest.py**. Do not create a second fake loader or duplicate fixture tree. **configs/scenarios/phase4_room_demo.yaml**, resolved with defaults, is a useful hand-checkable reference: twelve saving months, EUR 24,000 net annual income, EUR 100 monthly debt, EUR 8,000 starting savings, EUR 900 expenses and EUR 5,000 reserve, with zero-interest 25-year financing.

| Location | Monthly room rent | Usable savings | Cash-limited maximum price |
|---|---:|---:|---:|
| Madrid | EUR 300 | EUR 11,400 | EUR 38,000 |
| Barcelona | EUR 350 | EUR 10,800 | EUR 36,000 |
| Jaén | EUR 150 | EUR 13,200 | EUR 44,000 |
| Getafe | Missing | Unavailable | Unavailable |

The mortgage limit is EUR 225,000 for each viable location; savings therefore bind. Under the synthetic unit prices, affordable area is approximately 12.67/14.4/44 m² and the 80 m² target ratios are approximately 0.1583/0.18/0.55 for Madrid/Barcelona/Jaén. Assert precise engine values with suitable numeric tolerances; do not use these display approximations as implementation constants.

Also use **phase4_staged_growth_demo.yaml** to exercise two savers/one borrower, room → flat-alone → flat-shared, explicit expense changes and separate rent/purchase growth. UI is expected to present those backend results, not add a new financial oracle.

### 12.2 Test at the correct level

| Level | Required evidence |
|---|---|
| Pure presentation/conversion | Lossless scenario round-trip; numeric units; metric-specific status/value; bin boundaries; zero/ratio >1/unbounded cash; malformed join; preserved holes/multipolygons; no input mutation |
| Session/controller | Valid/invalid/apply/import transitions; participant and future-path retention; stable selections; stale-run labels; cache invalidation for assumptions/locations/releases/versions; independent sessions |
| Streamlit AppTest | Supported widget edit/apply, error correction, import and display transitions, downloads tied to the applied run |
| Application/CLI integration | Real builder/reader/evaluator; UI-applied Scenario and run JSON/CSV equal the same ordered CLI invocation; missing saving versus missing buying evidence; unviable path and available-zero cases |
| Real browser | WebGL polygons, hover, map picking, selector, zoom, legends, layout, dynamic stage/path table edits and an actual changed scenario |
| Installed package | Fresh map-enabled wheel launches outside checkout; core-only wheel preserves existing workflows |

Keep tests focused on behavior that could fail across these boundaries. Do not copy the implementation into expected results or add snapshot tests for every caption. Reuse existing backend tests instead of retesting amortization in UI.

Use the supported installed AppTest API and dependency injection. `AppTest.from_file` does not accept a startup `args` parameter; configure the normal startup arguments or use a thin injected test entry point. Do not add production-only test flags. AppTest is a simulated app runtime; a passing test does not prove browser/WebGL rendering or map picking.

Check its supported element classes before automating data-editor changes. Do not invent an `AppTest.data_editor.set_value` API or manipulate private protocol objects. Test draft/table conversion as pure behavior and verify unsupported widget interactions in the real browser, including row addition/deletion.

### 12.3 Quality gate with optional dependencies

Update the repository's full gate so **every** `uv run` in **scripts/check.sh** includes `--extra map`. A prior `uv sync --extra map` alone is insufficient: a later default `uv run` can resynchronize without that extra. UI tests/type checks are part of the full gate; do not silently skip them when dependencies are absent.

```bash
uv sync --locked --extra map
bash scripts/check.sh
uv build
git diff --check
```

The gate must retain lock checking, Ruff format/lint, strict mypy, all existing and added import contracts and the full pytest suite. Include the tiny app entry point in appropriate lint checks. Preserve a separate documented core-only smoke workflow; it is not a reason to omit UI tests from the full development gate.

### 12.4 Browser and installed-wheel proof

Use an actual browser or a suitable automation tool against the local app. Record the browser/version, command, release/scenario and observed behavior. Check:

1. All four fixture municipalities render, including the polygon hole/multipolygon and Getafe's missing room state.
2. Switching all three layers gives correct units, thresholds and per-indicator statuses; zero/ratio >1 cases remain honest.
3. Hover/picking and selector choose the same code/details, and selection does not trigger economic recomputation.
4. Editing, adding/deleting table rows and applying staged income/living assumptions changes the correct run; invalid submission preserves an explicitly previous result.
5. Default no-tile rendering and table remain usable; basic layout/readability and source/synthetic labels are visible.
6. Downloaded bytes identify the applied run and agree with the existing encoders.

For fresh-wheel verification, create a new Python 3.12/3.13 environment outside the repository, install the built wheel **with `[map]`**, unset `PYTHONPATH`, and run the packaged `serve` path using absolute input paths. Confirm imports resolve from `site-packages`; verify the launch is not using `apps/` from the checkout. Build/validate the fixture release through installed commands or use an explicitly verified release, then exercise evaluation/download/replay.

Also verify a fresh installation **without** `[map]`: package import, CLI help, scenario validation and evaluation/replay work; attempting `serve` gives a useful missing-extra message. Do not claim this from an environment where Streamlit was already installed.

Exact source/wheel JSON comparison requires the same interpreter and economic dependency environment. Preserve source fingerprint/runtime checks rather than masking a mismatch. HTTP health, compilation and screenshots of a blank map do not establish rendered functionality. If browser tools are unavailable, finish independent engineering and report A10 unverified with the precise reason.

## 13. Acceptance criteria and completion report

| ID | Requirement |
|---|---|
| A1 | Baseline re-established; existing commands/scenarios remain usable; all import boundaries are preserved and launcher bypass edges are enforced |
| A2 | Optional map dependencies are locked; supported public framework APIs and packaged startup work; core installation does not require UI dependencies |
| A3 | Required scenario inputs are editable and losslessly preserved, including multi-participant paths, future milestones, stages, selection policy and independent location bindings |
| A4 | Draft/applied state, coordinated submission, import reset and failure behavior remain coherent across reruns; no stale result is labelled as a new scenario |
| A5 | Release and result caches are bounded and correctly identified; personal state is session-local; presentation changes do not reevaluate economics |
| A6 | Three map metrics, strict code/version joins, geometry preservation, fixed legends, status distinctions, zero/ratio >1 and selection fallback behave correctly |
| A7 | Details show returned limits, bottleneck, diagnostics, signed path, budgets and original source/projection/proxy evidence without recalculating economics |
| A8 | Safe shared-parser import and existing-owner downloads work; applied UI JSON/CSV matches the equivalent ordered CLI run and replays exactly in the same runtime |
| A9 | Full quality gate/build passes and fresh wheels with/without the map extra are verified outside the checkout, with actual installed paths/evidence |
| A10 | Real browser verification proves rendered geometry, hover/picking, selection, edits, statuses and default no-tile usability; AppTest/health alone is insufficient |
| A11 | An authorized observed release is evaluated and rendered for the real core municipalities with accurate source/geometry labels; synthetic data does not satisfy this criterion |
| A12 | README, architecture and progress accurately record commands, scope, decisions, verification, blockers and future extension boundaries; no redundant business rules/frameworks remain |

At the reviewed baseline, **A11 is blocked by inherited market access**. If all other criteria are verified, report **engineering and browser verified; observed-data integration blocked**. If A10 is also unverified, say so separately. Never mark all criteria complete or imply the implementation plan's observed-data condition has been satisfied by fixtures.

Finish with a concise report: implemented behavior, milestone/local commit references, actual checks, A1–A12 status, unresolved blockers and next action. Label planned checks as planned, failed checks as failed and unexecuted checks as unverified.

## 14. Future implementations and handoff

The pipeline must remain modular enough that the following features can be added **without substantial repository restructuring**. Preserve boundaries now; do not implement their speculative machinery in this phase.

| Future feature | Extension point to preserve |
|---|---|
| Save in A, buy in B | Existing independent bindings, destination-free `prepare_savings`, reusable purchase evaluation; later controls select a saving location while the map still represents buying destinations |
| Profession/location salary potential | Separate salary/employment data releases and service; scenario income remains an explicit input. Later evidence can contextualize feasibility without becoming an invented hiring probability |
| Historical views, including 2010 | Explicit observation periods, scenario/base months and versioned releases; later as-of selection/backcasting policies belong to market/application owners, not a UI date slider alone |
| More municipalities and segments | Same validated release contract and exact queries; honest sparse coverage, names/codes and per-indicator states rather than hard-coded pilot locations |
| Minimum income or years needed for purchase | Separate application solver over the existing finance/scenario contracts; UI consumes its results rather than embedding a search loop |
| Batch comparison/Hydra if justified | Optional batch composition producing the same validated Scenario and RunResult; no framework dependency inside finance/application |

Do not use the selected inspection city as the future fixed saving location. Do not merge salary potential into an affordability ratio or confuse asking prices with transaction prices. Historical modeling is the latest extension and needs actual period-specific data and assumptions.

Phase 6 should broaden permitted coverage and improve reproducible operation using this same UI/service boundary. It should not have to repair hidden formulas in widgets, redesign scenario serialization or replace a hard-coded city list. Hand off working synthetic workflows, explicit observed-data blockers, real cache/performance observations and the unverified criteria, if any.

## 15. Research basis

The following primary sources informed workflow and framework choices. They explain capabilities; the project decisions and acceptance criteria above are the implementation contract. Check the APIs against the locked installed versions rather than copying an old tutorial.

### Long autonomous implementation

- [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) — scoped milestones, executable checks and persistent progress. Applied through M1–M6 and recovery instructions.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — incremental verified work and recoverable execution state. Applied through scoped checkpoints, actual evidence and honest incomplete criteria.
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) — repository navigation and mechanically enforced architecture. Applied through existing source-of-truth docs, import contracts and thin composition.

### UI, map and verification

- [Streamlit package/version](https://pypi.org/project/streamlit/1.65.0/) and [PyDeck package](https://pypi.org/project/pydeck/) — stack/runtime feasibility.
- [Streamlit forms](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form) and [data editor](https://docs.streamlit.io/develop/api-reference/data/st.data_editor) — coordinated submissions and editable path/stage tables.
- [Streamlit resource caching](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource), [data caching](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data) and [session state](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) — read-only shared resources versus session-owned inputs/results.
- [Streamlit PyDeck chart](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart), [PyDeck Deck](https://deckgl.readthedocs.io/en/latest/deck.html), [layers](https://deckgl.readthedocs.io/en/latest/layer.html) and [tooltips](https://deckgl.readthedocs.io/en/latest/tooltip.html) — polygon rendering, selection, layer identity and optional basemaps.
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [supported testing elements](https://docs.streamlit.io/develop/api-reference/app-testing/testing-element-classes) and [app-testing concepts](https://docs.streamlit.io/develop/concepts/app-testing) — supported UI state tests alongside separate browser/widget rendering proof.

Repository interfaces, financial semantics and readiness were verified from the recorded checkout. This guide introduces no newly researched bank rule, market observation or source permission.
