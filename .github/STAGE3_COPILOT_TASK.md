# Gate 3B Stage 3 Copilot task

## Repository and branch boundary

Work only on the current PR head branch `implementation/gate3b-stage3-transition-route-stabilization`, which starts from exact Stage 2 SHA `4083acb035656b6c802814f861c3e9f80796fa0f` and targets `enhancement/gate3b-responsive-final-closure`.

Do not modify application business logic, calculations, governed data, qualification, recommendations, exports, dependencies, workflow files, viewport, browser, or Playwright version.

The final PR diff before review MUST contain exactly these three files and no others:

1. `src/browser_acceptance/minimal_runner.py`
2. `tests/browser_acceptance/test_minimal_contract.py`
3. `docs/enhancement_programme/GATE_3A_MINIMAL_BROWSER_ACCEPTANCE.md`

This task file `.github/STAGE3_COPILOT_TASK.md` is temporary. DELETE IT before finishing so it is absent from the final PR diff.

## Physical evidence driving the correction

Latest exact-head Chromium run against `4083acb035656b6c802814f861c3e9f80796fa0f` proved:

- narrow viewport `412 × 915`;
- pre-click sidebar state `COLLAPSED`;
- exact opener `[data-testid="stExpandSidebarButton"]`;
- exactly one opener;
- opener visible, enabled and viewport-intersecting;
- one normal Playwright click completed successfully;
- first post-click observation at ~222.744 ms was `PRESENT_OFF_CANVAS`;
- sidebar movement had begun;
- route enumeration was not reached.

The harness currently samples too early during CSS transition.

A dry-run review also found route-selection ordering defects that must be corrected in the same bounded implementation:

- current logic can require viewport intersection before a unique semantic route is allowed to scroll;
- fallback may be attempted after a preferred-route qualification failure instead of only when the preferred route is absent;
- locator is not explicitly reacquired after scrolling/Streamlit rerender;
- failure context may preserve stale pre-click sidebar state instead of latest observed state.

## Required Stage 3 implementation

### 1. Schema

Increment the evidence schema from `1.4.0` to `1.5.0`.

### 2. Sidebar transition observer

Preserve the exact opener selector `[data-testid="stExpandSidebarButton"]` and exactly one normal locator click when pre-state is exactly `COLLAPSED`.

Implement one deterministic bounded temporal observer using monotonic time and a small polling/yield mechanism. Do not use a single fixed post-click sleep as the success condition.

States remain:

- `MISSING`
- `COLLAPSED`
- `PRESENT_OFF_CANVAS`
- `TRANSITIONING`
- `OPEN_AND_REACHABLE`
- `AMBIGUOUS`

Permit these intermediate states after click while progress continues:

- `COLLAPSED`
- `PRESENT_OFF_CANVAS`
- `TRANSITIONING`

Each sample must record at least:

- sequence number;
- monotonic elapsed milliseconds;
- state and classification reasons;
- sidebar existence/count;
- Playwright visibility;
- width/height;
- left/right/top/bottom;
- transform;
- opacity;
- viewport intersection;
- centre-point intersection when applicable;
- forward-progress result;
- stable-open streak.

Success requires **two consecutive** `OPEN_AND_REACHABLE` samples with positive dimensions and viewport intersection.

Forward progress should be deterministic and may consider:

- left/right edges moving toward the viewport;
- width increasing;
- transform changing toward terminal position;
- viewport intersection becoming true;
- state progressing toward `OPEN_AND_REACHABLE`.

Do not require every metric to improve in every sample.

Add bounded stall detection using multiple consecutive non-progress samples. One sample must never constitute a stall.

Fail closed on:

- `MISSING`;
- `AMBIGUOUS`;
- timeout;
- bounded stall while still off canvas/transitioning;
- regression after apparent open progression;
- inconsistent evidence.

Persist complete transition history in `narrow-sidebar-post-open.json` including:

- schema version;
- opener selector and match count;
- pre-click state;
- click attempted/completed;
- observer timeout;
- polling policy;
- stall policy;
- sample count;
- ordered samples;
- first progress sample;
- first viewport-intersecting sample;
- first `OPEN_AND_REACHABLE` sample;
- second stable-open sample;
- stable-open streak;
- stall/timeout flags;
- terminal state and reason;
- total elapsed time.

### 3. Responsive route semantic uniqueness before scroll

Preferred route order remains:

1. `Showcase & Handoff`
2. `Capabilities & Limits`

Search inside the exact open sidebar scope using exact semantic link names.

For preferred route:

- count exact semantic matches before scrolling;
- if count > 1, fail immediately and do not evaluate fallback;
- if count == 1, select that semantic identity even if currently below/outside the viewport; do not evaluate fallback;
- if count == 0 only, evaluate the fallback route.

For fallback route:

- if count > 1, fail immediately;
- if count == 1, select it;
- if count == 0, fail with evidence.

Fallback is permitted only because the preferred route is genuinely absent. Never use fallback after preferred-route ambiguity, scroll failure, geometry failure, click failure, or destination failure.

