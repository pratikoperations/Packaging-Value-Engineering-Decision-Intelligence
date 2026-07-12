# PVE-0.4 QA Report

## Build
PVE-0.4 — Technical Qualification and Risk

## Scope
Deterministic technical-qualification aggregation and deterministic quality, supply, and implementation risk indicators using the existing canonical synthetic dataset.

## Technical Qualification Rules
- Every packaging alternative is evaluated against every declared technical requirement.
- Exactly one result per alternative and requirement is permitted.
- `not_qualified` overrides every other technical status.
- Missing, `not_assessed`, or `insufficient_data` results produce `insufficient_data`.
- `conditionally_qualified` is returned only when no failure or insufficient-data condition exists.
- `qualified`, `conditionally_qualified`, and `not_qualified` require valid evidence.
- Missing evidence converts the result basis to `insufficient_data`.
- Open validation activities and requirement gaps are returned explicitly as `validation_required` outputs.

## Risk Rules
- Quality, supply, and implementation are the required risk categories.
- Missing categories are reported as `not_recorded`; no hidden defaults are used.
- Probability bands are deterministic: <25 low, 25–49.999 medium, 50–69.999 high, >=70 critical.
- Effective risk is the higher of declared severity and probability-band severity.
- Multiple records in one category use the highest effective level.
- High and critical risks create explicit mitigation-and-validation actions.
- Overall risk is the highest effective recorded category; data completeness is reported separately.

## Automated Tests
Twelve new tests cover:
1. Demo insufficient-data technical outcome
2. Fully qualified technical outcome
3. Conditional qualification
4. Technical failure precedence
5. Missing qualification evidence
6. Duplicate technical result rejection
7. High demo quality risk
8. Explicit missing risk categories
9. Probability escalation
10. Complete low-risk set
11. Invalid probability rejection
12. Highest duplicate-category risk selection

Existing tests remain in scope. Expected total automated test count: 30.

## Scope Exclusions
- No application UI
- No recommendation scoring
- No supplier ranking or allocation
- No scenario or sensitivity engine
- No autonomous technical approval
- No final integration contract
- No PVE-0.5 functionality

## QA Status
**Conditional Pass** — implementation and test coverage are complete; final status depends on successful PVE CI and full PR-diff review.

## Release Recommendation
Open a draft PR. PVE-0.5 may begin only after PVE-0.4 passes CI and QA and is merged into `main`.
