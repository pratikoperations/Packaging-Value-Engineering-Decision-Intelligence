# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current completed build: PVE-0.4 — Technical Qualification and Risk
- Stable branch: `main`
- Stable merge commit: `ced6c5542faa700a43101f8f9fc702d15d78f0ca`
- Pull request: PR #7 merged and closed
- Original feature branch: Deleted

## Validation Reference
- Workflow: PVE CI
- Run number: 148
- Run ID: `29182036082`
- Validated PR commit: `db40eac200e1c9d4a61c29a19e18551014e405f2`
- Tests: 30 passed, 0 failed, 0 errors
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
10. `docs/qa/PVE-0.3_QA_REPORT.md`
11. `docs/qa/PVE-0.4_QA_REPORT.md`
12. `data/schemas/canonical_data_model.json`
13. `data/demo/corrugated_shipping_cases.json`
14. `src/data_models/validator.py`
15. `src/material_engine/engine.py`
16. `src/cost_engine/engine.py`
17. `src/technical_qualification/engine.py`
18. `src/risk_engine/engine.py`
19. `tests/technical_qualification/test_engine.py`
20. `tests/risk_engine/test_engine.py`

## Recovery Procedure
1. Confirm latest `main`, open pull requests, and CI status.
2. Confirm PVE-0.1 through PVE-0.4 are completed and merged.
3. Review the canonical model, deterministic engines, tests, and PVE-0.4 QA report.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Resume only the next approved build unit.
6. Do not modify the draft integration contract outside its approved build.
7. After changes, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Approved Build
PVE-0.5 — Scenario and Recommendation UI, after the PVE-0.4 post-merge closure PR is merged into `main`.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
