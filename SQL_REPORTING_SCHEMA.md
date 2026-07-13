# SQL Reporting Schema

## Purpose
Define PostgreSQL as a read-only reporting mirror without changing the authoritative SQLite persistence or PVE analytical logic.

## Fixed Architecture
- SQLite remains the operational source of truth.
- PostgreSQL stores reporting projections only.
- No operational persistence migration is authorized.
- Power BI receives SELECT access to approved reporting views only.

## Proposed Schemas
- `pve_reporting` — dimensions, facts, and approved reporting views
- `pve_audit` — load, reconciliation, lineage, and failure records

## Dimensions
- `dim_date`
- `dim_project`
- `dim_alternative`
- `dim_dataset_version`
- `dim_threshold_profile`
- `dim_scenario`
- `dim_decision_status`
- `dim_risk_category`

## Facts
- `fact_scenario_result`
- `fact_cost_analysis`
- `fact_technical_qualification`
- `fact_risk_assessment`
- `fact_business_threshold_result`
- `fact_decision_snapshot`

## Audit Tables
- `reporting_load_run`
- `reporting_reconciliation_result`
- `reporting_source_lineage`
- `reporting_load_error`

## Reporting Views
- `vw_executive_project_summary`
- `vw_cost_savings_analysis`
- `vw_alternative_comparison`
- `vw_technical_qualification`
- `vw_risk_exposure`
- `vw_scenario_history`
- `vw_decision_history`

## Technical Rules
- surrogate keys for reporting relationships
- authoritative SQLite source IDs retained as alternate keys
- foreign-key enforcement
- UTC timestamps
- append-only treatment for immutable decision evidence
- idempotent reporting loads
- indexed project, scenario, dataset, threshold, and alternative references
- no cross-project references
- incomplete or unreconciled loads never become reportable
- Power BI service identity receives SELECT permission only on approved views

## Data Ownership
- Python and SQLite own operational truth.
- PostgreSQL owns only the reporting projection and load audit.
- Power BI owns presentation and aggregation only.

## Explicit Non-Goals
No SQLite replacement, no dual-write operational workflow, no API, no ERP integration, no supplier portal, and no enterprise persistence design.