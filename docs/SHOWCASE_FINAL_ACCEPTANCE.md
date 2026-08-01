# Showcase Final Acceptance

## Status

**Acceptance state: PASSED — EXACT-HEAD CI AND HOSTED DESKTOP/ANDROID EVIDENCE RECORDED**

This document records final pre-merge acceptance of Build 6 against one exact feature-branch commit. Post-merge validation remains required against the resulting integration merge SHA before the showcase can be declared frozen.

## Repository identity

- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Candidate branch: `showcase/build-6-final-hardening-freeze`
- Required base SHA: `ac42a215e5a35697e8c9f0bc14eb75c3120fc0e5`
- Exact tested SHA: `a30aa9c78a3d35158ad7f7b6a0d95009c6baaa77`
- Hosted preview: `https://packaging-value-engineering-decision-intelligence-build6.streamlit.app`

## Page inventory

1. Home
2. Showcase & Handoff
3. Project Dashboard
4. Guided Workflow
5. Specification Review
6. Data Upload
7. Business Rules & Thresholds
8. Scenario Analysis
9. Decision Records
10. SourceMate
11. Calculation Evidence
12. Decision Evidence Ledger
13. Capabilities & Limits

## Sidebar structure accepted

Directly visible:

- Home
- Showcase & Handoff
- Capabilities & Limits

Collapsible groups:

- Workspace: Project Dashboard; Guided Workflow
- Inputs & Governance: Specification Review; Data Upload; Business Rules & Thresholds
- Analysis & Decision: Scenario Analysis; Decision Records
- Evidence & Explanation: SourceMate; Calculation Evidence; Decision Evidence Ledger

## Per-page hosted acceptance

Desktop and Android evidence demonstrated that the application starts, the governed sidebar renders, grouped navigation is usable, representative grouped pages open, the five-minute Showcase & Handoff journey renders, synthetic-data disclosure remains visible, and no uncaught red runtime exception appears in the accepted route.

| Page | Desktop | Android | Notes |
|---|---|---|---|
| Home | PASS | PASS | Synthetic-data warning visible. |
| Showcase & Handoff | PASS | PASS | Five-minute route, seven governed steps, and controlled links render. |
| Project Dashboard | PASS | PASS | Grouped navigation and selected-page state verified. |
| Guided Workflow | PASS | PASS | Rendered in hosted evidence. |
| Specification Review | PASS | PASS | Available in accepted Inputs & Governance group. |
| Data Upload | PASS | PASS | Available in accepted Inputs & Governance group. |
| Business Rules & Thresholds | PASS | PASS | Available in accepted Inputs & Governance group. |
| Scenario Analysis | PASS | PASS | Controlled link and grouped page opening verified. |
| Decision Records | PASS | PASS | Rendered in hosted evidence. |
| SourceMate | PASS | PASS | Rendered without uncaught exception. |
| Calculation Evidence | PASS | PASS | Controlled route preserved and accepted. |
| Decision Evidence Ledger | PASS | PASS | Controlled route preserved and accepted. |
| Capabilities & Limits | PASS | PASS | Directly visible governance closing page. |

## Five-minute journey acceptance

Required route:

1. Home
2. Project Dashboard
3. Scenario Analysis
4. SourceMate
5. Calculation Evidence
6. Decision Evidence Ledger
7. Capabilities & Limits

| Control | Desktop | Android | Notes |
|---|---|---|---|
| Route structure rendered | PASS | PASS | Seven governed steps at 42 seconds each. |
| Transition limit represented | PASS | PASS | Maximum six page transitions. |
| Synthetic disclosure visible | PASS | PASS | Visible before commercial or technical results. |
| No uncaught exception | PASS | PASS | Prior page-link exception absent after correction. |
| Governance closing present | PASS | PASS | Capabilities & Limits remains directly accessible. |

## Responsive presentation checks

- long navigation labels remain accessible;
- sidebar groups collapse and expand on Android;
- tables remain readable or horizontally usable where required;
- proof and limitation sections stack vertically;
- download buttons remain accessible at full container width;
- controlled page links remain accessible at full container width;
- live-demo recovery remains read-only;
- mandatory warnings are not hidden.

## Implemented corrections accepted

- proof and limitation sections render sequentially;
- page links and downloads use full available width;
- live-demo recovery is separate from technical recovery;
- Home and journey links use the registered Streamlit page registry;
- the prior `streamlit.errors.StreamlitPageNotFoundError` was corrected;
- the flat 13-link sidebar was consolidated into four governed groups while preserving all pages and routes.

## Export evidence

The governed ten-minute journey exported successfully in both formats:

- Markdown export: successful;
- JSON export: successful.

The exports preserve synthetic-data disclosure, proof-versus-limit boundaries, human approval requirements, potential-versus-realized savings separation, and the limitations of SourceMate, Calculation Evidence, and the Decision Evidence Ledger.

## Automated validation evidence

- Exact-head workflow run: `30687748523`
- Validation job: `91336808643`
- Exact test count: `746`
- Failures: `0`
- Errors: `0`
- Artifact ID: `8814551912`
- Artifact SHA-256: `75abff464dc40b039baea31348cfb00bcadd931ae0525099e5463af4eed83096`

## Remaining limitations

- browser rendering is not proven by unit tests alone; hosted evidence remains manual;
- no automated browser or screenshot framework is included;
- the application uses synthetic demonstration data only;
- dashboard metrics and wide tables may truncate or require horizontal movement on small screens;
- the showcase is not native-mobile software;
- no authentication, enterprise integration, security certification, operational monitoring, or production support is provided;
- the showcase does not prove realized savings, engineering approval, supplier award, or production readiness.

## Proof-versus-limit confirmation

The showcase proves deterministic decision support, governed explanation, calculation traceability, lifecycle evidence, controlled exports, responsive grouped navigation, and reproducible handoff. It does not prove realized savings, engineering or regulatory approval, supplier allocation, enterprise integration, security certification, autonomous execution, or production readiness.

## Final acceptance rule

Pre-merge Build 6 acceptance is **PASSED** against exact feature SHA `a30aa9c78a3d35158ad7f7b6a0d95009c6baaa77`. Final freeze requires merge into `showcase-handoff-development`, exact post-merge CI, artifact evidence, and repeated hosted acceptance against the exact integration merge SHA.
