# Data expansion decisions

Reviewed 14 October 2026. Target is **16 municipalities**, including twelve beyond
the original four. Historical coverage_audit.csv is unchanged. No permitted
observed market release exists; synthetic data never closes this blocker.

## Identity and geography

| Official INE name | Code | Control | IGN feature | Core |
|---|---|---|---|---|
| Palma | 07040 | 7 | 1167875 | False |
| Badalona | 08015 | 5 | 1171327 | False |
| Barcelona | 08019 | 3 | 1171331 | True |
| Jaén | 23050 | 3 | 1166762 | True |
| Getafe | 28065 | 0 | 1173568 | False |
| Madrid | 28079 | 6 | 1173581 | True |
| Málaga | 29067 | 2 | 1166881 | False |
| Salamanca | 37274 | 5 | 1169418 | False |
| Dos Hermanas | 41038 | 4 | 1166955 | False |
| Sevilla | 41091 | 7 | 1167008 | False |
| Teruel | 44216 | 0 | 1167417 | False |
| Mislata | 46169 | 1 | 1172705 | False |
| València | 46250 | 8 | 1172786 | False |
| Valladolid | 47186 | 8 | 1170099 | False |
| Bilbao | 48020 | 9 | 1174180 | False |
| Zaragoza | 50297 | 3 | 1167753 | False |

Identifiers were verified against actual retained INE 2026 XLSX bytes. Current
[INE in-year changes](https://www.ine.es/daco/daco42/codmun/codmun_anual.htm)
were captured/reviewed; none affect these municipalities. València is the official
name; the explicit selected market-label crosswalk uses Valencia. Complete
municipal IGN responses were obtained through the existing permitted official
capture adapter and validated by existing registry/geometry owners. No topology
repair, clipping, simplification or province substitution occurred.

The recipe is [expanded.yaml](../configs/sources/expanded.yaml); source metadata
and portable paths identify actual retained capture bytes. Local raw bytes:
`data/raw/expanded-geography`; derived subset `data/processed/expanded-geography`.
[Hash reference](../data/manifests/expanded_geography.json) is **not a backup**.
These files are official geography only, not an observed market release.

## Selected product matrix

| Product | Unit | Reference interval, end exclusive | Meaning | Current readiness |
|---|---|---|---|---|
| Purchase | EUR/m² | 2026-09-01–2026-10-01 | Asking, weighted zonal medians, pooled homes | 16 blocked cells |
| Whole-home rent | EUR/m²/month | 2026-09-01–2026-10-01 | Conventional asking, weighted zonal medians, pooled homes | 16 blocked cells |
| Room | EUR/month | 2026-04-01–2026-07-01 | Asking city mean, room | 16 unavailable authorized captures |

Core remains Madrid, Barcelona, Jaén, each requiring all three products. The
other thirteen are optional coverage extensions, not demoted failing core cities.
No authorized new market observation was captured. The blocked observed recipe
retains all 48 explicit missing cells and refuses restricted source use before
building. Local-use permission and redistribution permission remain separate.

## Bounded source review (three candidates; decision frozen)

1. **Idealista published products/licensed exports:** current
[general terms](https://www.idealista.com/ayuda/articulos/terminos-y-condiciones-generales-de-idealista/)
still restrict manual/automatic copying without written permission. Selected
asking/room products fit the intended semantics, but acquisition is restricted
and redistribution unresolved. No provider contact, account or new capture.
2. **Official SERPAVI 2026:** [catalogue](https://publicaciones.transportes.gob.es/serpavi-2026-sistema-estatal-de-referencia-del-precio-del-alquiler-de-vivienda)
and [official sample](https://publicaciones.transportes.gob.es/downloadcustom/sample/4078)
describe tax-derived rental statistics; the sample identifies 2024 observations.
The 2026 publication title is not the observation year. This is a separately
labelled historical whole-home product, not current entrant asking rent or room
rent. Bulk reproduction/usage terms for a compatible selected release remain
unverified. No substitution or market capture was made.
3. **MIVAU municipal valuations:** [official bulletin](https://apps.fomento.gob.es/boletinonline2/?nivel=2&orden=35000000)
describes valuations for municipalities above 25,000 inhabitants. The historical
XLS route failed through the browser access tool. Valuation is not asking price;
it provides neither the selected room nor whole-home asking product. Not selected.

One initial review and one bounded follow-up for inaccessible official pages were
performed. Stop here until documented permitted captures or new material evidence
arrive. A public URL, attribution or reviewed CSV is not a copying licence.

## Supported synthetic engineering cases

The original four-city pilot remains unchanged. One generator at
`tests/fixtures/synthetic/expand.py` prepares independent 16-/250-location inputs
for the existing builder. Generated registry, market rows and geometry are all
synthetic, even where codes resemble real municipalities. Fixed capture metadata
is self-authored fixture metadata, not fabricated provider retrieval times.

The 16 case has 48 cells: **43 available, 4 missing, 1 source-declared unsupported**.
Getafe, Badalona and Mislata lack room observations; Teruel lacks purchase;
Dos Hermanas has a source-declared unsupported rent cell. The existing exact
query contract still returns missing for an absent row of a supported profile;
dataset source status is reported separately from scenario/query suitability.
A segmented test variant adds exact flat/two-bedroom evidence (64 cells, 59
available); this proves contract behavior only, not production segment coverage.

Policies remain unchanged: exact periods/segments, complete/fresh selection,
explicit pooled-proxy permission, no older/other-city/provider fallback. Available
zero capacity is real; zero/nonfinite market prices are invalid. Reported source
availability does not imply suitability for every scenario. Future fixed-saving,
salary and historical models remain deferred. See [runbook](RUNBOOK.md).
