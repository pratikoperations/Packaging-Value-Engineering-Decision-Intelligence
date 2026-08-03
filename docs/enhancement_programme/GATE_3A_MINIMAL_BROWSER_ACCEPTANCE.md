# Gate 3B — Governed Responsive Final Closure

## Status

Stage 2 exact-opener and deterministic-evidence candidate. Browser acceptance remains unpassed, and no production browser certification is claimed.

Stage 1 physically established that the narrow sidebar is `COLLAPSED` at 412 × 915 and identified the exact visible, enabled, viewport-intersecting Streamlit opener as `[data-testid="stExpandSidebarButton"]`. The Stage 1 run stopped before responsive route-candidate enumeration, so the corrected route-selection logic has not yet been physically accepted.

## Purpose

Gate 3B verifies that the exact integrated programme version can start, render, expose all registered routes, accept representative scenario inputs, display Calculation Evidence, produce governed JSON and Markdown downloads, complete desktop grouped navigation, and demonstrate meaningful responsive access at Android-sized width.

Stage 2 implements the smallest evidence-backed correction: one exact evidence-backed physical opener click for the confirmed `COLLAPSED` state, followed by post-open state and geometry verification. It also removes random evidence identifiers and all evidence-only DOM mutation from control inventory deduplication.

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
12. When the sidebar is already `OPEN_AND_REACHABLE`, continue without an opener click.
13. When the sidebar is exactly `COLLAPSED`, require one unique, visible, enabled and viewport-intersecting `[data-testid="stExpandSidebarButton"]`.
14. Physically click that exact opener once using a normal Playwright locator click.
15. Wait for the sidebar to become visible, recapture its state and geometry, and require `OPEN_AND_REACHABLE` with positive dimensions and viewport intersection.
16. Enumerate all exact semantic route matches and select exactly one visible instance whose rendered rectangle intersects the active viewport.
17. Revalidate viewport intersection and clickable-centre geometry after scrolling the selected instance.
18. Verify the responsive physical-click destination heading.
19. Navigate to the already resolved governed Calculation Evidence destination at narrow width and verify its heading.
20. Guarantee responsive failure evidence before re-raising any exception.
21. Reject visible Streamlit exceptions, Playwright page errors and material browser-console errors.
22. Require one successful exact-head run before acceptance.

## Stage 1 physical evidence

The accepted Stage 1 diagnostic run established:

- viewport: `412 × 915`;
- sidebar state: `COLLAPSED`;
- sidebar exists in the DOM;
- rendered width: `0`;
- rendered height: `915`;
- transform: `matrix(1, 0, 0, 1, -300, 0)`;
- sidebar viewport intersection: false;
- exact opener: `[data-testid="stExpandSidebarButton"]`;
- opener match observed in `stHeader`;
- opener visible, enabled and viewport-intersecting;
- no speculative click was attempted;
- responsive route-candidate enumeration was not reached.

This evidence authorizes only the exact Stage 2 opener behavior. It does not authorize a generic role/name locator, icon-name locator, DOM-order fallback or speculative control search.

## Sidebar-state decision

Home-link visibility is not the responsive sidebar-state contract. A route link is downstream content, not the state primitive for the sidebar container.

The responsive state model uses `[data-testid="stSidebar"]` existence, Playwright visibility, non-zero rendered geometry, computed display, visibility, opacity and viewport intersection. It records one of:

- `OPEN_AND_REACHABLE`;
- `PRESENT_OFF_CANVAS`;
- `COLLAPSED`;
- `TRANSITIONING`;
- `MISSING`;
- `AMBIGUOUS`.

`OPEN_AND_REACHABLE` requires the sidebar to exist, be visibly rendered with non-zero dimensions and meaningfully intersect the 412 × 915 viewport.

State handling is fail-closed:

- `OPEN_AND_REACHABLE`: continue without clicking;
- `COLLAPSED`: apply the exact governed opener contract;
- `PRESENT_OFF_CANVAS`, `TRANSITIONING`, `MISSING` and `AMBIGUOUS`: fail with evidence and do not click.

