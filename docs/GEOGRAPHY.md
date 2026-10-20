# National municipal map: official geography, synthetic economics

## What is available

The national atlas contains **8,132 official municipal identities**, 81 original
shared/nonmunicipal context areas and all 52 INE province outlines. The map uses
real geographic boundaries and **explicitly synthetic housing prices and rents**.
It is not an observed affordability map or a real-world ranking of municipalities.

The selected national display is
`display-179a320c8ce3602b7ccc970503837f206d1b422f8424be1f574b68fa3dc8ca3c`,
50 m nominal shared-coverage simplification, **20,673,592 bytes (19.72 MiB)**.
It retains every municipal code, all original polygon parts/173 holes and neutral
context, plus one declared source-conflict patch. Maximum relative area change
is 1.701928%; maximum measured displacement bound is 246.139481 m. Twenty-six
features retain source detail through a consistent shared-edge policy.

Full checks, actual browser outcomes and measured limits are recorded in
[Phase 7 progress](progress/PHASE_7.md). Exact hashes/paths and availability are in
[`national_geography.json`](../data/manifests/national_geography.json). Large data
files are ignored by Git and are not included in the wheel. A fresh clone or a
manifest alone does not contain the retained dataset.

## Run from this workspace

Run these commands from the repository root. Choose either Conda or uv; the
geographic and market artifacts listed below must already be present. A fresh
clone needs the [portable data bundle](#portable-data-bundle) as well.

### Option 1: Conda

Create an environment with Python 3.12 and install the package with map support:

```bash
conda create -n spanish-housing python=3.12 pip
conda activate spanish-housing
python -m pip install -e '.[map]'
```

If the environment already exists, activate it and run the installation command.
This editable installation uses the dependency ranges in `pyproject.toml`, rather
than the exact versions in `uv.lock`. Python 3.13 is also supported. For the
retained, pinned wheel installation, use the portable-bundle instructions below.

Launch the map in the activated Conda environment:

```bash
spain-housing serve \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase7_national_demo.yaml \
  --release data/releases/synthetic-5b2e10583ed3460cf983a2e3e75a27d36a3e8ba0860ca842c0bb1f8e4b3d4726 \
  --geography data/processed/geography/geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d \
  --display-geography data/processed/map-display/display-179a320c8ce3602b7ccc970503837f206d1b422f8424be1f574b68fa3dc8ca3c \
  --allow-synthetic --port 8501
```

### Option 2: uv (locked dependencies)

Install the locked environment and launch the same release:

```bash
uv sync --locked --extra map
uv run --locked --extra map spain-housing serve \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase7_national_demo.yaml \
  --release data/releases/synthetic-5b2e10583ed3460cf983a2e3e75a27d36a3e8ba0860ca842c0bb1f8e4b3d4726 \
  --geography data/processed/geography/geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d \
  --display-geography data/processed/map-display/display-179a320c8ce3602b7ccc970503837f206d1b422f8424be1f574b68fa3dc8ca3c \
  --allow-synthetic --port 8501
```

### Using the map

For either option, open `http://127.0.0.1:8501`. Stop the server with `Ctrl+C`.
Default metric is target affordability; maximum
purchase price and affordable area are also available. Search/select by full
municipal code. Territorial/province controls and selected zoom change the view,
not the financial population. Desktop fit uses the map's 960×480 nominal layout
and Web Mercator; explicit camera actions reset the view. Municipality strokes
are shown in detailed views and suppressed at national scale for legibility.

Inputs are drafts until Apply. Invalid edits/imports preserve the last applied
result. National summaries use bounded overview/detail caches. Use **Prepare full
run.json** to generate the complete monthly output; the overview itself is never
presented as a complete replayable run. Complete national JSON is about 209 MB.
Summary CSV and scenario downloads are immediately available.

For the partial demonstration, keep the same geography/display and replace only
`--release` with:
`data/releases/synthetic-eff8fd7cc93fe292f3f66c4acf892fa784cebe09b222ef58864a011fe5796acc`.
It has 20 economic municipalities and 57/60 synthetic product cells; the rest of
the atlas remains visible/selectable as outside coverage. Deliberate gaps are
Getafe room rent, Badalona purchase price and Palma whole-home rent. Missing
purchase inputs retain purchase capacity but make price-based comparisons missing.
Outside coverage, not evaluated, missing, unsupported, unviable and numeric zero
are distinct. Original four-/16-/250-location regression demos remain unchanged.

## Portable data bundle

The actual current archive is `data/raw/phase7-national-portable.tar.gz`, with
size/SHA-256 in `data/raw/phase7-national-portable.json` after final packaging.
It contains original official captures, canonical national/regional atlases,
selected/alternate national and regional displays, generated synthetic inputs/
releases, wheel, configs, lock, locked requirements and these instructions.
It is a **local** archive; there is no published URL or authorized off-machine
copy. Obtain the actual archive and checksum receipt from this workspace's owner.
The earlier regional-only `phase7-portable.tar.gz` is a historical bundle.

Verify SHA-256 against the receipt, then extract into an empty directory:

```bash
mkdir /tmp/housing-phase7
tar -xzf data/raw/phase7-national-portable.tar.gz -C /tmp/housing-phase7
cd /tmp/housing-phase7
```

Then choose one of the following installation methods from the extracted folder.

### Conda

```bash
conda create -n spanish-housing python=3.12 pip
conda activate spanish-housing
python -m pip install --require-hashes -r requirements-map.txt
python -m pip install --no-deps dist/spain_housing-0.1.0-py3-none-any.whl
```

If `spanish-housing` already exists, activate it instead of creating it again.
Run the `spain-housing serve` command from the Conda section above while still
in the extracted folder; the bundle contains the same configs and artifact paths.

### venv

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-map.txt
.venv/bin/python -m pip install --no-deps dist/spain_housing-0.1.0-py3-none-any.whl
```

Use `.venv/bin/spain-housing serve` with the same arguments as the Conda launch
command. Core-only installations use
`requirements-core.txt` and do not install Streamlit. Exact replay requires the
saved code/model/Python/dependency evidence; a compatible version range alone is
insufficient. No server token, tiles, provider account or runtime download is used.

## Official source evidence and overlap treatment

Acquired 19 October 2026 from the
[IGN administrativeunit collection](https://api-features.ign.es/collections/administrativeunit?f=json):
42 municipal pages (702,058,118 bytes), one province page (187,127,244 bytes),
service metadata, queryables and original response/capture records. Captures are
an explicitly retained API snapshot, not a claim of transactional provider
isolation or a provider-advertised immutable edition.

The [INE January 2026 dictionary](https://www.ine.es/daco/daco42/codmun/diccionario26.xlsx)
reconciles all 8,132 codes exactly; 619 IGN/INE label differences retain both
labels in the crosswalk. Leading zeroes and control digits remain intact. The
retained [in-year change page](https://www.ine.es/daco/daco42/codmun/codmun_anual.htm)
contained no creations/removals and 15 name changes when reviewed. The atlas
retains the named January snapshot, including its earlier labels.

All 81 shared/nonmunicipal territories retain their original source identifiers
and no economic code. The source's collective code-53 province feature is
excluded from orientation; its component context territories remain. Mainland,
Balearic/Canary islands, Ceuta and Melilla are included. Chafarinas, Alhucemas,
Vélez de la Gomera and special Isla de los Faisanes limitations are explicit;
no false municipal destinations are invented for absent/special source areas.

Canonical source: 14,048 polygon components, 173 holes, 4,443,152 vertices,
186,469,439 payload bytes. Original coordinates are unchanged. Both the API and
independently retained [IGN ATOM](https://www.ign.es/atom/dataset_feeds/lin_lim_mun.es.xml)
GML archive (66,245,318 bytes, updated 10 August 2026) contain the same
Bellver de Cerdanya (25051) / Prullans (25179) overlap. Local EPSG:25831 measurement
is **1,440.944794 m²**. The display records 1,446.027048 m² in the selected mainland
QA CRS EPSG:25830; these are the same intersection in different metric CRSs.

On 20 October the user approved the exact positive-area intersection as neutral
display context, assigned to neither municipality. Shared line-only boundaries
are not conflict area. The new patch has no economic identity, price or result;
hover and attribution explain the treatment. It is not an official ownership
determination. Canonical validation still reports `source_coverage_valid: false`
with only the two inspected geometry fingerprints permitted. This source defect
is not silently repaired or broadly excused. The derivative opts in explicitly
with `--neutral-source-conflicts`; new/changed source defects still fail.
Canonical review notes are historical acquisition evidence, not current approval
state. An attributed unmodified two-feature extract is retained under
`tests/fixtures/geography/ign_overlap` for offline regression.

Separate source decisions/actual timestamps/licence evidence remain under
[IGN CC BY 4.0 conditions](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf)
and the [INE legal notice](https://www.ine.es/dyngs/AYU/index.htm?cid=125).
Attribution does not imply endorsement. Synthetic market rows retain self-authored
evidence; official geometry never gives those prices observed status.

## Rebuild offline

From an extracted bundle or the current checkout:

```bash
spain-housing build-geography \
  --config configs/sources/national_geography.yaml \
  --data-root data/raw/national-geography --artifact-root rebuilt/geography
spain-housing build-map-display \
  --geography data/processed/geography/geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d \
  --artifact-root rebuilt/map-display --tolerance-m 50 --neutral-source-conflicts
spain-housing validate-geography \
  --geography data/processed/geography/geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d \
  --display-geography data/processed/map-display/display-179a320c8ce3602b7ccc970503837f206d1b422f8424be1f574b68fa3dc8ca3c
```

Preparation may take several minutes; runtime uses only verified registry and
prepared display data. Full source parsing is not repeated for financial runs.
The regional canonical recipe is `data/raw/national-geography/madrid-recipe.json`.

`generate-demo --geography ... --config configs/demos/national.yaml --output-root
rebuilt/inputs --variant complete` (or `partial`) emits an actual input directory
and recipe. Feed that recipe/directory to existing `build-release --config ...
--data-root ... --release-root rebuilt/releases --geography ... --allow-synthetic`.
Raw-root receipts contain exact input/release paths. The generator hashes seed,
version, province and full code independently of ordering/other locations. Its
epoch is configured synthetic metadata, not provider retrieval time.

Display preparation uses metric GEOS coverage simplification, with one bounded
retention pass for failed features and a temporary exterior to preserve shared
interfaces. The exterior is never published. Limits remain 2% area and 250 m
symmetric measured boundary displacement/bound; source components/holes remain.
Seven decimal geographic coordinates and the versioned `delta-7-v2` row/delta
encoding are declared in the manifest and decode to the same validated polygons.
Old GeoJSON and `delta-7-v1` artifacts remain readable. Size results: 20 m 28.90
MiB (fails), 50 m 19.72 MiB (selected), 100 m 19.10 MiB (compatible alternative).
The 100 m alternative is
`display-6ec9ea4fbc50973d7e3edf32adeefe7c881021c9a47db3837e7f3049dd3742ce`.

## Boundaries and remaining work

Canonical/display artifacts are independent schema 1; dataset schema 2 pins the
canonical geography/registry. Existing dataset schema 1, financial formulas,
scenario/run schemas, selectors and canonical economic exports remain unchanged.
Full API/CLI/replay uses complete results. National UI overviews share result
iteration with full evaluation; selected detail and full export verify pinned
scenario/release/code/runtime evidence and aggregate parity. The internal map
renderer shares immutable geometry and compacts PyDeck JSON; financial values
and detached default projection remain equivalent.

`python scripts/measure_national.py --release ... --geography ... --defaults ...
--scenario ... --output ...` measures economic-only processing. Add
`--display-geography ...` for full backend session/projection/serialization,
selected details, explicit export and memory. It declares warm-up/sample scope;
it does not claim browser timing. Actual browser timings/graphics backend,
verification and remaining limitations are in the progress report.

Observed-market acquisition/use remains blocked. Future observed releases can
reference compatible geography with their own evidence; this phase adds no real
price scraper, salary model, new geographic financial mode, tax solver or public
deployment.
