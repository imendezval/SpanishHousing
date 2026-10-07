# Phase 3 progress

Current milestone: M2. M1 verified. Initial worktree has user-owned untracked `AGENTS.md`, Phase 2 and Phase 3 guides; preserved and excluded from commits.

Baseline `b523385`: locked sync passed. The full gate initially failed on README Python-block formatting as predicted by the guide. Locked `ruff format README.md` repaired it, then `bash scripts/check.sh` passed all 136 tests, strict mypy, Ruff and seven import contracts. Finance and scenario behavior are unchanged.

M1 release/capture/recipe contracts and shared storage boundary are implemented. Full locked gate: 145 tests, strict mypy, formatting/lint and eight import contracts pass; sensitivity tests prove finance-to-storage and storage-to-ingestion violations are detected. Added Shapely for topology and openpyxl for the selected official INE XLSX, with their type stubs and reviewed single lockfile update. M2–M6 pending. A1 verified; A2 market route blocked; remaining acceptance pending.

Bounded source review: Idealista general terms restrict automated/manual copying without written permission. The reviewed API/export page invites a contract/contact route but establishes no permission for this dataset. Market acquisition/local use/redistribution are unresolved or restricted; do not capture its data into a new release. September 2026 report is still explicitly labelled September. Official IGN metadata/license, queryables and actual items were inspected; Barcelona municipality and province are distinct features. INE's current operation links a 2026 XLSX and in-year changes; acquisition/reconciliation next.

Next: source decision record, retained-input normalization and permitted official geography acquisition. Complete independent storage/query/CLI work despite the market blocker. Historical audit remains unchanged.
