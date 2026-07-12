# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current build: PVE-0.7 — QA and Interview Release
- Stable branch: `main`
- Stable base commit: `1b3a6f0250f3645df08e908b3be30d75b99294e7`
- Working branch: `agent/pve-0.7-qa-interview-release`
- Last completed build: PVE-0.6 — Decision Package Export

## Previous Validation Reference
- Workflow: PVE CI
- Run number: 239
- Run ID: `29184081746`
- Tests: 52 passed, 0 failed, 0 errors
- QA result: Pass for PVE-0.6 closure

## Mandatory Reading Order
1. `README.md`
2. `PROJECT_STATUS.md`
3. `VERSION_MANIFEST.md`
4. `BUILD_INSTRUCTIONS.md`
5. `ACTIVITY_LOG.md`
6. `BUILD_HISTORY.md`
7. `CHANGELOG.md`
8. `DECISION_LOG.md`
9. `docs/MASTER_ARCHITECTURE.md`
10. `docs/MASTER_BUILD_PLAN.md`
11. `docs/INTERVIEW_DEMO_GUIDE.md`
12. `docs/FINAL_RELEASE_CHECKLIST.md`
13. `docs/qa/PVE-0.6_QA_REPORT.md`
14. `docs/qa/PVE-0.7_QA_REPORT.md`
15. `data/schemas/canonical_data_model.json`
16. `data/demo/corrugated_shipping_cases.json`
17. `src/data_models/validator.py`
18. `src/cost_engine/engine.py`
19. `src/material_engine/engine.py`
20. `src/technical_qualification/engine.py`
21. `src/risk_engine/engine.py`
22. `src/scenario_engine/engine.py`
23. `src/recommendation/engine.py`
24. `src/exports/decision_package.py`
25. `app.py`
26. `tests/release/test_end_to_end_release.py`

## Recovery Procedure
1. Confirm latest `main`, active branch, open pull requests, and PVE CI status.
2. Confirm PVE-0.1 through PVE-0.6 are completed and merged.
3. Confirm PVE-0.7 contains only release QA, documentation, recovery, and test hardening.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Confirm the expected PVE-0.7 test total is 58.
6. Run the UI with `streamlit run app.py` after installing `requirements.txt`.
7. Follow `docs/INTERVIEW_DEMO_GUIDE.md` for the interview walkthrough.
8. Complete `docs/FINAL_RELEASE_CHECKLIST.md` before release approval.
9. Confirm JSON and Markdown exports retain fixed human-approval and boundary controls.
10. Do not finalize the draft integration contract without explicit approval.

## Release Completion Rule
PVE-0.7 becomes completed only after all release tests and CI pass, the release PR is merged, and post-merge governance closure is recorded.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
