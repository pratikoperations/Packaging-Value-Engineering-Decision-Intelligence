# PVE 1.2 Controlled Build Plan

## Release
PVE 1.2 — Corrugated Packaging Engineering and Validation Intelligence

## Budget control
- Planned effort: 74 hours.
- Controlled contingency: 2 hours.
- Absolute cap: 76 hours.
- Contingency is restricted to regression, CI, migration compatibility, integration defects, or release-evidence repair; it cannot fund new scope.

## Build sequence

| Build | Scope | Hours | Cumulative hours | Release completion | Status |
|---|---|---:|---:|---:|---|
| 1 | Architecture, governance and engineering boundary lock | 8 | 8 | 10.8% | Complete and validated |
| 2 | Corrugated specification, style and tolerance model | 11 | 19 | 25.7% | Complete and validated |
| 3 | Technical requirements, evidence and supplier capability | 10 | 29 | 39.2% | Complete and validated |
| 4 | Compression, stacking, environment and line screening | 12 | 41 | 55.4% | Complete and validated |
| 5 | Material, pallet, logistics and sustainability analysis | 11 | 52 | 70.3% | Complete and validated |
| 6 | Should-cost, failure cost and implementation economics | 9 | 61 | 82.4% | Complete and validated |
| 7 | Recommendation, confidence and immutable persistence | 7 | 68 | 91.9% | Not started |
| 8 | Demonstration cases, regression testing and release QA | 6 | 74 | 100% | Not started |

## Completed Builds 1–5
Builds 1–5 established corrugated-only governance, specification and tolerance models, evidence and supplier compatibility, supplied-evidence technical screening, line/environment blockers, material analysis, simple pallet comparisons, explicit logistics scenarios, and physical sustainability indicators.

## Completed Build 6
Implemented:
- explicit supplied should-cost components for board/paper, conversion, printing, coating/treatment, manufacturing waste, quality inspection, and freight;
- no inferred market prices, supplier margins, paper prices, conversion rates, or waste percentages;
- baseline/proposed expected failure-cost scenarios using annual cases, damage rate, and loss per damaged case;
- distinct and traceable source classification/reference for all commercial inputs;
- risk-adjusted annual benefit equal to gross annual benefit minus incremental expected failure cost;
- explicit inventory days, MOQ/batch, transition stock, obsolete stock, write-off, and incremental working-capital scenarios;
- one-time tooling, artwork, trial, and implementation costs with duplicate-component protection;
- first-year net benefit and payback months;
- available, unavailable, and technically blocked outputs with supporting inputs, assumptions, limitations, and blocking conditions;
- additive normalization for `should_cost_inputs`, `failure_cost_inputs`, `inventory_inputs`, and `one_time_costs`.

Build 6 validation:
- Functional head: `01bc744f90e820a6364c90b55eb1b38a02572a67`.
- PVE CI #819, run `29309084978`, success.
- 282 tests passed, 0 failures, 0 errors.

Build 6 does not implement engineering recommendation persistence, database migrations, immutable technical-assessment records, role-based approval, autonomous approval, or Build 7 functionality.

## Later-build intent

### Build 7 — Recommendation, confidence and immutable persistence
Add engineering recommendation for review, keep evidence confidence separate from technical outcome, add append-only technical assessments, archive protection, and cross-project isolation.

### Build 8 — Demonstration cases, regression and release QA
Add synthetic cases, full regression, release evidence, documentation, and closure validation.

## Release acceptance gates
1. Scope remains corrugated-only.
2. Calculations remain deterministic and explainable.
3. Thresholds and commercial inputs remain sourced, explicit, and traceable.
4. Assumptions remain explicit.
5. Source classifications remain distinct.
6. Technical/compliance blockers override commercial, economic, material, logistics, and sustainability benefits.
7. Engineering validation and human approval remain mandatory.
8. Autonomous approval remains prohibited.
9. Historical records remain immutable and project-scoped.
10. Complete tests and current-head CI pass before closure.
11. PR #26 remains draft and unmerged until separate authorization.

## Build authorization rule
Completion of Build 6 does not authorize Build 7. Build 7 is not started or authorized.
