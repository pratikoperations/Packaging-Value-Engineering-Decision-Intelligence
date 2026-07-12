# Recovery Manifest

## Purpose
Enable complete recovery of the current stable project state from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`
- Original interview release: PVE-0.7 — QA and Interview Release
- Current stable controlled build: PVE-1.0.5 — Controlled Scenario Execution
- Current stable version: `1.0.5-controlled-scenario-execution`
- Current status: Completed, validated, merged, and governance-closed

## Current Stable Merge Reference
- Pull request: PR #21 merged and closed
- Merge method: Squash merge
- Merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Source branch: `agent/pve-1.0.5-controlled-scenarios`
- Source branch status: Deleted

## Final PVE-1.0.5 Validation Reference
- Workflow: PVE CI
- Run number: 455
- Run ID: `29192749111`
- Validated head commit: `fb3b2421a457081d83631f5952510e7c533c7f8b`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 160 passed, 0 failed, 0 errors
- QA result: Pass

## Budget Reference
- Original PVE 1.0 working budget: 90 hours
- Hard ceiling: 110 hours
- Cumulative effort used through PVE-1.0.5: 72.5 hours
- PVE-1.0.5 actual effort used: 17.5 hours
- Confirmed remaining working budget: 17.5 hours

## Mandatory Reading Order
1. `README.md`
2. `PROJECT_STATUS.md`
3. `VERSION_MANIFEST.md`
4. `ACTIVITY_LOG.md`
5. `BUILD_HISTORY.md`
6. `CHANGELOG.md`
7. `DECISION_LOG.md`
8. `docs/qa/PVE-1.0.5_QA_REPORT.md`
9. `docs/design/PVE-1.0.5_CONTROLLED_SCENARIO_EXECUTION_DESIGN.md`
10. `pages/01_Project_Dashboard.py`
11. `pages/02_Upload_Validate.py`
12. `pages/03_Business_Thresholds.py`
13. `pages/04_Controlled_Scenarios.py`
14. `src/application/runtime.py`
15. `src/scenario_execution/service.py`
16. `src/persistence/scenario_repository.py`
17. `src/recommendation/engine.py`
18. `tests/scenario_execution/test_controlled_scenarios.py`
19. `data/schemas/canonical_data_model.json`
20. `data/demo/corrugated_shipping_cases.json`
21. `app.py`

## Recovery Procedure
1. Confirm `main` contains merge commit `99416d91025b6cfbff40142ce9fbcd462eb1028f` and the subsequent PVE-1.0.5 governance-closure commit.
2. Run `python -m unittest discover -s tests -p "test_*.py" -v` and confirm 160 tests pass.
3. Install `requirements.txt` and run `streamlit run app.py`.
4. Use the Project Dashboard to select an active project.
5. Validate canonical JSON or limited CSV input and save an immutable dataset version.
6. Select an immutable threshold profile.
7. Run a controlled scenario using explicit bounded assumptions.
8. Confirm scenario results preserve engineering validation, critical-risk, not-qualified, insufficient-data, and autonomous-approval controls.
9. Keep the integration contract draft unless separately approved.

## Stable Scope Boundary
PVE-1.0.5 excludes decision snapshots, decision-history UI, recommendation-engine modification, authentication, external database, supplier ranking or allocation, ERP integration, AI approval, and additional packaging categories.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses governed integration packages only.
