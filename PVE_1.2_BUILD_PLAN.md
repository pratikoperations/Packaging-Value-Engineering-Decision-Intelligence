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
| 4 | Compression, stacking, environment and line screening | 12 | 41 | 55.4% | Not started |
| 5 | Material, pallet, logistics and sustainability analysis | 11 | 52 | 70.3% | Not started |
| 6 | Should-cost, failure cost and implementation economics | 9 | 61 | 82.4% | Not started |
| 7 | Recommendation, confidence and immutable persistence | 7 | 68 | 91.9% | Not started |
| 8 | Demonstration cases, regression testing and release QA | 6 | 74 | 100% | Not started |

## Completed Build 1
Locked corrugated-only architecture, deterministic-calculation governance, sourced-threshold rules, source classification, approval boundaries, persistence intent, risks, exclusions, and acceptance gates.

## Completed Build 2
Implemented configuration-driven corrugated baseline/proposed specifications, style and converting profiles, sourced tolerances, artwork/compliance fields, transparent comparison, and upload/template compatibility.

## Completed Build 3
Implemented:
- corrugated technical requirement profiles without inferred thresholds;
- full-context evidence matching and validity checks;
- wrong-project, wrong-specification, wrong-supplier, wrong-site, expired, superseded, and conflict detection;
- distinct source classifications;
- supplier capability assessment limited to compatible, incompatible, or evidence missing;
- evidence-confidence classifications based on evidence quality only;
- additive normalization for evidence and capability records;
- regression coverage for JSON, CSV-compatible normalization, and Excel generation.

Build 3 validation:
- Functional head: `b818901eb35a851f9015d7f15d8eb8eee9cd2aa5`.
- PVE CI #779, run `29308208791`, success.
- 243 tests passed, 0 failures, 0 errors.

## Later-build intent

### Build 4 — Compression, stacking, environment and line screening
Compare supplied evidence with project-defined requirements and add environmental, stacking, and packing-line blockers. No unsourced universal BCT prediction.

### Build 5 — Material, pallet, logistics and sustainability analysis
Add deterministic material, simple pallet orientation, pallet movement, logistics, and physical sustainability indicators.

### Build 6 — Should-cost, failure cost and implementation economics
Add explicit damage, MOQ, working capital, transition stock, obsolescence, tooling, artwork, trial, benefit, and payback scenarios.

### Build 7 — Recommendation, confidence and immutable persistence
Add engineering recommendation for review, confidence separation, append-only technical assessments, archive protection, and project isolation.

### Build 8 — Demonstration cases, regression and release QA
Add synthetic cases, full regression, release evidence, documentation, and closure validation.

## Release acceptance gates
1. Scope remains corrugated-only.
2. Calculations remain deterministic and explainable.
3. Thresholds remain sourced, versioned, applicable, and traceable.
4. Assumptions remain explicit.
5. Source classifications remain distinct.
6. Technical/compliance blockers override commercial attractiveness.
7. Engineering validation and human approval remain mandatory.
8. Autonomous approval remains prohibited.
9. Historical records remain immutable and project-scoped.
10. Complete tests and current-head CI pass before closure.
11. PR #26 remains draft and unmerged until separate authorization.

## Build authorization rule
Completion of Build 3 does not authorize Build 4. Build 4 is not started or authorized.
