# PHASE 1 — Foundations and Data Feasibility

Implementation guide for an autonomous Codex run. Prepared 4 October 2026.

**Outcome:** an installable, validated and mechanically constrained foundation for the Spain housing affordability simulator, together with an evidence-based pilot data plan. Phase 1 does not deliver the financial calculator or interactive map.

## 0. Start here

Read this section first, then the relevant sections below as each milestone begins.

1. Inspect the actual repository, working tree, existing instructions and recent commits. Preserve existing user work.
2. Read the project brief and implementation plan. Prefer their canonical repository copies: `docs/PROJECT_BRIEF.md` and `docs/IMPLEMENTATION_PLAN.md`. The supplied originals are named `SPAIN_HOUSING_PROJECT_BRIEF.md` and `SPAIN_HOUSING_IMPLEMENTATION_PLAN.md`.
3. If resuming, read `docs/progress/PHASE_1.md`, verify its claims against files and Git history, and run the existing baseline checks.
4. Work through milestones M1–M6 in Section 10. Continue autonomously between them; a milestone is a verification checkpoint, not a permission checkpoint.
5. Finish only when the acceptance criteria in Section 12 have evidence, or explicitly report a material blocker and incomplete criteria.

### Authority and interpretation

- Follow current user instructions and applicable repository instructions. This guide supplies detailed Phase 1 implementation choices where the earlier plans left choices open.
- The project brief owns product meaning and financial semantics; the implementation plan owns component boundaries; this guide owns the initial deliverables and verification process.
- Do not silently change product meaning or broaden the phase to resolve a conflict. Make routine implementation choices independently, record material decisions concisely, and escalate only decisions that materially change the user's goal or require unavailable authorization.
- Do not create `AGENTS.md` solely for this task. Keep project knowledge in the requested documents and concise progress record; respect any existing applicable instruction files.
- Use a single Codex implementation workflow unless the user authorizes delegation. This guide does not require additional agents.

### Autonomous execution mandate

Implement the whole phase, rather than stopping after scaffolding or a partial schema. Local implementation, tests, documentation, public-source inspection and reviewable local commits are within scope. Do not publish/deploy the app, push/merge remotely, contact providers, purchase data or introduce credentials as part of this phase.

## 1. Scope and success boundary

### Required

- A Python package with the agreed module ownership and clean installation.
- Validated scenario, market-observation and small result/interface contracts.
- Deterministic configuration loading and a working scenario-validation CLI.
- Clearly synthetic development fixtures, isolated from observed market data.
- A bounded coverage audit of purchase prices, whole-home rents and room rents, including geographic boundaries and access conditions.
- Enforced import boundaries, formatting, linting, type checking, meaningful tests and a repeatable quality command.
- Minimal setup/architecture documentation and a resumable progress record.

### Deferred

- Monthly savings accumulation, mortgage amortisation and `P_max` computation: Phase 2.
- Production collectors, complete market datasets and release-building workflows: Phase 3.
- The complete location evaluator, projections over monthly market series and geographic-mode execution: Phase 4.
- Streamlit, PyDeck, rendering, hosting and deployment: Phase 5 or later.
- Salary inference, historical reconstruction, detailed taxes, variable down-payment optimisation, gross-to-net conversion, savings returns and provider/API integrations beyond audit examples.

Small calendar utilities, validation helpers and reading a few source examples are allowed. A full financial timeline builder or provider framework is not necessary to validate a scenario.

**Do not create fake implementations that return plausible budgets, zero-filled results or placeholder market prices.** An empty reserved package namespace is acceptable; pretend functionality is not.

## 2. Initial tooling decisions

These defaults make the guide executable without another design round. Preserve a compatible existing setup rather than replacing it merely for consistency.

| Area | Default for a new repository |
|---|---|
| Python | Python 3.12 development baseline; explicit supported version range |
| Package / import name | Distribution `spain-housing`; import package `spain_housing` |
| Layout | Installable `src/` layout |
| Dependency manager | `uv`, one committed `uv.lock` |
| Build backend | A standard backend, such as Hatchling; declare it in `pyproject.toml` |
| Runtime dependencies | Pydantic 2 and PyYAML; standard library for CLI and simple fixtures |
| Development dependencies | pytest, Ruff, mypy, PyYAML type stubs, Import Linter |
| CLI | Standard-library argparse; entry point `spain-housing` |
| Configuration | YAML defaults/examples, Pydantic validation, JSON normalised export |

