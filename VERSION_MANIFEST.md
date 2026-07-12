# Version Manifest

## Current Version
- Project version: `0.5.0-scenario-recommendation-ui`
- Build: `PVE-0.5`
- Status: `0.5.0-scenario-recommendation-ui completed`
- Stable branch: `main`
- Merge commit: `930a4e25d3392b7107616ec498501ef48aa72a8e`
- Pull request: PR #9 merged and closed
- Original feature branch: Deleted

## Validation Evidence
- Workflow: PVE CI
- Run number: 190
- Run ID: `29182740157`
- Validated PR commit: `252bf329fcb50c9d3c7c7fb1392309599356eb54`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 42 passed, 0 failed, 0 errors

## Current Deliverables
- Scenario engine: `src/scenario_engine/engine.py`
- Recommendation engine: `src/recommendation/engine.py`
- Streamlit UI: `app.py`
- Scenario tests: `tests/scenario_engine/test_engine.py`
- Recommendation tests: `tests/recommendation/test_engine.py`
- PVE-0.5 QA report: `docs/qa/PVE-0.5_QA_REPORT.md`

## Rule Scope
- Explicit annual-volume, cost, and material assumptions
- Transparent cost and material recalculation
- Qualification- and risk-gated recommendation statuses
- Explainable preferred-alternative ordering
- User-visible constraints, rationale, and validation requirements

## Scope Boundary
No supplier ranking, supplier allocation, autonomous technical approval, final integration contract, decision-package export, or PVE-0.6 functionality is included. The integration contract remains draft.

## Next Approved Build
- PVE-0.6 — Decision Package Export

## Later Build
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.6 begins only after the PVE-0.5 post-merge closure PR is merged into `main`.
