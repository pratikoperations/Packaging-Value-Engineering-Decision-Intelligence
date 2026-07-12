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

## Automated Tests
Eight new tests cover:
1. Baseline material totals
2. Alternative material reduction
3. Missing material components
4. Duplicate baseline
5. Baseline cost totals
6. Alternative savings
7. Currency mismatch
8. Missing cost inputs

The existing ten PVE-0.2 data-validation tests remain in scope, for a total expected test count of 18.

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
**Conditional Pass** — implementation and test coverage are complete; final status depends on successful PVE CI and full PR-diff review.

## Release Recommendation
Open a draft PR. PVE-0.4 may begin only after PVE-0.3 passes CI and QA and is merged into `main`.
