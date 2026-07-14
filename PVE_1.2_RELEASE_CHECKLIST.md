# PVE 1.2 Release Checklist

## Scope and budget
- [x] Corrugated-only scope preserved.
- [x] Eight controlled builds completed.
- [x] 74 of 74 planned hours consumed.
- [x] 0 of 2 contingency hours consumed.
- [x] Build 8 limited to demonstration cases, regression, documentation, and release QA.

## Technical governance
- [x] Deterministic calculations retained.
- [x] Missing inputs return unavailable, insufficient-data, or validation-required outcomes.
- [x] No hidden universal BCT, ECT-to-BCT, McKee, market-price, margin, or wastage assumptions.
- [x] Technical and evidence blockers override commercial attractiveness.
- [x] Engineering validation and explicit human approval remain mandatory.
- [x] Approved, Rejected, and Conditional are not generated automatically.

## Evidence and source governance
- [x] Uploaded, manually entered, supplier-declared, laboratory-tested, predicted, and assumed values remain distinct.
- [x] Evidence matching retains project, specification, supplier, site, material, method, laboratory, batch, date, and validity context.
- [x] Evidence confidence remains separate from recommendation and technical-success probability.

## Persistence and isolation
- [x] Schema version 4 is additive.
- [x] Migration from schema versions 1, 2, and 3 is tested.
- [x] Technical assessments are append-only.
- [x] Repository and database update/delete rejection are tested.
- [x] Historical datasets, thresholds, scenarios, decisions, and readiness records remain immutable.
- [x] Archived-project write protection is tested.
- [x] Cross-project isolation is tested.

## Demonstration and regression
- [x] Eight governed synthetic cases are included.
- [x] Every case is labelled synthetic demonstration data.
- [x] End-to-end intake-to-assessment test is included.
- [x] JSON and CSV-compatible normalization regression is included.
- [x] Excel-template regression is included.
- [x] Functional full suite passed: 300 tests, 0 failures, 0 errors.
- [x] Final documented-head CI #865, run `29309867905`, passed with zero failures and errors.
- [x] Final closure head `6a2c372238a531c3ca6977753ff2d90d69e07b5f` passed PVE CI #875, run `29309985760`, with 300 tests, 0 failures, and 0 errors.

## Documentation
- [x] README reconciled for PVE 1.2 completion state.
- [x] PROJECT_STATUS reconciled.
- [x] Controlled build plan reconciled.
- [x] Architecture and governance records reconciled.
- [x] Release QA report created.
- [x] Release notes created.
- [x] Final release-evidence correction completed.

## Release control
- [x] PR #26 remains draft.
- [x] PR #26 remains unmerged.
- [x] PR was not marked ready for review.
- [x] No deployment, pilot, activation, or production work performed.
- [ ] Separate authorization obtained for marking ready, merging, or release publication.