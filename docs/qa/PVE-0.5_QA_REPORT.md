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

## Validated CI Evidence
- Workflow: PVE CI
- Run number: 180
- Run ID: `29182662530`
- Job: `validate-repository`
- Validated commit: `bae91d28000c8f54a97aaf23190b1e692f09106d`
- Status: completed
- Conclusion: success
- Workflow steps: all passed
- Tests run: 42
- Tests passed: 42
- Failures: 0
- Errors: 0

## Scope Exclusions
- No supplier allocation
- No supplier ranking
- No autonomous technical approval
- No final integration contract
- No decision-package export
- No PVE-0.6 functionality

## QA Status
**Pass** — PVE-0.5 implementation and all 42 automated tests passed PVE CI run #180.

## Release Recommendation
PVE-0.5 is ready for review and merge after the final QA commit passes CI. PVE-0.6 may begin only after PVE-0.5 is merged into `main`.
