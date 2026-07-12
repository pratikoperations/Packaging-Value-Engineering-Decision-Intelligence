# Version Manifest

## Current Version
- Project version: `0.4.0-technical-risk`
- Build: `PVE-0.4`
- Status: `0.4.0-technical-risk completed`
- Stable branch: `main`
- Merge commit: `ced6c5542faa700a43101f8f9fc702d15d78f0ca`
- Pull request: PR #7 merged and closed
- Original feature branch: Deleted

## Validation Evidence
- Workflow: PVE CI
- Run number: 148
- Run ID: `29182036082`
- Validated PR commit: `db40eac200e1c9d4a61c29a19e18551014e405f2`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 30 passed, 0 failed, 0 errors

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

## Next Approved Build
- PVE-0.5 — Scenario and Recommendation UI

## Later Builds
- PVE-0.6 — Decision Package Export
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.5 begins only after the PVE-0.4 post-merge closure PR is merged into `main`.
