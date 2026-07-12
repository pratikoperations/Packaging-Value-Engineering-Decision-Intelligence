# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current completed build: PVE-0.6 — Decision Package Export
- Stable branch: `main`
- Stable merge commit: `70dd9dcbf60ab0896e4e38aedf8e20dc65c40985`
- Pull request: PR #11 merged and closed
- Original feature branch: Deleted

## Validation Reference
- Workflow: PVE CI
- Run number: 227
- Run ID: `29183476545`
- Validated PR commit: `55b5294c6c1a4924dca681a47680af70be551b4d`
- Tests: 52 passed, 0 failed, 0 errors
- QA result: Pass

## Mandatory Reading Order
1. `PROJECT_STATUS.md`
2. `BUILD_INSTRUCTIONS.md`
3. `VERSION_MANIFEST.md`
4. `ACTIVITY_LOG.md`
5. `BUILD_HISTORY.md`
6. `CHANGELOG.md`
7. `DECISION_LOG.md`
8. `docs/MASTER_ARCHITECTURE.md`
9. `docs/MASTER_BUILD_PLAN.md`
10. `docs/qa/PVE-0.5_QA_REPORT.md`
11. `docs/qa/PVE-0.6_QA_REPORT.md`
12. `data/schemas/canonical_data_model.json`
13. `data/demo/corrugated_shipping_cases.json`
14. `src/cost_engine/engine.py`
15. `src/material_engine/engine.py`
16. `src/technical_qualification/engine.py`
17. `src/risk_engine/engine.py`
18. `src/scenario_engine/engine.py`
19. `src/recommendation/engine.py`
20. `src/exports/decision_package.py`
21. `app.py`
22. `tests/exports/test_decision_package.py`

## Recovery Procedure
1. Confirm latest `main`, open pull requests, and CI status.
2. Confirm PVE-0.1 through PVE-0.6 are completed and merged.
3. Review the canonical model, deterministic engines, export module, tests, UI, and PVE-0.6 QA report.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Run the UI with `streamlit run app.py` after installing `requirements.txt`.
6. Review JSON and Markdown exports for complete decision basis and fixed safety controls.
7. Resume only the next approved build unit.
8. Do not modify the draft integration contract outside its approved build.

## Next Approved Build
PVE-0.7 — QA and Interview Release, after the PVE-0.6 post-merge closure PR is merged into `main`.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
