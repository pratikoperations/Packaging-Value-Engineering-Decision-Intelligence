# Build History

## Completed Builds
- PVE-0.1 through PVE-0.7.2: completed and merged.
- PVE-1.0.1 — Foundation and Persistence: PR #17, merge `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`, 85 tests, 14.5 hours.
- PVE-1.0.2 — Project Dashboard: PR #18, merge `87f3897c68503cddc2c7e64827d8c395b45065a5`, 100 tests, 11.5 hours.
- PVE-1.0.3 — Upload and Validation: PR #19, merge `c3e5247510c062fe64ac1da171dcc2f107ff4967`, 126 tests, 16.5 hours.
- PVE-1.0.4 — Configurable Business Thresholds: PR #20, merge `301a0d92d41f46a15e37c5bd059e8673c3f666a6`, 143 tests, 12.5 hours.
- PVE-1.0.5 — Controlled Scenario Execution: PR #21, merge `99416d91025b6cfbff40142ce9fbcd462eb1028f`, 160 passed, 0 failed, 0 errors, 17.5 hours, source branch deleted.

## PVE-1.0.6 — Decision Snapshot and Final Release Closure
**Status:** Completed, validated, squash merged, source branch deleted, and governance-closed.

### Implemented Scope
- Immutable decision snapshots from saved scenarios
- Exact project, scenario, dataset, and threshold references
- Dataset-defined baseline exclusion
- Recommendation-for-review statuses
- Technical, risk, threshold, and control evidence
- Project-scoped read-only decision history
- Archived-project repository write protection
- Final interview guide, QA report, and release checklist

