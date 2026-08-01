# Gate 3 Automated Browser Acceptance Implementation

## Status

Implementation candidate. Exact-head browser CI and three consecutive clean runs remain required.

## Baseline

- Programme SHA: `745e99fe8ec24cbb0dad7dcf700c70f70fe32750`
- Frozen showcase SHA: `2954c293ca09882cadd7f23b5862f50334170a11`
- Unchanged main SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`
- Feature branch: `enhancement/automated-browser-acceptance`

## Scope

- test-only Playwright dependency in `requirements-browser.txt`;
- Chromium only;
- managed local Streamlit process on an ephemeral localhost port;
- 60-second startup timeout and governed health polling;
- graceful process-group shutdown with force-kill fallback;
- desktop viewport `1440 x 1000`;
- Android-sized viewport `412 x 915`;
- 13 registered page contracts;
- four sidebar group contracts;
- scenario, recommendation, Calculation Evidence and export journeys;
- JSON and Markdown content validation;
- page error, console error, failed request and HTTP 5xx capture;
- checkpoint screenshots and machine-readable run summary;
- zero automatic retries.

## Acceptance gate

Final Gate 3 acceptance requires three separately dispatched clean workflow runs at the same exact SHA. A diagnostic rerun after a failure does not count.

## Limitations

- Chromium browser acceptance, not cross-browser certification;
- responsive narrow viewport, not native Android testing;
- no accessibility certification;
- no load or performance testing;
- no hosted enhancement validation until an exact accepted enhancement SHA is deployed separately;
- no production-readiness claim.

## Governance boundaries

The implementation must not modify primary business engines, governed synthetic datasets, independent calculation formulas, `main`, or `showcase-handoff-development`.
