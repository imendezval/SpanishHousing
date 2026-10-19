# Spain Housing Affordability Simulator — Codex Project Brief

Planning baseline: 4 October 2026. This document consolidates the requirements and design discussion; it does not claim that an application or complete dataset already exists.

Implementation checkpoint (Phase 7): official national geography and explicitly
synthetic national economic inputs are prepared. The national display is blocked
by an inspected overlap in both official boundary products; a real-geography
Madrid regional demonstration is available. Observed housing inputs remain
unavailable. See [current progress](progress/PHASE_7.md) and
[geography/run instructions](GEOGRAPHY.md); financial meaning below is unchanged.

## 1. Project objective and scope

Build an interactive Python application with a map of Spain and adjustable personal/financial parameters. For each location, estimate:

1. How much someone can save before purchasing, given local rent and their living arrangements.
2. How large a mortgage their income at purchase can support.
3. Their maximum affordable property price under both constraints.
4. Approximate affordable floor area, or affordability of a chosen property such as a 100 m² flat.

The project primarily concerns access to buying housing. Renting is essential because it determines the savings accumulated before purchase. Flats and houses are eventual supported property types; an initial ordinary-existing-flat scope was recommended but is not a mandatory restriction.

### Confirmed initial geographic mode

**Live and buy locally:** evaluate each mapped location as both the place of residence during saving and the buying destination. Local rents influence savings; local purchase prices determine what those savings and mortgage capacity can buy.

### Non-negotiable architectural requirement

**Keep the pipeline modular enough that the future implementations in Section 12 can be added with minimal restructuring.** In particular, saving location and buying location must be independent internal inputs from the beginning, even though they are equal in the initial mode. Time/year and income assumptions must also remain explicit inputs rather than being hard-coded into map logic.

## 2. Inputs and proposed defaults

Separate user-controlled scenario inputs from external geographic observations and financial assumptions.

| Input group | Required inputs / behaviour |
|---|---|
| Starting finances | Starting savings, each buyer's contributions where relevant, emergency reserve to retain |
| Income | Current income, target income, year the target is reached; support an income trajectory rather than one constant salary |
| Saving horizon | Adjustable number of years; user suggested 6–8 years, with 7 years proposed as the default |
| Living stages | Periods in an individual room, a flat alone, or a flat shared with a partner/others; editable durations and cost shares |
| Rental accommodation | Rental size/bedrooms where applicable; keep separate from the intended purchase size |
| Other spending | Food, transport, utilities, leisure, dependants and other recurring expenses; editable budgets |
| Existing debts | Monthly repayments, with a time path if obligations change |
| Buying arrangement | Alone or jointly; specify who contributes savings and whose income supports the mortgage |
| Mortgage | Financing fraction, duration, annual nominal interest rate, maximum total-debt-to-net-income ratio |
| Purchase costs | Simplified percentage initially; later regional/property/buyer-specific taxes and other costs |
| Desired property | Flat/house, target floor area, approximate quality/condition; initially coarse if data is coarse |
| Time assumptions | Scenario start/base period, purchase date, and any salary/rent/expense/property-price growth assumptions |
| Geographic mode | Initially local/local; retain separate saving and buying location fields |

Proposed starting financial assumptions:

- Mortgage finances **80%** of the purchase price; buyer supplies **20%**.
- Additional purchase-cost allowance: **10%** of price. Total initial cash requirement: **30%**.
- Maximum total monthly debt repayments: **35%** of net monthly income.
- Mortgage duration: **25 years**, adjustable, including 20/25/30-year choices.
- Mortgage interest must be explicit and adjustable. No permanent interest-rate default was agreed.

These are modelling assumptions, not universal legal requirements or guaranteed lending criteria. Banco de España describes 30–35% debt ratios and approximately 80% valuation-based financing as common references. INE reported a 26-year average term for mortgages constituted in July 2026; 25 years remains a reasonable configurable baseline.

### Income conventions

Use **net income** in savings and affordability calculations. For the initial interface, annual net income divided by 12 avoids ambiguity between 12 and 14 salary payments. Gross-to-net conversion is deferred.

Allow user-defined income milestones and a documented interpolation rule. If the target salary is reached after purchase, use the income reached **at purchase**, not that later target. Future salary growth is a scenario assumption, not assured bank-recognised income.

**Sharing rent is independent of buying jointly.** A flatmate or partner sharing expenses does not automatically become a mortgage borrower. Household expense shares, savings contributions and borrower income must be represented separately.

