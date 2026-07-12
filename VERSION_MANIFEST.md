# Version Manifest

## Current Version
- Project version: `0.3.0-cost-material-engine`
- Build: `PVE-0.3`
- Status: `0.3.0-cost-material-engine ready`
- Stable branch: `main`
- Working branch: `agent/pve-0.3-cost-material-engine`
- Base commit: `6a6f5d080f906f3a6b01b73cd04465db7da356ef`

## Validation Evidence
- Workflow: PVE CI
- Run number: 98
- Run ID: `29181336986`
- Validated commit: `da769f756cd6a5edfd38e61fc8176642c51c41d9`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 18 run, 18 passed, 0 failed, 0 errors

## Completed Foundation
- PVE-0.2 status: `0.2.0-data-model completed`
- Canonical data-model version: `0.2.0`
- Synthetic demo category: Corrugated shipping cases

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

## Next Planned Build
- PVE-0.4 — Technical Qualification and Risk

## Later Builds
- PVE-0.5 — Scenario and Recommendation UI
- PVE-0.6 — Decision Package Export
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.4 begins only after PVE-0.3 passes final CI and PR #5 is merged into `main`.
