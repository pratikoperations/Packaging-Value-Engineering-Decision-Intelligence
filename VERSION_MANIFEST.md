# Version Manifest

## Current Version
- Project version: `0.2.0-data-model`
- Build: `PVE-0.2`
- Status: `0.2.0-data-model completed`
- Stable branch: `main`
- Merge commit: `33b4319c3b74d8caaad6bc03cb85cb6ebf1727ff`
- Pull request: PR #3 merged and closed
- Original feature branch: Deleted

## Validation Evidence
- Workflow: PVE CI
- Run number: 68
- Run ID: `29180955427`
- Validated PR commit: `d02f45fcf0d17904b1cd7efa3577a89dfec7cf98`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 10 passed, 0 failed, 0 errors

## Current Deliverables
- Canonical data-model version: `0.2.0`
- Synthetic demo category: Corrugated shipping cases
- Validation module: `src/data_models/validator.py`
- Test suite: `tests/data_validation/test_validator.py`

## Scope Boundary
No application UI, cost calculation, savings calculation, material-optimization engine, recommendation scoring, supplier ranking, or allocation is included. The integration contract remains draft.

## Next Approved Build
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
PVE-0.3 begins only after the PVE-0.2 post-merge closure PR is merged into `main`.
