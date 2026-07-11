# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current build: PVE-0.2 — Data Model and Demo Data
- Stable branch: `main`
- Stable base commit: `d4672eadc23f23ba5528a44ff91fba649e6eff68`
- Working branch: `agent/pve-0.2-data-model-demo-data`

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
1. Confirm latest `main`, current branch, open PRs, and CI status.
2. Confirm PVE-0.1 is completed and merged.
3. Confirm PVE-0.2 scope and review the canonical model and synthetic dataset.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Resume only remaining PVE-0.2 validation, QA, or documentation work.
6. Do not introduce PVE-0.3 cost or material calculations before PVE-0.2 is merged.
7. After changes, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Build After Merge
PVE-0.3 — Cost and Material Engine

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
