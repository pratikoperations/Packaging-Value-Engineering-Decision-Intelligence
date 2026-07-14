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
| 6 | Should-cost, failure cost and implementation economics | 9 | 61 | 82.4% | Not started |
| 7 | Recommendation, confidence and immutable persistence | 7 | 68 | 91.9% | Not started |
| 8 | Demonstration cases, regression testing and release QA | 6 | 74 | 100% | Not started |

## Completed Build 1
Locked corrugated-only architecture, deterministic-calculation governance, sourced-threshold rules, source classification, approval boundaries, persistence intent, risks, exclusions, and acceptance gates.

## Completed Build 2
Implemented configuration-driven corrugated baseline/proposed specifications, style and converting profiles, sourced tolerances, artwork/compliance fields, transparent comparison, and upload/template compatibility.

## Completed Build 3
Implemented governed technical requirements, evidence matching and validity, source separation, supplier compatibility-only assessment, evidence confidence, and additive upload normalization.

## Completed Build 4
Implemented supplied BCT/ECT comparison, governed safety and derating factors, stacking/environment/warehouse screening, packing-line compatibility, blocker precedence, non-approval outcomes, and additive normalization. No prediction coefficients or universal engineering constants were added.

## Completed Build 5
Implemented:
- board area from supplied blank dimensions only, with no inferred geometry;
- supplied baseline/proposed case-weight, annual-material-consumption, and material-change comparisons;
- simple standard rectangular pallet orientations: length × width and width × length;
- cases per layer, validated layers, cases per pallet, footprint utilisation, pallet height, gross weight, and annual pallet movements;
- explicit-input logistics comparisons for pallet movements, freight cube, warehouse positions, and vehicle spaces;
- physical indicators for annual paper use/reduction, packaging weight, packaging-to-product ratio, recycled and virgin fibre, pallets avoided, and transport movements avoided;
- unavailable-output behavior for missing inputs and carbon emissions;
- technical-blocker precedence over material, logistics, and sustainability benefits;
- additive normalization for material, pallet, logistics, and physical-sustainability profiles.

Build 5 validation:
- Functional head: `0e31f3369ad1dccb9592f7b4b30f30bfa58f925c`.
- PVE CI #805, run `29308755665`, success.
- 271 tests passed, 0 failures, 0 errors.

Build 5 does not implement mixed-SKU palletisation, truck-load optimisation, three-dimensional optimisation, inferred box geometry, carbon calculation, damage cost, MOQ, working capital, implementation economics, or Build 6 functionality.

## Later-build intent

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
6. Technical/compliance blockers override commercial, material, logistics, and sustainability benefits.
7. Engineering validation and human approval remain mandatory.
8. Autonomous approval remains prohibited.
9. Historical records remain immutable and project-scoped.
10. Complete tests and current-head CI pass before closure.
11. PR #26 remains draft and unmerged until separate authorization.

## Build authorization rule
Completion of Build 5 does not authorize Build 6. Build 6 is not started or authorized.
