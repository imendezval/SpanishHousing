# Phase 3 data access and readiness

Reviewed 7 October 2026. Engineering is verified; an observed market release is
**blocked**. The historical [Phase 1 audit](DATA_COVERAGE.md) records publication
evidence, not permission to acquire or distribute a new dataset. Current source
decisions are frozen in [pilot_source_decisions.json](../data/manifests/pilot_source_decisions.json)
and the offline recipe in [pilot.yaml](../configs/sources/pilot.yaml).

## Market observations

| Profile | Exact interval (end exclusive) | Statistic and basis | Readiness |
| --- | --- | --- | --- |
| Pooled residential sale, €/m² | 2026-09-01 to 2026-10-01 | Weighted zonal medians, asking | Blocked |
| Pooled whole-home rent, €/m²/month | 2026-09-01 to 2026-10-01 | Weighted zonal medians, asking | Blocked |
| Room rent, €/month | 2026-04-01 to 2026-07-01 | Mean, asking | Core cities blocked; Getafe unsourced |

Madrid, Barcelona and Jaén require nine real core observations. Getafe is an
optional extension: its sale/rent acquisition is also blocked, and no suitable
room observation has been established. No new Idealista captures or observed
market release were created. Synthetic integration fixtures are explicitly
labelled and require opt-in; they provide no market evidence.

Idealista's [general terms](https://www.idealista.com/ayuda/articulos/terminos-y-condiciones-generales-de-idealista/)
restrict copying through automated or manual means without written permission.
The reviewed [API/export route](https://www.idealista.com/data/asesoramiento-inmobiliario-tecnologico/api-comparables-y-metricas/)
offers a provider contact/contract route, not a permission grant for this pilot.
Local acquisition/use is restricted and release redistribution remains unresolved.
Attribution alone does not resolve those restrictions.

Resume market acquisition only with documented permission or an approved licensed
replacement that satisfies the selected products, periods, statistics and basis.
Record the decision and capture original bytes with actual retrieval timestamps;
do not relabel another product or derive room rents from whole-home rents.

## Verified real geography

| Municipality | INE code | Control digit | IGN feature ID | Full national code | Polygon parts |
| --- | --- | --- | --- | --- | --- |
| Madrid | 28079 | 6 | 1173581 | 34132828079 | 1 |
| Barcelona | 08019 | 3 | 1171331 | 34090808019 | 2 |
| Jaén | 23050 | 3 | 1166762 | 34012323050 | 2 |
| Getafe | 28065 | 0 | 1173568 | 34132828065 | 1 |

The [INE 2026 dictionary](https://www.ine.es/daco/daco42/codmun/diccionario26.xlsx)
is effective 1 January 2026; retained in-year changes were reviewed and do not
change these four identities. INE-origin information is reusable under the
[INE legal notice](https://www.ine.es/dyngs/AYU/index.htm?cid=125), with attribution,
date and no implied endorsement.

Actual [IGN administrative-unit service](https://api-features.ign.es/collections/administrativeunit?f=json)
responses were inspected before selecting feature IDs and full national codes.
Municipalities were distinguished from same-name provinces. The service links
the [IGN licence](https://www.ign.es/resources/licencia/Condiciones_licenciaUso_IGN.pdf);
the derived subset retains its attribution. The service advertises no official
edition, so capture timestamps and hashes identify this snapshot.

All selected geometries are valid CRS84 longitude/latitude polygons. Multipart
territories and holes are retained without clipping, simplification or repair.
Six original captures (INE dictionary, changes and four complete IGN responses)
are retained locally in `data/raw/pilot-geography/`. The verified subset is in
`data/processed/pilot-geography/`. Its small committed hash/version reference is
[pilot_geography.json](../data/manifests/pilot_geography.json). It is explicitly
**not a market release**.

These raw and processed directories are ignored by Git. Back them up together
with the recipe and capture sidecars: URLs and hashes cannot reconstruct absent
source bytes. Reverify offline with:

```bash
uv run --locked python scripts/verify_pilot_geography.py \
  --config configs/sources/pilot.yaml \
  --data-root data/raw/pilot-geography \
  --output-root data/processed/pilot-geography
```

## Phase 4 handoff

The repository, release validator and exact query contract are ready for Phase 4
integration. Official geography is ready independently. The production map must
wait for a validated observed release with the required market cells and suitable
use rights. Engineering tests and synthetic releases must never be presented as
real-pilot readiness. See [Phase 3 progress](progress/PHASE_3.md) for acceptance
results and installed-wheel evidence.
