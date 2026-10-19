# Phase 7 geography and synthetic municipal economics

## Current availability

The official national atlas and complete/partial **synthetic** economic releases
are available locally. The national display is **blocked**, not complete: the
IGN API and independently downloaded CNIG GML archive both contain an overlap
between Bellver de Cerdanya (25051) and Prullans (25179). Its measured area is
1,440.945 m² in EPSG:25831. Canonical coordinates remain unchanged. Only those
two explicitly fingerprinted original geometries are permitted as retained
source evidence; a new or changed defect fails validation.

The proposed display-only treatment is to show the intersection as neutral
source-boundary conflict, assigning it to neither municipality. This requires
the pending user decision; it has **not** been implemented. Normal display
preparation still refuses this coverage. Do not bypass its topology gate.

A contiguous **179-municipality Madrid** official-geography demonstration works
with synthetic inputs. It is regional evidence, not a national map. The old
four-/16-/250-location synthetic fixtures remain available and unchanged.

Actual IDs, hashes, counts and availability are recorded in
[`data/manifests/national_geography.json`](../data/manifests/national_geography.json)
and [`progress/PHASE_7.md`](progress/PHASE_7.md). Large files are ignored by Git;
the wheel and Git repository do not contain national data. A manifest is not a
backup. There is no published download URL or off-machine copy for this capture.

## Sources, extent and rights

