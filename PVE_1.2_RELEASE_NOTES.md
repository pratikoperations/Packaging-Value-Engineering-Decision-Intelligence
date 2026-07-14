# PVE 1.2 Release Notes

## Corrugated Packaging Engineering and Validation Intelligence

PVE 1.2 extends the stable PVE 1.1 intake-readiness platform with a corrugated-specific, evidence-governed engineering decision-support workflow.

## Added
- configuration-driven corrugated baseline and proposed specifications;
- box style, converting profile, artwork, compliance, and sourced tolerance models;
- technical requirements, evidence matching, expiry/conflict detection, and supplier compatibility checks;
- evidence-confidence classification that does not represent probability of technical success;
- deterministic supplied-evidence BCT/ECT screening, stacking, environmental, warehouse, and packing-line checks;
- supplied-geometry material analysis and simple rectangular pallet-pattern comparisons;
- explicit-input logistics and physical sustainability indicators;
- supplied should-cost, failure-cost, MOQ, inventory, working-capital, obsolescence, first-year benefit, and payback analysis;
- review-only engineering recommendations;
- additive schema version 4 and append-only technical assessments;
- eight governed synthetic demonstration cases and end-to-end release QA.

## Governance
- Technical and evidence blockers override commercial, material, logistics, and sustainability attractiveness.
- Missing inputs are never silently inferred.
- Supplier-declared, predicted, and assumed values are never represented as laboratory-tested facts.
- Engineering validation and explicit human approval remain mandatory.
- The system never automatically generates Approved, Rejected, or Conditional decisions.

## Validation
- Functional Build 8 head: `9465d9d6292a9d65834cfc11f27d1f056b9408a4`.
- PVE CI #849, run `29309701227`: success.
- Final documented head: `edf517c308cb204c683169d66f47e5b23fd3b0b5`.
- PVE CI #865, run `29309867905`: success.
- Final closure head: `6a2c372238a531c3ca6977753ff2d90d69e07b5f`.
- PVE CI #875, run `29309985760`: success.
- Final feature head: `20b60393eb21c75e56676ec119fb2c1818d33db0`.
- PVE CI #883, run `29313538879`: success.
- PR #26 squash-merge commit: `8c5511e096b4526a85630e38ef939db371b307b1`.
- Post-merge PVE CI #896, run `29317676780`, job `87035353112`: success on `main`.
- Post-merge tests: 300 passed, 0 failures, 0 errors.
- Artifact: `pve-full-test-output`, artifact ID `8304598530`.

## Budget
- Planned release: 74 hours.
- Completed: 74 hours, 100%.
- Pending planned work: 0 hours, 0%.
- Controlled contingency used: 0 of 2 hours.

## Release control
PVE 1.2 is complete, squash-merged through PR #26, post-merge validated on `main`, and governance-closed as a decision-support release. It is not a production-ready enterprise system. Deployment, activation, pilot, publication as production software, and production use remain separately unauthorized. PVE 1.3 has not started. Tag `pve-v1.2` is recommended after this governance-closure PR is merged and final `main` CI passes.
