# Automated Browser Acceptance Strategy

## Objective

Add a Playwright-based acceptance layer that verifies Streamlit behaviour without replacing the existing unit and regression suite.

## Target environments

- Primary CI target: locally started Streamlit application on an ephemeral port.
- Final smoke target: accepted hosted enhancement URL after integration authorization.
- Browser scope: Chromium desktop plus one Android-sized browser viewport.
- Native Android or iOS support is not claimed.

## Startup and teardown

CI must start Streamlit as a managed subprocess, allocate an unused port, poll a governed readiness signal until ready, record startup logs, and terminate the process in teardown even after test failure. Startup timeout must be explicit and capped at 60 seconds unless separately justified.

## Planned coverage

- application startup and health;
- all 13 registered pages;
- directly visible Home, Showcase & Handoff and Capabilities & Limits links;
- four governed sidebar groups;
- five-minute demonstration route;
- synthetic-data disclosure visibility;
- Markdown and JSON downloads;
- absence of visible uncaught Streamlit exceptions;
- desktop viewport;
- Android-sized viewport;
- retained proof-versus-limit content.

## Selectors and waits

Use stable accessible roles, governed labels or explicit test identifiers owned by the application. Do not select by generated CSS classes or fragile DOM position. Use readiness conditions and locator assertions rather than arbitrary sleeps.

## Timeout and retry policy

- per-action timeout: 10 seconds;
- navigation/readiness timeout: 30 seconds;
- application startup timeout: 60 seconds;
- final acceptance evidence: zero automatic retries;
- diagnostic rerun may be performed once but must be reported as instability and cannot replace a clean acceptance run.

## Runtime error capture

Capture browser `pageerror`, uncaught exceptions, failed network requests relevant to application operation, and console errors. Expected benign warnings must be explicitly allowlisted; unexplained errors fail the run.

## Export-content validation

Downloads must be more than present: Markdown must decode and contain required headings and synthetic limitations; JSON must parse, contain required keys and preserve synthetic-data disclosure. Each test uses an isolated download directory.

## Reliability gate

Final browser acceptance requires three consecutive clean CI runs at the same exact SHA, with no retry-dependent pass and no unexplained flaky failure.

## CI evidence

A successful run retains exact SHA, browser version, result summary, startup log, downloaded-file validation summary, artifact digest, and traces/screenshots on failure or selected checkpoints.

## Exclusions

- comprehensive cross-browser certification;
- native mobile testing;
- performance or load testing;
- accessibility certification;
- full visual-regression baselines.

## Initial effort ceiling

24 hours, excluding contingency. Scope must be reduced rather than exceeding the programme cap.