Acquired 19 October 2026 from the official
[IGN administrativeunit collection](https://api-features.ign.es/collections/administrativeunit?f=json):
42 municipal pages (702,058,118 bytes), one province page (187,127,244 bytes),
collection/queryable metadata and original response/capture records. Pagination
must end normally, reconcile advertised counts and contain unique source IDs.
This is a retained API snapshot, not a claim of transactional provider isolation
or a provider-advertised immutable edition.

The retained [INE 1 January 2026 dictionary](https://www.ine.es/daco/daco42/codmun/diccionario26.xlsx)
contains **8,132 municipalities**. Exact full-code joins reconcile every one;
619 different IGN/INE labels are retained in the crosswalk. Leading zeroes and
control digits are preserved. The retained
[in-year change page](https://www.ine.es/daco/daco42/codmun/codmun_anual.htm)
has no creations/removals and 15 name changes as reviewed on capture. The atlas
keeps the named January snapshot, including its earlier labels, rather than
silently presenting those labels as current at another date.

There are **81 shared/nonmunicipal territories**, retained as neutral context
with source IDs and no economic destination. All **52 INE province outlines**
are retained. The source's additional collective code-53 province feature is
excluded from province orientation; its component neutral territories remain in
the municipal layer. Mainland, Balearic/Canary islands, Ceuta and Melilla are
included. The selected source does not represent Chafarinas, Alhucemas and Vélez
de la Gomera as municipalities; Isla de los Faisanes has special shared
international jurisdiction. None receives a fabricated code or mortgage result.

Canonical counts: 14,048 polygon components, 173 holes, 4,443,152 vertices;
186,469,439 payload bytes. The canonical reader validates all original polygon
geometry and permits only the pinned source overlap as an explicit defect.
`validate-geography` reports `source_coverage_valid: false` for this artifact.
It does not certify that the source can be simplified.

Supporting alternate evidence is the retained
[IGN ATOM feed](https://www.ign.es/atom/dataset_feeds/lin_lim_mun.es.xml) and linked
66,245,318-byte GML ZIP, updated 10 August 2026. A two-feature diagnostic confirmed
the same overlap. No geometry from that archive was patched into the API atlas.

Official geography and INE identities retain separate source decisions,
attribution and original capture timestamps under the reviewed CC BY 4.0 terms:
[IGN licence](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf),
[INE legal notice](https://www.ine.es/dyngs/AYU/index.htm?cid=125).
Synthetic market releases retain self-authored economic provenance; they never
relocate IGN captures into a synthetic source decision. Composed redistribution
uses the least permissive component. Attribution does not imply endorsement.

## Artifact and calculation boundaries

- Canonical geography schema 1: original coordinates, independent registry,
  provinces, reconciliation report, recipe, captures and checksums.
- Display schema 1: pinned canonical parent, metric simplification recipe,
  display/province geometry, measured quality and checksums.
- Dataset schema 2: independently pinned geography/registry, economic rows,
  coverage and market evidence; no embedded or fabricated boundary collection.
- Dataset schema 1: original embedded boundaries, permissions and serialized
  shape preserved. Dispatch is explicit; scenario/run schemas remain version 1.

Builds and runtime reads are offline. Dataset-v2 commands require explicit
`--geography`; map serving additionally requires `--display-geography`. Geometry
changes do not change economic cache identity. Financial code consumes the
verified municipality registry; it does not read canonical coordinates.

Display preparation uses GEOS shared-coverage simplification, with separate
metric transforms for mainland, Balearics and Canarias. Candidates are bounded
at 20/50/100 m; no independent per-feature simplification, clipping, snapping or
component/hole removal is allowed. Gates: 2% relative area, measured symmetric
boundary displacement 250 m, valid shared coverage and 20 MiB payload. Madrid's
50 m derivative is 946,036 bytes / 22,629 vertices, maximum area change 0.1682%,
maximum densified Hausdorff displacement 126.001 m. National candidates remain
blocked by the original overlap; no national fidelity/payload result is claimed.

## Restore the actual local bundle

The actual local archive is `data/raw/phase7-portable.tar.gz`; its SHA-256 and
size are in `data/raw/phase7-portable.json`. It contains retained captures,
canonical national/regional artifacts, regional display, generated complete/
partial/regional inputs/releases, wheel, configs, lock and locked requirements.
Obtain these actual files from this workspace's owner. A fresh clone alone
cannot reproduce this pinned snapshot. No external transfer has been authorized.

After copying the archive and receipt to a new machine, verify the receipt's
SHA-256 before extraction. Extract into a new, empty directory:

```bash
mkdir /tmp/housing-phase7
# Use the actual archive location after copying it to your machine.
tar -xzf data/raw/phase7-portable.tar.gz -C /tmp/housing-phase7
cd /tmp/housing-phase7
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-map.txt
.venv/bin/python -m pip install --no-deps dist/spain_housing-0.1.0-py3-none-any.whl
```

Conda may provide Python 3.12/3.13 instead; install into that environment with
`python -m pip`. Keep exact runtime/dependency evidence for replay. Core-only
installation uses `requirements-core.txt`; it does not install Streamlit.
Neither the conda environment name nor compatible version ranges alone pins a
replay runtime.

## Run the available regional map

These are actual directories from the retained bundle; no placeholder build
path is required. Run from its extracted root or the current checkout:

```bash
.venv/bin/spain-housing serve \
  --defaults configs/defaults.yaml \
  --scenario configs/scenarios/phase7_national_demo.yaml \
  --release data/releases/synthetic-d4c90f6afb5bcb790c8e498b1a9ee5aaae9a85c25421d3c629960224cc78e3ea \
  --geography data/processed/geography/geography-d1dc47df359e230ed58cd438c11712f6b8b1b0a2301c6524313deb8a804066bf \
  --display-geography data/processed/map-display/display-3018daeaf69b898617c881a5a725395c52d2c2478328a45b5625c62548ad9497 \
  --allow-synthetic --port 8501
```

Open `http://127.0.0.1:8501`. Financial values are synthetic; municipality
boundaries/identities are official-derived. Default metric is target
affordability; other metrics are affordable area and maximum purchase price.
Search/select by code. Province/territorial controls change presentation, not the
evaluated population. Neutral context, outside market coverage, not evaluated,
missing input, unsupported and unviable states are distinct.

## Rebuild from retained bytes

From the extracted root, canonical national preparation is:

```bash
.venv/bin/spain-housing build-geography \
  --config configs/sources/national_geography.yaml \
  --data-root data/raw/national-geography --artifact-root rebuilt/geography
.venv/bin/spain-housing validate-geography \
  --geography data/processed/geography/geography-ccdea7cf1810513db612c10ee67ecd977de8ccecada39e7df2dfc4090925e32d
```

The regional recipe is retained at
`data/raw/national-geography/madrid-recipe.json`. Use that as `--config` to
rebuild the contiguous regional atlas. For its display:

```bash
.venv/bin/spain-housing build-map-display \
  --geography data/processed/geography/geography-d1dc47df359e230ed58cd438c11712f6b8b1b0a2301c6524313deb8a804066bf \
  --artifact-root rebuilt/map-display --tolerance-m 50
```

Generate synthetic inputs with packaged `generate-demo --geography ... --config
configs/demos/national.yaml --output-root rebuilt/inputs --variant complete`
(or `partial`). Build the returned `recipe.json` with existing `build-release
--config ... --data-root <returned-input-directory> --release-root rebuilt/releases
--geography ... --allow-synthetic`. Receipts in the raw root contain actual input,
release and geography paths. The complete national release has 24,396 synthetic
observations; the partial release has 20 municipalities, 57/60 cells, with
deliberate Getafe room, Badalona sale and Palma whole-home gaps.

The generator hashes seed, version, province and full municipal code, with
configured ranges; ordering, adding locations and Python hash seeds do not alter
existing code-local prices. Its timestamp is a declared deterministic epoch,
not an official retrieval time. Geography gives these values no observed status.

For a new official acquisition, use the packaged
`ingestion.adapters.official.capture_official_pages` with an explicit reviewed
IGN decision, URL, raw root and inventory path. It retains and resumes all pages;
`download_official_capture` retains registry/terms/metadata bytes. A new capture
has its own timestamps and hashes: review counts/changes/context/geometry and
prepare a new recipe. Do not overwrite this pinned recipe with newly downloaded
bytes or expect new API content to reproduce the old artifact ID.

## Scale, verification and remaining work

`application.overview` reuses the full evaluator's iteration, projects existing
aggregates, and discards each monthly trace. It is explicitly not `RunResult`.
National sessions retain two overviews, two selected details, and at most the
explicitly prepared current full export. Details and exports verify the applied
scenario, release, code and runtime, and reject disagreement with the overview.
Full API/CLI evaluation/replay and canonical JSON/CSV formats are preserved.
Metric/view actions do not execute finance. Full national export may be large
and is generated only on request; it is not part of normal rerender timing.

`scripts/measure_national.py` accepts explicit retained paths and records one
warm-up plus three economic samples, runtime and Linux peak RSS. The executed
measurement was 4.272 s median at 8,132 × 84 months, 383,276 KiB total peak,
48,168 KiB above the loaded-resource peak; selected detail 10–12 ms. It excludes
geometry/browser/export. Source overlap resolution is prerequisite to national
render, full map timing and national browser acceptance. Regional browser and
installed/restoration evidence is enumerated in the progress report.

Observed housing inputs remain blocked by acquisition/use permissions. Future
observed releases can reference compatible geography with their own provenance;
this phase introduces no real-price scraper, geography-driven finance, salary
model, geographic mode extension or deployment.