Do not install pandas, GeoPandas, NumPy, Streamlit, PyDeck, Hydra, DVC or a database solely to prepare future phases. Add only dependencies needed by an implemented Phase 1 requirement. Record compatibility issues and exact locked versions; do not choose pre-release dependencies without a concrete need.

Configure mypy in strict mode for package code and use Ruff as the single formatter/import-style tool, with normal correctness and import checks enabled. Keep tool settings in `pyproject.toml`; do not add overlapping Black/isort configurations. Fix diagnostics rather than suppressing whole directories. Target the chosen Python baseline consistently across the tools.

Use project-scoped environments. Do not modify a global Python installation or generate several competing lockfiles. A clean install must install the package, not merely its dependencies. Tests must import the installed package; do not patch `sys.path` or rely on `PYTHONPATH=src` to hide packaging mistakes.

## 3. Repository layout and code ownership

Use this ownership map. Existing equivalent paths may be retained with a documented mapping; do not maintain duplicate canonical documents or implementations.

| Path | Phase 1 responsibility |
|---|---|
| `pyproject.toml`, `uv.lock`, `.python-version` | Installation, tooling, build and entry point |
| `README.md` | Short project map and verified setup/validation commands |
| `docs/PROJECT_BRIEF.md` | Canonical product specification, imported once from the supplied brief |
| `docs/IMPLEMENTATION_PLAN.md` | Canonical overall architecture/roadmap |
| `docs/phases/PHASE_1_foundations.md` | This phase guide |
| `docs/ARCHITECTURE.md` | Concise ownership/dependency explanation and contract conventions |
| `docs/DATA_COVERAGE.md` | Audit conclusions and pilot recommendation; links to canonical audit rows |
| `docs/progress/PHASE_1.md` | Current milestone state, evidence, decisions, blockers and next action |
| `configs/defaults.yaml` | Single source of economic default values |
| `configs/scenarios/` | Valid, documented example scenarios |
| `configs/sources/catalog.yaml` | Source candidates and access notes; not a functioning collection framework |
| `src/spain_housing/models/` | Shared typed contracts, field/cross-field validation and calendar conventions |
| `src/spain_housing/config.py` | Safe loading, merge semantics and validation delegation |
| `src/spain_housing/cli.py` | Thin scenario-validation entry point |
| `src/spain_housing/finance/` | Reserved namespace; numerical implementation deferred |
| `src/spain_housing/markets/` | Reserved namespace; storage/geographic implementation deferred |
| `src/spain_housing/ingestion/` | Audit validation helper only if needed; production adapters deferred |
| `src/spain_housing/application/` | Reserved namespace; orchestration deferred |
| `src/spain_housing/ui/` | Reserved namespace; interface deferred |
| `src/spain_housing/py.typed` | Package typing marker |
| `tests/` | Schema, configuration, CLI, packaging and architecture checks |
| `tests/fixtures/synthetic/` | Tiny synthetic observations and contract examples |
| `data/manifests/coverage_audit.csv` | Canonical structured audit evidence |
| `data/raw/`, `data/processed/`, `data/releases/` | Documented storage locations; create only as needed, ignore large/restricted contents |
| `scripts/check.sh` | One thin wrapper around canonical quality commands |

Suggested model files: `scenario.py`, `market.py`, `results.py`, `contracts.py`. Add `base.py` or `types.py` only for genuinely shared validation/types. Avoid one file per field and avoid a sprawling model file containing configuration I/O, source parsing and calculations.

Keep `__init__.py` exports small. Importing the package must not read files, create directories, make network requests or import every future component.

### Dependency rules

The table concerns direct internal imports. For the foundational components, also prevent forbidden dependencies reached indirectly.

| Component | Allowed direct internal dependencies |
|---|---|
| `models` | Other model modules only |
| `finance` | `models` |
| `markets` | `models` |
| `ingestion` | `models`; future normalisation/storage helpers with documented ownership |
| `application` | `models`, `finance`, `markets` |
| `config` | `models` |
| `ui` | `models`, `application`; runtime assembly at the entry point |
| CLI / future app launcher | Configuration and required service modules; no duplicated rules |

- Finance remains independent of UI, providers, configuration-file formats and geography.
- Models must not import financial implementations, source adapters, configuration loaders or application services.
- Market queries must never acquire source data as a side effect.
- Future adapters normalise into the shared observation contract; provider field names stop at their boundary.
- Runtime assembly belongs at entry points, not in global registries or model validators.

Configure Import Linter contracts for these internal boundaries in `pyproject.toml`. Use independence/forbidden contracts where appropriate; do not force the graph into one linear hierarchy because ingestion and numerical finance are independent branches. When forbidding direct UI-to-finance imports, allow the legitimate indirect UI → application → finance path. Do not bypass checks using dynamic imports, broad ignore lists or re-exports.

