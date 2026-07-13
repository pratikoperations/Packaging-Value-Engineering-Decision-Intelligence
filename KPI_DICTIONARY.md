# KPI Dictionary

## Purpose
Define each executive KPI so Power BI reports authoritative PVE outcomes without introducing conflicting business logic.

| KPI | Business Definition | Source | Calculation Rule | Unit | Key Filters / Exclusions | Reconciliation |
|---|---|---|---|---|---|---|
| Evaluated Projects | Distinct projects with at least one governed scenario result | `fact_scenario_result` | Distinct authoritative project IDs | Count | Respect project isolation | Match Python project count |
| Evaluated Alternatives | Distinct non-baseline alternatives evaluated | `fact_scenario_result` | Distinct alternative IDs excluding declared baseline | Count | Exclude dataset-defined baseline | Match Python alternative count |
| Baseline Annual Cost | Stored annual cost for declared dataset baseline | `fact_cost_analysis` | Sum stored baseline annual cost | Currency | One declared baseline per dataset | Exact match to Python |
| Proposed Annual Cost | Stored annual cost for evaluated alternative | `fact_cost_analysis` | Sum stored proposed annual cost | Currency | Current scenario and alternative context | Exact match to Python |
| Potential Annual Savings | Difference between stored baseline and proposed annual cost | `fact_cost_analysis` | Aggregate stored savings outcome; do not recreate cost engine logic | Currency | Exclude baseline as recommendation | Exact match to Python |
| Savings Percentage | Stored savings relative to baseline annual cost | `fact_cost_analysis` | Use governed stored percentage or controlled aggregation from stored totals | Percent | Handle zero baseline explicitly | Exact match within defined rounding |
| Technically Qualified Alternatives | Alternatives with authoritative qualified status | `fact_technical_qualification` | Count stored qualified outcomes | Count | No DAX requalification | Exact status match |
| Critical-Risk Alternatives | Alternatives with authoritative critical-risk status | `fact_risk_assessment` | Count stored critical-risk outcomes | Count | No DAX risk scoring | Exact status match |
| Recommended-for-Review Decisions | Decision snapshots with authoritative recommendation-for-review status | `fact_decision_snapshot` | Count stored statuses | Count | Never label as approval | Exact status match |
| Blocked Decisions | Authoritative blocked outcomes | `fact_decision_snapshot` | Count stored blocked statuses | Count | Include reason on drill-through | Exact status match |
| Insufficient-Data Decisions | Authoritative insufficient-data outcomes | `fact_decision_snapshot` | Count stored insufficient-data statuses | Count | No inferred completion | Exact status match |

## Governance Rules
- Python outputs are authoritative.
- DAX may aggregate but must not recreate qualification, risk, eligibility, threshold, or recommendation logic.
- Currency, rounding, and sign conventions must match PVE output conventions.
- Each KPI must show project, scenario, dataset, threshold, and generated-at context where relevant.
- Any deterministic variance blocks release.

## Ownership
- Business definition owner: Procurement / Packaging project owner
- Analytical truth owner: Existing PVE Python logic
- Reporting implementation owner: Power BI edition maintainer
- Reconciliation owner: QA reviewer