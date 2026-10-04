# Architecture

The installable `src/spain_housing` package keeps validated contracts in `models`, configuration file handling in `config`, and the CLI in `cli`. `finance`, `markets`, `ingestion`, `application`, and `ui` are reserved namespaces until their scheduled phases. Import Linter enforces their dependency direction.

Saving and buying locations are separate bindings in every scenario. Dates and periods are explicit. Market observations carry measure, segment, provenance, and status. Synthetic fixtures live only under `tests/fixtures/synthetic`; observed source evidence lives in `data/manifests/coverage_audit.csv`.

The future financial engine receives prepared monthly budgets; it does not read configuration, fetch market data, or infer geography. Market-data and purchase-cost protocols mark replaceable boundaries without committing to providers or policies yet.
