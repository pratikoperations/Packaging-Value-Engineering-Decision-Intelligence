# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current build: PVE-0.4 — Technical Qualification and Risk
- Stable branch: `main`
- Stable base commit: `eb32194e2eaf57c8972e12bf12ca5535fad22b2f`
- Working branch: `agent/pve-0.4-technical-qualification-risk`
- Last completed build: PVE-0.3 — Cost and Material Engine

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
1. Confirm latest `main`, current branch, open PRs, and CI status.
2. Confirm PVE-0.1 through PVE-0.3 are completed and merged.
3. Confirm PVE-0.4 excludes UI, recommendations, supplier ranking, allocation, scenarios, autonomous approval, final contract, and PVE-0.5 logic.
4. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
5. Review technical outcomes, evidence gaps, risk indicators, and validation-required outputs.
6. Resume only remaining PVE-0.4 validation, QA, or documentation work.
7. Do not modify the draft integration contract outside its approved build.
8. After changes, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Build After Merge
PVE-0.5 — Scenario and Recommendation UI

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
