# Offline MVP runbook

Supported: Python 3.12/3.13, explicit local/local scenarios, immutable releases.
The Phase 6 workflow below remains available. For Phase 7 official geography,
actual local archive/restoration and runnable national map commands, use
[GEOGRAPHY.md](GEOGRAPHY.md). The national display includes the approved neutral
treatment of a retained official-source overlap. Initial software-rendered
browser performance remains
an open goal; see the measured limits in the progress report.
The tested synthetic path below needs no provider account. Observed-market
reproduction remains blocked; official geography is independently verified.
See [expansion decisions](DATA_EXPANSION.md) and [architecture](ARCHITECTURE.md).

## 1. Install and retain exact evidence

From the checkout root, install uv if needed, then:

```bash
uv sync --locked --extra map
bash scripts/check.sh
uv build
project_root="$(pwd)"
work_root="$(mktemp -d /tmp/spain-housing-demo.XXXXXX)"
```

Keep `uv.lock`, checkout revision, the wheel, defaults, scenario, original captures,
recipe and validated release together in your backup. An editable installation
(`python -m pip install -e '.[map]'`) works with conda/venv, but pip's compatible
version ranges alone do not establish an identical replay runtime. The map extra
is optional for core CLI/evaluation. The complete development gate includes it.

## 2. Prepare a labelled synthetic input bundle and build offline

The original four-city regression fixture is unchanged. For expanded engineering:

```bash
uv run --locked --extra map python tests/fixtures/synthetic/expand.py \
  --output-root "$work_root/inputs" --locations 16
uv run --locked --extra map spain-housing build-release \
  --config "$work_root/inputs/recipe.json" --data-root "$work_root/inputs" \
  --release-root "$work_root/releases" --allow-synthetic > "$work_root/build.json"
release_dir="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["path"])' "$work_root/build.json")"
uv run --locked --extra map spain-housing validate-release \
  --release "$release_dir" --allow-synthetic
uv run --locked --extra map spain-housing inspect-release \
  --release "$release_dir" --allow-synthetic > "$work_root/coverage.json"
```

`--release` is the **entire returned directory path**, including its hash.
The 16 case has 43/48 captured cells: four missing and one source-declared
unsupported. All market rows, registry and geometry are self-authored fixtures.
The 250-location generator option is a scaling test, not observed Spanish data.

## 3. Evaluate, export and exactly replay

```bash
uv run --locked --extra map spain-housing evaluate-scenario \
  --defaults "$project_root/configs/defaults.yaml" \
  --scenario "$project_root/configs/scenarios/phase4_room_demo.yaml" \
  --release "$release_dir" --allow-synthetic \
  --output-dir "$work_root/room-run" > "$work_root/evaluated.json"
uv run --locked --extra map spain-housing replay-run \
  --run "$work_root/room-run/run.json" --release "$release_dir" --allow-synthetic \
  --output-dir "$work_root/room-replay" > "$work_root/replayed.json"
cmp "$work_root/room-run/run.json" "$work_root/room-replay/run.json"
cmp "$work_root/room-run/summary.csv" "$work_root/room-replay/summary.csv"
```

Use a new output directory each time. The run JSON owns resolved inputs and actual
code/model/runtime evidence; replay does not merge current defaults. With implicit
destinations the validator's code-sorted release order matches the UI. For explicit
`--locations`, preserve that same order for exact UI/CLI comparisons. CSV codes
should be imported as text to retain leading zeros. Changing any package Python
source, even reporting/UI code, changes the economic fingerprint; replay refusal
then requires a new evaluation, not altered saved evidence.

Repeat with `phase4_staged_growth_demo.yaml` for two savers/one borrower, expense
milestones, room→flat stages and separate rent/purchase growth. Current profiles
must be complete/fresh at the scenario base; available coverage alone does not
promise suitable segments or every living mode. Selected gaps never trigger
older-period/nearby-city/provider substitution. Pooled proxies require opt-in.

## 4. Launch the map

```bash
uv run --locked --extra map spain-housing serve \
  --defaults "$project_root/configs/defaults.yaml" \
  --scenario "$project_root/configs/scenarios/phase4_room_demo.yaml" \
  --release "$release_dir" --allow-synthetic --port 8501
```

Open http://127.0.0.1:8501; **Fit released areas** reveals sparse fixture geometry.
Inspect **Dataset coverage and source definitions** separately from financial
results. Three metrics, source badges, code selection/table and zoom use the
released metadata. No external tiles/tokens or provider access is required.

Apply submits coordinated edits; imports stage a draft and require Apply.
Invalid submissions retain the explicitly previous successful run/downloads.
Downloads use existing serializers and refer to that applied run, not pending
browser edits. A room gap can disappear under a supported flat-saving scenario;
a purchase gap preserves capacity but prevents market comparisons. Source-declared
unsupported coverage is separate from the existing exact-query missing-row state.

Stop with Ctrl+C. To select a new release, stop/restart with its explicit path.
Restart deliberately resets to the supplied startup scenario; save a scenario
first if you want to preserve it. Same-path **Reload validated release** revalidates
artifacts and clears that session's applied memo; Apply is required afterwards.
Corrupt releases show a load error, not replacement prices. No implicit latest
release or source acquisition occurs on startup, rerun or reload.

## 5. Transfer/restore actual bytes and verify another installation

Two distinct routes:

- **Evaluate a restored release:** copy the entire content-addressed directory,
  preserving manifest and all payloads. Validate/inspect before selecting it.
  Evaluation works without raw captures and without network.
