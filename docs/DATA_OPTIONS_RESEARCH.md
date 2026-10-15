# Housing data options: research and next steps

Reviewed: **15 October 2026**. Scope: the six data routes discussed after Phase 6.
This is research and a proposed implementation handoff. No supplier was contacted,
account created, purchase made or market release published. Existing source
decisions, phase acceptance results, application code and synthetic fixtures are
unchanged. The user's request authorizes this further investigation; the bounded
review recorded in Phase 6 remains the historical result of that phase.

## Findings and choices

**Real, reusable housing observations are available.** The remaining difficulty is
obtaining observations that match the project's selected products, dates and
geography: current asking purchase prices, whole-home rents and room rents across
the sixteen municipalities. This review did not establish an openly reusable
replacement covering all three products there.

Open-source software and openly redistributable data are separate decisions. A
licensed private dataset could support an open-source application if its contract
permits the intended service. Publishing the dataset, retaining historical bytes
and letting users download source values require their own coverage in that
contract. A repository permission status records eligibility under the project's
rules; it is not a determination that every reuse of a public factual number is
unlawful.

| Route | What it could deliver | Access/cost established here | Main dependency |
|---|---|---|---|
| 1. Idealista permission | A small attributed asking-price pilot without building a listing collector | Contact route verified; free permission or sponsorship not established | Written product-specific permission and actual coverage |
| 2. Licensed API/export | Current asking observations with a continuing supply | Products verified; no public numeric quote established for this use | Price, room coverage, public outputs and permanent retention terms |
| 3. Another open source | A dataset others can reproduce and redistribute under its terms | Historical research datasets found; no verified complete current replacement | Source authority, freshness and comparable municipal products |
| 4. Official statistics | A useful historical/contract/valuation comparison with real observations | Open government feeds and actual sample rows inspected | Accept a different measurement basis and narrower initial coverage |
| 5. Authorized supplied data | A pilot using a partner's or the user's permitted observations | Existing offline CSV ingestion inspected | Actual file, permission evidence and documented methodology |
| 6. Official map + synthetic prices | Geographically recognizable demonstration | Sixteen retained official features already exist locally | Explicit support for separate geometry/price provenance |

For a low-budget public project, route 4 is the strongest verified starting point.
Routes 1 and 2 best preserve the original current-asking-price product, subject to
provider responses. Route 6 improves the demonstration while acquisition proceeds.

## 1. Ask Idealista for permission

### What was verified

