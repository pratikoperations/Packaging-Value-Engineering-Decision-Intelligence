# PVE-0.3 QA Report

## Build
PVE-0.3 — Cost and Material Engine

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
- Run number: 98
- Run ID: `29181336986`
- Job: `validate-repository`
- Validated commit: `da769f756cd6a5edfd38e61fc8176642c51c41d9`
- Status: completed
- Conclusion: success
- Workflow steps: all passed
- Tests run: 18
- Tests passed: 18
- Failures: 0
- Errors: 0

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
**Pass** — PVE-0.3 implementation and all 18 automated tests passed PVE CI run #98.

## Release Recommendation
PVE-0.3 is ready for review and merge after the final QA commit passes CI. PVE-0.4 may begin only after PVE-0.3 is merged into `main`.
