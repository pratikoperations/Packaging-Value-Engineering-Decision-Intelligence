# PVE 1.2 Release QA Report

## Release
PVE 1.2 — Corrugated Packaging Engineering and Validation Intelligence

## Status
Builds 1–8 are complete and validated on draft PR #26. This report does not authorize merge, deployment, activation, or production use.

## Budget
- Planned effort: 74 hours.
- Completed effort: 74 hours.
- Release completion: 100%.
- Pending planned effort: 0 hours, 0%.
- Controlled contingency used: 0 of 2 hours.
- Absolute cap: 76 hours.

## Validation
### Functional Build 8 head
- Head: `9465d9d6292a9d65834cfc11f27d1f056b9408a4`.
- Workflow: PVE CI #849.
- Run ID: `29309701227`.
- Result: success.
- Automated tests: 300 passed.
- Failures: 0.
- Errors: 0.

### Final documented head
- Head: `edf517c308cb204c683169d66f47e5b23fd3b0b5`.
- Workflow: PVE CI #865.
- Run ID: `29309867905`.
- Result: success.
- Automated tests: 300 passed.
- Failures: 0.
- Errors: 0.

### Final closure head
- Head: `6a2c372238a531c3ca6977753ff2d90d69e07b5f`.
- Workflow: PVE CI #875.
- Run ID: `29309985760`.
- Result: success.
- Automated tests: 300 passed.
- Failures: 0.
- Errors: 0.
- Mandatory-file, JSON, synthetic-label, project-separation, build-identity, integration-contract, release-document, focused-report, and full-suite gates passed.

## Synthetic demonstration cases
The governed file `data/pve_1_2_corrugated_demonstration_cases.json` contains eight cases. Every case and the dataset itself are explicitly labelled synthetic demonstration data.

1. Right-sized proposal with sufficient evidence and review-only positive outcome.
2. Commercially attractive proposal blocked by compression failure.
3. Packing-line incompatibility.
4. Wrong-specification or conflicting evidence.
5. Damage-cost reversal with negative risk-adjusted benefit.
6. MOQ, transition-stock, working-capital, and obsolescence impact.
7. Pallet and logistics improvement without material saving.
8. Humid/export case requiring additional validation.

## End-to-end coverage
The Build 8 release-QA suite covers:
- project input and upload normalization;
- configuration-driven corrugated specifications and sourced tolerances;
- evidence confidence and supplied-evidence technical screening;
- material, simple pallet-pattern, logistics, and physical sustainability outputs;
- should-cost, failure-cost, inventory, working-capital, obsolescence, first-year benefit, and payback;
- review-only engineering recommendation;
- append-only technical-assessment persistence;
- update and delete rejection;
- archived-project protection and cross-project isolation;
- JSON and CSV-compatible normalization and Excel-template regression.

## Migration validation
Additive migration is validated from schema versions 1, 2, and 3 to schema version 4. No historical table is removed or rewritten.

## Immutability validation
Update and delete triggers remain present for:
- project datasets;
- threshold profiles;
- scenarios;
- decision snapshots;
- readiness assessments;
- technical assessments.

## Decision governance
- Technical and evidence blockers override commercial, material, logistics, and sustainability attractiveness.
- Evidence confidence remains separate from recommendation status and is not probability of technical success.
- `Approved`, `Rejected`, and `Conditional` are never generated automatically.
- Engineering validation and explicit human approval remain mandatory.

## Known limitations and exclusions
- No universal BCT prediction, ECT-to-BCT conversion, or McKee coefficient.
- No structural simulation, CAD, dieline generation, OCR, or AI certificate interpretation.
- No mixed-SKU palletisation, truck-load optimisation, or global three-dimensional optimisation.
- No carbon calculation without a separately governed and authorized methodology.
- No supplier ranking, allocation, RFQ comparison, negotiation, ERP integration, authentication, deployment, pilot, activation, or production use.
- Synthetic cases are not validated supplier, manufacturing, laboratory, regulatory, or commercial data.

## Release-readiness recommendation
PVE 1.2 has completed functional, documented-head, and final closure validation and is ready for explicit authorization to mark PR #26 ready for review and proceed to a separate squash-merge decision. It is not production-ready enterprise software and remains draft and unmerged until separately authorized.