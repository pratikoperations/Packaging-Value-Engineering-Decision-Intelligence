# Version Manifest

## Current Version
- Project version: `0.6.0-decision-package-export`
- Build: `PVE-0.6`
- Status: `0.6.0-decision-package-export ready`
- Stable branch: `main`
- Working branch: `agent/pve-0.6-decision-package-export`
- Base commit: `47ad5730699e49ab64accb41b19e488ebc166ffa`

## Validation Evidence
- Workflow: PVE CI
- Run number: 217
- Run ID: `29183379595`
- Validated commit: `21c0fc1586ab60847da71d5f0ce6d8ab94c9aeb9`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 52 run, 52 passed, 0 failed, 0 errors

## Completed Foundation
- PVE-0.5 status: `0.5.0-scenario-recommendation-ui completed`
- Canonical data-model version: `0.2.0`

## Current Deliverables
- Decision-package assembler: `src/exports/decision_package.py`
- Export package API: `src/exports/__init__.py`
- Machine-readable JSON renderer
- Human-readable Markdown renderer
- Streamlit download controls: `app.py`
- Export tests: `tests/exports/test_decision_package.py`
- PVE-0.6 QA report: `docs/qa/PVE-0.6_QA_REPORT.md`

## Export Scope
- Structured executive summary
- Scenario assumptions
- Baseline and alternative cost/material results
- Technical qualification and risk outcomes
- Recommendation rationale, constraints, and validation requirements
- Explicit read-only and engineering-approval controls

## Scope Boundary
No autonomous technical approval, supplier allocation, final integration contract, external system integration, or PVE-0.7 release packaging is included. The integration contract remains draft.

## Next Planned Build
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.7 begins only after PVE-0.6 passes final CI and PR #11 is merged into `main`.