Prove the boundary checker detects at least one forbidden import using a disposable test package or temporary copy, never by leaving a violation in production code. Empty namespaces alone are not evidence of enforcement.

## 4. Scenario contract and validation semantics

### 4.1 Essential fields

Use one canonical `Scenario` contract with nested typed records. Names below are recommended; if equivalent names are used, keep examples, CLI and documentation consistent.

| Field / record | Semantics |
|---|---|
| `schema_version` | Explicit initial scenario format version, e.g. `1` |
| `start_month` | First day of the first saving month, an explicit calendar date |
| `saving_months` | Positive integer; proposed default 84 |
| Participants | Unique stable IDs; each participant's net annual income path, monthly debt path and starting savings contribution |
| `saver_ids` | Participants whose income, debts and starting contributions enter the saving pool |
| `borrower_ids` | Participants whose income/debts support the eventual mortgage; independent of rent sharing |
| Living stages | Arrangement, start/end month offsets, household rent share, rental area/segment where relevant |
| Household non-housing expense path | Monthly amounts borne by the saving pool; do not duplicate each participant's separately represented debts |
| `retained_reserve_eur` | Non-negative amount excluded from purchase funds later |
| Mortgage assumptions | Financed fraction, maximum total-debt ratio, term in years, annual nominal interest rate |
| Purchase-cost assumptions | Initial proportional allowance; give it a named policy type such as `proportional` |
| Target property | Type and positive target floor area, independent of rental area |
| Market policy | Explicit frozen-market or growth-assumption policy, including market base period |
| Location plan | Separate saving and buying references/bindings, even in local/local mode |

Participant membership is fixed across the initial scenario horizon. Do not infer a participant from a sharing fraction. Time-varying household membership can be a later contract extension if needed.

In a joint scenario, the pool's expenses represent the actual combined burden, not one person's expenses multiplied implicitly. A participant outside `saver_ids` does not silently add income or savings. Starting contributions identify committed savings amounts, not everyone's total wealth. Reserve amounts may exceed starting contributions because savings can grow; this is a valid input.

### 4.2 Time and paths

- Stage/path offsets are integer months relative to `start_month`.
- Living stages use half-open intervals `[start_month_offset, end_month_offset)`, exactly cover `[0, saving_months)`, and have no gaps or overlap.
- Derive the purchase month as `start_month + saving_months` calendar months. Do not accept an independent purchase date that can disagree with the horizon.
- Store that derived value as a property or validation-report field; do not create a second editable source of truth. Normalised scenario exports must remain accepted by the scenario loader.
- Amount paths have ordered, unique milestones; they start at offset 0 and allow milestones beyond the purchase month.
- Net income values are annual euros; debt and expense values are monthly euros. The later engine converts annual net income to monthly income by dividing by 12.
- Choose and document `linear` or `step` interpolation, plus a final-value plateau. Initial default: linear income interpolation; step paths are appropriate for changing debts/expenses. Only validate the representation now; defer expansion and arithmetic.
- Accept zero income and zero debt. Reject negative amounts, non-finite values and inconsistent units.
- Do not reject a structurally valid scenario merely because it will produce negative cash flow or an unaffordable house later.

### 4.3 Numeric and structural constraints

- Monetary inputs are finite EUR amounts. Use a consistent representation, such as finite floats for this modelling application, and document rounding as presentation-only.
- Fractions use decimal form: `0.35`, not `35` or `"35%"`.
- Financed fraction: greater than zero and at most one for the initial fixed-fraction policy.
- Debt ratio: from zero to one. Term: positive integer years. Nominal interest: non-negative, explicitly supplied; zero is valid.
- Purchase-cost allowance: non-negative. Rent share: greater than zero and at most one.
- Property/rental areas: finite and positive when supplied; flat stages require the necessary rental-area/segment input. Room stages do not require a flat's total area.
- Require non-empty participant sets, unique IDs and valid referenced saver/borrower IDs. Do not require the two ID sets to be identical.
- Reject unknown fields at every public model boundary to catch misspellings.
- Reject booleans and numeric strings in numeric/ID fields. Accept ordinary YAML/JSON number types where semantically correct. Parse documented ISO dates explicitly; do not blindly enable global strictness in a way that rejects valid file dates or accepts unwanted coercions.
- Normalise into fresh validated objects; do not mutate shared defaults or input dictionaries.

### 4.4 Location and extension readiness

