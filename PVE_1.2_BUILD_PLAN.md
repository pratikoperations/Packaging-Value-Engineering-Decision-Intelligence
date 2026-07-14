# PVE 1.2 Controlled Build Plan

## Release

PVE 1.2 — Corrugated Packaging Engineering and Validation Intelligence

## Budget control

- Planned effort: 74 hours.
- Controlled contingency: 2 hours.
- Absolute cap: 76 hours.
- Contingency may be released only for unexpected regression repair, CI-only failure, migration compatibility repair, cross-module integration defects, or release-evidence reconciliation.
- Contingency must not fund new scope, another category, a ninth build, advanced prediction, UI enhancement, external integration, or deployment.

## Build sequence

| Build | Scope | Hours | Cumulative hours | Release completion | Status |
|---|---|---:|---:|---:|---|
| 1 | Architecture, governance and engineering boundary lock | 8 | 8 | 10.8% | Complete and validated |
| 2 | Corrugated specification, style and tolerance model | 11 | 19 | 25.7% | Complete and validated |
| 3 | Technical requirements, evidence and supplier capability | 10 | 29 | 39.2% | Not started |
| 4 | Compression, stacking, environment and line screening | 12 | 41 | 55.4% | Not started |
| 5 | Material, pallet, logistics and sustainability analysis | 11 | 52 | 70.3% | Not started |
| 6 | Should-cost, failure cost and implementation economics | 9 | 61 | 82.4% | Not started |
| 7 | Recommendation, confidence and immutable persistence | 7 | 68 | 91.9% | Not started |
| 8 | Demonstration cases, regression testing and release QA | 6 | 74 | 100% | Not started |

## Completed Build 1

Build 1 locked corrugated-only architecture, deterministic-calculation governance, sourced-threshold rules, evidence classification, human-approval boundaries, append-only persistence intent, dependencies, risks, exclusions, and release acceptance gates.

## Completed Build 2

Build 2 implemented configuration-driven baseline and proposed corrugated specifications with:

- legacy dimension fields retained for upload and template compatibility;
- internal and external dimensions;
- box style and converting-process profiles;
- ply, flute combination, paper-layer structure, layer GSM profile, board grade, and caliper;
- joint type, closure method, print process, colour count, coating or treatment, blank dimensions, and manufacturer joint;
- gross packed weight and case-pack quantity;
- artwork revision, barcode or QR location, transport and regulatory markings, dangerous-goods applicability, customer-artwork approval, and printing-plate change indicators;
- sourced and versioned tolerance records with nominal, minimum, maximum, unit, inspection method, criticality, source classification, source reference, and validation status;
- transparent baseline/proposed difference reporting without an engineering conclusion;
- source-preserving normalization for intake and tolerance records;
- inherited JSON, CSV, and Excel workflow compatibility.

Build 2 does not implement production compression formulas, evidence matching, supplier capability, line screening, pallet analysis, damage-cost logic, or Build 3 functionality.

## Later-build intent

### Build 3 — Technical requirements, evidence and supplier capability

Evidence matching, certificate and test validity, supplier manufacturing compatibility, distribution requirements, and explainable evidence confidence.

### Build 4 — Compression, stacking, environment and line screening

Comparison of supplied performance evidence against project-defined requirements, environmental and stacking context, and packing-line compatibility blockers. No unsourced universal BCT prediction.

### Build 5 — Material, pallet, logistics and sustainability analysis

Deterministic material, simple pallet orientation, pallet movement, logistics, and physical sustainability indicators. No mixed-SKU optimization or carbon claims without governed factors.

### Build 6 — Should-cost, failure cost and implementation economics

Explicit cost and assumption-based scenarios for damage exposure, MOQ, working capital, transition stock, obsolescence, tooling, artwork, trials, first-year net benefit, and payback.

### Build 7 — Recommendation, confidence and immutable persistence

Engineering recommendation for review, evidence-confidence separation, append-only technical assessments, archive protection, and cross-project isolation.

### Build 8 — Demonstration cases, regression and release QA

Synthetic cases, complete regression suite, release evidence, documentation, current-head CI, and closure recommendation. Merge remains separately authorized.

## Dependencies

- PVE 1.1 merged and governance-closed baseline.
- Existing category registry, normalized uploads, readiness, blockers, traceability, output availability, scenarios, cost, material, recommendations, reports, and immutable persistence.
- Project-defined or governed technical requirements and thresholds.
- Synthetic evidence and demonstration data.
- Engineering ownership for project-specific acceptance criteria.

## Release-level acceptance gates

1. Scope remains corrugated-only.
2. Every formula is deterministic and explainable.
3. Every threshold is sourced, versioned, applicable, and traceable.
4. Assumptions remain explicit.
5. Supplier-declared, predicted, assumed, and laboratory-tested values remain distinct.
6. Technical and compliance blockers override commercial attractiveness.
7. Engineering validation and human approval remain mandatory.
8. Autonomous approval remains prohibited.
9. Historical records remain immutable and project-scoped.
10. Complete tests pass with zero failures and errors.
11. Current-head CI passes before any build is closed.
12. The pull request remains draft and unmerged until separate authorization.

## Build authorization rule

Completion of a build does not authorize the next build. Build 3 is not started or authorized.
