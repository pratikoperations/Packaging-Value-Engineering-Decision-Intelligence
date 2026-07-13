# Recovery Manifest

## Purpose
Recover the current PVE 1.0 final-release candidate from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`
- Current final build: PVE-1.0.6 — Decision Snapshot and Final Release Closure
- Pull request: PR #22
- Status: Final review pending
- Feature branch: `agent/pve-1.0.6-decision-release-closure`
- Stable base: `d04c648bbf1fb074903166bc33ac5d73de643222`

## Previous Stable Build
- PVE-1.0.5 — Controlled Scenario Execution
- PR #21 merged and closed
- Merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Tests: 160 passed, 0 failed, 0 errors
- Effort: 17.5 hours
- Source branch: Deleted

## PVE-1.0.6 Validation
- Final CI: PVE CI #507
- Run ID: `29221779591`
- Tests: 179 passed, 0 failed, 0 errors
- Actual effort: 17.0 hours
- Remaining program budget: 0.5 hours

## Mandatory Reading Order
1. `PROJECT_STATUS.md`
2. `VERSION_MANIFEST.md`
3. `CHANGELOG.md`
4. `BUILD_HISTORY.md`
5. `ACTIVITY_LOG.md`
6. `DECISION_LOG.md`
7. `docs/design/PVE-1.0.6_DECISION_SNAPSHOT_RELEASE_DESIGN.md`
8. `docs/qa/PVE-1.0.6_FINAL_QA_REPORT.md`
9. `docs/release/PVE_1.0_FINAL_RELEASE_CHECKLIST.md`
10. `docs/interview/PVE_1.0_FINAL_INTERVIEW_DEMO.md`
11. `pages/05_Decision_History.py`
12. `src/decision_snapshots/service.py`
13. `src/persistence/decision_repository.py`
14. `tests/decision_snapshots/test_decision_snapshots.py`

## Recovery Procedure
1. Check out `agent/pve-1.0.6-decision-release-closure` while PR #22 remains open, or `main` after merge.
2. Run `python -m unittest discover -s tests -p "test_*.py" -v` and confirm 179 tests pass.
3. Run the Streamlit application and select a project with a saved controlled scenario.
4. Prepare and save a decision snapshot.
5. Confirm exact project, scenario, dataset, and threshold references.
6. Confirm the dataset-defined baseline is excluded.
7. Confirm engineering validation and human approval remain mandatory and autonomous approval is prohibited.
8. Archive a project and verify prior history is readable while new snapshot creation is rejected.

## Stable Scope Boundary
No authentication, external database, ERP integration, supplier ranking or allocation, autonomous approval, analytical-engine modification, recommendation-engine modification, or additional packaging category.

## Separation Rule
This repository does not store AI Procurement Copilot source files. Cross-project communication uses governed integration packages only.