## Deterministic evidence controls

Before responsive sidebar-state classification, the harness writes:

- `screenshots/narrow-pre-action.png`;
- `narrow-sidebar-controls.json`.

The control inventory inspects, when present:

- `[data-testid="stSidebar"]`;
- `[data-testid="stSidebarCollapsedControl"]`;
- `[data-testid="stSidebarHeader"]`;
- `[data-testid="stHeader"]`.

Control deduplication uses a deterministic metadata signature comprising discovery scope, tag, role, accessible name, title, aria-label, data-testid, id, rendered rectangle, visibility, enabled state and viewport intersection. Signatures are JSON-serialized with sorted keys and the final inventory is deterministically ordered.

The inventory does not assign temporary attributes, does not use random values, does not depend on Python object identity, and does not mutate the application DOM.

## Exact opener controls

The responsive opener contract is limited to:

`[data-testid="stExpandSidebarButton"]`

Required guards:

- sidebar pre-state is exactly `COLLAPSED`;
- exactly one opener match;
- visible;
- enabled;
- non-zero geometry;
- viewport intersection;
- one normal Playwright click;
- no force click;
- no JavaScript click;
- no coordinate click;
- no accessible-name or icon-name primary locator;
- no `.first` selection or generic fallback.

After click, the harness writes `narrow-sidebar-post-open.json`, including the locator, match count, opener evidence, click-attempt and completion flags, pre-click state, post-click state, elapsed transition time and complete post-open sidebar evidence.

The route sequence continues only when the recaptured state is `OPEN_AND_REACHABLE`, the sidebar has positive rendered width and height, and its rectangle intersects the viewport.

## Responsive route-selection controls

The responsive contract validates user access and governed destination behavior at Android-sized width. It does not require the narrow layout to reproduce desktop sidebar grouping semantics.

Preserved controls:

- collect global and open-sidebar candidate counts;
- collect geometry, computed-style, ancestry and scroll-owner evidence for every exact semantic match;
- require exactly one visible, non-zero-size candidate intersecting the 412 × 915 viewport;
- reject zero or multiple qualifying candidates;
- prefer `Showcase & Handoff` and otherwise `Capabilities & Limits`;
- scroll only the uniquely selected candidate;
- recalculate geometry after scrolling;
- require the candidate centre point inside the viewport before a normal locator click;
- never substitute another route after a physical click failure.

## Failure-evidence boundary

The entire responsive sequence is covered by one evidence-producing exception boundary, including pre-action capture, state classification, exact opening, post-open verification, route selection, click, destination verification and narrow Calculation Evidence verification.

On responsive failure, the harness attempts to preserve:

- `screenshots/failure.png`;
- `failure-context.json`;
- `narrow-sidebar-controls.json`;
- `narrow-sidebar-post-open.json` when opener processing begins;
- `narrow-link-inventory.json`;
- `narrow-candidate-geometry.json` when route selection has begun.

`failure-context.json` records the exception type and message, failing phase, current URL, source commit, tested branch, sidebar classification and details, control-inventory summary, evidence filenames and evidence-write status.

## Preserved acceptance controls

- desktop four-group navigation;
- exactly 13 unique routes;
- governed scenario interaction;
- JSON and Markdown export validation;
- Calculation Evidence checks;
- zero material console errors;
- zero page errors;
- tracked-file cleanliness;
- PASS only after responsive route and narrow Calculation Evidence assertions succeed.

## Explicit exclusions

- Stage 2 does not itself establish browser acceptance;
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
- `narrow-sidebar-post-open.json` when the collapsed opener path is used;
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

## Required validation sequence

A new exact-head standard CI run is required after the Stage 2 commit.

A new exact-head physical Chromium run is required only after the Stage 2 standard CI result is reviewed and the default-branch workflow is repinned through a separate governed authorization.

Until both validation steps succeed and are reviewed, browser acceptance remains unpassed and no production browser certification is claimed.