- **Rebuild:** copy original retained captures, recipe/capture sidecars, crosswalk,
  code and compatible environment. Rebuild into a new root and compare release
  ID/files. Redownloading a mutable URL may produce different bytes.

For the synthetic route, make and restore an actual archive:

```bash
mkdir "$work_root/backup"
tar -czf "$work_root/backup/inputs.tgz" -C "$work_root/inputs" .
tar -czf "$work_root/backup/releases.tgz" -C "$work_root/releases" .
mkdir "$work_root/restored-inputs" "$work_root/restored-releases"
tar -xzf "$work_root/backup/inputs.tgz" -C "$work_root/restored-inputs"
tar -xzf "$work_root/backup/releases.tgz" -C "$work_root/restored-releases"
uv run --locked --extra map spain-housing build-release \
  --config "$work_root/restored-inputs/recipe.json" \
  --data-root "$work_root/restored-inputs" --release-root "$work_root/rebuilt" \
  --allow-synthetic > "$work_root/rebuilt.json"
```

Compare the original/rebuilt release basenames and every payload byte. Keep a
verified copy on your own separate durable backup medium; `/tmp` is temporary.
No remote transfer or durable off-machine backup is performed by this phase.
URLs/hash references are not backups; local-only licensed bytes must not be
committed or distributed without appropriate rights.

For a fresh wheel with lock-derived dependencies (use your chosen Python 3.12/3.13):

```bash
uv export --locked --extra map --no-dev --no-emit-project \
  --output-file "$work_root/map-requirements.txt"
python -m venv "$work_root/map-env"
uv pip sync --python "$work_root/map-env/bin/python" "$work_root/map-requirements.txt"
uv pip install --python "$work_root/map-env/bin/python" --no-deps \
  "$project_root/dist/spain_housing-0.1.0-py3-none-any.whl"
cd "$work_root"
env -u PYTHONPATH "$work_root/map-env/bin/python" -c \
  'import spain_housing; print(spain_housing.__file__)'
env -u PYTHONPATH "$work_root/map-env/bin/spain-housing" inspect-release \
  --release "$release_dir" --allow-synthetic
```

The import must resolve to this environment's site-packages. Repeat evaluation,
replay and serve with that installed executable and absolute paths. Serve uses
its own interpreter and installed launcher. For core-only verification, export
requirements without `--extra map`, install in a separate new environment, and
exercise help/validate/evaluate/replay; `serve` must explain the missing extra.
Do not use an environment where Streamlit was already installed to prove this.

## 6. Observed input prerequisites and geography-only restoration

The selected observed recipe `configs/sources/expanded.yaml` has 16 verified
municipality identities and original three-city core. Its current market decisions
are restricted/unresolved and it deliberately refuses publication. Do not enable
synthetic permission to bypass observed rights or fill its 48 market cells.
Provide permitted retained purchase/whole-home products across expansion areas,
and the original Madrid/Barcelona/Jaén room core, with exact source periods,
definitions, permission scope and retained original bytes. Additional rooms and
segments can remain explicitly partial.

Retained permitted official geography is at `data/raw/expanded-geography` with
capture sidecars; processed files are at `data/processed/expanded-geography`.
Archive raw bytes together with `expanded.yaml` and the code/lock. Verify a restored
bundle offline with the existing geography command:

```bash
uv run --locked --extra map python scripts/verify_pilot_geography.py \
  --config configs/sources/expanded.yaml --data-root data/raw/expanded-geography \
  --output-root data/processed/restored-expanded-geography
```

This produces official geography only, not market prices or an observed release.
Capture hashes/time identify the IGN snapshot; reference metadata alone cannot
restore missing raw bytes. Acquisition reproduction, dataset rebuild and economic
replay are separate claims.

## 7. Explicit source update and rollback

1. Check only selected products at their actual cadence (monthly prices, quarterly
   room report); acquire only authorized inputs and retain original bytes.
2. Review column/locale/period/unit/statistic/basis/segment/methodology changes.
   Record exact crosswalks, captures, versions and legitimate gaps in a new recipe.
3. Build/validate/inspect into a new immutable release. Run the room/growth checks
   and UI/CLI parity before selecting it. A preparation failure leaves old releases
   intact. No missing-price conversion rescues malformed input.
4. Stop/restart against the new explicit release; keep scenario/base/profile policy
   unchanged unless the user deliberately changes it.
5. Roll back by restarting against the old intact release and saved scenario.
   Replay old runs only with their original code/runtime, not today's checkout.

| Error | Owner / corrective action |
|---|---|
| Restricted/unresolved source use | Recipe/permission decision; supply documented authorized inputs |
| Capture hash/size or login HTML | Restore original bytes; do not edit checksum to hide corruption |
| CSV column/width/value/period/profile/unit drift | Capture/row/profile diagnostic; review extraction/selected definition before building |
| Registry/geometry mismatch | Verify code/control/full feature/version; no repair or guessing |
| Coverage/payload hash contradiction | Restore complete validated release; no in-place editing |
| Missing/unsupported scenario input | Inspect report then selection policy/segment/freshness; no automatic fallback |
| Replay release/code/runtime mismatch | Restore matching release, code and environment or evaluate a new run |
| Missing map extra / occupied port | Install optional map dependencies / select an unused port |

Next essential extension is saving in A and buying in B, with explicit
purchase-time income assumptions and the existing independent binding/service
boundaries. Salary realism and historical modelling remain later work.
