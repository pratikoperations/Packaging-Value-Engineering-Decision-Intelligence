# Automated Browser Acceptance Strategy

## Objective

Add a Playwright-based acceptance layer that verifies hosted or locally started Streamlit behaviour without replacing the existing unit and regression suite.

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

## Test design principles

- use stable accessible selectors or governed labels;
- avoid brittle pixel-perfect comparisons;
- use explicit readiness conditions rather than arbitrary sleeps;
- capture traces and screenshots only on failure and selected acceptance checkpoints;
- isolate download directories per test;
- keep tests deterministic and read-only;
- run the existing regression suite separately.

## Planned test modules

- startup and smoke;
- navigation inventory;
- sidebar grouping;
- showcase journey;
- export downloads;
- governance disclosures;
- mobile viewport;
- runtime error detection.

## CI evidence

A successful run must retain:

- exact commit SHA;
- browser version;
- test result summary;
- failure trace and screenshots when applicable;
- downloaded export checks;
- artifact digest.

## Exclusions

- comprehensive cross-browser certification;
- native mobile testing;
- performance or load testing;
- accessibility certification;
- full visual-regression baselines.

## Initial effort ceiling

24 hours, excluding contingency. Scope must be reduced rather than exceeding the programme cap.