Represent geographic references with both level and string code, preserving leading zeros. Separate `saving_location` and `buying_location` internally. A mapped-location binding is appropriate for local/local evaluation; an explicit reference is appropriate for a fixed saving place.

The Phase 1 contract must be able to represent these concepts without executing them:

1. Local/local mode with independent bindings resolved to the same place later.
2. A fixed saving place and mapped buying destinations.
3. An explicit historical start/base date, without selecting any historical dataset automatically.

Document that only local/local evaluation will be implemented first. Validating a future-mode request is not a claim that it can already be evaluated. Do not introduce hard-coded `today`, implicit `latest`, a fixed list of cities or a salary database inside the scenario model.

### 4.5 Financial semantics to preserve, not implement

The future fixed-financing engine must calculate:

```text
P_savings = usable_savings / ((1 - financed_fraction) + purchase_cost_fraction)
M_max = max(0, debt_ratio × net_monthly_borrower_income - other_monthly_debt)
P_mortgage = maximum_loan(M_max, nominal_rate, term) / financed_fraction
P_max = min(P_savings, P_mortgage)
```

The initial 30% cash allowance, 80% financing, 35% debt limit and 25-year term are configurable modelling assumptions. The purchase-cost allowance is not a universal tax rate. Sharing rent does not make a person a borrower. Do not implement these equations or duplicate them in configuration validators during Phase 1.

## 5. Market and output contracts

### 5.1 Observation/query schema

An observation describes a published statistic or explicitly modelled estimate; it is not assumed to be a raw property listing.

| Field group | Required meaning |
|---|---|
| Geography | Code as string, level and boundary-version reference where known |
| Time | Observation period start/end, retrieval timestamp and source release/methodology version where known |
| Measure | Metric, finite positive value, unit and statistic |
| Market meaning | Asking, transaction, valuation or tax-declared basis; rental-contract category where available |
| Segmentation | Flat/house/room/pooled category; size/bedroom band where provided |
| Evidence | Source ID/URL, observed/estimated/synthetic kind and quality notes |
| Sample information | Positive count if known; unknown stays absent, not invented |
| Estimates | Documented method/reference when estimated |

Support at least purchase €/m², whole-home rent €/m²/month, whole-home rent €/month and room rent €/month, with metric/unit compatibility validation. Keep mean, median and percentiles distinguishable. Do not call a published city benchmark a size-specific flat estimate unless its segmentation supports that claim.

Use period intervals consistently; half-open intervals are recommended. Period end must follow start. Retrieval time can be later than observation time. Do not demand that every metric has identical dates; represent mismatches so later selection policies can handle them.

A `MarketQuery` includes explicit geography, period, metric and optional property segment. A lookup result distinguishes available, missing and unsupported data; missing is not a zero-valued observation. Synthetic values have unmistakable source/kind markers and must not be presented as real published evidence.

### 5.2 Small interfaces and result records

Define typed, minimal contracts for:

- `MarketData`: query → observation/lookup result.
- `PurchaseCostPolicy`: price + purchase context → cost breakdown.
- `PreparedMonthlyBudget`: dated income/rent/expense/debt inputs for the future numerical engine.
- `SavingsResult`, `PurchaseResult`, `LocationResult`, `RunResult`: future numerical outputs, individual metric statuses and reproducibility metadata.

Use a small `Protocol` at replaceable market/cost boundaries; abstract method declarations are allowed, fake concrete implementations are not. Inputs/context types belong with shared contracts so models do not import finance or application implementations.

Result records should support both capacity limits, a binding-bottleneck label, calculation viability, optional unavailable geographic indicators and provenance. Define only fields needed by the brief, keeping unavailable/error states distinct from numeric zero. No generic plugin registry, universal workflow class or nested hierarchy is needed.

A run's dataset-release ID, resolved scenario, schema version and model/code version belong in run metadata. Environment paths and credentials do not belong in economic assumptions. Persisting all these run artifacts is a later workflow; Phase 1 validates the records and round trips a small synthetic example.

## 6. Configuration and CLI implementation

### 6.1 Loading and precedence

`config.py` owns loading and merge behaviour. Models own validation. CLI commands delegate to both.

1. Load explicit defaults and a scenario YAML/JSON file using safe loaders. Reject duplicate keys, including nested duplicates, before information is silently discarded.
2. Recursively merge mappings: defaults first, scenario values second. Lists replace whole lists; never merge participants or stages by position. Explicit nulls must not fall back silently to defaults.
3. Validate the final object. Unknown keys and inappropriate nulls fail with field-specific messages.
4. Serialize the resolved scenario deterministically as JSON with dates/enums converted through the model's serializer and stable key ordering.

