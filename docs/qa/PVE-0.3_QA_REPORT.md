# PVE-0.3 QA Report

## Build
PVE-0.3 — Cost and Material Engine

## Status
Completed and merged

## Scope
Deterministic material and commercial calculations for the existing synthetic corrugated shipping-case dataset.

## Implemented Calculations

### Material Engine
- Declared case weight by alternative
- Sum of declared component weights
- Component-to-case weight variance
- Annual material mass in kilograms
- Material change in grams versus baseline
- Material change percentage versus baseline

### Cost Engine
- Aggregated declared unit-cost inputs by alternative
- Annual cost at declared annual volume
- Unit savings versus baseline
- Annual savings versus baseline
- Cost change percentage versus baseline

## Guardrails
- Exactly one baseline is required
- Alternative identifiers must be unique
- Annual volume must be positive and use `cases_per_year`
- Material weights must be positive
- Every alternative must have material components and cost inputs
- Cost currency and unit must match the project currency
- Baseline unit cost must be greater than zero
- Calculations are deterministic and use declared inputs only

## Validated CI Evidence
- Workflow: PVE CI
- Run number: 108
- Run ID: `29181583399`
- Job: `validate-repository`
- Validated PR commit: `847be5db56b413ec49868c50ea58092686555a5c`
- Status: completed
- Conclusion: success
- Workflow steps: all passed
- Tests run: 18
- Tests passed: 18
- Failures: 0
- Errors: 0

## Merge Record
- Pull request: PR #5
- PR status: Merged and closed
- Merge method: Squash merge
- Merge commit: `de9d18a428274bfafd369e7509f88b20bc33db89`
- Stable branch: `main`
- Original feature branch: Deleted

## Scope Exclusions
- No application UI
- No technical qualification or risk rules
- No recommendation scoring
- No supplier ranking or allocation
- No logistics optimization
- No scenario or sensitivity engine
- No autonomous technical approval
- Integration contract remains draft

## QA Status
**Pass** — PVE-0.3 implementation and all 18 automated tests passed PVE CI run #108 and were merged through PR #5.

## Release Recommendation
PVE-0.3 is complete. PVE-0.4 is the next approved build after this closure PR is merged into `main`.
