# Spain Housing Simulator — Repository and Implementation Plan

Date: 4 October 2026.

Companion to `SPAIN_HOUSING_PROJECT_BRIEF.md`, which remains the detailed product, data and calculation specification. This plan defines repository ownership, dependency boundaries and implementation phases without repeating that specification. Proposed package name: `spain_housing`.

## 1. Architecture decision

Use one installable Python package with clear internal modules. The CLI and Streamlit application call the same scenario-evaluation service. Offline data preparation produces immutable dataset releases; interactive calculations consume a selected release.

The aim is to preserve the core contracts when adding the already-planned features. A larger number of folders does not itself create modularity: inputs, outputs, dependency direction and ownership are what matter.

Do not create a separate service, repository or general-purpose plugin framework for each component. Add real implementations as they become necessary; future feature packages need not exist as empty directories now.

## 2. Configuration: start without Hydra

Recommendation: YAML for readable defaults/examples, Pydantic for validated scenario and configuration models, and JSON for resolved run/scenario exports. Keep Python dependencies in `pyproject.toml` and use one committed dependency lockfile.

Separate three kinds of configuration:

| Kind | Examples | Where it belongs |
|---|---|---|
| Scenario/model assumptions | Income milestones, living stages, saving horizon, mortgage/cost assumptions, projection policy | Validated scenario objects and saved YAML/JSON |
| Data collection and selection | Provider parameters, locations, dataset release | Source configuration and explicit release selection |
| Runtime settings | Data root, output root, credentials when needed | CLI/environment settings; credentials excluded from committed scenario files |

Resolve scenario values deterministically: documented defaults, then saved scenario, then explicit user overrides. Validate the final resolved scenario and preserve it with each export. A loaded snapshot must not change implicitly while a run is being evaluated.

Hydra supports hierarchical config composition and job sweeps, but those are not the initial application's main need. Slider updates and evaluation across locations are ordinary in-process computations. If batch scenario sweeps later justify Hydra, place it around a separate batch entry point that converts its config into the same validated scenario object; do not make the financial engine depend on Hydra/OmegaConf.

References:

