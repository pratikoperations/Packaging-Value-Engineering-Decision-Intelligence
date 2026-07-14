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
| 7 | Recommendation, confidence and immutable persistence | 7 | 68 | 91.9% | Complete and validated |
| 8 | Demonstration cases, regression testing and release QA | 6 | 74 | 100% | Not started |

## Completed Builds 1–6
Builds 1–6 established corrugated-only governance, specification and tolerances, evidence and supplier compatibility, deterministic technical screening, material/pallet/logistics analysis, physical sustainability indicators, and explicit-input economics.

## Completed Build 7
Implemented:
- review-only outcomes: criteria met for engineering review, criteria not met, laboratory validation required, packing-line trial required, transport trial required, evidence conflict, insufficient technical data, and engineering review required;
- recommendation precedence that prevents economic or logistics attractiveness from overriding technical and evidence blockers;
- evidence confidence retained separately from recommendation and from probability of technical success;
- additive SQLite migration version 4 with a `technical_assessments` table;
- retained project, readiness, dataset/version, baseline/proposed specification versions, rule-set version, threshold/evidence references, formula inputs, assumptions, technical/commercial outcomes, blockers, required trials, confidence, recommendation, content hash, and timestamp;
- append-only repository behavior plus database triggers prohibiting update and delete;
- archived-project write protection;
- cross-project validation for dataset, readiness, threshold, and evidence references;
- historical datasets, readiness assessments, scenarios, thresholds, and decision snapshots preserved unchanged.

Build 7 validation:
- Functional head: `432ed1c196d989841021aff8656e35abf1c2034d`.
- PVE CI #839, run `29309404539`, success.
- 293 tests passed, 0 failures, 0 errors.

Build 7 does not implement demonstration cases, final release QA, merge preparation, role-based approval, autonomous approval, or Build 8 functionality.

## Later-build intent

### Build 8 — Demonstration cases, regression and release QA
Add governed synthetic cases, complete regression and migration validation, release evidence, documentation reconciliation, closure recommendation, and current-head CI. Merge remains separately authorized.

## Release acceptance gates
1. Scope remains corrugated-only.
2. Calculations remain deterministic and explainable.
3. Thresholds and commercial inputs remain sourced, explicit, and traceable.
4. Assumptions remain explicit.
5. Source classifications remain distinct.
6. Technical and evidence blockers override commercial, economic, material, logistics, and sustainability benefits.
7. Engineering validation and human approval remain mandatory.
8. Autonomous approval remains prohibited.
9. Historical records remain immutable and project-scoped.
10. Technical assessments remain append-only and immutable.
11. Complete tests and current-head CI pass before closure.
12. PR #26 remains draft and unmerged until separate authorization.

## Build authorization rule
Completion of Build 7 does not authorize Build 8. Build 8 is not started or authorized.