No interpolation of arbitrary environment variables, Python expressions or YAML object constructors. No network operations. Runtime paths are passed explicitly or through a documented runtime setting, not inferred by walking user directories.

Economic defaults live in `configs/defaults.yaml`, not simultaneously in YAML, CLI parser arguments and model constructors. Constructors may provide structural constants, such as schema tags, but should not conceal missing economic inputs. The nominal interest rate must be explicit in each valid example; an example's rate is illustrative, not a verified live default.

### 6.2 Minimum CLI

Implement only:

```bash
spain-housing --help
spain-housing validate-scenario --defaults PATH --scenario PATH
spain-housing validate-scenario --defaults PATH --scenario PATH --json
```

The text form summarises successful validation, horizon, derived purchase month and declared mode. The JSON form writes only the normalised scenario to stdout so it can be loaded again; diagnostic text goes to stderr.

- Success: exit code 0.
- Invalid user/configuration input or unreadable source file: non-zero, conventionally 2, with a concise explanation.
- Unexpected programming errors: non-zero; do not hide them by returning success.
- Resolve explicit file paths normally and support operation outside the repository working directory after installation.
- Do not add `evaluate`, `collect`, `map` or other non-functional commands advertising later work.

Three valid example scenarios are required: room-only, staged room/flat/shared-flat, and joint saving with separately specified borrowers. Store common economic defaults once. Keep deliberately invalid cases in tests rather than mixing them with user-facing examples.

## 7. Synthetic fixtures and bounded source audit

### 7.1 Synthetic fixtures

Create a tiny deterministic fixture covering at least three locations and the main metrics. At least one missing metric should be intentional. Values must be simple, plausible test numbers with `synthetic` evidence markers, not claimed observations.

Real administrative codes may be used as join identifiers if clearly labelled; that does not make the fixture's prices real. Synthetic inputs and manually constructed expected records must not enter the observed audit or production dataset directories. Do not download a full boundary dataset solely to give these fixtures polygons; geometry processing is deferred.

### 7.2 Audit sample

Default city sample: Madrid, Barcelona, Valencia, Málaga, Palma, Bilbao, Sevilla, Zaragoza, Valladolid, Salamanca, Jaén and Teruel. Add four contrasting surrounding municipalities, for example Getafe, Badalona, Mislata and Dos Hermanas. Equivalent substitutions are allowed for a documented coverage reason, not solely to avoid reporting gaps.

For every area, assess purchase €/m², whole-home rent and room €/month. Check geographic identifiers and suitable boundary sources. The point is to establish obtainable evidence and resolution, not to create a national collector.

Start with the source candidates in the project brief: Idealista public price/room reports, MIVAU SERPAVI and valuation tables, IGN/CNIG boundaries. Audit primary sources where practical. A third-party article can identify a source but is not proof that its data file/API is obtainable.

### 7.3 Canonical audit evidence

Write `data/manifests/coverage_audit.csv` with at least:

```text
location_name, location_code, geographic_level, metric,
source_id, source_url, accessed_at, observation_period,
access_route, verification_status, value, unit, statistic,
segment, coverage_notes, reuse_status, evidence_scope, next_action
```

Use documented statuses, such as:

- `numeric_verified`: actual source value and its meaning/period checked.
- `publication_verified`: relevant publication exists, but exact numeric/segment access is unresolved.
- `restricted`: access requires credentials, contract or approval not available.
- `unavailable`: source does not provide this metric/area, supported by inspection.
- `not_verified`: attempted verification failed or evidence is insufficient.

Only `numeric_verified` carries a source-verified numeric value. A provider-wide failure may be recorded for multiple locations, but `evidence_scope` must say provider-level; do not imply each location was individually inspected. Missing/blocked audit values remain blank, never zero. Distinguish access failure from evidence that data does not exist.

Record reuse rights as verified, restricted or unknown with evidence; public readability is not proof of permission to redistribute a full dataset. Retain minimal permitted samples/source references. Full source text, large downloads and licensed data are not necessary Phase 1 artifacts.

### 7.4 Bound the research

Use a small number of well-targeted searches/download attempts per source. If a route repeatedly fails, try one materially different legitimate route, document the failure and continue other work. Do not spend the phase repeatedly probing a blocked portal or bypassing a sign-in/access restriction.

Do not contact a provider or buy an API plan. Prepare a concrete pending access question only if it remains necessary for a viable pilot after public alternatives are assessed.

### 7.5 Audit conclusions

`docs/DATA_COVERAGE.md` must summarise, without duplicating every CSV row:

