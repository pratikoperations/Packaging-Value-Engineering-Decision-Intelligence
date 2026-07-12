# Version Manifest

## Current Version
- Project version: `0.5.0-scenario-recommendation-ui`
- Build: `PVE-0.5`
- Status: Implementation complete — CI and QA pending
- Stable branch: `main`
- Working branch: `agent/pve-0.5-scenario-recommendation-ui`
- Base commit: `e28299d5ad5bf127aee16cf479ccf3576cf85ea8`

## Completed Foundation
- PVE-0.4 status: `0.4.0-technical-risk completed`
- Canonical data-model version: `0.2.0`

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

## Next Planned Build
- PVE-0.6 — Decision Package Export

## Later Build
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.6 begins only after PVE-0.5 passes CI and QA and is merged into `main`.