## 3. Monthly savings simulation

Represent the saving period as monthly steps, with living stages that cover the horizon without unintended gaps or overlap.

Example, not a fixed requirement:

| Years | Living arrangement | User's rent burden |
|---|---|---|
| 1–3 | Individual room | Full room rent |
| 4–5 | Flat alone | Full flat rent |
| 6–7 | Flat with partner | Configured share of total flat rent |

For month `t`, define:

- `Y_t`: net income available to the relevant saving household/person.
- `R_t`: that household/person's rent contribution, selected from the saving-location data and living stage.
- `E_t`: non-rent expenses, including utilities where they are not already included in rent.
- `D_t`: existing debt repayments.
- `S_0`: initial savings.

Monthly contribution:

```text
saving_t = Y_t - R_t - E_t - D_t
```

Baseline savings accumulation:

```text
S_end = S_0 + sum(saving_t)
usable_savings = max(0, S_end - retained_emergency_reserve)
```

Optional later savings returns can use an explicit recurrence with a documented timing convention. Do not assume investment returns silently.

Required behaviour:

- Negative monthly contributions reduce savings; do not clamp each month to zero.
- Flag a scenario whose funds run out as unviable under its assumptions; do not silently assume additional credit.
- Allocate shared expenses consistently; avoid counting a partner's contribution twice.
- Avoid double-counting utilities included in a room/flat rent.
- Record the monthly path, not just its final sum, so the result is explainable.

## 4. Purchase-capacity calculations

### 4.1 Definitions

| Symbol | Meaning |
|---|---|
| `P` | Property purchase price, excluding additional purchase costs |
| `S` | Usable savings at the purchase date |
| `f` | Financed fraction of price; baseline `0.80` |
| `c` | Additional purchase-cost fraction; baseline `0.10` |
| `d` | Maximum total-debt-to-net-income ratio; baseline `0.35` |
| `Y_buy` | Net monthly income of the actual borrowers at purchase |
| `D_buy` | Other monthly debt repayments of those borrowers at purchase |
| `a` | Annual nominal mortgage interest rate, as a decimal |
| `r` | Monthly interest rate, `a / 12` |
| `n` | Number of monthly payments, `12 × mortgage_years` |

### 4.2 Bottleneck A: savings for upfront cash

Under a fixed financing fraction and proportional purchase costs:

```text
required_upfront_cash(P) = ((1 - f) + c) × P
P_savings = S / ((1 - f) + c)
```

For the agreed simplified 20% + 10% model:

```text
P_savings = S / 0.30
```

The 10% allowance represents **purchase costs**, not a universal tax rate. Taxes vary with location, property and buyer eligibility. Later, replace the proportional allowance with a purchase-cost function and solve the cash constraint numerically if necessary. Keep mortgage-formalisation costs distinct from purchase costs so expenses are not wrongly allocated or duplicated.

### 4.3 Bottleneck B: income supporting mortgage repayments

The debt threshold covers **all debt repayments**, not just the new mortgage:

```text
M_max = max(0, d × Y_buy - D_buy)
```

For a fixed-rate, fully amortising loan with monthly payments:

```text
L_max = M_max × (1 - (1 + r)^(-n)) / r     if r > 0
L_max = M_max × n                         if r = 0
P_mortgage = L_max / f
```

Use the nominal interest rate for the payment calculation. Fees and associated product costs should be accounted for explicitly rather than treating an all-in comparison rate as the contractual nominal rate.

The baseline assumes the valuation supports the price and the chosen financing fraction. Banks can lend against valuation and apply additional eligibility checks; this application estimates affordability, not approval.

### 4.4 Final maximum price: minimum of the two limits

```text
P_max = min(P_savings, P_mortgage)
```

**Use the minimum, not the maximum.** A buyer must satisfy both the cash and repayment constraints. This formula applies to the baseline in which the financed fraction is fixed at 80%.

Return both limits and identify the binding constraint:

- `P_savings < P_mortgage`: upfront savings are binding.
- `P_mortgage < P_savings`: mortgage capacity is binding.
- Approximately equal: both bind, within a documented numerical tolerance.

For any displayed target property, return its required upfront cash, mortgage amount, monthly payment and shortfall against both constraints.

Also show the remaining household budget after purchase, accounting for other expenses and ownership costs where available. A debt-ratio-compliant result does not automatically imply comfortable living.

## 5. Outputs and map behaviour