- Supported resolution and candidate pilot locations.
- Which metrics are actually verified and their dates/market definitions.
- Room-rent gaps, source freshness and segmentation limits.
- Advertised versus tax-declared rents and valuation versus asking prices.
- Access/reuse limitations and any unverified claims.
- Whether Phase 3 can proceed immediately, with restricted coverage, or requires a specific access/data decision.

Do not fill room gaps with an invented universal flat-rent multiplier. Do not label a province statistic as a city observation. A complete, honest audit can conclude that broad coverage is blocked; Phase 1 readiness and Phase 3 data readiness are separate findings.

## 8. Clean-code and redundancy rules

Apply these during implementation, not only during a final cleanup.

1. Each rule has one owner. Validate ratios, IDs, stages and units through the canonical models; do not revalidate them differently in CLI, fixtures and config wrappers.
2. Reuse an existing helper when it has the same semantics. Do not force different meanings into one generic abstraction merely to reduce line count.
3. Prefer clear functions and a few typed records. Introduce classes/interfaces only for real state or replaceable boundaries; no speculative factories, service locators or inheritance trees.
4. Keep functions focused. Split files at coherent ownership boundaries; do not impose arbitrary line-count limits that fragment the code.
5. Use descriptive field names with units. Avoid ambiguous `salary`, `price`, `rate` and positional arrays at public boundaries.
6. Annotate public functions. Limit untyped dictionaries to the raw loading boundary and immediately validate them. Do not silence type errors with project-wide ignores or unexplained casts.
7. Use targeted exceptions and useful error context. No blanket catches, `except: pass`, silent fallbacks or defaults substituting for invalid input.
8. No shared mutable default objects, import-time I/O, hidden global configuration or repeated scenario parsing in multiple modules.
9. Keep documentation about reasons/conventions concise. Do not repeat obvious code in comments, copy entire specifications into every module or generate unused schema artifacts automatically.
10. Remove abandoned code and temporary files belonging to this task. Do not leave `TODO` bodies pretending to implement required functionality. Document actual future scope rather than scattering empty method stubs.
11. Keep production code and test fixtures separate. Do not make public implementation APIs accept fixture-specific exceptions.
12. Before adding a module or dependency, identify its requirement and owner. If neither is clear, it probably does not belong in Phase 1.

## 9. Reliable autonomous execution and recovery

### 9.1 Persistent state

Maintain one concise `docs/progress/PHASE_1.md` rather than several overlapping progress systems. Keep the specifications stable and the progress record current.

Include:

- Current milestone and M1–M6 statuses: not started / in progress / verified / blocked.
- Last verified commit and exact verification commands/results.
- Acceptance IDs A1–A10 with status and evidence links.
- Material decisions: choice, reason, alternatives rejected only where useful.
- Known blockers, source-access failures and exact next action.
- A short completed-milestone history; do not paste full terminal logs.

Evidence can be a test path, command/result, audit row group or relevant diff/commit. A test that exists but was not executed is not passing evidence. A blocked source is not a successful acquisition.

### 9.2 Work loop

For each coherent slice:

1. Identify the relevant requirement, owning module and check.
2. Inspect existing code and make the smallest coherent implementation.
3. Run focused checks, inspect results and repair regressions.
4. Review the diff for duplicated rules, coupling, excess scaffolding and schema drift.
5. Update progress/decision notes and commit a verified checkpoint when feasible.
6. Continue to the next slice without requesting routine confirmations.

Do not mark a milestone verified merely because files exist or a command compiles. Validate its observable behaviour. Do not delete requirements, weaken tests or relax architecture/type checks to manufacture a passing gate. A demonstrated faulty test can be corrected with its reason recorded.

### 9.3 Git discipline

- Inspect `git status` before edits; identify pre-existing changes and leave them intact.
- Use a suitable local topic branch if appropriate. Do not force-switch over user changes or nest another Git repository inside an existing one.
- Commit coherent, verified implementation checkpoints with descriptive messages. Do not commit unrelated user changes using blanket staging.
- Do not reset/clean/stash user work, rewrite history, push or merge as part of this phase.
- If Git identity/commit permission is unavailable, continue implementable local work and report that checkpoint commits could not be created. Do not invent an identity or modify global Git configuration.

### 9.4 Resume after interruption or context compaction

Read the phase's start section, current progress, relevant specs and recent Git history. Verify working-tree state and the last claimed baseline. Continue the recorded next milestone; do not rebuild the scaffold, rename modules again or restart completed research.

Before an anticipated handoff, record partial work and next actions. Prefer a verified checkpoint. If unfinished edits remain, describe them explicitly; do not label the tree clean or tests passing without checking.

