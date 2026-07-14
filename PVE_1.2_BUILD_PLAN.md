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
| 5 | Material, pallet, logistics and sustainability analysis | 11 | 52 | 70.3% | Not started |
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
Implemented:
- supplied BCT and ECT comparison against explicit project-defined requirements;
- no BCT prediction, ECT-to-BCT conversion, McKee coefficients, or hidden engineering constants;
- governed safety and environmental factors requiring source, version, applicability, and valid status;
- stack layers, pallet load, storage duration, static/dynamic stacking, humidity, temperature, refrigerated, and humid-context checks;
- floor/rack storage, pallet overhang/underhang, handling touches, mixed loads, and stretch-wrap compression checks;
- packing-line dimensional limits, erector, sealing, flap, barcode, speed, squareness, warp, and mandatory-trial checks;
- blocker precedence over commercial attractiveness;
- explainable outcomes: criteria met, criteria not met, validation required, evidence conflict, or insufficient technical data;
- additive normalization for factors, warehouse profiles, and packing-line profiles.

Build 4 validation:
- Functional head: `3abaf7d4053af17fbfb6b6dba1cdedefda9c3a45`.
- PVE CI #793, run `29308512768`, success.
- 257 tests passed, 0 failures, 0 errors.

## Later-build intent

### Build 5 — Material, pallet, logistics and sustainability analysis
Add deterministic material, simple pallet orientation, pallet movement, logistics, and physical sustainability indicators. No mixed-SKU optimisation or carbon claims without governed factors.

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
Completion of Build 4 does not authorize Build 5. Build 5 is not started or authorized.
