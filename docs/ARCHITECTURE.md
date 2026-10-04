# Architecture

The installable `src/spain_housing` package keeps validated contracts in `models`, configuration file handling in `config`, and the CLI in `cli`. `finance`, `markets`, `ingestion`, `application`, and `ui` are reserved namespaces until their scheduled phases. Import Linter enforces their dependency direction.

Saving and buying locations are separate bindings in every scenario. Dates and periods are explicit. Market observations carry measure, segment, provenance, and status. Synthetic fixtures live only under `tests/fixtures/synthetic`; observed source evidence lives in `data/manifests/coverage_audit.csv`.

The future financial engine receives prepared monthly budgets; it does not read configuration, fetch market data, or infer geography. Market-data and purchase-cost protocols mark replaceable boundaries without committing to providers or policies yet.

`Scenario` stores the first saving month, positive horizon, dated market policy, and two location bindings. The purchase month is derived, never separately editable. Income milestones are annual net euros; the examples choose linear interpolation. Debt and household expenses use monthly euros and step paths in the examples. Each path records its own linear/step choice and plateaus after its last milestone. Phase 1 validates these choices but does not expand paths into cash flows. Floating-point money is finite, with rounding reserved for presentation.

`config.py` owns YAML/JSON parsing and recursive defaults → saved-scenario merging. Lists replace lists, and explicit nulls do not inherit defaults. `models` owns all domain validation. The CLI delegates to both and only validates; no command advertises evaluation or data collection yet. Runtime paths and credentials are excluded from economic scenario records.

`MarketQuery` is period/segment-aware; `MarketObservation` distinguishes source-published, estimated and synthetic evidence. Its metric determines the legal unit. `MarketLookup` and output indicators keep missing/unsupported states separate from numeric zero. A `RunResult` binds a resolved scenario to release, schema, model and code identifiers. Future release readers implement `MarketData`; purchase-cost policies implement `PurchaseCostPolicy`.
