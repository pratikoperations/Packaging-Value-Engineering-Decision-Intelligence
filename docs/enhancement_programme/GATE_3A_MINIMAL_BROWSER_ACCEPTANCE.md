# Gate 3A — Minimal Interview Browser Acceptance

## Status

Implementation candidate. This gate is intentionally narrower than superseded Gate 3 PR #82 and supports interview-readiness evidence only.

## Purpose

Gate 3A verifies that the exact integrated programme version can start, render, expose all registered routes, accept representative scenario inputs, display Calculation Evidence, and produce governed JSON and Markdown downloads in Chromium.

## Acceptance scope

1. Start the Streamlit application.
2. Render the exact Home heading.
3. Resolve exactly 13 non-empty, unique route destinations.
4. Select one governed synthetic scenario.
5. Change annual volume, one unit-cost adjustment and one material-weight adjustment.
6. Verify Calculation Evidence is visible.
7. Download and validate machine-readable JSON and human-readable Markdown.
8. Perform one physical grouped-sidebar navigation to Calculation Evidence.
9. Perform one narrow 412 × 915 rendering and navigation smoke check.
10. Reject visible Streamlit exceptions, tracebacks, Playwright page errors and material browser-console errors.
11. Require one successful exact-head run.

## Explicit exclusions

- no three-run ledger;
- no production browser certification;
- no cross-browser certification;
- no hosted-environment reliability claim;
- no load, performance or accessibility certification;
- no production data;
- no business-formula, governed-data, recommendation, qualification, risk or export-calculation changes;
- no autonomous procurement or technical approval;
- no Power BI validation.

## Workflow

Workflow: `Gate 3A Minimal Interview Browser Acceptance`

Job: `validate-interview-browser-acceptance`

Trigger: manual `workflow_dispatch` only.

Runtime:

- Ubuntu 24.04;
- Python 3.12;
- Playwright Chromium only;
- zero automatic retries;
- twenty-minute timeout;
- read-only repository permission.

## Evidence artifact

Artifact: `gate3a-minimal-browser-acceptance-evidence`

Required evidence:

- `acceptance-report.json`;
- `route-inventory.json`;
- `runtime-events.json`;
- governed JSON and Markdown downloads;
- Home, Calculation Evidence and narrow-view screenshots;
- Streamlit log;
- failure screenshot and context when applicable.

## Passing claim

A successful exact-head run supports the claim that the portfolio prototype has a governed Chromium acceptance check covering startup, all registered routes, representative scenario-input interaction, Calculation Evidence, decision-package downloads, desktop navigation and narrow-screen rendering.

It does not support a production browser certification claim.
