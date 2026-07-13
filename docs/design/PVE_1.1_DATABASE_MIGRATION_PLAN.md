# PVE 1.1 Additive Database Migration Plan

## Current Constraint
The current `src/persistence/migrations.py` initializes schema version 1 idempotently but explicitly does not provide ordered sequential migrations. PVE 1.1 therefore requires a controlled upgrade to ordered, additive migrations before any new persistence is used.

## Migration Strategy
- Keep schema version 1 unchanged as the historical baseline.
- Add version 2 as an ordered, idempotent migration.
- Record each applied version in `schema_migrations`.
- Apply migrations in ascending order inside transactions.
- Never drop, rename, rewrite, or bulk-update existing immutable tables.
- Back up the SQLite file before applying version 2 in non-test environments.

## Additive Project Metadata
Add nullable columns to `projects` so existing rows remain valid:
- `objective TEXT`
- `change_type TEXT`
- `product_sku TEXT`
- `business_unit_plant TEXT`
- `project_owner TEXT`
- `volume_unit TEXT`
- `current_unit_cost REAL`
- `proposed_unit_cost REAL`
- `current_supplier TEXT`
- `proposed_supplier TEXT`
- `target_saving REAL`
- `target_completion_date TEXT`
- `implementation_cost REAL`
- `testing_cost REAL`
- `tooling_cost REAL`
- `qualification_cost REAL`
- `expected_realization_percent REAL`
- `project_description TEXT`
- `business_justification TEXT`
- `sustainability_objective TEXT`

Existing PVE 1.0 rows retain their current `category`, `currency`, and `annual_volume`. New PVE 1.1 project creation validates category, objective, change type, and common mandatory metadata at the service layer.

## New Tables

### `project_intake_values`
Stores normalized field-level intake facts without rewriting immutable datasets.
- intake value ID
- project ID
- baseline/proposed context
- field key
- normalized value and unit
- source classification
- evidence reference
- supplier name
- test date
- validation status
- created timestamp

Source classification allowed values:
- uploaded_fact
- manually_entered_fact
- supplier_declared
- laboratory_tested
- predicted
- assumption

### `document_register`
Stores metadata only; no document interpretation.
- document ID
- project ID
- document type/name
- category
- baseline/proposed context
- supplier
- document date
- valid-until date
- filename/reference
- verification status
- requirement level
- upload status
- reviewer comments
- created timestamp

### `readiness_assessments`
Stores traceable assessment snapshots.
- assessment ID
- project ID
- dataset ID nullable
- category/objective/change type
- weighted component JSON
- blockers JSON
- available outputs JSON
- unavailable outputs JSON
- stage status
- readiness percentage
- engine version
- source commit
- created timestamp

### `testing_checklists`
Stores generated checklist snapshots.
- checklist ID
- project ID
- category/objective/change type
- checklist JSON
- generated timestamp
- source commit

## Immutability and Protection
- Existing triggers on `project_datasets`, `threshold_profiles`, `scenarios`, and `decision_snapshots` remain unchanged.
- New readiness assessments and testing checklists are append-only and receive update/delete prevention triggers.
- Document-register metadata may be corrected only while a project is active; archived projects are read-only.
- Intake values may be superseded through new records or a new immutable dataset version; historical records are not overwritten after assessment capture.

## Foreign Keys and Isolation
- Every new record carries `project_id` with `ON DELETE RESTRICT`.
- Repository methods verify active-project ownership before writes.
- Dataset-linked readiness records must reference a dataset belonging to the same project.
- Cross-project references are rejected in both service and repository layers.

## Rollback Position
Version 2 is additive. Automated rollback is not promised. Recovery is by restoring the pre-migration SQLite backup. Failed migration transactions must leave schema version 1 intact.

## Acceptance Evidence
- Fresh database reaches version 2.
- Existing version-1 database upgrades to version 2 without data changes.
- Historical dataset/scenario/decision hashes and row contents remain identical.
- Existing 179 tests pass.
- New migration, foreign-key, immutability, and archive-protection tests pass.