Use geographic polygons coloured by a selected metric. Display missing data distinctly instead of presenting it as affordable or unaffordable.

| Map mode | Calculation / interpretation |
|---|---|
| Maximum purchase price | `P_max` in euros for the scenario evaluated at each location |
| Approximate affordable area | `P_max / local_purchase_price_per_m2` |
| Target-property affordability | `P_max / estimated_target_property_price` |
| Binding bottleneck | Savings, mortgage capacity, or both |

For target-property affordability:

- `1.2`: budget covers 120% of the estimated target price.
- `1.0`: just affordable under the assumptions.
- `0.7`: budget covers 70%.

Initial target-price approximation:

```text
estimated_target_property_price = target_m2 × local_price_per_m2
```

Area and target-price results are estimates. Size, condition, property type and available supply affect actual options; use segmented data when available. Do not imply that an average-derived result guarantees an available property at that price.

Clicking a location should reveal:

- Income and living scenario, usable savings, and savings trajectory.
- Both price limits, final budget, and binding bottleneck.
- Local room/flat rent and purchase-price assumptions.
- Approximate affordable area and target-property price.
- Upfront cash and repayment shortfalls for the target.
- Observation periods, source information, and estimated/missing-data flags.

## 6. Modular architecture and interfaces

Keep calculations independent of the interface and source providers. Suggested boundaries:

| Module | Responsibility | Inputs → outputs |
|---|---|---|
| Scenario model | Validate personal assumptions, income paths, living stages and timing | User inputs → normalised scenario |
| Data adapters | Collect each provider's data and preserve source meaning | Source files/API responses → raw observations |
| Data normalisation / release builder | Resolve geography, units, periods and quality; produce validated snapshots | Raw observations → versioned market dataset |
| Market-data access | Retrieve data for an explicit location, period and property/rental type | Dataset + query → observations/estimates with provenance |
| Savings simulator | Model monthly saving in a saving location | Scenario + saving-location costs → monthly path and usable savings |
| Purchase-cost model | Calculate cash costs in a buying location | Price + place/date + property/buyer attributes → costs |
| Mortgage calculator | Loan/payment capacity independent of geographic UI | Borrower finances + mortgage assumptions → maximum loan |
| Purchase calculator | Apply cash and mortgage constraints | Savings + borrower income + buying assumptions → price limits and binding constraint |
| Market comparison | Translate purchasing budget into local housing options | Budget + buying-location market data → area and target affordability |
| Map/scenario controller | Choose geographic evaluation mode and coordinate modules | Scenario + locations → one result per mapped location |
| Interface | Edit parameters and present results | Scenario controls + result objects → interactive map and breakdown |

Conceptual flow:

```text
scenario + saving-location rental costs
    -> savings simulator
    -> usable savings

usable savings + income at purchase + mortgage assumptions + buying-location costs
    -> purchase calculator
    -> P_savings, P_mortgage, P_max, bottleneck

P_max + buying-location property prices
    -> local market comparison
    -> affordable area / target affordability
```

Mode orchestration:

| Mode | Saving location | Buying location | Savings computation |
|---|---|---|---|
| Initial: local/local | Each mapped location | Same location | Once per location |
| Future: fixed saving place | Selected fixed location | Each mapped location | Once per saving scenario, reused across destinations |

The savings simulator must never infer the buying destination. The purchase calculator receives accumulated savings without requiring knowledge of where they were earned. Source-specific formats, tax rules, calendar years and map rendering must not be embedded in the financial engine.

Cache prepared datasets and reusable calculations by their relevant inputs/version identifiers. Parameter changes should use local prepared data, not trigger new data collection.

## 7. Data requirements, sources and collection strategy

### 7.1 Candidate sources researched during planning