### 9.5 Blocker handling

Continue independent work when a source, credential or optional CI route is blocked. Use public alternatives and clearly restricted pilot coverage where honest evidence supports them.

Ask for a decision only when progress genuinely depends on a product/architecture choice outside this guide, required paid/authenticated access, or conflicting requirements that cannot be resolved faithfully. State the concrete issue and completed independent work. An unavailable dependency install or failed packaging gate is an incomplete engineering result, not a reason to claim success based on inspection alone.

Do not run repeatedly failing commands without a new hypothesis. After a few attempts, narrow the failure, try a different justified approach or document the blocker. Once a quality gate passes, repeat it when changes or unresolved concerns justify repetition, not as a time-filling loop.

## 10. Milestones and execution order

### M1 — Inspect, establish scope and package skeleton

- Inventory the repository and discover existing instructions/tooling.
- Put the supplied docs at their canonical paths without redundant copies.
- Initialise the short progress record and capture any pre-existing baseline failures.
- Establish `src/spain_housing`, six core namespaces and packaging/lockfile.
- Add a minimal CLI help command and development/check commands.
- Identify source examples early enough to inform contracts; full audit comes in M5.

**Verify:** locked sync installs the package; CLI help works; package import has no side effects. Commit the coherent scaffold if possible.

### M2 — Scenario models and boundary enforcement

- Implement time/units/participant/stage/mortgage/property/location records.
- Add essential cross-field validation and deterministic serialization.
- Encode import boundaries with Import Linter and prove a forbidden edge is detected.
- Write focused scenario validation tests, including extension-readiness cases.

**Verify:** valid scenarios are accepted; malformed structure is rejected; independent saving/buying representation and old calendar dates need no different schema; boundary checks pass and have demonstrated failure sensitivity.

### M3 — Configuration, examples and validation CLI

- Implement safe duplicate-aware YAML/JSON loading and mapping/list merge rules.
- Implement canonical defaults and the three user-facing example scenarios.
- Wire the validation command, JSON output and informative failure behaviour.

**Verify:** each example validates; JSON output reloads without information loss; defaults are unchanged after sequential loads; execution works with explicit paths outside the repository directory; bad files yield non-zero status.

### M4 — Market/result contracts and fixtures

- Implement market queries, observations, lookup states, minimal cost/market protocols and result records.
- Add deterministic synthetic fixtures with a deliberate missing metric.
- Validate metric/unit/provenance/status consistency and run-metadata round trips.
- Refine the ownership documentation around concrete code.

**Verify:** observed, estimated and synthetic examples remain distinguishable; missing metrics stay non-numeric; key records serialize/validate consistently; no numerical calculator or fake provider was added.

### M5 — Bounded coverage audit and pilot recommendation

- Audit the selected cities/surroundings across the three required housing metrics.
- Record actual evidence, dates, source meaning, access and reuse status in the canonical CSV.
- Check identifiers/boundary sources; propose the defensible initial resolution and pilot.
- State data readiness and concrete unresolved decisions in the audit summary.

**Verify:** all sampled area/metric combinations have an honest status; verified values have primary evidence; blocked/unknown values are blank and labelled; source conclusions match evidence rather than sample fixture values.

### M6 — Integration review, clean installation and handoff

- Run the full quality gate and installed-package/CLI smoke checks.
- Review public contracts and dependencies against the brief and upcoming Phase 2/3 needs.
- Remove duplicated/unused implementation artifacts, fix documentation commands and record remaining limitations.
- Produce the completed acceptance/evidence record and final handoff.

**Verify:** Section 12 is satisfied or incomplete criteria are explicitly named. Run no later phase automatically.

## 11. Verification gate and meaningful checks

Provide `scripts/check.sh` as a thin, fail-fast wrapper. It must run the same commands documented in the README; it must not repair files or update the lockfile secretly.

For the default toolchain, the gate should cover:

```bash
uv lock --check
uv run --locked ruff format --check .
uv run --locked ruff check .
uv run --locked mypy src/spain_housing
uv run --locked lint-imports
uv run --locked pytest
```

Run the locked environment sync, standard package build and built-wheel installation smoke separately at M1/M6 as appropriate. Use a disposable environment and working directory outside the repository to check the installed import and console script. Editable imports alone do not prove that the wheel is correctly packaged. Build/install tooling may need authorised package-index access; distinguish an environment/network block from a code failure.

Use at least these behaviour checks, preferably grouped/parameterised rather than duplicating similar tests:

