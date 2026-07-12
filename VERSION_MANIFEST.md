# Version Manifest

## Current Version
- Project version: `0.2.0-data-model`
- Build: `PVE-0.2`
- Status: `0.2.0-data-model ready`
- Stable branch: `main`
- Working branch: `agent/pve-0.2-data-model-demo-data`
- Base commit: `d4672eadc23f23ba5528a44ff91fba649e6eff68`

## Validation Evidence
- Workflow: PVE CI
- Run number: 58
- Run ID: `29180838040`
- Validated commit: `436820a54ff066b2c2265403bda628c78107962d`
- Job: `validate-repository`
- Conclusion: success
- Tests: 10 run, 10 passed, 0 failed, 0 errors

## Current Deliverables
- Canonical data-model version: `0.2.0`
- Synthetic demo category: Corrugated shipping cases
- Validation module: `src/data_models/validator.py`
- Test suite: `tests/data_validation/test_validator.py`

## Scope Boundary
No application UI, cost calculation, savings calculation, material-optimization engine, recommendation scoring, supplier ranking, or allocation is included. The integration contract remains draft.

## Next Planned Build
- PVE-0.3 — Cost and Material Engine

## Later Builds
- PVE-0.4 — Technical Qualification and Risk
- PVE-0.5 — Scenario and Recommendation UI
- PVE-0.6 — Decision Package Export
- PVE-0.7 — QA and Interview Release

## Contract Versions
- Draft export contract: `PVE-CONTRACT-v1.0`
- Dataset export marker: `PVE-CONTRACT-v1.0-DRAFT`
- Planned Procurement Copilot adapter: `PC-PVE-ADAPTER-v1.0`

## Version Rule
PVE-0.3 begins only after PVE-0.2 passes final documentation CI and PR #3 is merged into `main`.
