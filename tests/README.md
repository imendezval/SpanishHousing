# Test suite

Run the complete suite with the locked map dependencies, which are also needed
by CLI subprocesses and Streamlit AppTest:

```bash
uv run --locked --extra map pytest
bash scripts/check.sh
```

`scripts/check.sh` is the existing full gate: lock, formatting, lint, typing,
production import contracts and pytest. There is no separate testing framework.

## Where tests belong

| Location | Responsibility |
|---|---|
| `models/` | Scenario/market/result validation, strict types, evidence coherence and serialization contracts |
| `finance/` | Savings, mortgage and purchasing-capacity calculations; independent numeric references, feasibility and invalid public API inputs |
| `application/` | Input preparation, selection/projection, evaluation, evidence, complete/compact/detail parity and export/replay integration |
| `data/` | Source normalization, provenance, integrity, permissions, immutable releases, registry/topology and coverage |
| `data/test_atlas.py` | Independent canonical geography assembly and publication |
| `data/test_display.py` | Display fidelity, source-conflict treatment and geometry encodings |
| `data/test_demo.py` | Synthetic generation and geography-backed release composition |
| `application/test_geography_evaluate.py` | Hand-calculated financial reference using complete/partial geography-backed markets |
| `ui/test_controls.py` | Lossless scenario/draft conversion and participant trajectories |
| `ui/test_state.py` | Session isolation, atomic imports, bounded results/details and export invalidation |
| Other `ui/` tests | Map projection/picking/specification, AppTest controls, release/display transitions and UI/CLI parity |
| `test_config.py`, `test_scenario_cli.py` | Configuration loading and the installed validation command |
| `test_launcher.py` | Resource reuse, manifest changes, explicit payload revalidation, synthetic opt-in and server arguments |
| `test_architecture.py` | Selected forbidden direct/indirect edges checked against the actual repository import configuration |

For a focused run, select an owner or a behavior:

```bash
uv run --locked --extra map pytest tests/finance tests/models
uv run --locked --extra map pytest tests/data/test_display.py
uv run --locked --extra map pytest tests/ui -k 'export or display'
```

## Fixtures and boundaries

- Shared `recipe`, `release_dir`, `expanded_dir`, `scenario` and `atlas_dir`
  fixtures live in `conftest.py`. They remain function scoped: corruption,
  deletion and revalidation tests must never share mutable artifact directories.
- Fixture paths belong to `fixtures/__init__.py`; tests do not import
  `conftest.py` as a helper module. Builders stay under `fixtures/synthetic/`.
- Synthetic geometry and market inputs are self-authored test data. The
  attributed `fixtures/geography/ign_overlap/` extract is retained real source
  evidence. Normal pytest runs download nothing and need no national data bundle.
- AppTest verifies widget and session behavior. PyDeck specification tests check
  renderer inputs. Neither proves a browser painted polygons or met national
  performance targets; those executed checks are recorded in
  [Phase 7 progress](../docs/progress/PHASE_7.md).
- Keep expected financial constants independent of the implementation. Full,
  compact, detail, CLI and UI parity tests supplement those references; agreement
  between two paths alone cannot prove that the financial answer is correct.

## Review after Phase 7

The starting suite had **156 test functions expanding to 356 collected cases**.
Most extra cases are meaningful parameter combinations: numeric coercion,
nonfinite values, exact market selection, corruption and financial boundaries.
The count alone was not a reason to remove them.

The review retained all original regression cases and kept 356 collected cases.
It moved mixed-owner tests, shared atlas setup and consolidated repeated cache
assertions under the launcher. It also strengthened weak checks:

- Architecture probes now use the real `pyproject.toml` and require the intended
  contract to report `BROKEN`, rather than testing newly invented miniature rules.
- The display-transition AppTest now actually changes the injected display and
  verifies rendered identity, retained results and no extra financial call.
- Download preservation compares against a saved immutable payload, avoiding
  comparison of a mutable session object with itself after rerendering.
- Draft/default preservation takes independent snapshots; rent-sharing checks
  change the input; scenario serialization checks a complete canonical round trip.

Review verification: the full `scripts/check.sh` gate passes on Python 3.12 and
3.13, with 356 cases each. An isolated copy with the models-to-finance restriction
removed made its architecture probe fail as intended; production configuration
was unchanged.

Keep checks at distinct boundaries even when they use the same edge case. For
example, accepting zero in a validated result, calculating zero capacity and
displaying zero distinctly from missing data protect different behavior. Remove
an assertion only when another check demonstrably covers the same contract at
the same boundary. Avoid adding a new test merely to repeat an implementation.
