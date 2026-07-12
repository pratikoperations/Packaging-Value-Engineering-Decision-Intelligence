# Version Manifest

## Current Version
- Project version: `0.4.0-technical-risk`
- Build: `PVE-0.4`
- Status: `0.4.0-technical-risk ready`
- Stable branch: `main`
- Working branch: `agent/pve-0.4-technical-qualification-risk`
- Base commit: `eb32194e2eaf57c8972e12bf12ca5535fad22b2f`

## Validation Evidence
- Workflow: PVE CI
- Run number: 138
- Run ID: `29181964082`
- Validated commit: `2e492a6034add0ba5bf6f8a222f38791043bf4e0`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 30 run, 30 passed, 0 failed, 0 errors

## Completed Foundation
- PVE-0.3 status: `0.3.0-cost-material-engine completed`
- Canonical data-model version: `0.2.0`

## Current Deliverables
- Technical qualification engine: `src/technical_qualification/engine.py`
- Risk engine: `src/risk_engine/engine.py`
- Technical tests: `tests/technical_qualification/test_engine.py`
- Risk tests: `tests/risk_engine/test_engine.py`
- PVE-0.4 QA report: `docs/qa/PVE-0.4_QA_REPORT.md`

## Rule Scope
- Technical status aggregation with explicit failure precedence
- Missing-result and missing-evidence handling
- Validation-required outputs
- Quality, supply, and implementation risk indicators
- Probability-based risk escalation
- Explicit risk-data completeness reporting

## Scope Boundary
No application UI, recommendation scoring, supplier ranking, supplier allocation, scenario or sensitivity engine, autonomous technical approval, final integration contract, or PVE-0.5 functionality is included. The integration contract remains draft.

## Next Planned Build
- PVE-0.5 — Scenario and Recommendation UI

## Later Builds
- PVE-0.6 — Decision Package Export
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.5 begins only after PVE-0.4 passes final CI and PR #7 is merged into `main`.
