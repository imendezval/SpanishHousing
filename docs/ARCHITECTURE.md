# Architecture

The installable `src/spain_housing` package keeps validated contracts in `models`, calculations in `finance`, dataset acquisition/preparation in `ingestion`, common persistence in `storage`, offline access and pure selection/projection in `markets`, scenario orchestration in `application`, configuration loading in `config`, and entry points in `cli`. `ui` remains reserved for Phase 5. Nine Import Linter contracts enforce dependency direction, including the indirect application/storage prohibition and pure market rules' separation from repository/storage.

Saving and buying locations are separate bindings in every scenario. Dates and periods are explicit. Market observations carry measure, segment, provenance, and status. Synthetic fixtures live only under `tests/fixtures/synthetic`; observed source evidence lives in `data/manifests/coverage_audit.csv`.

The financial engine receives prepared monthly budgets; it does not read configuration, fetch market data, or infer geography. Market-data and purchase-cost protocols mark replaceable boundaries. The proportional purchase-cost policy implements the existing costs-only protocol; the fixed-financing solver explicitly requires that concrete policy because an arbitrary cost function has no supplied inverse.

`Scenario` stores the first saving month, positive horizon, dated market policy, and two location bindings. The purchase month is derived, never separately editable. Income milestones are annual net euros; the examples choose linear interpolation. Debt and household expenses use monthly euros and step paths in the examples. Each path records its own linear/step choice and plateaus after its last milestone. Phase 4 expands these validated paths into cash flows. Floating-point money is finite, with rounding reserved for presentation.

`config.py` owns YAML/JSON parsing and recursive defaults → saved-scenario merging. Lists replace lists, and explicit nulls do not inherit defaults. `models` owns schema/domain validation. The CLI preserves scenario/dataset commands and composes evaluation/replay through application. It constructs the concrete snapshot at this boundary; it performs no policy selection, financial calculation or implicit acquisition. Runtime roots and credentials are excluded from economic scenarios.

`MarketQuery` is period/segment-aware; `MarketObservation` distinguishes source-published, estimated and synthetic evidence. Its metric determines the legal unit. `MarketLookup` and output indicators keep missing/unsupported states separate from numeric zero. A `RunResult` binds a resolved scenario to release, schema, model and code identifiers. `SnapshotMarketRepository` implements `MarketData`; purchase-cost policies implement `PurchaseCostPolicy`.

## Phase 2 ownership and contracts

`finance/savings.py` validates budget chronology and owns the monthly recurrence. It preserves signed contributions and balances, retains the reserve at purchase, and records exhaustion permanently when a closing balance is below −1e−8 EUR. That epsilon only affects viability; raw balances remain unchanged. The entire diagnostic path is returned even after exhaustion. Purchase capacity rejects an exhausted path.

`finance/mortgage.py` owns a stable annuity factor shared by payment and maximum-loan calculations, plus the total-debt payment allowance. Rates are annual nominal decimal fractions, payments are monthly EUR, and the first payment occurs one month after origination. Zero interest and representational rate underflow use the exact payment count. Non-finite derived outputs raise `ValueError`.

`finance/costs.py` owns the proportional purchase allowance, its cash fraction and the common upfront helper. The helper adds the down payment and both supplied cost components once. `finance/purchase.py` combines the cash and mortgage limits under a fixed financed fraction, retains their actual minimum, and labels both binding within €0.01 absolute tolerance. Target diagnostics call the common cost and mortgage functions. `finance/_validation.py` shares scalar finite-number checks across these public boundaries.

`PurchaseResult.savings_price_limit_eur` is still required but accepts `None` solely for the mathematically unbounded case (full financing, zero costs). The remaining limits remain finite. `target_loan_eur` is new; the target price, principal, cash, payment and two shortfalls must be all present or all absent. Existing finite target-free payloads remain valid. No persisted target result was found in the checkout; no data migration was needed. Scenario schema version and the cost protocol are unchanged. Phase 2 emits financial records only; Phase 4 must record its actual financial model version when producing `RunResult`.