### Completion Record
- Pull request: PR #22 merged and closed
- Squash merge commit: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`
- Source branch: Deleted
- Final CI: PVE CI #520
- Run ID: `29223657516`
- Tests: 179 passed, 0 failed, 0 errors

### Mandatory Controls
Engineering validation and human approval remain mandatory. Autonomous approval is prohibited. Critical risk and not-qualified outcomes remain blocked. Insufficient data cannot become recommended. Snapshots remain immutable and project isolation remains enforced.

### Budget
- Actual effort: 17.0 hours
- Cumulative effort: 89.5 hours
- Remaining program budget: 0.5 hours

### Exclusions
No authentication, external database, ERP integration, supplier ranking or allocation, autonomous approval, analytical-engine modification, recommendation-engine modification, or new packaging category.

### Final State
PVE 1.0 is fully completed and governance-closed.

## PVE 1.1 — All-Category Project Intake and Validation Readiness
**Status:** Completed, validated, squash-merged, and governance-closed.

### Completed Builds
- Build 1 — Architecture and Scope Lock: 6 hours.
- Build 2 — Project Creation Expansion: 7 hours.
- Build 3 — Category Input Definitions: 14 hours.
- Build 4 — Excel Template Generation: 10 hours.
- Build 5 — Excel Upload and Normalization: 10 hours.
- Build 6 — Readiness and Blocking Engine: 9 hours.
- Build 7 — Commercial and ROI Extension: 5 hours.
- Build 8 — Guided Streamlit Workflow and Updated Reports: 8 hours.
- Build 9 — Testing and Release QA: 11 hours.

### Completion Record
- Pull request: PR #25 merged and closed.
- Final feature head: `dc85db49afee46bde3118684761c0a176dd32194`.
- Squash merge commit: `37f4ae58e0d57c4531293371e423d771ada7ae50`.
- Final CI: PVE CI #735.
- Run ID: `29302903427`.
- Tests: 221 unittest tests plus 4 focused report tests; 225 total executions; 0 failures; 0 errors.

### Release Acceptance
Eight packaging categories, category-specific Excel templates, validated Excel normalization, transparent readiness scoring, blocker override, reasoned output availability, commercial and ROI calculations, category testing checklists, JSON and Markdown reports, source traceability, immutable historical evidence, archived-project write protection, and project isolation were validated. Readiness never grants automatic approval and no unsupported technical-feasibility claim is made.

### Budget
- Fixed cap: 80 hours.
- Total consumed: 80 hours.
- Remaining: 0 hours.

### Final State
PVE 1.1 is fully completed, validated, merged, and governance-closed.

## E1.7 — Governed Approved Specification Consumption Contract
**Status:** Completed, verified, merge-committed into `e1-development`, and governance-closed.

### Implemented Scope
- Deterministic governed consumption envelopes derived only from immutable E1.6 approved specification snapshots.
- Immutable purpose-specific consumption authorization records.
- Project-scoped application and read boundaries, deterministic hashes, idempotency, concurrency controls, runtime composition, controlled UI, integration flow, and governance contract.

### Completion Record
- Feature branch: `e1/governed-approved-specification-consumption` retained.
- Final feature SHA: `b08bf9d92dcda173ce4ecd2f913e0d3f9f1b5940`.
- Pull request: PR #68 merged and closed.
- Merge method: merge commit.
- Historical E1.7 implementation SHA: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Scope statistics: 10 commits; 15 changed files; 2,907 additions; 0 deletions.
- Validation: workflow run `30628727103`, job `91149911990`; 656 tests passed; 0 failures; 0 errors.
- Artifact: `8792456475`; SHA-256 `69635bdcf5125aed1e1e5e4c846cd31ccf8fad866daed4d2a5d702b3b62bd771`.
- At this historical milestone, `main` remained at `300054cceb255e8e1273e8012a3ba0c0a236556d`.

### Mandatory Claim Boundary
E1.7 prepares governed approved-specification consumption envelopes and records purpose-specific authorizations. It does not execute cost, scenario, risk, material, sourcing, recommendation, or award engines and does not approve a downstream business decision.

## E1 Release-Candidate Governance Freeze — Historical Record
**Status:** E1.1 through E1.7 completed; final E1 merge exact-SHA validated and technically qualified as the governed release candidate.

### Completion and Lineage
- E1.7 implementation PR #68 merged and closed.
- E1.7 governance-closure PR #69 merged and closed.
- Governed E1 product baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- The earlier SHA `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7` remains the E1.7 implementation lineage.

### Final Validation
- Workflow run: `30640190796`.
- Job: `91187867871`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Artifact: `8797098203`.
- Artifact SHA-256: `5697d07b0b4664810bbad29615e04892528aa232ff18353d1e00f611b023b384`.
- At this historical milestone, `main` remained at `300054cceb255e8e1273e8012a3ba0c0a236556d` and promotion still required separate authorization.

## E1 Promotion to Main
**Status:** Completed, merge-committed into `main`, exact-SHA validated, and governance-closed.

### Completion Record
- Pull request: PR #71 merged and closed.
- Merge method: merge commit.
- Original pre-E1 rollback `main` SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- E1.7 implementation lineage: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Governed E1 product baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- Final pre-promotion and retained `e1-development` SHA: `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- Merge commit and promoted `main` SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Promotion scope: 33 commits; 55 changed files; 8,774 additions; 4 deletions.

### Exact Post-Merge Validation
- Workflow run: `30656143928`.
- Job: `91240891645`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Artifact: `8803331290`.
- Artifact SHA-256: `943cad0adb2f8f4d20c5c9b0f2e1520655043c2224cfb079ee67d4e5d28e2d39`.

### Governance Boundary
Promotion establishes a stable source-code baseline only. It does not authorize deployment, release, tagging, live organizational data, production use, production-readiness claims, autonomous approval, or autonomous execution of engineering, commercial, sourcing, supplier-award, cost, scenario, risk, material, recommendation, deployment, release, or production decisions.

## Showcase and Handoff Release — Build 1
**Status:** Implemented on `showcase/build-1-governance-closure` and pending PR validation and separate merge authorization.

### Scope
- Reconciles the six canonical governance and recovery records after PR #71 promotion.
- Preserves detailed historical build records and explicitly labels pre-promotion statements as historical milestone evidence.
- No source code, UI, tests, workflows, dependencies, or data are modified.

### Budget
- Build 1 authorized maximum: 5 hours.
- Total programme budget: 50 hours.
- Builds 2–6 remain separately unauthorized.
