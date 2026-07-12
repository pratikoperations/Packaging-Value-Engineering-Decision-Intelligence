# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current completed build: PVE-0.3 — Cost and Material Engine
- Stable branch: `main`
- Stable merge commit: `de9d18a428274bfafd369e7509f88b20bc33db89`
- Pull request: PR #5 merged and closed
- Original feature branch: Deleted

## Validation Reference
- Workflow: PVE CI
- Run number: 108
- Run ID: `29181583399`
- Validated PR commit: `847be5db56b413ec49868c50ea58092686555a5c`
- Tests: 18 passed, 0 failed, 0 errors
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
10. `docs/qa/PVE-0.2_QA_REPORT.md`
11. `docs/qa/PVE-0.3_QA_REPORT.md`
12. `data/schemas/canonical_data_model.json`
13. `data/demo/corrugated_shipping_cases.json`
14. `src/data_models/validator.py`
15. `src/material_engine/engine.py`
16. `src/cost_engine/engine.py`
17. `tests/data_validation/test_validator.py`
18. `tests/material_engine/test_engine.py`
19. `tests/cost_engine/test_engine.py`

## Recovery Procedure
1. Confirm latest `main`, open pull requests, and CI status.
2. Confirm PVE-0.1, PVE-0.2, and PVE-0.3 are completed and merged.
3. Review the canonical model, deterministic engines, tests, and PVE-0.3 QA report.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Resume only the next approved build unit.
6. Do not modify the draft integration contract outside its approved build.
7. After changes, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Approved Build
PVE-0.4 — Technical Qualification and Risk, after the PVE-0.3 post-merge closure PR is merged into `main`.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
