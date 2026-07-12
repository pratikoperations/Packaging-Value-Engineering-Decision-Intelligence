# PVE-0.6 QA Report

## Build
PVE-0.6 — Decision Package Export

## Scope
Deterministic assembly of a read-only packaging decision package with machine-readable JSON and human-readable Markdown report exports.

## Decision-Package Contents
- Package metadata and explicit internal schema/version status
- Structured executive summary
- Project and category context
- Scenario volume and applied assumptions
- Baseline specification and results
- Proposed-alternative cost and material results
- Technical qualification outcomes, reasons, evidence, and gaps
- Quality, supply, and implementation risk outcomes
- Recommendation status, rationale, constraints, and validation requirements
- Explicit decision controls preventing autonomous approval, allocation, external integration, or final-contract claims

## Export Formats
- Deterministic, sorted, UTF-8 JSON with trailing newline
- Deterministic Markdown executive report
- Streamlit download controls for both formats

## Validation Rules
- Required top-level sections must be present.
- Metadata, project identity, source commit, and generated timestamp must be non-empty.
- Annual volume must be positive.
- Exactly one baseline alternative must exist and match the baseline specification.
- Scenario, qualification, and risk outcomes must cover every alternative.
- Recommendation outcomes must cover every proposed alternative.
- Exported alternative identifiers must be unique.
- Every proposed alternative must include cost/material, qualification, risk, and recommendation sections.
- Decision controls must remain read-only and must explicitly reject autonomous technical approval, supplier allocation, external integration, and final integration-contract status.

## Automated Tests
Ten new tests cover:
1. Required package sections
2. Deterministic assembly and JSON rendering
3. Complete decision basis
4. Safety and ownership controls
5. Machine-readable JSON
6. Human-readable Markdown
7. Missing-section validation
8. Decision-control tampering rejection
9. Missing scenario-alternative rejection
10. Required source-commit metadata

Existing tests remain in scope. Expected total automated test count: 52.

## Scope Exclusions
- No autonomous technical approval
- No supplier allocation
- No final integration contract
- No external system integration
- No PVE-0.7 release packaging

## QA Status
**Conditional Pass** — implementation and test coverage are complete; final status depends on successful PVE CI and full PR-diff review.

## Release Recommendation
Open a draft PR. PVE-0.7 may begin only after PVE-0.6 passes CI and QA and is merged into `main`.