Do not use `.first` or DOM order to identify responsive route candidates.

### 4. Scroll, reacquire, revalidate

After semantic uniqueness is established:

1. capture pre-scroll geometry;
2. scroll the uniquely selected semantic locator into view;
3. reacquire the route locator from the exact sidebar scope using the same exact accessible name;
4. recount and require exactly one match after reacquisition;
5. capture post-scroll geometry;
6. require visible, enabled, positive dimensions, viewport intersection, centre point inside viewport and pointer-events not disabled;
7. perform exactly one normal Playwright locator click;
8. record click attempted/completed;
9. do not substitute another route after click failure.

`narrow-candidate-geometry.json` must include at least:

- schema version;
- preference order;
- preferred/fallback titles and match counts;
- fallback evaluated/reason;
- selected title;
- semantic scope;
- pre-scroll geometry;
- post-scroll reacquired match count;
- post-scroll geometry;
- visible/enabled/intersection/centre/pointer-events;
- click attempted/completed;
- destination heading result.

### 5. Destination and Calculation Evidence

After the physical route click:

- verify the expected destination heading;
- verify application readiness and no visible exception;
- then use the already governed resolved URL for narrow `Calculation Evidence` verification;
- preserve `412 × 915`;
- preserve zero page errors and zero material console errors;
- capture narrow success screenshot on success.

### 6. Latest-state failure evidence

Failure evidence must report the latest physically observed state, not stale pre-click state.

`failure-context.json` must include at least:

- exact failing phase;
- exception type/message;
- latest sidebar state/sample;
- transition terminal reason;
- transition sample count;
- stable-open streak;
- route-selection reached;
- selected route;
- pre-scroll reached;
- post-scroll reacquisition reached;
- route click attempted/completed;
- destination verification reached;
- evidence filenames and actual write status.

Before re-raising responsive exceptions, best-effort refresh/write:

- `failure.png`;
- `failure-context.json`;
- `narrow-sidebar-post-open.json` when opener path was reached;
- `narrow-link-inventory.json`;
- `narrow-candidate-geometry.json` when route path was reached.

### 7. Required tests

Update/add focused contract tests proving at minimum:

- schema `1.5.0`;
- `OPEN_AND_REACHABLE` path performs no opener click;
- `COLLAPSED → PRESENT_OFF_CANVAS → OPEN_AND_REACHABLE` succeeds;
- `COLLAPSED → TRANSITIONING → OPEN_AND_REACHABLE` succeeds;
- two consecutive stable-open samples required;
- stable-open streak resets on regression;
- off-canvas progress is permitted;
- bounded stall and timeout fail;
- `MISSING` and `AMBIGUOUS` fail;
- exactly one opener click;
- no force/JavaScript/dispatch-event/coordinate click;
- no generic/fallback opener;
- semantic uniqueness happens before scroll;
- preferred route may begin outside viewport;
- duplicate preferred fails closed and fallback is not evaluated;
- fallback is evaluated only when preferred count is zero;
- duplicate fallback fails closed;
- both routes absent fails;
- locator is reacquired after scroll;
- post-scroll exact count must remain one;
- visible/enabled/positive geometry/intersection/centre/pointer-events checks remain;
- failed preferred click/destination does not trigger fallback;
- latest-state failure evidence is preserved;
- no random evidence IDs or evidence-only DOM mutation;
- route enumeration only occurs after stable sidebar success;
- governed narrow Calculation Evidence, JSON and Markdown export controls remain unchanged.

Run the focused browser contract suite and any repository tests required by existing project guidance.

### 8. Documentation

Update `docs/enhancement_programme/GATE_3A_MINIMAL_BROWSER_ACCEPTANCE.md` to document:

- Stage 2 physical transition evidence;
- why one post-click sample was insufficient;
- temporal state machine;
- progress/stall rules;
- two-sample stable terminal requirement;
- semantic uniqueness before scroll;
- fallback only on preferred absence;
- post-scroll locator reacquisition;
- fail-closed ambiguity;
- latest-state evidence;
- browser acceptance still unpassed pending exact-head CI and one physical Chromium PASS;
- no production browser certification claim.

## Prohibited shortcuts

Do not introduce:

- force clicks;
- JS clicks;
- `dispatch_event` clicks;
- coordinate clicks;
- generated CSS/nth-child selectors;
- arbitrary fixed recovery sleeps as the success mechanism;
- automatic retries;
- second opener click;
- generic opener fallback;
- `.first` for responsive route identity;
- DOM mutation for evidence;
- workflow changes;
- dependencies;
- application/business/data changes.

## Final branch requirements

Before finishing:

1. DELETE `.github/STAGE3_COPILOT_TASK.md`.
2. Ensure final diff versus `4083acb035656b6c802814f861c3e9f80796fa0f` contains exactly the three authorized files and no others.
3. Ensure focused tests pass.
4. Ensure no workflow file changed.
5. Do not merge the PR.
6. Leave the PR ready for external governed review.
