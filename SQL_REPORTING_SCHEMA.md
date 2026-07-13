# SQL Reporting Schema

## Purpose
Define a read-optimized reporting layer without changing the authoritative PVE analytical logic.

## Proposed Schemas
- `pve_core` — governed operational references exposed for integration
- `pve_reporting` — dimensions, facts, and read-only views for Power BI
- `pve_audit` — refresh, reconciliation, and lineage records

## Key Tables
### Dimensions
`dim_project`, `dim_alternative`, `dim_dataset_version`, `dim_threshold_profile`, `dim_scenario`, `dim_date`, `dim_decision_status`, `dim_risk_category`

### Facts
`fact_scenario_result`, `fact_cost_analysis`, `fact_technical_qualification`, `fact_risk_assessment`, `fact_business_threshold_result`, `fact_decision_snapshot`

### Audit
`reporting_load_run`, `reporting_reconciliation_result`, `reporting_source_lineage`

## Technical Rules
- surrogate keys for reporting relationships
- authoritative source IDs retained as alternate keys
- foreign-key enforcement
- UTC timestamps
- append-only treatment for immutable evidence
- indexed project, scenario, dataset, threshold, and alternative references
- Power BI service account receives SELECT access to approved views only

## Reporting Views
- `vw_executive_project_summary`
- `vw_cost_savings_analysis`
- `vw_alternative_comparison`
- `vw_technical_qualification`
- `vw_risk_exposure`
- `vw_scenario_history`
- `vw_decision_history`

## Migration Boundary
The first implementation design must decide whether the reporting database mirrors the current SQLite source or becomes the future shared persistence platform. No migration is authorized during planning.