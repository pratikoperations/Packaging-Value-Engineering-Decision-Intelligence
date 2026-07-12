# PVE-0.5 QA Report

## Build
PVE-0.5 — Scenario and Recommendation UI

## Scope
Deterministic scenario assumptions, transparent packaging-alternative comparison, explainable recommendation rules, and a lightweight Streamlit demonstration UI.

## Scenario Rules
- Annual volume is an explicit positive scenario input.
- Unit-cost and material-weight adjustments are explicit by alternative.
- Unspecified adjustments default visibly to 0%.
- Adjustments must remain between -50% and +100%.
- Unknown alternative identifiers are rejected.
- Scenario calculations reuse the validated deterministic cost and material engines.
- Every result includes its applied assumptions.

## Recommendation Rules
- Recommendations apply to packaging alternatives, not suppliers.
- Technical failure or critical risk produces `not_recommended`.
- Incomplete technical qualification produces `insufficient_data`.
- No positive savings and no material reduction produces `not_recommended`.
- Conditional qualification, high risk, incomplete risk data, or open validation produces `conditionally_recommended`.
- Fully qualified, complete, non-high-risk alternatives with value improvement produce `recommended`.
- Preferred-alternative ordering is transparent: recommendation status, annual savings, material reduction, risk, then stable identifier.
- No opaque weighted score, supplier ranking, allocation, or autonomous technical approval is used.

## UI Scope
- Synthetic demo-data loading
- Annual-volume scenario input
- Alternative-level cost and material assumptions
- Side-by-side cost, material, qualification, risk, and recommendation comparison
- Preferred-alternative display
- Expandable rationale, constraints, and validation requirements
- Explicit engineering-approval disclaimer

## Automated Tests
Twelve new tests cover:
1. Base scenario consistency
2. Annual-volume sensitivity
3. Cost adjustment
4. Material adjustment
5. Unknown alternative rejection
6. Adjustment-bound validation
7. Demo insufficient-data recommendation
8. Qualified low-risk recommendation
9. Technical-failure rejection
10. Critical-risk rejection
11. Conditional qualification handling
12. Incomplete-risk conditional recommendation

Existing tests remain in scope. Expected total automated test count: 42.

## Scope Exclusions
- No supplier allocation
- No supplier ranking
- No autonomous technical approval
- No final integration contract
- No decision-package export
- No PVE-0.6 functionality

## QA Status
**Conditional Pass** — implementation and test coverage are complete; final status depends on successful PVE CI and full PR-diff review.

## Release Recommendation
Open a draft PR. PVE-0.6 may begin only after PVE-0.5 passes CI and QA and is merged into `main`.