| Data | Starting source | Coverage / essential interpretation |
|---|---|---|
| Current purchase prices | [Idealista sale reports](https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/) | Monthly geographic €/m² reports; treat as asking-market evidence, not completed transaction prices; coverage varies |
| Current whole-home rental prices | [Idealista rental reports](https://www.idealista.com/sala-de-prensa/informes-precio-vivienda/alquiler/) | Starting market benchmark; size-specific monthly rent is initially approximate |
| Room rents | [Idealista room report example](https://www.idealista.com/sala-de-prensa/notas-de-prensa/2026/08/24/266632-la-oferta-de-habitaciones-se-dispara-un-12-y-el-precio-se-queda-casi-plano) | Selected city benchmarks; complete municipal coverage and bulk access remain unresolved |
| Official rental history | [MIVAU SERPAVI](https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi) | Tax-source rental statistics; geographic tables, sample counts and percentiles; separates collective/single-family housing |
| Official property valuations | [MIVAU municipal XLS referenced by official documentation](https://apps.fomento.gob.es/BoletinOnline2/sedal/35103500.XLS) | Municipal series for places above 25,000 inhabitants; valuations are distinct from asking or transaction prices |
| Geographic polygons | [IGN/CNIG boundaries](https://centrodedescargas.cnig.es/CentroDescargas/limites-municipales-provinciales-autonomicos) | Municipal, provincial and regional boundaries; preserve geographic identifiers and boundary versions |
| Spending benchmarks | [INE Household Budget Survey / EPF](https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176806&idp=1254735976608&menu=resultados&secc=1254736194790) | Category/regional spending context; editable user budgets remain authoritative for the scenario |
| Mortgage reference assumptions | [Banco de España guidance](https://clientebancario.bde.es/pcb/es/blog/consejos-para-firmar-tu-primera-hipoteca.html), [INE mortgage statistics reference](https://www.ine.es/dyngs/Prensa/H0726.htm) | References for configurable assumptions; refresh defaults instead of hard-coding dated statistics |
| Tax detail, deferred | [AEAT property-purchase guidance](https://sede.agenciatributaria.gob.es/Sede/iva/iva-operaciones-inmobiliarias/compro-vivienda-tengo-que-pagar-itp.html) and regional tax authorities | New/used property treatment, regional rules and eligibility must be modelled explicitly if implemented |
| Salary context, deferred | [INE salary survey](https://www.ine.es/dyngs/Prensa/EAES2024.htm?print=1), AEAT statistics where appropriate | Geography/occupation coverage must be audited; distinguish salary from household income |

The official SERPAVI download and geographic-statistic structure are also documented in [this government response](https://www.congreso.es/entradap/l15p/e10/e_0100000_n_000.pdf). The links above are source candidates/references, not guarantees that downloads, APIs or reuse rights have already been validated.

### 7.2 Match the observation to the question

Someone starting to rent now needs a **current entrant-market** estimate. Tax-based rental statistics can contain older contracts and should not silently replace current asking rents. Keep measures separate, retaining their definitions and periods.

Further distinctions to preserve:

- Permanent residential rent versus seasonal/tourist accommodation.
- Room versus whole flat; flat versus house.
- Size/bedrooms and condition where available.
- Advertised versus transaction versus valuation prices.
- Mean versus median, and available percentiles.
- Included versus excluded bills.

Do not estimate room rent as a universal fraction of flat rent. Do not assume smaller and larger properties share exactly the same €/m² price. Do not infer size-specific rents by combining unrelated medians as though they describe the same properties.

### 7.3 Collection routes and coverage

Start with published reports and official downloadable tables. A provider API or licensed export can be added if broader coverage or segmentation is needed.

[Idealista/data](https://www.idealista.com/data/asesoramiento-inmobiliario-tecnologico/api-comparables-y-metricas/) advertises current/historical comparables, geographic metrics and exports. Access, pricing, room coverage and redistribution rights require confirmation; do not assume a free unrestricted API.

**First concrete data task:** audit approximately 10–15 contrasting cities plus surrounding municipalities. For each, assess purchase-price, whole-flat-rent and room-rent availability, period, meaning, resolution, access conditions and reuse rights.

Room data is the leading coverage risk. Begin at the geographic resolution the weakest essential dataset supports. Municipal data is desirable; city-level coverage may be the practical starting point. Any provincial fallback must be explicit. Missing observations should stay missing or be marked as estimates with a documented method.

## 8. Data model, storage and reproducibility

### 8.1 Observation schema

Use stable official location codes, not place names alone. A normalised observation should contain:

| Field | Purpose |
|---|---|
| `location_code`, `geographic_level` | Unambiguous area and level; preserve leading zeros |
| `period_start`, `period_end` | Period the observation describes |
| `metric`, `value`, `unit` | E.g. room €/month, rent €/m²/month, purchase €/m² |
| `property_type`, `size_band` / `bedrooms` | Segmentation, where provided |
| `source`, `source_url`, `retrieved_at` | Provenance and collection date |
| `statistic` | Mean/median/percentile etc. |
| `sample_count` | Reliability context when available; do not invent missing counts |
| `observed_or_estimated`, `estimation_method` | Distinguish direct observations from modelled/fallback values |
| `methodology_version`, `quality_flags` | Track definitions, changes, coverage and limitations |

Keep observation time separate from retrieval/release time. A file downloaded in 2026 may describe 2024. Geography and price measures must align; do not join city prices to province-wide polygons without labelling that change in meaning.

### 8.2 Storage layers

| Layer | Contents | Initial storage |
|---|---|---|
| Raw | Original source downloads/captures | Immutable dated snapshots, original format |
| Processed | Standardised observations and geographic mappings | Parquet; small curated tables may be CSV |
| Release | Validated dataset selected by the application | Parquet + simplified geographic polygons + manifest |

Keep the application's working dataset local to its runtime. Refresh collection independently of interface interactions. A database server is unnecessary initially; file-based storage is sufficient, with DuckDB optional later.

### 8.3 Versioning decision

**Version datasets from the beginning; do not require DVC for the initial prototype.** Slow source changes do not eliminate reproducibility requirements.

- Git: code, collection/processing scripts, assumptions, small curated tables/corrections where redistribution is permitted, and dataset manifests.
- Larger raw/binary/geographic files: immutable snapshots outside ordinary Git plus backup.
- DVC: add when large datasets need convenient version checkout, multi-machine/team synchronisation or a richer reproducible pipeline. Git then stores references; the actual data still needs preserved storage and, for sharing/backup, a configured remote. See [DVC documentation](https://doc.dvc.org/user-guide).

A dataset manifest should record URLs, retrieval dates, observation periods, checksums, processing version and dataset-release identifier. Preserve source revisions instead of overwriting old snapshots.

A saved scenario must record **inputs + dataset release + calculation/model version**. Changes in results should be attributable to changed inputs, new observations or changed calculations.

Proposed refresh policy, not a requirement to set up an automation now:

- Housing prices/rents: quarterly initially, optionally monthly later.
- Rooms: follow available releases, commonly quarterly benchmarks.
- Official statistics: on new releases.
- Boundaries: check annually.
- Tax assumptions: review relevant rule changes.

## 9. Temporal modelling and uncertainty

Distinguish three concepts explicitly:

1. **Present-day comparison:** a clearly labelled counterfactual using today's market assumptions.
2. **Future projection:** advance salary, rents, other expenses, savings and property prices to the chosen purchase date under explicit scenarios.
3. **Historical simulation:** deferred; detailed requirements in Section 12.

Never silently combine a future salary with current house prices. All monetary quantities used in a comparison must have a consistent time and nominal/real basis. A simple present-price scenario is allowed, but label its frozen-price assumption.

Growth inputs are assumptions, not predictions. Keep salary, rent, non-housing expenses, savings returns and property-price growth independently adjustable. Use ranges or sensitivity scenarios where supported rather than false precision. Display the observation date and the estimation status of each key geographic input.

Mortgage eligibility, employment stability, valuation and actual property availability can restrict access beyond the two financial constraints. Present results as affordability estimates under the configured assumptions.

## 10. Python implementation approach and validation

Suggested initial stack, not an immutable technology commitment:

- pandas/NumPy for data handling and calculations.
- GeoPandas for geographic processing.
- Streamlit for controls, scenario/stage editing and application layout.
- PyDeck for map polygons, colours, tooltips and selection; [Streamlit documentation](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart).
- Parquet for prepared numeric data; optional DuckDB as query needs grow.

The calculation engine should work without the UI and without live network requests. The interactive map is feasible; consistent geographic data is the main difficulty.

Build order recommended during planning:

1. Define scenario/data/result contracts and perform the geographic coverage audit.
2. Implement and validate the financial engine with transparent scenarios.
3. Integrate a small validated geographic dataset.
4. Add controls, map layers and click-through explanations.
5. Broaden coverage based on observed data quality.

Meaningful financial checks should include a savings-limited case, mortgage-limited case, changing rent stages, negative cash-flow periods, other debts, reserve exclusion and the zero-interest formula. Verify that the same fixed-fraction price satisfies both constraints and that the local/local controller uses the same place through independent location inputs.

## 11. Open decisions to resolve before broad implementation

| Decision | Current position |
|---|---|
| Geographic resolution | Determined by coverage audit; do not promise complete municipality-level Spain coverage yet |
| Free reports versus provider service | Start with reports/downloads; API/export only after access and scope are confirmed |
| Room-rent gaps | Resolve first; unavailable or documented estimates, never implicit flat-rent ratios |
| Property segmentation | Existing flats recommended initially; houses need separate data/estimates |
| Income interpolation | Milestones proposed; exact interpolation/plateau convention must be documented |
| Interest assumption | Adjustable; choose and date any baseline rather than silently assuming one |
| Expense defaults | Editable; distinguish cash expenses from unsuitable aggregate spending measures |
| Time mode | Present comparison and future scenarios are desired; select and label initial implementation |
| Cost precision | Baseline 10% allowance accepted for simplicity; actual purchase-cost rules deferred |
| Geographic fallback / uncertainty | Explicit policy and quality labels needed |

## 12. Future implementations

**Architectural requirement for every item below: additions should extend data adapters, scenario inputs or orchestration without substantially restructuring the savings, mortgage and purchase engines. Prepare interfaces now; do not implement all future features prematurely.**

### 12.1 Save/rent in one place, buy in another — essential next geographic mode

This is essential to the user, although initial implementation focuses on local/local.

- User selects a fixed saving location.
- Savings are calculated there using its rents and living stages.
- The map evaluates buying destinations using those same accumulated savings, borrower income and destination-specific property prices/costs.
- Reuse the savings result across destinations.
- No new financial formulas should be necessary because saving and buying locations are already independent.

### 12.2 Salary datasets and realistic earning potential by profession/place

Address: **"The map assumes salary X, but how plausible is earning it here?"**

- Add profession/occupation, experience, local labour market, commuting and remote-work context.
- Begin with salary benchmarks/distributions where available and suitable vacancy counts.
- Consider INE salary surveys, AEAT statistics and appropriately accessible vacancy data; audit geographic/occupational resolution and definitions.
- Distinguish earnings by residence from jobs located locally; commuting and remote work can connect them differently.
- Household income is not a salary distribution. The [INE income atlas](https://www.ine.es/dyngs/Prensa/ADRH2023.htm) can provide context but must not be substituted directly for wages.
- Benchmarks or vacancy counts do not establish a calibrated personal hiring probability. Do not label them as an individual's chance without a defensible model.
- Add a separate map layer/context module; retain the ability to enter an assumed salary independently.

### 12.3 Larger down payments and richer purchase financing

The baseline fixes borrowing at 80% of price. Later permit a smaller financed fraction when a buyer has more savings, so income-limited buyers are not artificially capped by mandatory 80% borrowing.

A possible extension, under proportional purchase costs and sufficient valuation, is to solve for price `P` and loan `L` satisfying:

```text
L <= f_max × P
L <= L_max
(1 + c) × P - L <= S
```

This is an extension of the agreed baseline, not a reason to change its initial fixed-fraction formula silently. Keep its solver replaceable behind the purchase-calculator interface.

### 12.4 More precise costs, income and market modelling

Deferred refinements discussed:

- Regional/property/buyer-specific taxes and purchase costs, including applicable eligibility rules.
- Gross-to-net income conversion.
- Optional returns on accumulated savings.
- Richer ownership expenses and household-budget checks.
- Houses as well as flats, and market segmentation by size/quality.
- Wider geographic coverage and better uncertainty estimates.
- More frequent refreshes, provider APIs or DVC if dataset scale justifies them.

These belong in dedicated assumptions/data/calculation modules rather than map-specific conditionals.

### 12.5 Historical simulation and change over time — latest implementation priority

The user wants to run comparable scenarios for a historical starting point, for example **2010**, then inspect how the geographic distribution of affordability has changed or evolved.

- Treat start year, saving horizon and purchase year separately: starting to save in 2010 and buying seven years later means a 2017 purchase, not a 2010 purchase.
- Retrieve period-appropriate rent, purchase-price, mortgage and, where relevant, salary/cost data.
- Preserve geographic boundary versions and provide a consistent comparison geography across years where needed.
- Keep nominal figures within a period consistent; offer inflation-adjusted outputs for comparisons across periods if implemented.
- Distinguish an actual historical path from a fixed historical-price counterfactual and from an as-of forecast. Avoid unlabelled hindsight or use of future observations.
- Historical room-rent coverage may be particularly limited; label reconstruction and uncertainty explicitly.
- Enable comparable map snapshots, a time slider or animation, and differences in budget/affordable area/target affordability.
- Decide whether comparisons hold the buyer profile constant or follow a changing salary/profile; these answer different questions and must be labelled.

This is intentionally the **last major implementation**. Its eventual addition should mainly require historical data adapters and temporal orchestration because period-aware data access and reusable financial engines already exist.
