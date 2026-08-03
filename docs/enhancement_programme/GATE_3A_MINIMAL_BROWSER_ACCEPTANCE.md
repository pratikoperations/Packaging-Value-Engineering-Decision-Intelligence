# Gate 3B — Governed Responsive Final Closure

## Status

Stage 1 evidence-first diagnostics and sidebar-state classification candidate. Browser acceptance remains unpassed, and no production browser certification is claimed.

The latest physical failure occurred before responsive route-candidate enumeration. The run failed inside the previous sidebar-opening helper while waiting for an unverified role/name locator. The existing viewport-intersection route-selection correction was therefore not physically exercised.

## Purpose

Gate 3B verifies that the exact integrated programme version can start, render, expose all registered routes, accept representative scenario inputs, display Calculation Evidence, produce governed JSON and Markdown downloads, complete desktop grouped navigation, and demonstrate meaningful responsive access at Android-sized width.

Stage 1 is diagnostic and state-classification work. It improves observability and removes unsafe responsive sidebar-opening assumptions without introducing a speculative opener click strategy.

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
10. At 412 × 915, capture pre-action sidebar and control evidence before any responsive state decision.
11. Classify the sidebar from its container geometry, computed state and viewport intersection.
12. Proceed only when the sidebar is already OPEN_AND_REACHABLE.
13. Enumerate all exact semantic route matches and select exactly one visible instance whose rendered rectangle intersects the active viewport.
14. Revalidate viewport intersection and clickable-centre geometry after scrolling the selected instance.
15. Verify the responsive physical-click destination heading.
16. Navigate to the already resolved governed Calculation Evidence destination at narrow width and verify its heading.
17. Guarantee responsive failure evidence before re-raising any exception.
18. Reject visible Streamlit exceptions, Playwright page errors and material browser-console errors.
19. Require one successful exact-head run before acceptance.

## Stage 1 sidebar-state decision

Home-link visibility is no longer the responsive sidebar-state contract. A route link is downstream content, not the state primitive for the sidebar container.

The responsive state model uses `[data-testid="stSidebar"]` existence, Playwright visibility, non-zero rendered geometry, computed display, visibility, opacity and viewport intersection. It records one of:

- `OPEN_AND_REACHABLE`;
- `PRESENT_OFF_CANVAS`;
- `COLLAPSED`;
- `TRANSITIONING`;
- `MISSING`;
- `AMBIGUOUS`.

`OPEN_AND_REACHABLE` requires the sidebar to exist, be visibly rendered with non-zero dimensions and meaningfully intersect the 412 × 915 viewport.

Stage 1 does not assume or click a new sidebar opener. If the sidebar is not already open and reachable, the harness fails deterministically with full evidence. A later opener-behaviour change requires direct evidence from the Stage 1 physical artifact.

## Evidence-first controls

Before responsive sidebar-state classification, the harness writes:

- `screenshots/narrow-pre-action.png`;
- `narrow-sidebar-controls.json`.

The control inventory inspects, when present:

- `[data-testid="stSidebar"]`;
- `[data-testid="stSidebarCollapsedControl"]`;
- `[data-testid="stSidebarHeader"]`;
- `[data-testid="stHeader"]`.

It enumerates unique relevant controls using `nth(index)` and records accessible metadata, Playwright and DOM geometry, computed styles, viewport and centre-point intersection, DOM ancestry and nearest scroll-owner evidence.

The responsive sidebar path does not use the generic `_first_visible()` helper, `.first.wait_for()` or `.first.click()` to discover or activate an opener.

## Responsive route-selection controls

The responsive contract validates user access and governed destination behavior at Android-sized width. It does not require the narrow layout to reproduce desktop sidebar grouping semantics.

The responsive harness selects the exact semantic link instance that is physically reachable in the active viewport. It does not assume DOM order or identical desktop and mobile navigation markup.

Preserved controls:

- collect global and open-sidebar candidate counts;
- collect geometry, computed-style, ancestry and scroll-owner evidence for every exact semantic match;
- require exactly one visible, non-zero-size candidate intersecting the 412 × 915 viewport;
- reject zero or multiple qualifying candidates;
- scroll only the uniquely selected candidate;
- recalculate geometry after scrolling;
- require the candidate centre point to lie inside the viewport before a normal locator click;
- prohibit DOM-order selection through `.first` for the responsive route;
- retain a controlled fallback route only before click when the preferred route has no uniquely qualifying candidate;
- never substitute another route after a physical click failure.

## Failure-evidence boundary

The entire responsive sequence is covered by one evidence-producing exception boundary, including pre-action capture, state classification, future opening logic, route selection, click, destination verification and narrow Calculation Evidence verification.

On responsive failure, the harness attempts to preserve:

- `screenshots/failure.png`;
- `failure-context.json`;
- `narrow-sidebar-controls.json`;
- `narrow-link-inventory.json`;
- `narrow-candidate-geometry.json` when route selection has begun.

`failure-context.json` records the exception type and message, failing phase, current URL, source commit, tested branch, sidebar classification and details, control-inventory summary, evidence filenames and evidence-write status. A detailed inner failure context is not replaced by a less detailed outer record.

## Preserved acceptance controls

- desktop four-group navigation;
- exactly 13 unique routes;
- governed scenario interaction;
- JSON and Markdown export validation;
- Calculation Evidence checks;
- zero material console errors;
- zero page errors;
- tracked-file cleanliness;
- PASS only after the responsive route and narrow Calculation Evidence assertions succeed.

## Explicit exclusions

- no speculative sidebar-opener click in Stage 1;
- no three-run ledger;
- no production browser certification;
- no cross-browser certification;
- no hosted-environment reliability claim;
- no load, performance or accessibility certification;
- no production data;
- no business-formula, governed-data, recommendation, qualification, risk or export-calculation changes;
- no autonomous procurement or technical approval;
- no Power BI runtime validation.

## Execution controls

- Ubuntu 24.04;
- Python 3.12;
- Playwright Chromium only;
- viewport 412 × 915 for responsive acceptance;
- zero automatic retries;
- no force click;
- no coordinate clicks;
- no generated positional or `nth-child` selectors;
- no JavaScript or dispatch-event click;
- no application or Streamlit session-state mutation;
- no fixed recovery sleep;
- read-only repository permission;
- exact-SHA reporting;
- tracked-file cleanliness.

## Required evidence

- `acceptance-report.json`;
- `route-inventory.json`;
- `runtime-events.json`;
- `narrow-sidebar-controls.json`;
- `screenshots/narrow-pre-action.png`;
- `narrow-link-inventory.json`;
- `narrow-candidate-geometry.json` when route selection is reached;
- selected candidate index and href;
- pre-scroll and post-scroll rectangles;
- destination-heading result;
- governed JSON and Markdown downloads;
- Home and Calculation Evidence desktop screenshots;
- `screenshots/narrow-smoke.png` on success;
- `screenshots/failure.png` and `failure-context.json` when applicable;
- Streamlit log.

## Passing claim

A future successful exact-head run may support the claim that the portfolio prototype has a governed Chromium acceptance check covering startup, all registered routes, representative scenario-input interaction, Calculation Evidence, decision-package downloads, desktop grouped navigation and meaningful Android-sized responsive access.

Until that run succeeds and is reviewed, browser acceptance remains unpassed and no production browser certification is claimed.
