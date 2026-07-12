# PVE-1.0.1 QA Report

## Build
PVE-1.0.1 — Foundation and Persistence

## Status
QA Pass — ready to be marked ready for review

## Objective
Create a tested SQLite persistence and project-service foundation without changing current analytical engines or public Streamlit behavior.

## Architecture
- `Database` manages SQLite connections, transactions, foreign keys, and WAL mode.
- `migrations.py` provides schema initialization with version recording only.
- The current implementation does not claim sequential future-migration support.
- Repository classes isolate SQL from application and analytical layers.
- `ProjectService` exposes project lifecycle operations.
- Immutable records are protected by database triggers.

## Database Tables
- `schema_migrations`
- `projects`
- `project_datasets`
- `threshold_profiles`
- `scenarios`
- `decision_snapshots`
- `export_records`

## Immutability Controls
Database triggers reject update and delete operations on:
- `project_datasets`
- `threshold_profiles`
- `scenarios`
- `decision_snapshots`

Project records remain metadata-editable and archiveable. Historical evidence remains retained through restrictive foreign keys.

## Cross-Project Integrity Controls
Repository validation rejects:
- scenarios linked to a dataset from another project
- scenarios linked to a project-specific threshold profile from another project
- decisions linked to a scenario from another project
- decisions linked to a dataset from another project
- decisions linked to a project-specific threshold profile from another project
- decisions whose dataset differs from the scenario dataset
- decisions whose threshold profile differs from the scenario threshold profile

Global threshold profiles remain valid across projects when their `project_id` is `NULL`.

## Test Coverage Added
- schema initialization
- repeatable schema initialization
- foreign-key enforcement
- project create/read/update/archive/list
- application-service validation
- dataset version increments and duplicate detection
- threshold version increments
- dataset immutability
- threshold immutability
- scenario immutability
- decision-snapshot immutability
- missing-parent rejection
- export-to-decision linkage
- temporary database isolation
- seven cross-project and scenario-consistency rejection tests

## Test Result
- Previous total: 60
- Initial persistence tests: 18
- Corrective integrity tests: 7
- Total: 85
- Passed: 85
- Failures: 0
- Errors: 0

## Governance Preservation
The original contents of the following files were restored before appending PVE-1.0.1 records:
- `ACTIVITY_LOG.md`
- `BUILD_HISTORY.md`
- `VERSION_MANIFEST.md`

Historical branches, commit SHAs, workflow details, job names, acceptance results, scope boundaries, recovery records, and closure evidence remain preserved.

## Preserved Controls
- deterministic decision logic
- engineering validation requirement
- no autonomous technical approval
- synthetic-data disclaimer
- non-production disclaimer
- draft integration contract
- AI Procurement Copilot separation
- existing Streamlit behavior

## Explicit Exclusions
No dashboard UI, upload, CSV parsing, configurable threshold UI, decision-history UI, authentication, external database, PDF or Excel extraction, ERP integration, supplier workflow, AI approval, or new packaging category.

## Budget
- Approved PVE-1.0.1 allocation: 13 hours
- Revised estimated implementation effort used: 14.5 hours
- Estimated remaining program budget: 75.5 hours

## Validated CI Evidence
- Workflow: PVE CI
- Run number: 352
- Run ID: `29187803058`
- Validated commit: `45df68e769018ddc6aa83cb383fa477ea8504419`
- Job: `validate-repository`
- Status: completed
- Conclusion: success
- All workflow steps: passed

## QA Result
**Pass**

## Merge Rule
Keep PR #17 as draft until review approval. Do not merge automatically. Merge only after review of every changed file.
