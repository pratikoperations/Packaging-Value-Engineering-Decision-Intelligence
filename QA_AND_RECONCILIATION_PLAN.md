# QA and Reconciliation Plan

## Objective
Prove that Power BI faithfully reports authoritative PVE outputs and does not alter decision logic.

## Reconciliation Checks
- project counts
- dataset, scenario, and threshold version counts
- baseline and proposed annual cost
- potential savings and savings percentage
- technical qualification outcomes
- risk severity and critical-risk counts
- threshold outcomes
- recommendation-for-review status
- decision snapshot references and timestamps

## Acceptance Standard
For deterministic totals and statuses, Power BI must match Python outputs exactly. Any variance blocks release.

## Test Scenarios
- qualified, low-risk alternative
- critical-risk alternative
- not-qualified alternative
- insufficient-data alternative
- business-threshold failure
- dataset-defined baseline exclusion
- archived project with readable history and prohibited new writes
- two projects with intentionally similar identifiers to test isolation

## Manual Calculation Checks
At least five representative scenarios must be independently calculated from source inputs and compared with Python, SQL reporting views, and Power BI measures.

## Non-Functional QA
- refresh failure handling
- duplicate-load prevention
- filter and drill-through correctness
- row-level-security tests where enabled
- report performance
- synthetic-data disclosure
- no approval or production-grade overclaim

## Release Gate
No implementation release until reconciliation evidence, test results, known limitations, and sign-off are recorded.