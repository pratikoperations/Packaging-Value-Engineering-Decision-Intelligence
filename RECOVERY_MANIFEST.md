# Recovery Manifest

## Purpose
Enable complete recovery of the finished project from GitHub without relying on chat history.

## Final Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Final build: PVE-0.7 — QA and Interview Release
- Final version: `0.7.0-qa-interview-release completed`
- Final status: Completed
- Stable branch: `main`
- Release PR: PR #13 merged and closed
- Release merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`

## Final Validation Reference
- Workflow: PVE CI
- Run number: 268
- Run ID: `29184423320`
- Validated commit: `d6ae2079e332a33edcc71d0011d642f0ae1eb5f9`
- Tests: 58 passed, 0 failed, 0 errors
- QA result: Pass

## Mandatory Reading Order
1. `README.md`
2. `PROJECT_STATUS.md`
3. `VERSION_MANIFEST.md`
4. `ACTIVITY_LOG.md`
5. `BUILD_HISTORY.md`
6. `CHANGELOG.md`
7. `docs/INTERVIEW_DEMO_GUIDE.md`
8. `docs/FINAL_RELEASE_CHECKLIST.md`
9. `docs/qa/PVE-0.7_QA_REPORT.md`
10. `docs/MASTER_ARCHITECTURE.md`
11. `docs/MASTER_BUILD_PLAN.md`
12. `data/schemas/canonical_data_model.json`
13. `data/demo/corrugated_shipping_cases.json`
14. `src/data_models/validator.py`
15. `src/cost_engine/engine.py`
16. `src/material_engine/engine.py`
17. `src/technical_qualification/engine.py`
18. `src/risk_engine/engine.py`
19. `src/scenario_engine/engine.py`
20. `src/recommendation/engine.py`
21. `src/exports/decision_package.py`
22. `app.py`
23. `tests/release/test_end_to_end_release.py`

## Recovery Procedure
1. Confirm `main` contains merge commit `fb0962ba611fcf59ae7ab194dd2514970a19909d` and the final closure commit after this PR merges.
2. Run `python -m unittest discover -s tests -p "test_*.py" -v` and confirm 58 tests pass.
3. Install `requirements.txt` and run `streamlit run app.py`.
4. Follow the interview demonstration guide.
5. Confirm JSON and Markdown exports retain fixed human-approval controls.
6. Keep the integration contract draft unless separately approved.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses governed integration packages only.
