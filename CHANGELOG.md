# Changelog

## [e1-release-candidate-governance-baseline] — Frozen

### Completed
- E1.1 through E1.7 completed on the governed E1 development line.
- E1.7 implementation PR #68 and governance-closure PR #69 merged and closed.
- Final E1 merge SHA and governed release-candidate baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- The earlier SHA `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7` remains the E1.7 implementation merge lineage and is superseded as the current RC recovery point.
- Exact-SHA validation run `30640190796`, job `91187867871`, succeeded.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Artifact `8797098203`; SHA-256 `5697d07b0b4664810bbad29615e04892528aa232ff18353d1e00f611b023b384`.
- `main` remained unchanged at `300054cceb255e8e1273e8012a3ba0c0a236556d`.

### Governance Boundaries Preserved
- RC freeze records qualification and recovery lineage only.
- No promotion to `main`, deployment, release, tagging, production use, or another E1 development slice is authorized.
- E1 non-execution, human-approval, non-autonomous-approval, non-deployment, and non-production boundaries remain mandatory.

## [e1.7-governed-approved-specification-consumption] — Governance Closed

### Added
- Deterministic governed consumption envelopes derived only from immutable E1.6 approved specification snapshots.
- Immutable purpose-specific authorization records, project-scoped read boundaries, canonical hashes, idempotency, concurrency controls, controlled runtime composition, UI handoff, integration coverage, and governance contract.

### Completed
- Feature branch retained: `e1/governed-approved-specification-consumption`.
- Final feature SHA: `b08bf9d92dcda173ce4ecd2f913e0d3f9f1b5940`.
- PR #68 merged and closed by merge commit.
- Merge commit and final `e1-development` SHA: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Scope: 10 commits; 15 changed files; 2,907 additions; 0 deletions.
- Workflow run `30628727103`, job `91149911990`: 656 tests passed; 0 failures; 0 errors.
- Artifact `8792456475`; SHA-256 `69635bdcf5125aed1e1e5e4c846cd31ccf8fad866daed4d2a5d702b3b62bd771`.
- `main` remained unchanged at `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- E1.7 marked completed, verified, merged, and governance-closed.

### Mandatory Controls Preserved
- E1.7 prepares governed approved-specification consumption envelopes and records purpose-specific authorizations only.
- No cost, scenario, risk, material, sourcing, recommendation, or award engine is executed.
- No downstream business decision is approved.
- Approved-snapshot integrity, project scope, immutability, lineage, deterministic hashing, and human authorization remain mandatory.

### Excluded
- Analytical execution and outputs.
- Supplier selection or award.
- Engineering, commercial, sourcing, production, or autonomous approval.
- Workflow or dependency changes.
- Deployment, release, tagging, branch deletion, or modification of `main`.

## [1.1-all-category-intake-validation-readiness] — Completed

### Added
- Project intake for corrugated, folding carton, rigid plastic, flexible packaging, labels, closures, glass, and metal packaging.
- Category-specific objectives, change types, fields, documents, units, warnings, blockers, analyses, and testing requirements.
- Macro-free category Excel templates with structured source classification and evidence fields.
- Excel upload parsing, normalization, structural validation, completeness validation, and persistence blocking for invalid uploads.
- Transparent weighted readiness scoring, blocker override, readiness stages, and reasoned output availability.
- Common commercial savings, realized savings, first-year net benefit, payback, and material-reduction calculations.
- Guided Streamlit workflow plus JSON and Markdown executive reports.
- Eight synthetic category samples and three detailed demonstration cases.

### Completed
- Builds 1–9 completed within the fixed 80-hour cap.
- PR #25 merged and closed.
- Final feature head: `dc85db49afee46bde3118684761c0a176dd32194`.
- Squash merge commit: `37f4ae58e0d57c4531293371e423d771ada7ae50`.
- Final CI: PVE CI #735.
- Run ID: `29302903427`.
- Tests: 221 unittest tests plus 4 focused report tests; 225 total executions; 0 failures; 0 errors.
- Total effort: 80 hours.
- Remaining budget: 0 hours.
- Release marked complete, validated, merged, and governance-closed.

### Mandatory Controls Preserved
- Engineering validation required.
- Human approval required.
- Autonomous approval prohibited.
- Readiness percentage cannot approve a project.
- Critical blockers override percentage and commercial attractiveness.
- Supplier-declared and predicted values are not shown as laboratory-tested.
- Historical datasets, thresholds, scenarios, and decision snapshots remain immutable.
- Archived projects remain read-only.
- Project isolation remains enforced.

### Excluded
- PVE 1.2 development.
- Power BI and PostgreSQL reporting integration.
- Deployment, activation, pilot, and production.
- ERP integration, OCR, and AI document reading.
- Authentication, cloud database, supplier ranking or allocation, machine learning, live pricing, and autonomous approval.
- Full technical feasibility across all packaging categories.

## [1.0.6-decision-snapshot-final-release] — Completed

### Added
- Immutable decision snapshots from saved scenarios
- Exact project, scenario, dataset, and threshold references
- Dataset-defined baseline exclusion
- Recommendation-for-review statuses without autonomous approval
- Project-scoped read-only decision history
- Archived-project repository write protection
- Final interview guide, QA report, and release checklist

### Completed
- PR #22 merged and closed
- Squash merge commit: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`
- Source branch deleted
- Final CI: PVE CI #520
- Run ID: `29223657516`
- Tests: 179 passed, 0 failed, 0 errors
- Actual effort: 17.0 hours
- Cumulative effort: 89.5 hours
- Remaining program budget: 0.5 hours
- Post-merge governance closure completed
- No next build started

