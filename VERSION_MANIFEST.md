# Version Manifest

## Current Version
- Project version: `0.6.0-decision-package-export`
- Build: `PVE-0.6`
- Status: `0.6.0-decision-package-export completed`
- Stable branch: `main`
- Merge commit: `70dd9dcbf60ab0896e4e38aedf8e20dc65c40985`
- Pull request: PR #11 merged and closed
- Original feature branch: Deleted

## Validation Evidence
- Workflow: PVE CI
- Run number: 227
- Run ID: `29183476545`
- Validated PR commit: `55b5294c6c1a4924dca681a47680af70be551b4d`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 52 passed, 0 failed, 0 errors

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

## Next Approved Build
- PVE-0.7 — QA and Interview Release

## Version Rule
PVE-0.7 begins only after the PVE-0.6 post-merge closure PR is merged into `main`.