The general conditions limit reuse in another application and require written
authorization for relevant uses. I found no published blanket nonprofit exception.
The 2026 methodology PDF separately has attribution language about reproduction.
Those texts do not, by themselves, establish the precise permission needed for
bulk extraction, downloadable data and permanent public snapshots. Ask which
terms govern the specific press-report aggregates rather than assuming listing
API terms and press data are identical. Sources: [general conditions](https://www.idealista.com/ayuda/articulos/terminos-y-condiciones-generales-de-idealista/),
[2026 methodology](https://st3.idealista.com/cms/archivos/static/price-indicator/es-metodologia-informes-de-precios-vivienda-2026.pdf?VersionId=t7nqokhgfa6VQpcM43AdTT8K3J5FSjj3&fv=lJHOzQn2&v=1556008208).

The appropriate first route is the [Idealista/data institutions and other profiles
contact form](https://www.idealista.com/data/servicios-instituciones-y-otros-perfiles/).
It offers custom data services. Its advertised APIs, widgets and files are access
products, not a published open-data grant. The [press room](https://www.idealista.com/sala-de-prensa/)
also lists a press team, but directs other enquiries to customer service; do not
present this project as a journalist's request.

### Request a bounded grant

Start with the original three-city core, Madrid, Barcelona and Jaén: up to nine
city/product cells per release. Ask for an expansion quote or permission covering
the sixteen named INE codes, up to forty-eight cells. This is a small aggregate
export request, not a request for individual listings, photographs or contacts.

Specify:

- Asking purchase price in EUR/m²; whole-home rent in EUR/m²/month or EUR/month;
  room rent in EUR/month. Require an explicit supported/missing answer for each.
- Exact reference intervals, methodology, geographic definition, pooled/type
  distinctions, contract category and any imputed values. The provider's current
  house-price methodology uses zonal medians and can estimate insufficient-data
  periods; an attributed published indicator is not necessarily a raw observation.
- Permission to acquire the selected aggregates, calculate results and display
  them publicly, including on a noncommercial open-source project.
- Separate permission for downloadable scenario outputs containing source values,
  redistribution of the selected aggregate table, and long-term retained snapshots
  for reproducibility after the arrangement ends.
- Attribution text, update frequency, permitted delivery method, duration,
  termination treatment, and any fee or sponsorship conditions.

### Steps

1. Prepare a one-page project description with the repository URL, screenshot,
   actual organizational status and the short municipality/product list.
2. Submit the bounded request through the official form. Ask specifically about
   press-report aggregate reuse, then an export if that is a different product.
3. Keep the response and applicable terms as permission evidence. A general
   acknowledgement or API key alone does not answer the reuse questions.
4. Obtain a small sample and validate periods, units, source geography and gaps.
5. If the answer supports the intended use, record the scoped source decision,
   retain original bytes and build a separate observed recipe through route 5's
   existing pipeline.
6. If refused or unaffordable, keep the requesting effort bounded and move to
   route 4. Waiting for a response should not hold up unrelated engineering.

Suggested message, **draft only**:

> Asunto: Reutilización de indicadores agregados en proyecto abierto de vivienda
>
> Desarrollo SpanishHousing, un simulador de capacidad de ahorro y compra de
> vivienda cuyo código es público: https://github.com/imendezval/SpanishHousing.
> Solicito información sobre la autorización para reutilizar indicadores
> municipales agregados de venta, alquiler de vivienda y habitaciones, inicialmente
> para Madrid, Barcelona y Jaén. No necesitamos anuncios individuales ni datos
> personales. Queremos mostrar resultados y atribuir la fuente, permitir descargar
> resultados que incluyen esos indicadores y conservar las instantáneas necesarias
> para reproducir los cálculos. ¿Podrían confirmar las condiciones aplicables,
> cobertura, método de entrega y eventual coste o posibilidad de colaboración sin
> ánimo de lucro? Podemos facilitar una descripción y lista exacta de indicadores.

Do not claim registered charity or university status unless that is true. Free
access, acceptance and response time remain unknown.

## 2. Obtain a licensed API or export

### Products and their differences

| Product | Verified offering | What must still be confirmed |
|---|---|---|
| [Idealista/data comparables and metrics](https://www.idealista.com/data/asesoramiento-inmobiliario-tecnologico/api-comparables-y-metricas/) | Comparables, market metrics and integration/export services | Exact municipal aggregates, rooms, sample definitions, quote and public reuse rights |
| [Idealista Search API](https://developers.idealista.com/access-request) | Application for access to property information through an API key | Whether it supplies the needed aggregate products at all; access is not an aggregate-data redistribution licence |
| [CASAFARI residential API](https://es.casafari.com/productos/api/) | Residential listing/comparable/history and market integration products | Spanish municipality coverage, rooms, aggregation method, pricing and the approved public use case |

The reviewed pages do not establish a public numeric price for this project's
requirements. Treat all three as request/quote routes; do not budget using an
unverified claim of a free API or a guessed monthly subscription.

CASAFARI's FAQ explicitly rules out indefinite caching under its ordinary offer
and points to custom agreements. Its data-supply conditions restrict redistribution
and tie display to an agreed use case; their definition of derived data is broad.
That creates a concrete compatibility question for this repository's permanent
offline snapshots and downloads, even if only a few rows are wanted. Sources:
[API FAQ](https://es.casafari.com/productos/api/), [data-supply conditions](https://www.casafari.com/data-supply-terms-conditions/).

### Steps

1. Send the same small aggregate specification to Idealista/data and, if useful,
   CASAFARI. Ask for a one-off pilot export and a recurring update quote separately.
2. Require sample rows before choosing a product. Check rooms explicitly; support
   for apartment rentals does not establish room-rental coverage.
3. Agree the rights for acquisition, public display, result downloads, source-table
   redistribution and historical retention separately. Include backups and use
   after cancellation. Obtain amendments for any rights the standard terms omit.
4. Compare total cost: licence, setup, update minimums, permitted users, calls,
   storage and hosting. A small periodic file may be a better fit than a live API.
5. Prefer supplier-computed aggregates with documented sample/deduplication rules.
   Raw listings would add substantial collection, deduplication and aggregation
   work that is not implemented by buying an API key.
6. Capture authorized downloads into the offline ingestion process. Keep keys in
   acquisition configuration; the evaluator and UI should consume an immutable
   release without contacting the supplier.
7. Verify a real release and its downloaded outputs against the final contract
   before exposing them publicly. Exercise the installed package as well as source.

**Stop condition:** a provider will only permit temporary live display, while this
project still requires retained, reproducible snapshots. That product would need a
different agreement or an explicitly approved change to the reproducibility goal.
Do not implement an elaborate integration before resolving that mismatch.

## 3. Find another openly licensed asking-price source

### Findings

I searched government catalogs, research repositories and other published housing
data for comparable purchase, whole-home and room products. No complete current
drop-in replacement was verified. This is a bounded research result, not a claim
that no such source can exist.

Examples illustrate the checks needed:

- [A Zenodo rental dataset](https://zenodo.org/records/7863984) describes April 2023
  advertisements for provincial capitals. Its age and stated coverage do not
  establish current room or purchase coverage for the sixteen targets. The landing
  page alone does not establish the full upstream permission chain.
- [A UOC-listed 2026 real-estate dataset](https://recerca.uoc.edu/documentos/69d683cee563040e2b22e538?lang=en)
  explicitly describes collecting portal records by scraping. Repository hosting
  and an uploader's licence do not resolve the upstream provider's permissions;
  author/source evidence would need review before adopting it.
- [The Observatorio del Alquiler study](https://www.observatoriodelalquiler.org/estudios/estudio-sociodemografico-de-los-inquilinos-en-espana)
  discusses whole homes and rooms using Q2 2024 information, principally at broader
  geographic levels. It is a possible partnership lead, not a verified openly
  licensed municipal feed. A province's figure must not be relabelled as its city.

The government feeds under route 4 are stronger verified reuse candidates, but
answer different questions from current advertised prices.

### Steps

1. Define the minimum acceptable product before downloading: asking basis,
   reference date, municipal identity, product and statistic. Keep the three-city
   core and sixteen-city expansion separate.
2. Check a dataset's original publisher, actual licence, upstream sources and
   attribution obligations. Follow a mirror to its original data owner. The code
   repository's licence is not sufficient evidence for copied third-party data.
3. Inspect actual downloadable rows, including the latest nonempty reference
   period. A recent catalog update is not a recent market observation.
4. Produce the exact coverage matrix: municipality × purchase/home-rent/room-rent.
   List unserved products and suppressed observations without filling them in.
5. Review aggregation and sampling. Duplicate advertisements, tourist lets,
   permanent/seasonal contracts and constructed/usable floor area can materially
   change the meaning of a price.
6. Adopt a candidate only for the products it demonstrably supports. Where licence
   or source authority is unresolved, ask its owner a precise question rather than
   treating an accessible CSV as permission.
7. Use the existing offline importer and validation for an approved candidate.

**Readiness:** no recommended complete current asking-price replacement emerged.
Continue this route with a bounded candidate list or a partner introduction, not
an indefinite search that prevents a narrower real pilot.

## 4. Use official statistics

This is the most actionable free route found. It changes the market evidence:
historical tax-declared rents, signed contracts, registered sales or valuations.
The result should state that basis and date prominently. It must not present an
older declared rent as the rent a newcomer can obtain today.

### 4a. Madrid/Getafe: explicitly licensed historical rent and valuation feeds

The Comunidad de Madrid catalog publishes a [municipal monthly-rent dataset](https://datos.gob.es/es/catalogo/a13002908-alquiler-medio-mensual-de-viviendas-arrendadas-con-valor-catastral-para-municipios-de-mas-de-20-000-habitantes-por-tipo-de-vivienda-municipios)
under **CC BY 4.0**, with CSV/JSON downloads. I fetched the actual 50,265-byte CSV:
its reference years are 2023 and 2024, despite the catalog's August 2026 update.
It contains Madrid and Getafe rows and distinguishes habitual/non-habitual homes.
The file uses semicolons and a legacy encoding, not UTF-8.

A separate [valuation-by-age dataset](https://datos.gob.es/es/catalogo/a13002908-valor-tasado-vivienda-libre-en-municipios-de-mas-de-25-000-habitantes-por-antiguedad-euros-m24)
also declares CC BY 4.0. I fetched its actual 969,741-byte JSON. It contains
2013–2025 rows, EUR/m² units and dwelling-age categories. Both sources contain
nonempty 2024 rows for these two municipalities:

| Municipality | 2024 habitual-home monthly rent | 2024 valuation, homes more than five years old |
|---|---:|---:|
| Madrid | EUR 1,012/month | EUR 4,211.9/m² |
| Getafe | EUR 752/month | EUR 2,383.3/m² |

These are **research examples of real source rows**, not current asking quotes,
matched-property comparisons or data already integrated into the application.
The age restriction is not a flat/house filter. The valuation series' annual
aggregation and source methodology still require review before a production
profile is approved. Do not substitute a price index for an absolute EUR/m² value.

Practical next steps:

1. Choose a separately named **2024 Madrid/Getafe historical pilot**, retaining
   the existing asking-price recipes and fixtures.
2. Verify the underlying rent and valuation definitions, including the valuation
   series' annual aggregation. Retain the licence and publisher metadata with the
   actual source bytes during implementation.
3. Crosswalk source codes explicitly: these files use a municipality code plus
   control digit, e.g. `0796` and `0650`. They are not the five-digit INE codes
   `28079` and `28065`. Validate against the existing registry, including controls.
4. Create separate `tax_declared` rent and `valuation` purchase profiles, with
   genuine year intervals and explicit pooled/age limitations. If a flat/house
   scenario uses pooled evidence, explicitly enable the existing
   `allow_pooled_property_proxy` policy and retain its warnings; it defaults to
   false. Do not claim a type-specific observation.
5. Leave rooms missing. Use a whole-home-only scenario to exercise available data;
   a room stage must continue to report missing inputs. Do not invent room prices
   by dividing whole-home rent.
6. Build, inspect and evaluate offline with the retained real IGN geography.
   Verify UI/CLI/export parity and reproduce the release from retained bytes.

This can establish a real pilot without a commercial provider response, subject
to the stated methodology checks. It does **not** meet the original sixteen-city,
current-asking-price and room requirements or retroactively verify Phase 6 A11.

### 4b. National tax-declared rents: AEAT / SERPAVI

[AEAT's housing statistics](https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto/estadistica-viviendas-declaradas-irpf.html)
currently list **2024** as the latest edition. They provide mean monthly rent and
mean monthly rent per m², including municipal tables above 20,000 inhabitants.
Use the block by **property location**, not the owner's residence. Coverage is the
common tax territory; [the scope methodology](https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto/estadistica-viviendas-declaradas-irpf/metodologia/ambitos-referencia.html)
excludes foral territories from property-location tables. Thus it cannot by itself
supply the shortlisted Bilbao observation.

These are tax-declaration aggregates for residential properties held by relevant
individual owners. They do not establish the entire rental market or separate
municipal room rents. The [variable definitions](https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto/estadistica-viviendas-declaradas-irpf/metodologia/variables-explotacion-clasificacion/variables-explotacion/bloque-i-viviendas-ubicacion-inmueble.html)
annualize declared income with ownership/time adjustments; the unit-rent statistic
is not obtained by dividing an arbitrary city mean rent by an arbitrary mean area.

AEAT documents reuse for commercial and noncommercial purposes subject to its
conditions: preserve meaning and metadata, attribute the source, give the update
date and imply no endorsement. Sources: [reuse policy](https://sede.agenciatributaria.gob.es/Sede/informacion-institucional/memorias/memoria-2024/4-principales-actuaciones-2024/4_1-prevencion-fraude-tributario-aduanero/4_1_7-reutilizacion-informacion.html),
[conditions](https://sede.agenciatributaria.gob.es/Sede/gobierno-abierto/reutilizacion-informacion/condiciones-reutilizacion.html).

Next steps: retain the selected municipal tables and methods, enumerate actual
target-code coverage and suppressed cells, separate habitual/other contracts, and
build annual tax-rent profiles. Pair with an explicitly selected purchase source.
The year in a SERPAVI publication title must not replace its underlying reference
year, and a property-specific reference lookup is not an observed room-rent feed.
The Transportes SERPAVI catalog returned an access error in this review; the direct
AEAT route was independently accessible.

### 4c. Catalonia: registered purchases plus contracted rents

This is a promising more recent regional pilot. [The municipal purchase page](https://habitatge.gencat.cat/ca/dades/indicadors_estadistiques/estadistiques_de_construccio_i_mercat_immobiliari/estadistica-de-les-compravendes/compravendes-habitatges-Catalunya/)
links its Q2 2026 XLSX. I downloaded and inspected the 11,526,981-byte workbook:
it contains Barcelona and Badalona, separate quarter/cumulative/rolling-year
worksheets and built-area price columns. The [purchase methodology](https://habitatge.gencat.cat/web/.content/home/dades/estadistiques/01_Estadistiques_de_construccio_i_mercat_immobiliari/02_Compravenda_i_preu_de_venda/01_Metodologia/Nota-metodologica.pdf)
defines registered deed prices, registration-date reference periods, and geographic
publication thresholds. These are transactions, not advertisements.

The [municipal rent dataset, `qww9-bvhh`](https://analisi.transparenciacatalunya.cat/Habitatge/Preu-mitj-del-lloguer-d-habitatges-per-municipi/qww9-bvhh)
provides quarterly municipal mean contract rents and counts from INCASÒL deposits.
I inspected its actual metadata and queried Barcelona: a **Q1 2026** row exists.
The metadata suppresses rents for fewer than six registered homes. Its licence
field says `SEE_TERMS_OF_USE`, with a link to the Generalitat licensing policy;
do not falsely label that field CC BY. The [policy](https://web.gencat.cat/ca/generalitat/dades-indicadors/dades-obertes/llicencies)
allows reuse/distribution/transformation under conditions, with dataset-specific
terms taking precedence and no sublicensing. Preserve those terms separately from
the code licence. [General reuse conditions](https://web.gencat.cat/ca/avis-legal)
also require source/date attribution and preservation of meaning.

Next steps:

1. Select a matched period available for both series, initially Q1 2026; do not
   assume the rent API is as current as the Q2 purchase workbook.
2. Finish the dataset-specific reuse review, including the purchase workbook's
   Registrars attribution and any third-party notice. If ambiguous, request a
   reuse-conditions certificate or confirmation from the publishing department.
3. Review habitual/seasonal-contract treatment and pool/type compatibility.
4. Select the relevant quarter worksheet and published purchase/rent columns;
   never combine a cumulative purchase series with a single-quarter rent label.
5. Start with Barcelona/Badalona, then measure the overlap for a larger Catalonia
   pilot using official codes and unsuppressed observations.
6. Keep rooms missing unless a separate permitted source is obtained. Broader
   Catalonia coverage changes the geographic pilot; it does not fill Madrid/Jaén.

### 4d. Other official purchase benchmarks

[MIVAU's municipal valuation tables](https://apps.fomento.gob.es/boletinonline2/?nivel=2&orden=35000000)
are a broader valuation lead. The index page was accessible in this review; full
national extraction/coverage was not completed. Valuations must retain that basis.

AEAT also now lists [2024 housing-transfer statistics](https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto/estadistica-viviendas-transmitidas-irpf.html)
with municipal breakdowns. Ordinary HTTP requests accessed their methodology and
publication index when the browser reader failed. These merit further evaluation,
not immediate substitution: the scope excludes several seller groups and foral
territories. The [published variable definition](https://sede.agenciatributaria.gob.es/Sede/estadisticas/estadisticas-impuesto/estadistica-viviendas-transmitidas-irpf/metodologia/variables-explotacion-clasificacion/variables-explotacion.html)
includes seller costs/taxes in a transfer-value definition and describes unit
values as a ratio of total values to total area. Resolve the purchase-cost and
statistic mapping, and the distinction between sales and other transfers, before
using those values as a property-price benchmark. Do not use historic acquisition
values as current sale prices. No municipal transfer-table coverage matrix was
verified in this research.

## 5. Import a dataset already authorized for this project

### What the repository already supports

There is an offline curated CSV adapter and an immutable release builder. The
market model already distinguishes `asking`, `transaction`, `valuation` and
`tax_declared`; financial calculations need not be copied into an importer or UI.
The UI's existing upload is for scenario inputs, **not market CSV data**.

Inspect these implementation owners when implementing:

- `src/spain_housing/ingestion/adapters/curated.py`: exact UTF-8 CSV contract.
- `src/spain_housing/models/market.py`: metrics, units, periods and evidence.
- `src/spain_housing/models/dataset.py`: recipes, captures, profiles and decisions.
- `src/spain_housing/storage/release.py`: source-use and capture validation.
- `src/spain_housing/ingestion/release.py`: release construction.

The curated CSV currently requires exactly these thirteen unique columns:

```csv
profile_id,source_location,geographic_scope,raw_value,raw_unit,period_start,period_end,statistic,basis,source_locator,evidence_kind,estimation_method,quality_notes
```

Source decisions, original captures, geography and source URLs belong in the
recipe/provenance records as well. A CSV alone does not establish permission or
create a publishable release. The model has `sample_count`, but this curated CSV
does not currently carry it; an additive importer change may be needed if a
chosen source's counts must survive as structured observation metadata.

### Steps

1. Obtain a file and its provenance from the actual owner: agency, research
   partner, public publisher or an authorized supplier. Ask for aggregated rows;
   this app does not need names, contact details or exact household addresses.
2. Obtain the rights for the intended public outputs and retention, using the
   questions under route 1. Permission to view or receive a file is not necessarily
   permission to publish it.
3. Audit location codes, interval boundaries, currencies, units, sample definitions
   and missing-value markers. Preserve raw bytes/encoding; derive the normalized
   CSV separately. Never turn `-`, suppressed cells or parsing failures into zero.
4. Check representativeness. A partner's selected inventory or a person's own lease
   is evidence about that sample, not automatically a municipal market benchmark.
   A personal budget assumption belongs in a separately designed assumption input,
   not an invented observed city price.
5. Create a source decision, timestamped/hash-verified captures and a dedicated
   recipe. Use existing geography/crosswalks and exact product profiles. Private
   licensed sources may cite a real provider URL without publishing the raw file;
   self-collected sources need an honest provenance design, not an invented URL.
6. Build and validate offline. Inspect coverage and compare selected source rows
   with serialized observations. Mark unsupported/missing products explicitly.
7. Run scenarios that the evidence actually supports, verify UI/CLI/download
   agreement, then rebuild from retained bytes and exercise an installed wheel.
8. Store only redistributable artifacts publicly. Keep contractual restrictions
   attached to licensed datasets and derived outputs; preserve source attribution.

**Readiness:** the engineering route exists, but no authorized supplied market file
was provided during this research. No upload UI or second ingestion framework is
needed to begin with an offline import.

## 6. Use official boundaries with synthetic prices

### What exists and what does not

I verified that the current checkout contains sixteen location records and sixteen
real features in `data/processed/expanded-geography`, plus the small committed
reference `data/manifests/expanded_geography.json`. The GeoJSON is 1,331,314 bytes.
The retained INE registry and complete IGN boundaries, permission evidence and
archive were already prepared in Phase 6. Their [IGN licence](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)
and [INE reuse notice](https://www.ine.es/dyngs/AYU/index.htm?cid=125) are referenced
by the existing recipe. This research checked local presence/counts; it did not
repeat Phase 6's complete archive/rebuild verification.

The regular blocks in the expanded demonstration come from deliberately generated
rectangles. Official municipality boundaries would replace them with actual shapes
in their geographic positions. Sixteen selected municipalities still appear as
separate patches across Spain: this is not complete nationwide polygon coverage.

**This is not currently a configuration-only switch.** The release model has
`observed`/`synthetic` kinds, and `validate_source_use`/`validate_capture_permission`
explicitly reject real source decisions or real captures in synthetic releases.
Observed releases reject synthetic observations. The current synthetic UI warning
also describes both data and geometry as synthetic. Simply exchanging a GeoJSON,
renaming sources or disabling the checks would misrepresent provenance.

### Steps

1. Design an explicit demonstration mode with independent geography and market
   evidence. Keep actual geometry provenance and synthetic price provenance.
2. Add the smallest typed contract/validation change that supports that distinction
   end to end. Continue to reject synthetic prices in an observed release and
   reject unpermitted geography. Preserve existing fixtures and release behavior.
3. Produce the demonstration through existing geography/ingestion owners, joining
   official codes and the actual boundary version. Do not just relabel old fixture
   coordinates as official.
4. Reuse the evaluator and serializers. Label the map, selected-location details
   and exports **official boundaries; synthetic prices and financial results**.
5. Verify municipality placement, multipart shapes/holes, tooltips, missing cells,
   zoom/selection and parity. Ensure switching releases clears stale outputs.
6. Keep observed-data readiness unchanged. This does not satisfy Phase 6 A11 or
   produce real affordability estimates, even when the map looks convincing.

This is useful for demonstrating geographic behavior immediately. It does not
remove the need to choose one of routes 1–5 for meaningful market comparisons.

## Proposed order of work

1. **Choose the measurement promise.** If the priority is a useful free public
   prototype, start with route 4's historical pilot. If today's asking market,
   including rooms, is essential, first resolve route 1/2 access and terms.
2. **Prepare one small real release.** Madrid/Getafe 2024 is the most directly
   verified explicit-licence candidate here, subject to the outstanding valuation
   methodology check. Catalonia is a promising more recent alternative after its
   dataset-specific review. Neither is presented as the original full Phase 6.
3. **Send a bounded provider request in parallel**, if the user elects to pursue
   current asking data. The Spanish draft above is ready for user review/sending.
4. **Use route 6 only if the immediate priority is a better demonstration.** Its
   provenance change is real engineering work and should have its own scope.
5. **Expand only after a reproducible observed pilot works.** Publish a product/
   municipality coverage report; resolve rooms independently; keep unsupported
   stages visibly unsupported. Retain the financial engine and module boundaries.

## Verification and limits of this research

- Read the project brief, Phase 6 progress, current recipe, market models, CSV
  importer and release validation. Checked the working tree before writing.
- Reviewed primary provider, government, licence and dataset pages linked above.
- Actually downloaded/inspected the Madrid rent CSV and valuation JSON, Catalonia
  purchase workbook, rent API metadata and a Barcelona Q1 2026 API row. These were
  research inspections in memory, not retained production acquisition bundles.
- Read AEAT transfer-method pages using ordinary HTTP after browser-reader errors.
  An accessible table or index does not constitute validated release coverage.
- No commercial quote, permission response, complete national extraction,
  sixteen-city product matrix, room dataset, new market adapter or observed release
  was obtained. Historical phase acceptance statuses therefore remain unchanged.
- No application code changed. Application tests and installed-wheel checks were
  not rerun for this documentation-only task; existing Phase 6 results are recorded
  in `docs/progress/PHASE_6.md`, not claimed as new research verification.
