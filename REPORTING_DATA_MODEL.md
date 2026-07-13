# Reporting Data Model

## Modelling Principle
Use a star schema optimized for executive analysis while retaining exact links to authoritative PVE records.

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

## Required Traceability
Every fact must preserve the relevant project, scenario, dataset-version, threshold-version, alternative, source-record, and generated-at identifiers.

## Authoritative Logic Rule
Python outputs are authoritative. Power BI measures aggregate stored outcomes and must not independently recalculate qualification, risk, eligibility, or recommendation status.

## Core Measures
- evaluated projects
- evaluated alternatives
- baseline annual cost
- proposed annual cost
- potential annual savings
- savings percentage
- technically qualified alternatives
- critical-risk alternatives
- recommended-for-review decisions
- blocked decisions
- insufficient-data decisions

## Data Quality Rules
- no orphan facts
- no cross-project references
- immutable source identifiers
- one declared dataset-defined baseline per governed dataset
- reconciliation totals must match Python outputs exactly