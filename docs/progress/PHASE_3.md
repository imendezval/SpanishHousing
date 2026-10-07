# Phase 3 progress

Status: **engineering verified, real data blocked**, 7 October 2026. Independent M1–M6 engineering is finished. Full Phase 3 completion is not claimed: A2 permission scope, A3 real core observations and A10 observed-market readiness remain blocked. M1 checkpoint: `3e8240f`; M2 engineering/M3/M4: `426ea7f`; M5: `9e9c62c`; M6 evidence is recorded in the final documentation checkpoint following M5. Initial user-owned untracked `AGENTS.md` and Phase 2/3 guides are preserved and excluded from commits. No Phase 3 push, merge or deployment was performed.

Baseline `b523385`: locked sync passed. The full gate initially failed on README Python-block formatting as predicted by the guide. Locked `ruff format README.md` repaired it, then `bash scripts/check.sh` passed all 136 tests, strict mypy, Ruff and seven import contracts. Finance and scenario behavior are unchanged.

M1 release/capture/recipe contracts and shared storage boundary are implemented. Full locked M1 gate: 145 tests, strict mypy, formatting/lint and eight import contracts pass; sensitivity tests prove finance-to-storage and storage-to-ingestion violations are detected. Added Shapely for topology and openpyxl for the selected official INE XLSX, with type stubs and one reviewed lockfile update.

M2: retained CSV adapter and explicit locale normalization work; immutable official download captures carry hashes, timestamps, HTTP metadata and permission evidence. Source decisions are in `data/manifests/pilot_source_decisions.json`; nine real core market cells are blocked by acquisition/local-use permission. Historical audit is unchanged. No new Idealista capture/observed release was created.

M3: actual official INE XLSX and in-year changes retained, four municipal identities/control digits verified. Complete actual IGN municipal features are selected using inspected feature IDs and full national codes, not province/name guesses. All topology checks pass; Barcelona and Jaén retain two polygon parts. Raw six captures: `data/raw/pilot-geography`; verified local subset: `data/processed/pilot-geography` (356,690-byte boundaries). Small hash/reference metadata is in `data/manifests/pilot_geography.json`. `uv run --locked python scripts/verify_pilot_geography.py --config configs/sources/pilot.yaml --data-root data/raw/pilot-geography --output-root data/processed/pilot-geography` passed. No repair, simplification or invented official edition.

M4: actual builder, common canonical serialization/validator, content identity, runtime processing-source fingerprint, atomic staging/publication and idempotence work. Synthetic integration produces 11 observations/12 expected cells, with explicit missing Getafe room. Rebuild, relocation, changed-input identity, corruption/lineage/coverage rejection and failed-write cleanup verified. The M4 gate passed 203 tests, strict mypy, eight import contracts, Ruff and lock check. No observed market release exists.

M5: immutable indexed `SnapshotMarketRepository` and build/validate/query CLI verified. Tests cover exact month/quarter selection, supplied segment dimensions, pooled/flat distinction, ambiguity, provenance, no network/file access during queries, unchanged scenario CLI, outside-working-directory CLI and synthetic opt-in. Shared storage owns serialization/full validation; ingestion and markets do not import each other. No duplicated financial/scenario/map implementation was added.

## Acceptance results

| ID | Result | Evidence / limitation |
| --- | --- | --- |
| A1 | Verified | Current full gate passes; README formatting repaired; original finance/configuration tests preserved |
| A2 | Partly verified, blocked | Source decisions documented; official geography permitted; Idealista acquisition/local use restricted and redistribution unresolved |
| A3 | Blocked | Nine required core market cells have no permitted captures; no invented observations |
| A4 | Verified, real | Six official captures; INE codes/control digits; complete valid attributed IGN municipal geometries |
| A5 | Verified | Five canonical payloads, strict typed contracts, one verifier, exact profiles/coverage/lineage |
| A6 | Verified | Determinism, relocation, changed-input identity, atomicity, idempotence, corruption checks; wheel/source bytes match |
| A7 | Verified | Offline exact query semantics, genuine gaps versus invalid releases, immutable index |
| A8 | Verified | Installed build/validate/query CLI, scenario command preserved, explicit synthetic opt-in |
| A9 | Verified | 227 tests, strict mypy, Ruff, lock check, eight import contracts, build and fresh-wheel smoke |
| A10 | Blocked for real market | Geography reconstruction and retention instructions verified; observed-market queries unavailable |
| A11 | Verified | Structure and ownership retained; no finance/scenario/default changes from `b523385` |
| A12 | Verified | README, architecture, current access notes, historical audit link and progress updated |

## Final verification evidence

Session tool: `/tmp/phase2-tools/bin/uv`, cache `/tmp/phase2-uv-cache`.

```bash
uv sync --locked
bash scripts/check.sh
uv build
git diff --check
```

M6 result: **227 tests passed**, strict mypy checked 29 source files, all eight
import contracts kept, Ruff formatting/lint and lock check passed. Build produced
`dist/spain_housing-0.1.0.tar.gz` and `dist/spain_housing-0.1.0-py3-none-any.whl`.

Fresh Python 3.12.9 environment: `/tmp/spain-housing-phase3-wheel.yWbaZh/venv`.
Installed the wheel with `uv pip install --python <venv>/bin/python <wheel>`.
Ran `env -u PYTHONPATH <venv>/bin/python /tmp/phase3-wheel-smoke.py` from `/tmp`;
imports resolved inside the fresh environment's `site-packages`. The smoke
verified console help, scenario validation, synthetic opt-in refusal,
build/validate/query, manifest metadata, repository sale value 3000 (synthetic),
missing Getafe room and unsupported flat. The real recipe failed explicitly on
permission without publishing a release. The real geography verifier ran with
the installed wheel and reproduced the committed geography reference exactly.

Final test release ID:
`synthetic-2f4a3337875edaffda0a116c74bd48afaf1f97b15261b060471f066c59318771`.
Readiness `synthetic_only`, 11 available/12 expected cells, one missing room.
Temporary release artifacts are under the smoke directory's `releases/`.
Checkout code rebuilt into `source-releases/` with the identical ID;
`diff -r` found no payload differences. These fixtures are not observed prices
or production-map evidence. Hashes verify integrity, not source authenticity
or usage permission.

## Source readiness and Phase 4 handoff

Current access decisions and bounded API/export review are in
[DATA_ACCESS.md](../DATA_ACCESS.md) and the source manifest. Acquisition/local use
is restricted and redistribution unresolved for the nine core market cells and
Getafe sale/rent. Getafe room remains independently unsourced. The official INE
registry and IGN geometry are permitted and independently ready.

Next: obtain documented market acquisition/use and redistribution permission, or
an approved licensed replacement satisfying the selected source meanings and
exact periods. Retain actual captures, update the frozen recipe, build/validate
an observed release and query real core coverage to close A2/A3/A10. Phase 4 can
integrate the repository and existing financial contracts; production observed
readiness must remain blocked until those requirements pass. No independent
engineering failures remain in the current gate.

Back up ignored `data/raw/pilot-geography/` and
`data/processed/pilot-geography/` together with capture sidecars and
`configs/sources/pilot.yaml`; a URL/hash alone does not preserve original bytes.
The reference is committed in `data/manifests/pilot_geography.json` and is not a
market release. Offline reconstruction:

```bash
uv run --locked python scripts/verify_pilot_geography.py \
  --config configs/sources/pilot.yaml \
  --data-root data/raw/pilot-geography \
  --output-root data/processed/pilot-geography
```