See the callable [README example](../README.md#financial-python-api) and [Phase 2 evidence](progress/PHASE_2.md). Phase 3 independently owns data access and pilot coverage. Phase 4 owns annual-to-monthly expansion, saver/borrower selection, living stages, rent shares, utilities and market projections. It must prepare exactly N saving months, sample purchase finances at offset N, translate exhaustion to an unviable location, and supply explicit destination/date context and resolved target price. Geographic modes and caching reuse savings; nonlinear purchase taxes require an explicit new solver in purchase, and variable financing requires a separate solver using the same helpers.

## Phase 3 ownership and dataset contracts

`models/dataset.py` defines frozen recipe, capture, usage, location, profile, lineage, coverage, manifest and coordinate records. Existing market/scenario/financial schemas are preserved; shared market basis/statistic type aliases prevent duplicate definitions. A `ReleasedObservation` wraps the existing observation with one capture ID and source locator. Publication, reference intervals and actual timezone-aware capture timestamps remain distinct. The new dataset schema is explicitly version 1.

`ingestion/adapters/curated.py` reads one strict reviewed CSV format. `normalize.py` owns explicit locale/unit translation and crosswalks, preserving source statistics, pooled/room products, uncertainty, intervals and acquisition times. Curation is not permission. `adapters/official.py` separately downloads reviewed permitted INE/IGN inputs with timeout, HTTP/permission metadata and immutable hash-addressed capture bytes. Building never downloads.

`ingestion/geography.py` reconciles documented INE province/municipality/control columns and selects complete retained IGN features using verified full identifiers, municipality scope and official names. Missing/duplicate identities, projected/incorrect axes and incomplete paginated inputs are rejected. No clipping, geometry repair or simplification is implicit. Actual source snapshot hashes/time identify boundary versions when the service has no named edition.

`ingestion/release.py` assembles retained inputs, fingerprints actual processing/model/storage source content and delegates publication. `storage/release.py` alone owns canonical serialization, strict JSON/JSONL parsing, checksums, content identity, permission/lineage/profile/coverage verification, shared geometry validation and atomic/idempotent writes. Schema validation remains in models. Observed acquisition must be permitted for every included source; overall redistribution cannot exceed the least permissive decision. Synthetic releases require explicit opt-in and never become observed through that flag.

The common `storage` namespace is needed because ingestion and markets cannot depend on each other. Storage imports models and small parsing/topology tools; it cannot import implementation namespaces. Finance, models, scenario config, future application and direct UI access cannot import storage. Existing dependency contracts remain enforced, with sensitivity checks for the new forbidden edges. Shapely validates topology; openpyxl reads the selected INE XLSX. No geospatial/dataframe service or database was added.

`markets/repository.py` validates one explicit release at open, then uses an immutable in-memory index. `get` matches exact reference intervals and supplied segment dimensions, classifies unsupported capabilities before searching values, returns missing for valid gaps, and rejects ambiguity as unsupported. Invalid/corrupt release data raises an error instead of becoming a missing lookup. `manifest`, released locations and complete geometries are read-only. Runtime queries need no raw captures, configuration or network.

Readiness is separate from implementation: official four-municipality geography is verified; market acquisition remains blocked and there is no observed release. The source recipe and [current access notes](DATA_ACCESS.md) identify the affected core cells. [Phase 3 progress](progress/PHASE_3.md) owns executed evidence; the [README](../README.md#offline-dataset-workflow) documents reconstruction and installation. Phase 4 receives explicit release paths, profiles, geography/attribution, gaps and original provenance, and owns temporal selection and financial preparation. Save-in-A/buy-in-B mode and historical releases can reuse these explicit query/location/period boundaries.

## Phase 4 evaluation and replay

`Scenario.market_selection` defaults to latest complete profiles, age at most 12
calendar months since the end-exclusive boundary, unit whole-home rent, no pooled
proxy and no explicit profile IDs. IDs are checked against context once per run;
unknown IDs or multiple explicit choices for a metric are invalid requests.
Scenario/result schema version remains 1 for compatible defaulted additions.

`models/evaluation.py` carries immutable public context, original market-input
traces, borrower finances and structured runtime evidence. The snapshot's single
`evaluation_context` property projects validated release metadata and locations;
it excludes geometry, captures, file roots and its private index. Application
receives that context plus the existing `MarketData` protocol. Importing the
concrete repository from application would indirectly reach storage and is
forbidden. Selection/projection are pure market modules that do not import it.

`markets/selection.py` owns eligible exact dimensions, completed intervals,
freshness, source/basis/statistic ambiguity, latest choice and response/profile
agreement. Exact property profiles are preferred over explicitly permitted pooled
proxies. A selected missing cell never triggers older or pooled fallback. The
repository continues to match only exact periods; quarterly rooms retain their
original interval. Unsupported selectors/conditions and missing/stale products
remain separate states.

`markets/projections.py` compounds effective annual growth once from the last
covered month (June for Q2 rooms, September for September prices), using rent or
purchase growth respectively. Frozen policy retains original values throughout.
These are snapshot counterfactuals, not as-of historical forecasts. Original
observations never become projected observations. Starts before base are
unsupported; nonfinite/zero-underflow market arithmetic fails explicitly.

`application/prepare.py` owns the single amount-path sampler and destination-free
saving preparation. Annual income is divided by 12; debt and effective expenses
are monthly. Only savers enter the saving pool; borrowers are sampled separately
at purchase offset N. Exactly N budgets exist on success, with half-open stages
and no budget at purchase. All required rent inputs are resolved first; expected
issues retain useful traces but no shortened budgets/financial result.

Each stage prices one room or dwelling for the combined saving pool. Unit rent
uses explicit rental area; direct monthly rent does not multiply it. Rent share
is applied once; saver count and bedrooms are not rent divisors. Effective
non-housing spending is counted once, including only bills outside rent. Utility
flags preserve user assumptions without inferring an allowance. Explicit expense
milestones model changed spending when bills change.

`application/modes.py` resolves distinct saving/buying bindings and canonical
location order. `evaluate.py` composes complete budgets with `simulate_savings`,
then passes usable savings, purchase-month borrower finances, explicit destination
context and optional target price to the existing fixed-financing solver. Its
separate `evaluate_purchase` helper can reuse savings across destinations.
`compare.py` alone translates returned capacity into approximate area and target
ratio; it never recalculates cash limits or shortfalls. Public runs expose only
local/local; fixed-saving returns deferred unsupported results without market
or finance work. The lower-level location API supports separate A/B references.

Results include complete prepared budgets/path, purchase finances, each distinct
market-input trace and stable deduplicated warnings. Missing buying evidence
preserves capacity with absent target diagnostics. Missing saving evidence yields
no completed calculation; exhaustion retains the entire path and no purchase.
Indicators explicitly distinguish available, missing, unsupported and unviable.
Viable zero capacity is available, and target ratios may exceed one. Models
validate structural coherence; application owns computed relationships.

`application/version.py` records model semantics `finance-v1/scenario-v1`, package
version plus a framed SHA-256 fingerprint of all actual package Python source,
and sorted actual direct dependency/Python versions. It works from installed
source without Git, mtimes, output paths or wall-clock run timestamps. Source
reads for this fingerprint are declared evidence work, not market refreshes.

`application/export.py` owns economic JSON/CSV, separately from release storage.
Exports serialize first, stage both files beside the new destination and rename
together; existing destinations/writer locks are refused and only owned staging
is cleaned on failure. `run.json` is authoritative; CSV references the same
records with empty gaps and an explicit unbounded-cash flag. Municipality codes
must be spreadsheet text. Replay uses saved resolved inputs, explicit release
and identical model/code/runtime evidence, then compares deterministic content.
Legacy runs without context/runtime cannot prove exact replay.

Phase 5 receives the stable callable exports from `application`, typed results
and explicit synthetic demos. A launcher joins the separate read-only geometry
by location code/version; geometry is not embedded in the economic run. Rendering
must reuse budgets, finance, statuses and source traces without recalculation.
No cache, salary model, historical reconstruction, new tax model or map was
introduced. Observed integration remains blocked (Phase 4 A10); see
[Phase 4 evidence](progress/PHASE_4.md) and [data access](DATA_ACCESS.md).

## Phase 5 map boundary

`launcher.py` composes explicit configuration, the validated repository and a
small typed `ui/contracts.py` service bundle. The packaged CLI `serve` invokes
`sys.executable -m streamlit run` on the installed launcher, bound to loopback.
Its script entry calls the imported launcher module so reruns share the immutable
resource cache. This cache holds at most four releases, keyed by resolved path,
actual manifest-byte digest and synthetic permission. Explicit reload clears
resources and the requesting session's economic memo and revalidates artifacts.

The UI imports models and application serializers/services; the import gate also
forbids lower layers importing the launcher. No financial rule, market lookup,
release parser or serialization format is implemented in UI. Configuration's
safe mapping parser is shared by file loading and limited UTF-8 scenario uploads.

`controls.py` converts the entire resolved scenario into editable tables and
reconstructs it losslessly. Models own validation. `state.py` owns each session's
draft, applied run, import epoch and selected code. Its LRU memo holds at most
32 runs, identified by full scenario, ordered destinations, release/model/code
and actual runtime evidence. Drafts and salaries never enter a global cache.
Presentation controls do not evaluate; imports stage a draft and require Apply.
`app.py` exposes the applied run through existing JSON/CSV owners.

`map.py` performs a strict detached code/level/version join with immutable
geometry, preserving holes and multipart shapes. `presentation.py` projects
returned values and metric-specific statuses into fixed bins; `details.py`
presents returned paths, budgets and traces. Map picking uses feature codes,
with selector/table fallback. PyDeck's no-provider default avoids Streamlit's
remote themed-basemap fallback; external tiles/tokens are unnecessary. Rendering
uses stable public chart/editor APIs. Streamlit/PyDeck belong only to the optional
`map` extra. Phase 6 can extend presentation against these services without
moving economics into the UI. Observed integration remains blocked; synthetic
geometry and market values are explicitly distinguished from observed evidence.