- [Hydra introduction](https://hydra.cc/docs/intro/)
- [Hydra Compose API](https://hydra.cc/docs/advanced/compose_api/)
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Python Packaging Guide: src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

## 3. Repository structure

Use the `src/` package layout and install the project for development and tests. The following paths define ownership; small components may start as single files and become subpackages when their implementation grows.

| Path | Responsibility |
|---|---|
| `pyproject.toml` + one lockfile | Package metadata, dependencies, tooling and CLI entry point |
| `README.md` | Setup, data preparation, example evaluation and launching the app |
| `docs/PROJECT_BRIEF.md` | Product requirements, inputs, outputs, formulas and source candidates |
| `docs/IMPLEMENTATION_PLAN.md` | Architecture, phases and completion criteria |
| `configs/defaults.yaml` | Explicit default assumptions |
| `configs/scenarios/` | Small example scenarios |
| `configs/sources/` | Source-specific acquisition settings |
| `src/spain_housing/models/` | Validated scenario, monthly-input, observation, release and result contracts |
| `src/spain_housing/finance/` | Savings, mortgage, purchase-cost and purchasing-capacity calculations |
| `src/spain_housing/markets/` | Snapshot access, period/segment selection, market projections and geographic processing |
| `src/spain_housing/ingestion/` | Source adapters, normalisation, coverage checks and release building |
| `src/spain_housing/application/` | Preparing financial inputs, geographic modes, evaluation and market comparison |
| `src/spain_housing/ui/` | Controls, maps and result breakdowns |
| `src/spain_housing/config.py` | Configuration loading and conversion into validated models |
| `src/spain_housing/cli.py` | Thin entry points for prepare/build/evaluate workflows |
| `apps/streamlit_app.py` | Thin launcher for the package's UI |
| `data/raw/`, `data/processed/`, `data/releases/` | Local data artifacts; large/restricted files outside ordinary Git |
| `data/manifests/` | Git-tracked release references, hashes and provenance where permitted |
| `outputs/` | Exported resolved scenarios and results; normally excluded from Git |
| `tests/finance/`, `tests/data/`, `tests/application/` | Meaningful module and integration checks |
| `tests/fixtures/` | Small, clearly synthetic test data or permitted source examples |

Suggested initial implementation files:

- `models/`: `scenario.py`, `market.py`, `results.py`, `contracts.py`.
- `finance/`: `savings.py`, `mortgage.py`, `costs.py`, `purchase.py`.
- `markets/`: `repository.py`, `projections.py`, `geography.py`.
- `ingestion/`: `adapters/`, `normalize.py`, `validate.py`, `release.py`.
- `application/`: `prepare.py`, `evaluate.py`, `modes.py`, `compare.py`.

Avoid a miscellaneous `utils.py` for financial or market rules. Place each rule with the module that owns it. An occasional shared primitive can be introduced when a real need exists.

## 4. Module boundaries

### Allowed dependencies

| Component | May depend on | Must not depend on |
|---|---|---|
| `models` | Standard library and validation library | UI, providers, financial implementation |
| `finance` | Models and numeric helpers | Streamlit, provider API formats, file paths, geographic geometry |
| `markets` | Models and storage/geographic tools | UI or acquisition at query time |
| `ingestion` | Models, source clients and normalisation/storage tools | UI or affordability calculations |
| `application` | Models, finance and market-access contracts | Streamlit session state or specific raw-source layouts |
| `ui` / CLI | Application services, models and configuration | Independent copies of financial rules |

Entrypoints construct concrete providers/settings and pass them into application services. Define a small market-access interface and a purchase-cost interface at the changeable boundaries. Use normal typed functions elsewhere; interfaces do not require deep inheritance hierarchies.

### Main data flow

1. An adapter reads a provider source; the release builder writes standardised observations and a validated manifest.
2. A market repository opens one explicit dataset release and selects observations by location, period and segment, returning values with provenance or explicit missing-data status.
3. The application prepares monthly income, rent, expense and debt inputs. Market projections convert observed market values into scenario-time values under the selected policy.
4. The finance module calculates savings and purchase capacity, including `P_max = min(P_savings, P_mortgage)` for the fixed-financing baseline.
5. The application compares capacity with destination property prices and returns structured results.
6. The UI renders those results and assumptions.

The finance module receives a resolved monthly budget; it does not fetch rent or infer a location. Income-timeline and living-stage preparation have one owner, not separate implementations in the UI and CLI.

### Contracts to establish early

- `Scenario`: incomes, contributors/borrowers, living stages, dates, financial assumptions, desired property and geographic-mode settings.
- `MarketQuery`: location, period, metric and property/rental segment.
- `MarketObservation`: value, unit, statistic, period, source and quality/provenance.
- `PreparedMonthlyBudget`: the resolved monthly cash flows used by the savings engine.
- `SavingsResult` / `PurchaseResult`: paths, capacity limits and binding constraint.
- `LocationResult`: computed indicators, missing/invalid statuses and supporting observations.
- `RunResult`: results plus resolved scenario, dataset-release ID, schema version and model/code version.

Missing information is indicator-specific. For example, missing purchase-price data prevents affordable-area calculation but need not prevent a budget calculation if rental data is adequate. Missing room rent affects scenarios requiring rooms. An unviable cash-flow path must not be exported as an ordinary affordable case. Never convert missing values into zero-valued prices.

## 5. Implementation phases for Codex

Each phase delivers a usable result and preserves the existing contracts. Add checks with the component they verify; do not postpone all validation to the final phase. Complete each phase in reviewable commits and update the relevant documentation.

### Phase 1 — Foundations and coverage audit

**Responsibility:** establish the minimal package, contracts, configuration conventions and realistic data scope.

Deliver:

- Installable package, tooling/lockfile and documented commands.
- Validated scenario and observation models with explicit dates, units and separate saving/buying locations.
- A small synthetic dataset for deterministic development, clearly identified as synthetic.
- A coverage audit of roughly 10–15 contrasting cities and some surroundings, prioritising room-rent availability.
- A decision on the initial geographic resolution, supported property/rental segments and permitted acquisition routes.

**Done when:** an example scenario loads and validates, and data feasibility is documented with enough concrete source examples to avoid designing against an imaginary schema.

### Phase 2 — Financial engine

**Responsibility:** implement correct calculations independent of real data providers and the UI.

Deliver:

- Monthly savings with negative cash-flow handling and retained reserve.
- Mortgage-payment and maximum-loan calculations.
- A replaceable purchase-cost function, initially the proportional allowance.
- The fixed-financing purchase-capacity calculation and binding-bottleneck explanation.
- Target-property cash/payment requirements and shortfalls.

**Done when:** hand-checkable savings-limited, income-limited, staged-rent, debt and zero-interest examples produce the expected results. Calculations can run on prepared monthly inputs without network or geographic dependencies.

### Phase 3 — Pilot data release

**Responsibility:** turn accessible source material into a trustworthy local market snapshot.

Deliver:

- Only the source adapters needed for the pilot; traceable manually curated tables are acceptable where a report lacks bulk access.
- Normalised prices/rents and geographic identifiers, observation periods and segmentation.
- Boundaries at the same geographic level as the price data.
- Quality and coverage reports, hashes, manifests and an immutable pilot release.
- A repository implementation that reads prepared releases and returns explicit missing-data status.

**Done when:** the selected pilot locations can be queried consistently, provenance is retained, and unsupported locations/segments remain explicitly missing. Public/provider access assumptions have been validated.

Phase 2 and Phase 3 are logically independent after the contracts in Phase 1; neither should be blocked by implementing a map.

### Phase 4 — Scenario evaluation and CLI

**Responsibility:** assemble the modules into the first complete local/local workflow.

Deliver:

- One service callable from Python and the CLI.
- Monthly preparation of salary milestones, living stages and market costs.
- Explicit frozen-market and configurable-growth policies; never mix future income with current prices silently.
- Local/local orchestration, destination market comparison and all map indicators.
- Per-location statuses and explanations.
- JSON/CSV exports with resolved inputs and dataset/model identifiers.

**Done when:** one scenario evaluates the pilot locations end to end using real observations, and an exported run can be reproduced from its saved inputs and release. Dates and saving/buying locations are explicit even though only local/local mode is exposed.

### Phase 5 — Interactive map MVP

**Responsibility:** build the user workflow around the tested evaluator.

Deliver:

- Streamlit controls, including income milestones and multiple living stages.
- A PyDeck polygon map with selectable indicators and meaningful legends.
- Location selection showing limits, bottleneck, savings path, target affordability and source periods.
- Clear missing/estimated/unviable states and scenario import/export.
- Caching of loaded releases and repeated calculations using their true inputs/version identifiers.

**Done when:** changing assumptions recomputes the pilot map without collecting new data; UI and CLI produce equivalent results for the same resolved scenario.

### Phase 6 — Broader coverage and reproducible MVP

**Responsibility:** expand data coverage without changing the core financial engine and make normal operation reliable.

Deliver:

- More locations and available segments, based on observed coverage rather than a promise of every municipality.
- Documented fallback/estimation rules and source-update workflow.
- Practical performance improvements guided by measurement.
- A documented environment, supported commands, data retrieval/release steps and export/reproduction workflow.
- Targeted integration and UI smoke checks, including partial coverage.

**Done when:** another environment can run the supported MVP from its documented code, configuration and data release. Source/schema failures are diagnosed during release preparation instead of silently changing map results.

### Phase 7 — National municipal geography with synthetic market inputs

Execution guide: [PHASE_7_map_geo.md](phases/PHASE_7_map_geo.md).

Implemented independent canonical/display contracts, dataset-v2 composition,
retained official national identities/boundaries, deterministic complete/partial
synthetic economic inputs, atlas-superset UI and measured bounded evaluation.
Financial rules, old releases and original fixture demos remain unchanged.

Status: **national map available; browser performance goal remains unverified**.
The national atlas retains the inspected Bellver/Prullans overlap unchanged;
the selected display assigns its positive-area intersection to explicit neutral
context under the user's approved policy. All 8,132 municipalities and the
required territories remain represented. National backend, browser, installed
and two-root artifact evidence are tracked in [Phase 7 progress](progress/PHASE_7.md);
commands and actual local artifact availability are in [geography](GEOGRAPHY.md).
Do not equate synthetic economics with observed national affordability. The
software-rendered browser's initial confirmed image exceeds the 15 s goal;
backend timings do not establish that browser goal. Transfer of the prepared
local bundle to a durable off-machine destination is still required for backup.

## 6. Later phases and extension points

Keep the following order of major extensions; detailed model refinements can be implemented as smaller independent changes when prioritised.

| Later work | Modules extended | Core preparation now |
|---|---|---|
| **Save somewhere fixed, buy elsewhere — first essential extension** | `application/modes.py` and UI controls | Independent saving/buying inputs; reusable savings result; purchase-date borrower income explicit |
| **Salary realism by profession and location** | Add `employment/` data/context module, ingestion adapters, application result context and a map layer | User-assumed income independent of market context; observations carry geographic/time definitions |
| **Historical simulations and evolving maps — last major extension** | Historical adapters, market selection/projection policies, temporal orchestration and UI time controls | Explicit periods/dates, versioned releases, nominal/real basis, geographic versions and no implicit latest-data selection |

A fixed-saving-place mode must document the income assumption at purchase: moving destination must not silently retain or change salary. Initially it can use an explicit user-specified trajectory, independently of the later salary-context feature.

Other deferred refinements from the brief:

- Variable down payments: replace/extend the purchase solver behind its existing boundary.
- Detailed regional purchase costs: add policy data and cost implementations, preserving numerical ownership in the cost model.
- Gross-to-net conversion: add a conversion module feeding the income model.
- Savings returns: extend the savings model through explicit assumptions.
- Ownership-cost checks and richer property segmentation: extend budgets/market queries and results.
- Provider APIs, DuckDB, DVC or Hydra: introduce only when a demonstrated acquisition, storage, querying or batch-execution need justifies them.

Historical work should distinguish a historical path, a frozen historical comparison and an as-of forecast, and audit historical room coverage before promising it. Adding a time slider alone is not sufficient.

## 7. Codex implementation guardrails

1. Work within the current phase; do not implement placeholder future features beyond their required contracts.
2. Keep business rules in their owning modules and call the same evaluator from every entry point.
3. Preserve units, dates, geography, assumptions and provenance through the pipeline.
4. Validate one complete small workflow before scaling coverage or optimising.
5. Keep acquisition reproducibility distinct from affordability reproducibility.
6. Version intentional scenario/data schema changes; update examples and saved-run handling accordingly.
7. If real source data conflicts with the planned contract, document the evidence and make the smallest coherent change rather than adding source-specific exceptions throughout the engine.
