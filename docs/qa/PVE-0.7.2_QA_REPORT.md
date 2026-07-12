# PVE-0.7.2 QA Report

## Build
PVE-0.7.2 — Live Demo and Streamlit Width Compatibility

## Status
QA Pass — ready for review after final branch CI

## Objective
Publish the live Streamlit portfolio URL and replace deprecated `use_container_width=True` arguments with `width="stretch"` without changing application behavior.

## Live Deployment
https://packaging-value-engineering-decision-intelligence.streamlit.app/

## Changed Files
- `README.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `app.py`
- `tests/release/test_end_to_end_release.py`
- `docs/qa/PVE-0.7.2_QA_REPORT.md`

## Compatibility Rationale
Streamlit 1.59.1 reports that `use_container_width` is deprecated and should be replaced with `width`. The equivalent replacement for `use_container_width=True` is `width="stretch"`.

## Acceptance Criteria
- Live demo URL is prominent in `README.md`.
- Public deployment and export verification are recorded.
- All `use_container_width=True` instances in `app.py` are replaced with `width="stretch"`.
- `use_container_width` no longer appears in `app.py`.
- Synthetic-data disclaimer remains present.
- Autonomous-approval warning remains present.
- Engineering validation remains required.
- Draft integration-contract statement remains present.
- Application behavior and download functionality remain unchanged.
- No analytical engines, schemas, demo data, validator, recommendation logic, risk logic, export logic, integration contract, requirements, release, or AI Procurement Copilot files are changed.

## Test Baseline
- Previous total: 59
- New Streamlit width compatibility test: 1
- Current total: 60
- Failures: 0
- Errors: 0

## Validated CI Evidence
- Workflow: PVE CI
- Run number: 301
- Run ID: `29186214898`
- Validated commit: `4e2f99c5d276072dc97863b18698943967f4d16c`
- Job: `validate-repository`
- Status: completed
- Conclusion: success
- All workflow steps: passed

## Analytical Change Assessment
None. This update is limited to documentation and equivalent Streamlit presentation parameters.

## QA Result
**Pass**

## Merge Rule
Do not merge until the final branch head also passes PVE CI and the complete six-file diff is reviewed.
