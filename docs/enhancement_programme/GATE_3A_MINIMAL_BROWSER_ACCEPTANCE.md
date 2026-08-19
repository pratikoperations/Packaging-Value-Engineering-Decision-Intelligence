# Gate 3B — Governed Responsive Final Closure

## Status

Stage 3 transition-stabilized responsive routing candidate. Browser acceptance remains unpassed, and no production browser certification is claimed.

## Stage 2 physical transition evidence and Stage 3 correction

Stage 1 physically established that the narrow sidebar is `COLLAPSED` at `412 × 915` and identified the exact Streamlit opener `[data-testid="stExpandSidebarButton"]`.

Stage 2 physical run recorded `COLLAPSED → PRESENT_OFF_CANVAS` immediately after one exact opener click. That evidence proved movement started, but route enumeration was not reached. Because one post-click sample was insufficient, Stage 3 replaces one-shot post-click classification with a bounded temporal observer.

## Temporal sidebar state machine (Stage 3)

The responsive observer tracks only governed states:

- `MISSING`
- `COLLAPSED`
- `PRESENT_OFF_CANVAS`
- `TRANSITIONING`
- `OPEN_AND_REACHABLE`
- `AMBIGUOUS`

For collapsed-open flows, the harness performs exactly one normal Playwright click on `[data-testid="stExpandSidebarButton"]`, then samples the sidebar over monotonic elapsed time. Each sample records sequence, elapsed milliseconds, classification reasons, existence/count, visibility, geometry, transform, opacity, viewport intersection, centre-point status, progress signal, and stable-open streak.

### Progress and stall rules

- Intermediate post-click states `COLLAPSED`, `PRESENT_OFF_CANVAS`, and `TRANSITIONING` are permitted while forward progress continues.
- Forward progress is deterministic and can come from state rank improvement, geometry movement toward viewport, width growth, transform change, or viewport intersection becoming true.
- A single non-progress sample is tolerated.
- Bounded stall requires multiple consecutive non-progress samples.
- `MISSING` or `AMBIGUOUS` fail closed immediately.
- Regression after open progression fails closed.
- Timeout before stabilization fails closed.

### Stable terminal requirement

Success requires two consecutive `OPEN_AND_REACHABLE` samples with positive geometry and viewport intersection. This replaces the prior one-sample assumption.

## Responsive route selection controls (Stage 3)

Responsive route identity is resolved by semantic uniqueness before any responsive scroll within the exact open-sidebar scope:

1. Preferred route: `Showcase & Handoff`
2. Fallback route: `Capabilities & Limits`

Rules:

- If preferred count > 1: fail closed; fallback is not evaluated.
- If preferred count == 1: select preferred even if initially outside viewport; fallback is not evaluated.
- If preferred count == 0: evaluate fallback.
- If fallback count > 1: fail closed.
- If fallback count == 1: select fallback.
- If both are absent: fail closed.

In Stage 3, fallback is evaluated only when preferred is absent.

No DOM-order identity and no `.first` route-identity shortcut are used.

## Scroll, reacquisition, and click validation

After semantic uniqueness is established, Stage 3:

1. Captures pre-scroll candidate geometry.
2. Scrolls the selected locator into view.
3. Reacquires the semantic locator after scrolling from the same sidebar scope.
4. Requires post-scroll exact match count to remain one.
5. Captures post-scroll geometry.
6. Requires visible, enabled, positive geometry, viewport intersection, centre-point in viewport, and pointer-events enabled.
7. Performs exactly one normal Playwright click.
8. Verifies destination heading.

Fallback is never re-invoked after preferred ambiguity, click failure, or destination failure.

The responsive route stage reacquires the semantic locator after scrolling before the click contract is evaluated.

## Latest-state failure evidence

Failure context is updated to preserve latest physically observed sidebar state sample and transition terminal reason, not only pre-click classification. The responsive boundary attempts best-effort refresh of:

- `screenshots/failure.png`
- `failure-context.json`
- `narrow-sidebar-post-open.json` (when opener path is reached)
- `narrow-link-inventory.json`
- `narrow-candidate-geometry.json` (when route path is reached)

## Preserved governed controls

- Narrow viewport remains `412 × 915`.
- Desktop grouped navigation, governed JSON/Markdown export validation, and governed Calculation Evidence checks remain unchanged.
- Zero material console errors and zero page errors remain required.
- No force click, JavaScript click, dispatch-event click, coordinate click, generic opener fallback, workflow change, dependency change, or business/data logic mutation is introduced.

## Validation boundary

A new exact-head standard CI run is required.

A new exact-head physical Chromium run is required.

Until both validations succeed and are reviewed, browser acceptance remains unpassed and no production browser certification is claimed.
