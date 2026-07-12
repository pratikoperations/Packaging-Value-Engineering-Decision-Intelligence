# Changelog

## [1.0.5-controlled-scenario-execution] — Completed

### Added
- Immutable dataset-version selection
- Immutable threshold-profile selection
- Explicit bounded scenario assumptions
- Deterministic scenario execution using existing engines
- Technical qualification and risk evaluation
- Explainable business-threshold outcomes
- Mandatory engineering-control outcomes
- Immutable scenario-record storage
- Cross-project dataset and threshold protection
- Controlled scenario Streamlit page
- Design, QA, governance, and automated tests

### Completed
- PR #21 merged and closed
- Squash merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Final CI: PVE CI #455, run ID `29192749111`
- Validated head commit: `fb3b2421a457081d83631f5952510e7c533c7f8b`
- Tests: 160 passed, 0 failed, 0 errors
- Actual effort used: 17.5 hours
- Program budget remaining: 17.5 hours
- Source branch deleted
- Post-merge governance closure completed directly on `main`

### Preserved
- Existing recommendation engine
- Existing persistence schema and immutability triggers
- Existing project, upload, and threshold workflows
- Engineering-validation and non-autonomous-approval controls
- Draft integration-contract status
- AI Procurement Copilot repository separation

### Excluded
- Decision snapshots and decision-history UI
- Recommendation-engine modification
- Authentication and external database
- Supplier ranking or allocation
- ERP integration
- AI approval and new packaging categories

### Scope Boundary
PVE-1.0.5 stores deterministic scenario evidence only. Scenario statuses are not approvals; engineering validation and human approval remain mandatory.

## [1.0.4-configurable-thresholds] — Completed
- PR #20 merged and closed
- Merge commit: `301a0d92d41f46a15e37c5bd059e8673c3f666a6`
- Tests: 143 passed, 0 failed, 0 errors
- Effort used: 12.5 hours
- Program budget remaining: 35.0 hours
- Added controlled global and project-specific immutable threshold profiles, validation, duplicate suppression, active selection, business screening, and non-disableable engineering controls.

## [1.0.3-upload-validation] — Completed
- PR #19 merged and closed
- Merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Effort used: 16.5 hours
- Program budget remaining: 47.5 hours
- Added canonical JSON and limited CSV ingestion, normalization, validation, immutable dataset versions, and duplicate detection.

## [1.0.2-project-dashboard] — Completed
- PR #18 merged and closed
- Merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors
- Added the multi-project dashboard, explicit active workspace selection, metadata-only duplication, archiving, and portfolio metrics.

## [1.0.1-foundation-persistence] — Completed
- PR #17 merged and closed
- Merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors
- Added SQLite repository infrastructure, immutable evidence records, foreign-key enforcement, project lifecycle services, and cross-project integrity controls.

## [0.7.2-live-demo-streamlit-compatibility] — Completed
- PR #16 merged and closed
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors
- Added public portfolio discoverability and Streamlit width compatibility.

## [0.7.1-streamlit-deployment-disclaimer] — Completed
- PR #15 merged and closed
- Merge commit: `c3bc5fb291c7c087c2a4ab054b297841a7b5e73a`
- Tests: 59 passed, 0 failed, 0 errors
- Added the visible public synthetic-data disclaimer.

## [0.7.0-qa-interview-release] — Final Completed Release
- PR #13 merged and closed
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Final validated CI: PVE CI #268, run ID `29184423320`
- Tests: 58 passed, 0 failed, 0 errors
- QA result: Pass
- Final project status: Completed

## Prior Releases
- `0.6.0-decision-package-export` — Completed
- `0.5.0-scenario-recommendation-ui` — Completed
- `0.4.0-technical-risk` — Completed
- `0.3.0-cost-material-engine` — Completed
- `0.2.0-data-model` — Completed
- `0.1.0-foundation` — Completed
