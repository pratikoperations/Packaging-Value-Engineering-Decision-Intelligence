# Changelog

## [1.0.1-foundation-persistence] — Pending

### Added
- SQLite database connection manager with foreign-key enforcement
- Idempotent schema initialization and migration version tracking
- Repository modules for projects, datasets, threshold profiles, scenarios, decision snapshots, and export records
- Immutable database triggers for datasets, threshold profiles, scenarios, and decision snapshots
- Project lifecycle application service
- Temporary isolated database support for automated tests
- Comprehensive persistence and immutability test coverage

### Preserved
- Existing deterministic analytical engines
- Current public Streamlit application behavior
- Engineering-validation and non-autonomous-approval controls
- Synthetic-data and non-production disclaimers
- Draft integration-contract status
- AI Procurement Copilot repository separation

### Excluded
- Dashboard UI
- Upload and CSV parsing
- Configurable threshold UI
- Decision-history UI
- Authentication and external database
- ERP, supplier, AI approval, PDF, Excel, and new-category capabilities

### Scope Boundary
PVE-1.0.1 creates infrastructure only. It does not change packaging recommendations, risk logic, exports, or the public demonstration workflow.

## [0.7.2-live-demo-streamlit-compatibility] — Completed

### Added
- Public Streamlit portfolio URL published in repository documentation
- Live application, UI, and decision-package export verification recorded
- PVE-0.7.2 QA report

### Changed
- Replaced deprecated `use_container_width=True` Streamlit arguments with `width="stretch"`

### Scope Boundary
This maintenance update improves public portfolio discoverability and Streamlit API compatibility. It does not add analytical functionality or represent the application as production-ready.

## [0.7.1-streamlit-deployment-disclaimer] — Completed
- Visible synthetic-data warning added and validated through PR #15
- Tests: 59 passed, 0 failed, 0 errors

## [0.7.0-qa-interview-release] — Final Completed Release
- All seven original builds completed
- Release PR #13 merged
- Tests: 58 passed, 0 failed, 0 errors

## Prior Releases
- `0.6.0-decision-package-export` — Completed
- `0.5.0-scenario-recommendation-ui` — Completed
- `0.4.0-technical-risk` — Completed
- `0.3.0-cost-material-engine` — Completed
- `0.2.0-data-model` — Completed
- `0.1.0-foundation` — Completed
