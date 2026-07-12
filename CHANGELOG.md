# Changelog

## [1.0.1-foundation-persistence] — Pending

### Added
- SQLite database connection manager with foreign-key enforcement
- Schema initialization with version recording
- Repository modules for projects, datasets, threshold profiles, scenarios, decision snapshots, and export records
- Immutable database triggers for datasets, threshold profiles, scenarios, and decision snapshots
- Project lifecycle application service
- Cross-project integrity validation for scenario and decision links
- Temporary isolated database support for automated tests
- Comprehensive persistence, immutability, and project-integrity test coverage

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
PVE-1.0.1 creates infrastructure only. It does not change packaging recommendations, risk logic, exports, or the public demonstration workflow. The current schema utility does not claim sequential migration support.

## [0.7.2-live-demo-streamlit-compatibility] — Completed

### Added
- Public Streamlit portfolio URL published in repository documentation
- Live application, UI, and decision-package export verification recorded
- PVE-0.7.2 QA report

### Changed
- Replaced deprecated `use_container_width=True` Streamlit arguments with `width="stretch"`

### Preserved
- Application behavior and displayed data
- Recommendation and risk logic
- JSON and Markdown download functionality
- Synthetic-data disclaimer
- Engineering-validation warning
- Draft integration-contract status

### Completed
- PR #16 merged and closed
- Squash merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors

### Scope Boundary
This maintenance update improves public portfolio discoverability and Streamlit API compatibility. It does not add analytical functionality or represent the application as production-ready.

## [0.7.1-streamlit-deployment-disclaimer] — Completed

### Added
- Visible Streamlit warning that the application uses synthetic demonstration data only
- Static release test confirming the public synthetic-data disclaimer remains present

### Preserved
- Existing engineering-validation requirement
- Existing prohibition on autonomous packaging approval
- Draft integration-contract status
- All analytical engines, schemas, demo data, validator, recommendations, and export logic

### Completed
- PR #15 merged and closed
- Squash merge commit: `c3bc5fb291c7c087c2a4ab054b297841a7b5e73a`
- PVE CI #292 passed
- Tests: 59 passed, 0 failed, 0 errors

### Scope Boundary
This hotfix is non-functional deployment hardening only. It does not reopen the completed roadmap or add product functionality.

## [0.7.0-qa-interview-release] — Final Completed Release

### Added
- Final interview-ready README and local-run guidance
- Interview demonstration guide
- Final release checklist and acceptance criteria
- PVE-0.7 QA report
- Six end-to-end release tests
- Static Streamlit UI smoke validation
- CI enforcement for final release documentation and identity
- Recovery and governance closure records

### Completed
- PR #13 merged and closed
- Squash merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Stable branch: `main`
- Original feature branch: Deleted
- Final validated CI: PVE CI #268, run ID `29184423320`
- Tests: 58 passed, 0 failed, 0 errors
- QA result: Pass
- Final project status: Completed

### Scope Boundary
The final release adds no analytical engine, supplier ranking, supplier allocation, autonomous technical approval, finalized integration contract, external system integration, or production deployment capability.

## Prior Releases
- `0.6.0-decision-package-export` — Completed
- `0.5.0-scenario-recommendation-ui` — Completed
- `0.4.0-technical-risk` — Completed
- `0.3.0-cost-material-engine` — Completed
- `0.2.0-data-model` — Completed
- `0.1.0-foundation` — Completed