| Area | Checks |
|---|---|
| Scenario semantics | Single saver/borrower; joint scenario; shared rent without automatic borrower inclusion |
| Stages and dates | Coverage/gap/overlap; zero/negative horizon; month boundary across years; income target beyond purchase accepted |
| Values | Unknown fields; invalid fractions; non-finite amounts; booleans/numeric strings rejected; zero income/interest accepted |
| Geography/time extensibility | Leading-zero codes survive; independent saving/buying binding; historical date accepted without latest-data lookup |
| Configuration | Duplicate keys rejected; mapping merge/list replacement; no input mutation; missing required interest fails; round trip |
| Market data | Metric/unit mismatch rejected; positive observed values; missing distinct from zero; estimate method and synthetic markers |
| CLI | Valid examples; JSON-only stdout; invalid/missing input non-zero; path operation from another working directory |
| Architecture/package | Forbidden edge sensitivity; internal graph checks; clean installed wheel and no import-time I/O |

CI: reuse existing CI if present. For a GitHub repository, add one small workflow invoking the same locked checks/build, without provider credentials or live housing-source requests. If the hosting platform is unknown, the local gate is sufficient and CI setup is explicitly deferred. Do not introduce another CI stack simply to satisfy a template.

No live data/network dependency in unit tests. Data-source availability is audit evidence, not a flaky automated test. Do not pursue arbitrary coverage percentages or write tests that merely assert the implementation repeats itself.

## 12. Acceptance criteria and completion report

These criteria define Phase 1 completion. Preserve their meaning; record status/evidence in the progress file rather than editing them away.

| ID | Required evidence |
|---|---|
| A1 | Package installs from the lockfile; built wheel imports and console help works outside the repository |
| A2 | Source/document ownership follows Section 3; no duplicated financial/source/configuration rule implementations |
| A3 | Scenario contract covers the brief's essential inputs and validates the structural/unit/time rules |
| A4 | Saving/buying locations and dates are explicit; fixed-place and historical concepts are representable without changing the core scenario shape |
| A5 | Defaults/config merge are deterministic; the three examples validate; normalized JSON reloads; invalid input has useful errors |
| A6 | Typed market/provenance/status and minimum result/interface records work with clearly synthetic fixtures |
| A7 | Import boundaries are enforced; the failure-sensitivity check proves detection; financial/UI/data implementations have not leaked into this phase |
| A8 | Coverage audit and conclusions are evidence-based, including room gaps, dates, access/reuse and geographic resolution |
| A9 | Formatting, lint, types, tests and packaging checks pass; skipped/unavailable checks are explicitly distinguished from passes |
| A10 | README/architecture/progress are current; reproducible commands and Phase 2/3 handoff are clear; own changes are reviewable and checkpointed where possible |

A housing provider being blocked does not automatically prevent A8 if the audit is complete and honest. It may mean Phase 3 needs an access decision or a narrower pilot. Conversely, failure to run the required engineering gate means Phase 1 is incomplete, even if the files look finished.

Final report should be concise and include:

- Overall status: complete, or incomplete with exact acceptance IDs.
- What was implemented and where the important interfaces live.
- Executed verification commands/results and any environment limitations.
- Local checkpoint commits, if available.
- Pilot data recommendation and unresolved access/coverage decisions.
- The next concrete Phase 2/3 starting points; no claim that those phases are implemented.

## 13. Research basis and application to this project

The operational rules above are project-specific choices informed by primary engineering guidance, not a guarantee that a prompt alone makes a long autonomous run reliable.

- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 26 November 2025. Supports incremental changes, persistent progress, clean checkpoints and verified behaviour. Applied here through milestones and a resume record, without copying its web-app harness or requiring multiple agents.
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/), 11 February 2026. Supports navigable repository knowledge and mechanically enforced architectural constraints. Applied here through ownership rules, Import Linter and a concise documentation map, rather than a large instruction hierarchy.
- [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex), 23 February 2026. Supports explicit scope, checkpointed acceptance criteria, verification/repair and inspectable execution state. Applied here by the phase gate and evidence-backed status, rather than by copying the experiment's run duration or scale.
- [Pydantic strict-mode documentation](https://docs.pydantic.dev/latest/concepts/strict_mode/). Informs deliberate boundary validation and the difference between JSON/file date parsing and strict numeric validation.
- [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/). Informs committed lockfiles, locked checks and actual package installation.
- [Import Linter contract documentation](https://import-linter.readthedocs.io/en/v2.5.2/contract_types.html) and [current project](https://github.com/seddonym/import-linter). Supports enforceable internal dependency contracts; verify configuration against the version selected by the implementation lockfile.
