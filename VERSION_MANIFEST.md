# Version Manifest

## Current Version
- Project version: `0.3.0-cost-material-engine`
- Build: `PVE-0.3`
- Status: `0.3.0-cost-material-engine completed`
- Stable branch: `main`
- Merge commit: `de9d18a428274bfafd369e7509f88b20bc33db89`
- Pull request: PR #5 merged and closed
- Original feature branch: Deleted

## Validation Evidence
- Workflow: PVE CI
- Run number: 108
- Run ID: `29181583399`
- Validated PR commit: `847be5db56b413ec49868c50ea58092686555a5c`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 18 passed, 0 failed, 0 errors

## Current Deliverables
- Cost engine: `src/cost_engine/engine.py`
- Material engine: `src/material_engine/engine.py`
- Cost tests: `tests/cost_engine/test_engine.py`
- Material tests: `tests/material_engine/test_engine.py`
- PVE-0.3 QA report: `docs/qa/PVE-0.3_QA_REPORT.md`

## Calculation Scope
- Unit and annual cost by alternative
- Unit and annual savings versus baseline
- Cost change percentage versus baseline
- Component and case material weights
- Annual material mass
- Material change in grams and percentage versus baseline

## Scope Boundary
No application UI, technical qualification, risk engine, recommendation scoring, supplier ranking, allocation, scenario engine, autonomous technical approval, or PVE-0.4 functionality is included. The integration contract remains draft.

## Next Approved Build
- PVE-0.4 — Technical Qualification and Risk

## Later Builds
- PVE-0.5 — Scenario and Recommendation UI
- PVE-0.6 — Decision Package Export
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.4 begins only after the PVE-0.3 post-merge closure PR is merged into `main`.