### Mandatory Controls Preserved
- Engineering validation required
- Human approval required
- Autonomous approval prohibited
- Critical risk and not-qualified outcomes blocked
- Insufficient data cannot become recommended
- Snapshots immutable
- Project isolation enforced

### Excluded
- Authentication
- External database
- ERP integration
- Supplier ranking or allocation
- Autonomous approval
- Analytical-engine modification
- Recommendation-engine modification
- New packaging category

## [1.0.5-controlled-scenario-execution] — Completed
- PR #21 merged and closed
- Merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Tests: 160 passed, 0 failed, 0 errors
- Effort used: 17.5 hours
- Program budget remaining: 17.5 hours
- Source branch deleted
- Added controlled deterministic scenario execution, immutable scenario records, exact dataset and threshold binding, business-threshold explanations, and mandatory engineering controls.

## [1.0.4-configurable-thresholds] — Completed
- PR #20 merged and closed
- Merge commit: `301a0d92d41f46a15e37c5bd059e8673c3f666a6`
- Tests: 143 passed, 0 failed, 0 errors
- Effort used: 12.5 hours

## [1.0.3-upload-validation] — Completed
- PR #19 merged and closed
- Merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Effort used: 16.5 hours

## [1.0.2-project-dashboard] — Completed
- PR #18 merged and closed
- Merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors

## [1.0.1-foundation-persistence] — Completed
- PR #17 merged and closed
- Merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors

## [0.7.2-live-demo-streamlit-compatibility] — Completed
- PR #16 merged and closed
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors

## [0.7.1-streamlit-deployment-disclaimer] — Completed
- PR #15 merged and closed
- Merge commit: `c3bc5fb291c7c087c2a4ab054b297841a7b5e73a`
- Tests: 59 passed, 0 failed, 0 errors

## [0.7.0-qa-interview-release] — Completed
- PR #13 merged and closed
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Tests: 58 passed, 0 failed, 0 errors

## Prior Releases
- `0.6.0-decision-package-export` — Completed
- `0.5.0-scenario-recommendation-ui` — Completed
- `0.4.0-technical-risk` — Completed
- `0.3.0-cost-material-engine` — Completed
- `0.2.0-data-model` — Completed
- `0.1.0-foundation` — Completed
