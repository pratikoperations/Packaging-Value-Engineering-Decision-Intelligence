# Gate 3B — Governed Responsive Final Closure

## Status

Implementation candidate derived from the preserved Gate 3A browser-acceptance work. Gate 3B replaces only the brittle narrow grouped-sidebar expansion assertion. It does not claim acceptance until one successful exact-head physical Chromium run is reviewed.

## Purpose

Gate 3B verifies that the exact integrated programme version can start, render, expose all registered routes, accept representative scenario inputs, display Calculation Evidence, produce governed JSON and Markdown downloads, complete desktop grouped navigation, and demonstrate meaningful responsive access at Android-sized width.

## Acceptance scope

1. Start the Streamlit application.
2. Render the exact Home heading.
3. Resolve exactly 13 non-empty, unique route destinations.
4. Verify the four desktop sidebar groups through route discovery.
5. Select one governed synthetic scenario.
6. Change annual volume, one unit-cost adjustment and one material-weight adjustment.
7. Verify Calculation Evidence is visible.
8. Download and validate machine-readable JSON and human-readable Markdown.
9. Perform one physical desktop grouped-sidebar navigation to Calculation Evidence.
10. At 412 × 915, physically open the sidebar and click one controlled route exposed by the responsive layout, preferring Showcase & Handoff and otherwise Capabilities & Limits.
11. Enumerate all exact semantic route matches and select exactly one visible instance whose rendered rectangle intersects the active viewport.
12. Revalidate viewport intersection and clickable-centre geometry after scrolling the selected instance.
13. Verify the responsive physical-click destination heading.
14. Navigate to the already resolved governed Calculation Evidence destination at narrow width and verify its heading.
15. Capture narrow success evidence and, when applicable, failure evidence before browser state is discarded.
16. Reject visible Streamlit exceptions, Playwright page errors and material browser-console errors.
17. Require one successful exact-head run.

## Responsive-contract decision

The responsive contract validates user access and governed destination behavior at Android-sized width. It does not require the narrow layout to reproduce desktop sidebar grouping semantics.

The responsive harness selects the exact semantic link instance that is physically reachable in the active viewport. It does not assume DOM order or identical desktop and mobile navigation markup.

Desktop acceptance remains responsible for proving all four grouped-sidebar structures and physical grouped navigation. Narrow acceptance remains responsible for proving physical interaction, controlled-route access, governed destination behavior and absence of material runtime errors.

## Candidate-selection controls

- collect global and open-sidebar candidate counts;
- collect geometry, computed-style, ancestry and scroll-owner evidence for every exact semantic match;
- require exactly one visible, non-zero-size candidate intersecting the 412 × 915 viewport;
- reject zero or multiple qualifying candidates;
- scroll only the uniquely selected candidate;
- recalculate geometry after scrolling;
- require the candidate centre point to lie inside the viewport before a normal locator click;
- prohibit DOM-order selection through `.first` for the responsive route;
- retain a controlled fallback route only when the preferred route is absent or has no uniquely qualifying candidate;
- never substitute another route after a physical click failure.

## Explicit exclusions

- no three-run ledger;
- no production browser certification;
- no cross-browser certification;
- no hosted-environment reliability claim;
- no load, performance or accessibility certification;
- no production data;
- no business-formula, governed-data, recommendation, qualification, risk or export-calculation changes;
- no autonomous procurement or technical approval;
- no Power BI runtime validation.

## Dependency isolation

Playwright remains an optional browser-validation dependency. The package root uses a lazy runner import and standard repository contract tests import only dependency-free contracts, diagnostics, export validators and process-management helpers.

## Execution controls

- Ubuntu 24.04;
- Python 3.12;
- Playwright Chromium only;
- zero automatic retries;
- no force click;
- no coordinate clicks;
- no generated CSS selectors;
- no JavaScript or dispatch-event click;
- no application session-state mutation;
- no fixed recovery sleep;
- read-only repository permission;
- exact-SHA reporting;
- tracked-file cleanliness.

## Required evidence

- `acceptance-report.json`;
- `route-inventory.json`;
- `runtime-events.json`;
- `narrow-link-inventory.json`;
- `narrow-candidate-geometry.json`;
- selected candidate index and href;
- pre-scroll and post-scroll rectangles;
- destination-heading result;
- governed JSON and Markdown downloads;
- Home and Calculation Evidence desktop screenshots;
- `narrow-smoke.png` on success;
- `failure.png` and `failure-context.json` when applicable;
- Streamlit log.

## Passing claim

A successful exact-head run supports the claim that the portfolio prototype has a governed Chromium acceptance check covering startup, all registered routes, representative scenario-input interaction, Calculation Evidence, decision-package downloads, desktop grouped navigation, and meaningful Android-sized responsive access.

It does not support a production browser-certification claim.
