# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current completed build: PVE-0.2 — Data Model and Demo Data
- Stable branch: `main`
- Stable merge commit: `33b4319c3b74d8caaad6bc03cb85cb6ebf1727ff`
- Pull request: PR #3 merged and closed
- Original feature branch: Deleted

## Validation Reference
- Workflow: PVE CI
- Run number: 68
- Run ID: `29180955427`
- Validated PR commit: `d02f45fcf0d17904b1cd7efa3577a89dfec7cf98`
- Tests: 10 passed, 0 failed, 0 errors
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
10. `docs/qa/PVE-0.1_QA_REPORT.md`
11. `docs/qa/PVE-0.2_QA_REPORT.md`
12. `data/schemas/canonical_data_model.json`
13. `data/reference/allowed_values.json`
14. `data/demo/corrugated_shipping_cases.json`
15. `src/data_models/validator.py`
16. `tests/data_validation/test_validator.py`

## Recovery Procedure
1. Confirm latest `main`, open pull requests, and CI status.
2. Confirm PVE-0.1 and PVE-0.2 are completed and merged.
3. Review the canonical model, synthetic dataset, validator, tests, and PVE-0.2 QA report.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Resume only the next approved build unit.
6. Do not modify the draft integration contract outside its approved build.
7. After changes, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Approved Build
PVE-0.3 — Cost and Material Engine, after the PVE-0.2 post-merge closure PR is merged into `main`.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
