# PHASE 4 — Scenario Evaluation and CLI

Implementation guide for an autonomous Codex run. Prepared 7 October 2026.

**Outcome:** one reusable application service evaluates a resolved scenario across the pilot municipalities, prepares explainable monthly budgets, calls the existing financial engine, compares capacity with local housing prices, and exports a reproducible run through a thin CLI. The first exposed geographic mode is local/local. The architecture must already permit reusing a saving calculation when buying somewhere else.

**Repository basis:** [imendezval/SpanishHousing](https://github.com/imendezval/SpanishHousing), inspected at **3038f00c93075bd972bb1bf74add3d5478c9b8a5**. This includes Phase 3's offline dataset implementation and its honest blocked-market handoff. Intended guide location: **docs/phases/PHASE_4_scenario_CLI.md**. Inspect the current checkout; do not reset it to this commit.

## 0. Start here

1. Inspect applicable repository instructions, the working tree, recent commits and existing user changes.
2. Read **docs/PROJECT_BRIEF.md**, **docs/IMPLEMENTATION_PLAN.md**, **docs/ARCHITECTURE.md**, **docs/DATA_ACCESS.md**, and **docs/progress/PHASE_2.md** and **PHASE_3.md**. Read supplied earlier guides where present; do not recreate missing untracked guides.
3. Inspect **models/scenario.py**, **models/results.py**, **models/contracts.py**, **models/dataset.py**, the public financial API, **markets/repository.py**, **config.py**, **cli.py**, and existing examples/tests/import contracts.
4. Read Sections 3–10 before adding application code: they settle the preparation, selection, projection, status and export decisions.
5. Execute M1–M6 in Section 11. Continue between milestones without routine confirmation; keep **docs/progress/PHASE_4.md** current.
6. Finish against A1–A12 in Section 13. Distinguish verified engineering from integration with permitted observed market data.

The current user request and applicable repository instructions take precedence. The project brief owns product meaning; the implementation plan owns responsibilities; this guide supplies the Phase 4 decisions left open there. Ordinary implementation choices are the agent's responsibility. Record material decisions and ask only about a genuine blocker or a proposed change to the intended project.

This guide authorizes implementation, local checks, documentation and scoped local commits. Do not push, merge, deploy, contact providers or initiate paid/account access. Respect existing instructions and user-owned files. Do not create an agent service, a new AGENTS.md, or a parallel execution framework for this phase.

## 1. Verified baseline and inherited readiness

### 1.1 What is implemented

| Component | State at the reviewed commit | Phase 4 use |
|---|---|---|
| Scenario/configuration | Frozen typed records; explicit month, horizon, participant sets, living stages, market assumptions and independent location bindings | Expand these inputs, preserving the loader's merge semantics |
| Financial engine | Signed monthly savings, permanent exhaustion detection, mortgage capacity, proportional purchase costs, fixed-financing capacity and target diagnostics | Call its public functions; do not duplicate formulas |
| Dataset pipeline | Retained-input normalization, official-code reconciliation, geometry checks, hashes and immutable release publication | Consume prepared releases; no acquisition during evaluation |
| Shared storage | One release parser/verifier/writer | Remains behind the market repository |
| SnapshotMarketRepository | Validates an explicit release, then serves immutable exact queries in memory | Supplies MarketData and public metadata |
| Real geography | Four official municipality identities and complete IGN geometries independently verified | Preserve codes, versions and attribution |
| Market observations | Acquisition/local-use permission blocked; no observed market release exists | An inherited real-data blocker, not an excuse to skip engineering |
| Synthetic pilot | Eleven observations, twelve coverage cells; Getafe room intentionally missing | Exercise the real builder/reader and application with explicit opt-in |
| Application/UI | Reserved namespaces | Implement application only; leave rendering to Phase 5 |
| CLI | Scenario validation plus release build/validate/query | Preserve behavior and add evaluation/replay |

**Verification performed while preparing this guide:** `uv sync --locked`, the complete `bash scripts/check.sh`, and `uv build` passed on the recorded commit. The gate ran **227 tests**, strict mypy on 29 source files, Ruff formatting/lint, lock consistency and **eight import contracts**. This preparation did not implement Phase 4. Phase 3's progress record contains its own separate installed-wheel evidence; M1 and M6 must establish current evidence for the implementation checkout.

### 1.2 Readiness must remain honest

Phase 3 reports **engineering verified, real data blocked**. The nine core market cells for Madrid, Barcelona and Jaén have no permitted retained captures; Getafe sale/rent are also blocked, and its room observation is unsourced. Official geography is independently ready. The historical audit, source URLs, permission notes and geography metadata are not a market release.

Complete Phase 4 engineering using the labelled synthetic pilot. An end-to-end observed-market demonstration remains conditional on a permitted release becoming available. Do not reopen the source search indefinitely, copy values from the audit, manufacture observations, or relabel fixture output as observed data. If an authorized observed release is supplied during implementation, run the same workflow against it and retain the evidence.

## 2. Scope and ownership

### 2.1 Required deliverables

- A callable scenario evaluator and a separately callable saving-preparation path.
- One amount-path sampler for income, debt and non-housing expenses.
- Explicit market-profile selection, freshness rules and frozen/growth projections.
- Monthly preparation for room, flat-alone and flat-shared stages, with well-defined household shares.
- Local/local orchestration, borrower finances at purchase, financial capacity and target comparison.
- Typed partial results, supporting market inputs and readable explanations.
- Deterministic JSON/CSV export and replay against an explicit release.
- Thin evaluation/replay CLI commands, documented examples, meaningful tests and an installed-wheel verification.

### 2.2 Exclusions

No Streamlit/PyDeck map, new source acquisition, nationwide coverage expansion, salary dataset, gross-to-net converter, automatic hiring probability, historical reconstruction, regional tax engine, variable-financing solver, investment returns, ownership-cost model, database, DVC or Hydra.

Only local/local is exposed for completed evaluations. `fixed_saving` remains a valid existing scenario configuration; evaluation must report that this mode is deferred, rather than reject the scenario loader or silently run local/local. Do not change `joint_saving.yaml` into a different mode to hide that distinction.

Do not implement a minimum-required-salary solver or time-to-deposit search in this phase. The required map inputs are maximum price, affordable area, target affordability and the financial/source breakdown already specified in the implementation plan.

### 2.3 File responsibilities

| Path | Owns |
|---|---|
| models/scenario.py | Small additive market-selection settings and their validation |
| models/evaluation.py | Shared immutable evaluation metadata, market-use trace and purchase-finance records |
| models/results.py | Necessary result refinements and coherence validation |
| markets/selection.py | Reference-profile eligibility, exact segment choice and freshness |
| markets/projections.py | Pure conversion from a retained observation to scenario-time values |
| markets/repository.py | Existing snapshot reader; one public metadata projection for evaluation |
| application/prepare.py | Amount-path sampling, saver aggregation and complete monthly saving inputs |
| application/modes.py | Independent saving/buying location resolution and supported-mode decision |
| application/compare.py | Capacity-to-market indicators and their statuses |
| application/evaluate.py | Finance orchestration and complete location/run assembly |
| application/export.py | Economic-run JSON/CSV encoding, export and replay comparison helpers |
| application/version.py | Actual calculation-source fingerprint and runtime version evidence |
| cli.py | Argument parsing, configuration loading, snapshot construction and delegation |
| configs/scenarios/ | Explicit supported demonstration scenarios; no hidden fixture assumptions |
| tests/application/ | Preparation, orchestration, partial-result, export and CLI tests |
| docs/progress/PHASE_4.md | Verified checkpoint, decisions, blockers and next action |

These are responsibility boundaries, not a file-count target. Merge a genuinely tiny helper with its owner; split a file only when readability warrants it. Do not add miscellaneous utils, generic repositories, strategy registries or redundant service classes.

### 2.4 Dependency constraints, including indirect imports

- Models depend only on shared models, the standard library and validation tools.
- Finance remains unchanged and depends only on models and its existing numeric helpers.
- Market selection/projection depend on models and pure numeric/date helpers. They must not import repository/storage merely to select a profile or calculate growth.
- Application depends on models, finance and the pure market modules. It does not depend on config, ingestion, storage, CLI or UI.
- CLI constructs `SnapshotMarketRepository` and loads configuration, then passes typed objects to application.
- Future UI receives the same application service and typed inputs. A launcher may compose infrastructure; UI widgets must not reimplement preparation or import data acquisition.

**Important existing constraint:** application's storage prohibition also covers indirect dependencies. Importing the concrete repository into application would reach storage through `repository -> load_release`, violating that contract. Keep the concrete reader at the composition boundary. Pass `MarketData` plus immutable evaluation metadata into the evaluator.

Do not relax the contracts to make an import convenient. Extend sensitivity coverage for application-to-storage/ingestion and markets-to-finance edges. Preserve all existing contracts. Avoid a model import cycle: `market.py` already imports `scenario.GeographicReference`; new scenario settings must not import `market.py` back. The selection settings below can use profile IDs and a rent-source choice without introducing that cycle.

## 3. Contracts and public application surface

### 3.1 Additive scenario selection settings

Add one `MarketSelectionPolicy` record and a defaulted `Scenario.market_selection` field. Keep existing scenarios loadable. Put the default values explicitly in `configs/defaults.yaml` and serialize the resolved policy with the scenario.

| Setting | Phase 4 value/default | Meaning |
|---|---|---|
| strategy | `latest_complete` | Select the latest eligible complete reference profile relative to base_month |
| maximum_reference_age_months | 12 | Maximum elapsed calendar months since the profile's end-exclusive boundary |
| profile_ids | Empty tuple | Optional explicit release-profile choices; empty means use all profiles as candidates |
| whole_home_rent_source | `per_m2` | Explicit choice between unit rent and directly reported monthly whole-home rent |
| allow_pooled_property_proxy | false | Explicit permission to use a pooled home indicator for a requested flat/house |

Use strict nonnegative integers, strict booleans and unique nonempty profile IDs. Do not add a free-form options dictionary. There is one strategy now, not a plugin framework. Profile IDs constrain selection; they do not change a source's measure or segment. Cross-check them against the supplied dataset metadata once per run. An unknown ID, or multiple explicitly chosen profiles for the same metric, is an invalid evaluation request.

The `per_m2`/`per_month` setting chooses a metric; it is not a fallback preference. Missing area or a missing selected metric must not silently switch the calculation to another representation.

Keep scenario schema version 1 for these backward-compatible defaulted settings. An explicit null is still an override and must fail when the field is nonnullable. Do not add financial defaults inside the evaluator or change the config loader's list-replacement/null behavior.

### 3.2 Shared evaluation records

Define these small records in `models/evaluation.py`, without importing result implementation modules:

- **EvaluationContext:** release ID, kind, readiness, redistribution scope, selected release profiles, released location records, registry/boundary versions, attribution and dataset limitations. It contains the public metadata needed by selection/explanations; no paths, captures, mutable mappings, private index or geometry payloads.
- **MarketInputUse:** input role, selected profile ID, the original MarketObservation, reference anchor month, scenario base month, value at base, annual growth fraction, any requested property type for which a pooled proxy is used, and concise derivation/limitation notes.
- **PurchaseFinances:** purchase month, borrower monthly net income and borrower monthly other debt.
- **RuntimeEvidence:** actual Python version and direct runtime dependency versions needed to identify the environment. Keep values structured and sorted, not a shell-command transcript.

Add a public immutable `evaluation_context` property to the snapshot repository, assembled through one owner from its validated manifest/locations. CLI can pass this record to the evaluator; another data implementation can supply an equivalent context while retaining the existing `MarketData.get` protocol. Do not expose `_index` or add observation enumeration merely to avoid exact querying.

`MarketInputUse` records a derivation, not a new source observation. Keep the retained observation's value, dates, basis, statistic and evidence_kind unchanged. Do not mark a projected number as newly observed or replace an observed/estimated/synthetic label during projection.

### 3.3 Necessary output refinements

Preserve existing financial records and target-field coherence. Add defaulted fields to `LocationResult` for **prepared_budgets**, **market_inputs**, **purchase_finances** and **warnings**. They let Phase 5 explain inputs without recalculating them. Store each distinct market input once per location, rather than an entire copied observation for every projected month. Existing indicator observations can continue to identify the supporting purchase observation.

Add `unviable` to `Indicator.status`, with no value and a required reason, so financial exhaustion is not disguised as a data gap. An available indicator accepts any finite nonnegative value: zero is legitimate and target affordability can exceed one. The current Ratio/PositiveFinite union already admits that numeric range; simplify it to the existing nonnegative finite money primitive if useful, without adding a cap or rounding.

Add defaulted **evaluation_context** and **runtime_evidence** fields to `RunResult`. New evaluated runs must populate them; old contract-only payloads remain readable. Validate agreement between the legacy top-level dataset_release_id and the context's release ID. Preserve schema version 1 for compatible additions; record application semantics in model_version.

The resolved scenario contains every economic/selection assumption. The buying locations in the ordered results identify the requested mapped locations for replay. Do not add another mutable list with competing location meaning or store runtime release/output paths in the scenario.

Models validate record structure and coherence. Application owns computed relationships. Do not repeat the financial engine in Pydantic validators. Transient preparation success/failure objects may be frozen dataclasses beside `prepare.py`; they need not become another persisted schema.

### 3.4 Recommended callable surface

Expose ordinary typed functions rather than an inheritance hierarchy:

```python
def evaluate_scenario(
    scenario: Scenario,
    *,
    market_data: MarketData,
    context: EvaluationContext,
    mapped_locations: tuple[GeographicReference, ...],
) -> RunResult: ...


def evaluate_location(
    scenario: Scenario,
    *,
    saving_location: GeographicReference,
    buying_location: GeographicReference,
    market_data: MarketData,
    context: EvaluationContext,
) -> LocationResult: ...
```

`prepare_savings` separately accepts the scenario, explicit saving location, market data and metadata, and returns either a complete prepared input or a typed expected preparation issue. Its success includes exactly N budgets, starting savings and market-input traces. **It must not accept or infer the buying destination.**

Names may follow newer repository conventions, but these responsibilities and typed inputs must remain. Provide a small stable export from `application/__init__.py` for normal Python callers. No live network, configuration loading, data-root search, argument parsing or printing inside evaluation.

## 4. Reference selection and market projections

### 4.1 Keep the repository's exact contract

The retained room profile is **2026-04-01 to 2026-07-01**; sale and whole-home unit rent are **2026-09-01 to 2026-10-01**, with end dates exclusive. A quarterly observation is not an October observation.

Selection chooses a **ReferenceProfile** from context, then constructs a MarketQuery with that profile's exact interval and chosen segment. `get` continues to match exact periods and segments. Never change `get` to nearest-date, overlapping-period, annualized or provincial fallback behavior.

Choose the reference profile before looking up a location's value. If the chosen latest profile has a missing municipality cell, report that gap; do not quietly try an older profile or a different source for that municipality. This keeps the comparison consistent across the map.

### 4.2 Eligibility and freshness

For each required metric and requested segment:

1. Restrict candidates to explicit profile_ids when supplied.
2. Require metric/segment compatibility under Section 5.
3. Require `profile.period_end <= scenario.market_policy.base_month`. The reference interval must be complete at the chosen model base boundary.
4. Compute age as whole calendar months from period_end to base_month. Require age <= maximum_reference_age_months.
5. Require one source/basis/statistic series among eligible candidates; otherwise request an explicit profile choice and classify unresolved ambiguity as unsupported. Do not choose between asking, transaction, valuation or different statistics merely by date. Within that series choose the greatest eligible period_end; a remaining tie also requires an explicit profile choice.
6. Query the chosen exact interval and verify the returned observation agrees with its profile's location/metric/interval/segment/basis/statistic/source. A contradictory available response is an invalid provider response, not a missing value.

For base **2026-10-01**, September sale has age 0 and Q2 rooms age 3. This freshness convention measures time since completion; it differs deliberately from the growth anchor below. No compatible metric/segment is unsupported. A compatible product with no complete/fresh interval is missing, with a dated reason. No implicit relaxation of age or future-period use.

Phase 4 supports `start_month >= base_month`. Earlier starts/backcasting are a supported-scope limitation: return unsupported location results, without weakening structural scenario validation. Purchase month remains derived from start + saving_months.

These are snapshot counterfactuals/projections, **not as-of historical forecasts**. Observation publication/capture dates remain visible; do not claim that a historical actor could have known a release simply because its reference period predates the base.

### 4.3 One explicit projection convention

The reference anchor is the **last covered month**, `add_months(period_end, -1)`: June for Q2 rooms and September for September sale. This is a documented modelling convention for period aggregates, not evidence that their value was measured only in that last month.

For frozen policy, use the original value at base and throughout the horizon. Preserve/label the differing source periods; freezing does not turn them into same-month evidence.

For growth policy, use annual effective compound growth:

```text
m = calendar-month distance from reference anchor to requested scenario month
projected_value = observed_value × (1 + annual_growth_fraction) ** (m / 12)
```

Use rent growth for both room and whole-home rent, purchase growth for sale prices. Record each value at base and its anchor; project from that same anchor for every saving/purchase month. Do not reapply base-to-month growth twice or exponentiate relative to the saving offset when base and start differ.

Use a stable scalar implementation such as `exp((m / 12) * log1p(g))`, with an exact zero-growth path and explicit positive-finite output checks. Reject overflow, NaN, infinity and underflow to a zero market price as invalid evaluation arithmetic. Do not clamp, round, or report them as a missing market cell.

Income, debt and non-housing spending already have explicit AmountPaths; **market growth must not also grow those paths**. Salary milestones are nominal scenario assumptions. Frozen prices and changing salary are allowed when the output clearly identifies that frozen-market counterfactual.

## 5. Segments, living arrangements and rent burden

### 5.1 Supported segment mapping

| Scenario request | Query meaning | Failure/approximation rule |
|---|---|---|
| room | room_rent_per_month, room segment | Never derive it from whole-home rent |
| flat_alone / flat_shared, per_m2 | whole_home_rent_per_m2_month, flat segment | Requires rental_area_m2; bedrooms cannot supply missing area |
| flat_alone / flat_shared, per_month | whole_home_rent_per_month, flat segment | Uses directly reported complete dwelling rent; no area multiplication |
| target flat / house | purchase_price_per_m2, matching property type | Ordinary condition only; size-derived result remains approximate |

Carry an explicitly requested bedroom count as a query constraint for whole-home stages. If source bedrooms are unknown, they cannot satisfy it. Rental area is a conversion input, not a fabricated source size_band. For a direct monthly rent, preserve the supplied area in the scenario but do not pretend the source matches that exact area when it has no size segmentation.

Room-stage area/bedroom selectors have no defined room-unit matching meaning in this first workflow; a nonnull value returns unsupported rather than being silently ignored. Do not remove those fields from the shared scenario contract.

### 5.2 Pooled source approximation is explicit

The pilot's whole-home/sale profiles are pooled. Strict matching therefore cannot answer a flat/house request directly. With allow_pooled_property_proxy false, that requested comparison or rent input is unsupported.

When the user enables the flag, selection may use a pooled profile **only if no eligible exact property-type profile exists**. Carry every other requested dimension, such as bedrooms, unchanged. A pooled observation with unknown bedrooms still cannot satisfy a two-bedroom request. Query the actual pooled segment and record `proxy_for_property_type`, source segment and approximation notes in the trace/result.

Once a matching exact profile is selected, a missing location value does not trigger pooled fallback. Do not allow this flag to cross geography, metric, basis, statistic, dates or source restrictions. It never fabricates a room price.

Purchase targets with `condition = new` or `renovation` remain unsupported for market comparison because the source has no condition selector. Financial capacity can still be computed under the existing allowance. Do not invent premiums/discounts. Ordinary targets use price/m² × requested area, labelled as an approximation even with a matching flat/house profile.

Add clearly named Phase 4 examples with the pooled proxy explicitly enabled so the pilot workflow is usable. Do not enable it silently in existing examples/defaults just to avoid unsupported results.

### 5.3 Household rent arithmetic

```text
room full-unit rent = projected room €/month
whole-home full-unit rent, per_m2 = projected €/m²/month × rental_area_m2
whole-home full-unit rent, per_month = projected direct €/month
saving-household rent = full-unit rent × living_stage.rent_share
```

`rent_share` is the **combined saving pool's share of one selected rental unit**, not a separate discount applied to each saver. The existing joint-saving example's share 1 means the two savers together pay the entire flat rent; a lone saver sharing with an external flatmate can use share 0.5. Do not divide by saver count, borrower count or bedrooms again.

One stage prices one room or one whole dwelling. Do not infer multiple room leases from the number of participants. A richer multiple-unit household model is deferred; document the current unit assumption. A room share below one expresses a user-assumed shared burden for that room unit, not a discount derived from a flat price.

### 5.4 Utilities and non-housing budget

The existing schema supplies one aggregate household_nonhousing_expenses path and an inclusion flag, but no separate utility amount. Treat that path as the saving pool's **effective non-rent cash spending**, including only utilities paid outside rent.

Do not invent a utility allowance, subtract an unknown amount when the flag is true, multiply the aggregate budget by rent_share, or add bills on top automatically. `rent_includes_utilities` records the user's assumption; it does not establish the source's bill coverage. Preserve source uncertainty in the output.

If spending should change when a stage includes bills, the scenario supplies an expense milestone at that boundary. Add an example/test that demonstrates this. Clearly document the requirement in configuration comments and the result explanation. A future separately itemized utility path can extend preparation, without changing the savings engine.

## 6. Monthly preparation and participants

### 6.1 One amount-path sampler

For a validated AmountPath and integer offset t >= 0:

- At a milestone, return its exact amount.
- Step interpolation uses the most recent milestone at or before t.
- Linear interpolation between `(a, va)` and `(b, vb)` uses `va + (vb - va) × (t - a) / (b - a)`.
- After the final milestone, hold that final value.
- Never extrapolate before offset zero, round monthly amounts, or force a later target to occur at purchase.

Use this same function for annual net income, monthly debt and household spending. Source intervals and price projection are different concepts and retain their owners in markets.

### 6.2 Saving household and borrower sets

For saving offsets **0 through N−1**:

```text
monthly net saving income = sum(sample annual net income of saver_ids at t) / 12
monthly other debt = sum(sample monthly debt of saver_ids at t)
starting savings = sum(starting_savings_eur of saver_ids)
non-housing spending = sample household_nonhousing_expenses at t, once
```

Use a deterministic participant order and finite aggregate checks. Participants outside saver_ids do not contribute income, savings or debt to the saving pool. Their assumed contribution to shared rent is already represented by rent_share; do not count it twice.

At purchase offset **N**:

```text
borrower monthly net income = sum(sample annual net income of borrower_ids at N) / 12
borrower monthly other debt = sum(sample monthly debt of borrower_ids at N)
```

Borrower-only participants can support the mortgage without having contributed to the savings path. Saver-only participants can contribute savings without their salary supporting the mortgage. No implicit set union, partner promotion, default borrower or income tied to a destination salary dataset.

### 6.3 Calendar and stage application

Prepare exactly N consecutive `PreparedMonthlyBudget` records from start_month. Stages use half-open offsets `[start_month_offset, end_month_offset)`; at a transition, the new stage applies. There is no saving budget at offset N, which is the derived purchase month.

Resolve only the rent types required by the scenario. An all-flat scenario must not require room data. Reuse a selected room or whole-home base observation across relevant stages, applying that stage's area/share and the month's projection. Never query the snapshot for a future month's observed rent to represent a projection.

All required saving inputs must be available before simulating savings. If a later stage lacks a required observation, return missing_input/unsupported with a dated stage/metric reason; do not run a shortened horizon or publish partial savings as the complete result. Successfully resolved trace entries may be retained for diagnosis, but prepared_budgets stays empty for an incomplete preparation.

Pass the complete prepared budgets, summed starting savings and retained reserve to `simulate_savings`. Preserve its full signed path, zero boundary, reserve behavior and permanent funds_exhausted semantics. Do not clamp negative contributions or decide viability separately in application.

## 7. Financial orchestration and market comparison

### 7.1 Order and financial ownership

For each explicit saving/buying pair:

1. Prepare the saving-location budgets and simulate savings.
2. Resolve borrower finances at purchase independently of saver membership.
3. Create PurchaseContext with the **buying** location, derived purchase month and target property.
4. If savings are exhausted, return unviable and do not call the purchase solver.
5. Resolve the destination purchase observation/projection when supported.
6. If available, calculate `target_price = projected purchase €/m² × target area` and pass it to the existing fixed-financing solver. If unavailable, call the solver without a target so financial capacity remains available.
7. Compare the returned maximum price with the supported target market value and assemble the location result.

Use `ProportionalPurchaseCostPolicy(scenario.purchase_costs)` and `calculate_fixed_financing_capacity`. The solver deliberately requires that concrete policy; the costs-only protocol does not supply an inverse for arbitrary taxes. Do not pretend a generic policy is supported or add a second cash-limit solver here.

The inherited meanings remain:

| Quantity | Owner/meaning |
|---|---|
| Usable savings | Savings after retaining the reserve at purchase |
| Cash price limit | Cash covers down payment plus allowance under the configured financed fraction |
| Mortgage price limit | Borrower total-debt capacity supports the configured mortgage |
| Maximum purchase price | **min(cash price limit, mortgage price limit)** |
| Null cash price limit | Unbounded cash constraint only for full financing and zero costs |
| Target cash/payment shortfalls | Returned by finance; do not recompute in compare/CLI |

The default 80% financing and 10% purchase allowance imply a 30% cash requirement. The default 35% limit covers total debt; the mortgage term and nominal interest rate come from the scenario. Preserve the engine's binding tolerance and floating-point values. These estimates do not establish bank approval or an available property.

### 7.2 Market indicators

For a supported, positive projected buying price per square metre `q`:

```text
affordable_area_m2 = purchase.maximum_price_eur / q
target_price_eur = target_property.area_m2 × q
target_affordability_ratio = purchase.maximum_price_eur / target_price_eur
```

Ratio 1 means exactly covered; 1.2 means capacity covers 120% of the estimated target. Do not clamp it to one or convert it to a probability. Capacity zero with valid inputs produces available zero-valued indicators, not an unviable path. Return source periods/proxy notes alongside estimates.

Only calculate area and target ratio when the requested property segment/condition comparison is supported. Do not show pooled house/flat estimates without the explicit proxy policy. Return finite derived values; arithmetic overflow is an evaluation error.

### 7.3 Geographic mode boundary

The public run resolves the mapped locations through `modes.py`. For local/local, pass the same geographic reference into **two distinct parameters**, saving_location and buying_location. Do not replace them with one implicit global city variable in preparation or purchase.

For fixed_saving, emit unsupported results with the declared saving location and each requested buying destination, without doing market or finance work. This keeps the existing loader valid and the deferred behavior visible.

The reusable lower-level preparation and purchase orchestration must accept independent locations. Factor the buying-side work into one helper receiving an existing SavingsResult, PurchaseFinances and explicit buying location; evaluate_location composes saving preparation with this helper. A focused test may call evaluate_location with saving A and buying B to prove the boundary, without exposing the future mode through the CLI. Its rent queries must target A and its sale queries/context B. Adding the future mode should then mainly reuse one saving result across destinations, not rewrite preparation or finance.

## 8. Status rules, provenance and error behavior

### 8.1 Per-location and indicator statuses

| Situation | calculation_status | Savings/purchase | Comparison indicators |
|---|---|---|---|
| Complete viable saving inputs; supported buying comparison | available | Both populated, target diagnostics present | available |
| Complete viable saving inputs; buying observation missing/stale | available | Both populated, target fields absent | missing with specific reason |
| Complete viable saving inputs; buying segment/condition unsupported | available | Both populated, target fields absent | unsupported |
| Required saving rent absent/stale/outside release | missing_input | Neither complete savings nor purchase | missing |
| Required saving segment/rent conversion unsupported | unsupported | Neither complete savings nor purchase | unsupported |
| Complete savings path exhausts cash at any point | unviable | Full savings path retained; purchase absent | unviable |
| Geographic mode/time direction unsupported | unsupported | No calculations | unsupported |

`calculation_status = available` means financial capacity was computed. It does not mean every market indicator is available. The explanation and indicator statuses make partial comparison clear. Missing purchase prices must not discard valid rent-derived savings or price capacity.

Resolve required saving inputs first; when several saving issues exist, report all discovered issues and choose unsupported over missing_input for the location. Exhaustion takes precedence over buying-comparison limitations after a complete savings path exists. Zero usable savings without exhaustion is viable and can yield zero capacity.

Validate coherent new output records: a purchase requires viable savings; an unviable result has exhausted savings and no purchase; an available comparison requires purchase capacity and supporting buying evidence. Incomplete preparation must not carry a completed financial result. Keep legacy defaulted payloads readable where their existing fields are coherent.

### 8.2 What remains visible

Each used market input preserves its original observation, selected profile, reference anchor/base conversion, growth assumption and any proxy. Include source quality notes, household/utility assumptions and relevant dataset limitations in concise warnings. Deduplicate warnings in stable order; do not create an arbitrary numeric confidence score.

Run metadata preserves release ID/kind/readiness, geographic versions/attribution, model/code identifiers, runtime evidence and the resolved scenario. Synthetic releases remain synthetic even if every requested indicator is available. A release's incomplete readiness does not automatically forbid useful locations; use actual lookup/status outcomes.

### 8.3 Expected gaps versus failures

Expected market gaps and supported-scope limitations return typed location/indicator states and allow other locations to finish. Invalid configuration, contradictory provider metadata, corrupt releases, nonfinite arithmetic and export failures raise clear errors and produce CLI exit 2.

Do not catch every ValueError around a location and turn it into missing_input. Classify expected conditions where they arise using typed selection/preparation outcomes. Preserve unexpected failures as failures; no empty successful run or partially written export.

Validate requested locations once: nonempty, unique references, canonical ordering by level/code. The CLI accepts five-digit municipal codes, retaining leading zeros; a well-formed municipality absent from the release returns a missing result. Python callers requesting other geographic levels receive unsupported results. Do not substitute province/city-name matches.

## 9. Reproducible results and exports

### 9.1 Actual versions and deterministic assembly

Define one application model version identifying the inherited financial semantics plus this selection/preparation convention, for example `finance-v1/scenario-v1`. Do not leave Phase 1 placeholder model strings or imply a finance release exists when it does not. Update this version when calculation semantics change.

Compute code_version from the installed package version and an actual deterministic SHA-256 fingerprint of package Python source files, using sorted relative paths and framed file bytes. Include the package's implementation/model/config/CLI Python files; exclude caches, absolute paths, file mtimes and generated outputs. The helper belongs to application/version.py, performs this once per run, and does not import ingestion's processing_fingerprint function across the forbidden boundary. It must work from an installed wheel without Git or source-repository access.

Record actual runtime versions separately. Do not report a clean commit while executing modified source, generate a random run ID, or embed the current wall-clock time in the economic result. For identical resolved inputs, context, locations, code and environment, result ordering and JSON bytes must be deterministic.

Adding scenario/result source files can change the dataset builder's existing processing fingerprint even when fixture values are unchanged. Rebuild fixture releases through the actual builder; do not hard-code Phase 3's final synthetic release ID or bypass identity validation.

### 9.2 Export format and owner

`application/export.py` serializes the economic run; it does not read or validate dataset files. Use standard-library JSON and csv with explicit UTF-8, sorted JSON keys, newline termination and no NaN/Infinity. This is a separate format from a dataset bundle; do not import storage or duplicate its release validator.

An optional export directory contains exactly:

| File | Meaning |
|---|---|
| run.json | Authoritative typed RunResult, including resolved scenario and provenance |
| summary.csv | One row per location for map/table consumption, referencing the same run/release/model evidence |

There is no separate scenario copy with conflicting defaults. Scenario replay uses run.resolved_scenario, never merges today's defaults into it.

The CSV should include saving/buying levels and codes, calculation status/explanation, ending/usable savings and viability, both capacity limits, an explicit unbounded-cash flag, maximum price, binding constraint, target price/loan/cash/payment/shortfalls, area and ratio with their individual statuses/reasons, dataset kind/readiness/release ID and model/code versions. Detailed budgets and observations belong in JSON; do not flatten them into repeated rows or rederive finance fields.

Unavailable numeric fields are empty, not zero or the string None. The null unbounded cash limit is distinguished by the explicit flag. Preserve finite numeric precision; presentation rounding belongs to the later UI. Municipal codes remain strings; document that spreadsheet imports must treat them as text.

### 9.3 Local write and replay behavior

Publish run.json and summary.csv together through a temporary sibling directory and atomic final rename. The requested output directory must not already exist. Validate/serialize first, clean only this operation's staging directory on failure, and never overwrite user files. No force flag, silent append or broad output cleanup is needed.

Replay requires an explicit release path. The CLI reads the saved JSON through the existing load_mapping and RunResult validation; application receives the resulting record, not a config path. Open the release through the existing repository with the same synthetic opt-in rule, verify its release ID matches, validate the saved resolved scenario, and evaluate the saved mapped buying locations. Require matching model/code/runtime evidence before claiming exact replay. Compare deterministic JSON/result content; report a mismatch as an error, not successful reproducibility.

Legacy contract-only runs without evaluation metadata cannot prove replay; report that limitation clearly. Missing original code/environment must not be bypassed by copying saved numbers. A user can explicitly evaluate the saved scenario under newer code as a new run, outside exact replay.

## 10. CLI and documented Python workflow

### 10.1 Required commands

Preserve validate-scenario, build-release, validate-release and query-market, including their opt-in and exit-code behavior. Add:

```bash
spain-housing evaluate-scenario \
  --defaults /absolute/path/to/configs/defaults.yaml \
  --scenario /absolute/path/to/configs/scenarios/phase4_room_demo.yaml \
  --release /absolute/path/to/release \
  --locations 28079 08019 23050 28065 \
  --output-dir /absolute/path/to/new-run-directory \
  --allow-synthetic

spain-housing replay-run \
  --run /absolute/path/to/new-run-directory/run.json \
  --release /absolute/path/to/the-same-release \
  --allow-synthetic
```

`--defaults`, `--scenario` and `--release` are required for evaluation. Locations default to all released municipalities in canonical code order when omitted. `--output-dir` is optional; without it, no files are written. Replay accepts an optional new output directory using the same safe exporter.

Successful evaluation/replay writes the full RunResult JSON to stdout. Progress belongs on stderr; routine success should not emit progress noise. Expected per-location gaps, unviability or deferred mode results return exit 0, matching the existing query convention. Invalid invocation/configuration/release, omitted synthetic permission, arithmetic failure, replay mismatch or failed export returns 2 with empty stdout and a concise stderr diagnosis.

No implicit cwd-based defaults/data-root discovery, latest-release selection, network refresh or hard-coded pilot prices. Argument parsing may grow into private command-handler functions as needed; keep cli.py an adapter. It constructs the snapshot, passes its evaluation_context and MarketData interface to application, and uses the existing safe configuration loader. Do not place policy selection, budget loops or financial math in CLI.

### 10.2 Examples and replay documentation

Add one all-room frozen demo and one staged-living growth demo, explicitly enabling the pooled proxy and declaring source/bill approximations. Preserve existing examples as valid contracts. Keep the fixed-saving example valid but document its deferred evaluation result. Include an example with two savers but one borrower in local/local mode to prove participant-set behavior.

README must document exact commands, release selection, synthetic labels, expected Getafe room gap, partial buying-price results, frozen/growth meaning, utility budgets, Python usage and export/replay. Show Python callers constructing the repository at the boundary and calling the same service as CLI; do not provide a second notebook calculation.

Documentation examples are checked by the existing formatter. Do not claim observed-market integration from the fixture demo or change DATA_ACCESS to suggest a permission blocker was resolved by application code.

## 11. Autonomous work loop and milestones

### 11.1 Persistent evidence and recovery

Maintain one concise docs/progress/PHASE_4.md containing:

- Current milestone and acceptance-criterion states: pending, verified or blocked.
- Latest verified commit/checkpoint and whether relevant work is uncommitted.
- Material decisions/deviations with short reasons.
- Exact checks, outcomes and the environment used.
- Current release/scenario examples and reproducible demo command.
- Known blockers, independent work remaining and the next concrete action.

Do not duplicate this guide, append a transcript, or maintain competing task/status files. After interruption or compaction, inspect instructions, progress, git status/log and the current affected interfaces, verify the last relevant checkpoint, then resume the next incomplete task. Do not restart implemented milestones or trust a summary over current code.

Work in bounded increments: implement one coherent piece, run targeted meaningful checks, repair failures, update the checkpoint, and continue. Use the full gate at architectural/integration checkpoints and final completion. Repeat checks when changes/failures justify it; do not repeatedly run an unchanged passing suite to consume a long session.

Make scoped local commits when coherent checks pass; inspect the diff and preserve user changes. No automatic reset, stash, checkout overwrite, unrelated formatting sweep or commit of restricted/raw data. Do not commit a failing milestone as complete. If a required check cannot run, state why and leave its criterion unverified; complete independent work.

Use existing repository conventions to resolve normal naming/helper choices. Ask only if a material requirement conflicts with current instructions or genuinely missing information changes the product outcome. An inherited observed-data blocker does not require confirmation to continue fixture-based engineering. Mark completion only with evidence, never because scaffolding or a few happy paths exist.

### 11.2 M1 — Re-establish baseline and settle contracts

Read the current repository and guides; run locked sync and the full baseline gate. Confirm real-data readiness independently of code readiness. Introduce the small scenario/context/result additions, repository metadata projection, and unchanged dependency boundaries.

**Done when:** old scenario/examples and result fixtures still load; new defaults/null/duplicate-ID rules are tested; contexts are immutable; application can receive public metadata without importing storage indirectly; the baseline remains green. Record the actual reviewed commit and any inherited gap.

### 11.3 M2 — Reference selection and projections

Implement exact profile selection, completed-period/freshness/ambiguity handling, segment/proxy rules and pure frozen/growth arithmetic. Keep snapshot get semantics unchanged.

**Done when:** monthly sale and quarterly rooms retain their distinct intervals, selection queries exact periods, stale/future/ambiguous products have the correct states, no per-location older fallback occurs, proxies require opt-in, and growth matches independent reference values with finite-output failure checks.

### 11.4 M3 — Monthly preparation and household semantics

Implement the single path sampler, stage resolution, saver aggregation, rent conversions/shares and effective non-housing budgets. Produce complete prepared inputs or typed issues; call the existing savings engine.

**Done when:** boundary months, linear/step/plateau values, different saver sets, room-to-flat transitions, utility expense milestones, missing later-stage data and an exhausted/recovered path are verified. Exactly N budgets exist on success; incomplete inputs produce no shortened financial result. Preparation has no buying-location dependency.

### 11.5 M4 — Evaluation and comparison

Implement local/local mode orchestration, purchase-month borrower finances, finance calls, partial comparisons and result assembly. Populate original market traces, metadata and deterministic versions. Keep independent location arguments throughout.

**Done when:** savings-limited and mortgage-limited composed examples, zero capacity, partial buying data, unsupported property conditions and unviable paths behave as specified. Different saving/buying references work at the reusable lower-level boundary; the exposed fixed-saving mode remains deferred and clearly unsupported. Full quality/import checks pass.

### 11.6 M5 — CLI, export and exact replay

Add thin evaluate-scenario/replay-run handlers, economic JSON/CSV export, safe publication and example configurations. Extend documentation and integrate tests with the actual Phase 3 builder/repository.

**Done when:** Python and CLI results agree, ordered multi-location output includes Getafe's expected room gap, JSON revalidates as RunResult, CSV fields/statuses agree, replay succeeds with saved resolved inputs and rejects mismatched evidence, export does not overwrite or leave a partial final directory, and prior commands retain their behavior.

### 11.7 M6 — Full gate, installed package and handoff

Run the complete gate, build and a fresh-wheel workflow outside the repository. Review the final diff for duplicated rules, accidental dependency changes and undocumented assumptions. Run observed integration if a permitted release exists; otherwise retain the explicit blocked criterion.

**Done when:** all engineering acceptance criteria have current evidence, commands work without repository import-path assistance, progress/architecture/README agree with the code, and Phase 5 receives a stable callable evaluator and typed outputs. Report engineering completion separately from observed-data readiness.

## 12. Meaningful tests and verification

### 12.1 Hand-checkable composed case

Use the actual synthetic pilot builder and repository. This case is **synthetic**, not a claim about Madrid prices. Configure one saver/borrower, start 2026-10-01, horizon 3, constant annual net income €24,000, monthly debt €100, starting savings €8,000, reserve €5,000, non-housing spending €900, zero mortgage interest, term 25, fraction 0.8 and purchase allowance 0.1. Enable the pooled proxy and use frozen policy/base 2026-10-01.

The first two months rent a room; the third rents a shared 80 m² flat with share 0.5. The fixture reports room €300, whole-home €12.5/m²/month and sale €3,000/m². Target area is 80 m², ordinary flat.

| Check | Expected value |
|---|---|
| Rent in October, November, December | €300, €300, €500 |
| Contributions | €700, €700, €500 |
| Ending / usable savings | €9,900 / €4,900 |
| Purchase month and borrower income | 2027-01-01; €2,000/month |
| Maximum new mortgage payment | €600/month |
| Cash price limit | €16,333.333333… |
| Mortgage price limit | €225,000 |
| Maximum price / bottleneck | €16,333.333333… / savings |
| Target price / loan | €240,000 / €192,000 |
| Target upfront cash / payment | €72,000 / €640/month |
| Cash / payment shortfalls | €67,100 / €40/month |
| Affordable area / target ratio | 5.444444… m² / 0.068055555… |

Use independent expected numbers and appropriate tolerances, not expectations recomputed by calling the same function under test. Do not round application values to match the table.

### 12.2 Required edge and integration coverage

- **Paths/calendar:** exact milestones, step/linear/plateau, N−1 versus N, a target income after purchase, a debt change exactly at purchase, year transitions and a start later than base. For income €24,000 at offset 0 and €36,000 at 24, purchase at 12 uses €30,000/year, not the eventual target.
- **Selection:** distinct monthly/quarterly periods; exact query recording; explicit profile IDs; stale and future profiles; ambiguous latest profiles; incompatible source/basis/statistic series; no fallback after a selected location gap; returned-observation/profile disagreement rejected.
- **Projection:** frozen invariance; independent room/sale growth; negative growth above −1; zero growth; reference/base/start alignment; overflow/underflow. With 21% annual growth, room €300 anchored June 2026 becomes €363 in June 2027, including the bridge from its reference anchor.
- **Segments/rent:** pooled opt-in off/on, exact profile preferred, missing exact cell does not fall back, unknown bedrooms, per_m2 requiring area, direct monthly rent not multiplied by area, unsupported room selectors, no flat-to-room ratio.
- **Household:** two savers pay one household rent/expense budget, saver-only and borrower-only participants, non-saver savings excluded, borrower debt at purchase, utility spending changed by an explicit milestone without an invented subtraction.
- **Financial composition:** mortgage-limited and savings-limited cases, legitimate zero capacity, full financing/zero-cost unbounded cash limit, reserve exclusion and exhaustion that remains unviable after later recovery. Existing finance tests already verify formulas; application tests should verify the correct inputs and routing.
- **Partial results:** missing room affects room/staged scenarios but not all-flat ones; missing purchase price preserves capacity; unsupported condition preserves target-free capacity; absent municipality and unsupported geographic level stay explicit; no data gap becomes zero.
- **Modularity:** a recording MarketData fake proves rent queries use saving A and sale queries use buying B; no geography/destination is inferred inside saving preparation. CLI fixed_saving results are unsupported without market calls.
- **Reproducibility/export:** repeat runs, stable location order, immutable inputs, saved-scenario replay without defaults, code/release/runtime mismatch, strict finite JSON, CSV agreement, leading-zero codes, existing-output refusal, cleanup of only own staging files.
- **Real integration path:** build the fixture release with production ingestion, open it with the real repository and evaluate/replay through CLI in another working directory. Fake providers supplement this test; they do not replace it.
- **Offline behavior:** normal evaluation after opening the snapshot makes no network request or raw-data read. The code-version helper may read installed package source once; do not mistake that declared operation for a market refresh.

Use small hand-built data to test unusual segments/missing purchase cells where the standard pilot does not contain them. Keep all fixtures labelled synthetic and use real normalization/storage when testing bundle behavior. Do not modify persisted release bytes without rebuilding/verifying their identity. Move a genuinely shared fixture helper to tests/conftest.py if needed, instead of maintaining two different pilot builders.

### 12.3 Existing quality gate

Reuse, do not replace:

```bash
uv sync --locked
bash scripts/check.sh
uv build
git diff --check
```

The gate already checks lock consistency, formatting, lint, strict typing, import contracts and tests. Add targeted application/import sensitivity coverage; do not suppress existing failures or widen type ignores. New runtime dependencies are not expected for this phase. Use the standard library and existing validation stack.

### 12.4 Built-wheel verification outside the repository

Create a fresh Python environment, install the built wheel and its declared dependencies, change to a temporary directory outside the checkout, and unset PYTHONPATH. Verify imports resolve to that environment's site-packages. Copy or reference explicit fixture/config inputs; do not rely on cwd or editable-install paths.

Using the installed console script/API:

1. Build the synthetic release from retained fixture inputs with explicit opt-in and capture its returned path.
2. Validate it and exercise the pre-existing query/scenario commands.
3. Evaluate the frozen and staged-growth examples over all four municipalities; confirm synthetic metadata and the expected room gap.
4. Export both files, parse RunResult and inspect CSV/status agreement.
5. Replay against the same explicit release; verify equality and rejection when a release/model/code/runtime requirement is mismatched.
6. Demonstrate missing synthetic permission fails; demonstrate an existing output directory is preserved.
7. Compare installed/source code fingerprints and calculation outputs under the same environment; record any legitimate environment difference rather than ignoring it.

A permitted observed release, when available, gets a separate installed workflow over the core municipalities. Do not replace that evidence with fixtures or the geography-only subset. Record exact paths/versions/results in progress; temporary artifacts are not project deliverables to commit.

## 13. Acceptance criteria and completion report

| ID | Verified when |
|---|---|
| A1 | Current locked baseline is established; old commands, scenarios, dataset/financial contracts and user changes are preserved |
| A2 | Additive selection/context/result records are strict, immutable, backward-compatible where specified, and free of import cycles |
| A3 | Exact complete/fresh profile selection, ambiguity and pooled-proxy behavior match Section 4/5 with retained source periods |
| A4 | Frozen/growth projections use the declared anchors/rates, preserve observations and fail cleanly on nonfinite arithmetic |
| A5 | Monthly preparation produces exactly N budgets, correct saver/rent/expense inputs and borrower finances at N without duplicated rules |
| A6 | Local/local evaluations match independent composed references, reuse the financial engine, and retain separate location inputs for future reuse |
| A7 | Partial data, unsupported requests, unviability, zero capacity and target ratios above one have the correct separate states and provenance |
| A8 | CLI/Python outputs agree; JSON/CSV exports are coherent, deterministic and safely published; exact saved-run replay is verified |
| A9 | Full existing gate, relevant import sensitivity tests, build and fresh installed-wheel workflow pass with actual evidence |
| A10 | A permitted observed market release evaluates the real core municipalities and replays successfully; fixtures do not satisfy this criterion |
| A11 | Structure/dependencies remain enforced; no duplicated financial, selection, preparation or release rules and no unnecessary framework/dependency is introduced |
| A12 | README, architecture, progress and Phase 5 handoff accurately document supported assumptions, commands, limitations and readiness |

At the inspected baseline, A10 is blocked by Phase 3's market access condition. Complete independent engineering and report **engineering verified, observed-data integration blocked** when that remains the only blocker. Do not mark all Phase 4 criteria verified or claim the implementation plan's real-data completion condition was satisfied.

The final report should name the relevant commit/checkpoint, implemented behavior, exact verification outcomes, any unverified criteria, the release kind/readiness used, and the Phase 5 entry point. Keep it concise; detailed evidence lives in progress. Do not stop at a plan, partial scaffold or an unchecked claim of clean architecture.

## 14. Future extensions and Phase 5 handoff

**The pipeline must remain modular enough that later features extend inputs, data adapters or orchestration without substantially restructuring the repository or financial engine.**

| Future implementation | Boundary preserved by Phase 4 |
|---|---|
| Save/rent in A, buy in B — essential next geographic mode | Separate bindings and arguments; destination-free saving preparation; purchase context names B; savings/borrower finances can be reused across destinations |
| Salary realism by profession/location | User-assumed AmountPaths remain independent of employment observations; later context can explain plausibility without changing finance or inventing hiring probabilities |
| Historical scenarios/evolving maps — last major extension | Reference/capture dates, selected periods, explicit base/anchor conventions, geographic versions and code/release evidence remain available; future as-of rules extend selection |
| Larger down payments, richer taxes or investment returns | Dedicated finance/cost/return owners and explicit solver changes; no regional conditional or extra recurrence hidden in CLI/preparation |
| Itemized utilities/multiple rental units/better property segmentation | Extend typed budget/market inputs and preparation with actual amounts; preserve one financial budget boundary and source meaning |
| More locations or new storage/query tools | Supply the same MarketData and immutable context; no provider/source-file knowledge in application |

Phase 5 receives the callable evaluator, supported scenario examples, exact release/context composition, complete prepared/savings paths, financial limits/shortfalls, per-indicator statuses, proxy/source warnings and reproducible export/replay. It renders these values; it must not interpolate salary, allocate rent or recalculate capacity independently.

Keep geometry outside the economic evaluation result. The release's existing read-only polygons and the run's geographic version/code metadata provide the join; a launcher composes these for the UI. Future caching keys must include resolved inputs, mapped locations, dataset identity, model/code versions and selection policy. Do not add cache/global-session state before measured need.

Observed-data readiness remains a separate handoff item. UI development can use explicit synthetic demos, but a production map cannot claim those values are Spanish market evidence.

## 15. Research basis

The operating instructions use the earlier workflow research rather than recreating a generic agent harness: scoped checkpoints, verification before completion claims, one persistent progress record, recoverable local commits, repository-based knowledge and mechanically enforced module boundaries. These are engineering guidance, not a guarantee that a single unattended session cannot fail.

- [OpenAI: Run long horizon tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex) — concrete milestones, validation/repair loops and persistent execution state. Applied here through M1–M6, per-milestone checks and progress/resumption instructions.
- [Anthropic: Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — incremental work, verified features and an understandable state for the next context/session. Applied here without additional agents or competing status documents.
- [OpenAI: Harness engineering](https://openai.com/index/harness-engineering/) — navigable repository knowledge and enforced dependency direction. Applied here by preserving import contracts, keeping the concrete reader at composition and documenting decisions where they belong.
- [Python math documentation](https://docs.python.org/3.12/library/math.html) — log1p/finite-number behavior for the pure projection helper. Mortgage mathematics remains owned by the existing engine.
- [Python csv documentation](https://docs.python.org/3.12/library/csv.html) — standard-library table export; no dataframe dependency is required.
- [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/) — validated boundary records and immutable typed inputs; existing repository configuration conventions remain authoritative.

The reference-selection, period-anchor, freshness, pooled-proxy and household conventions in this guide are explicit **project modelling decisions**, not conclusions asserted by these workflow/library sources.
