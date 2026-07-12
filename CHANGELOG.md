# Changelog

## [1.0.4-configurable-thresholds] — Pending

### Added
- Controlled global default threshold profile
- Project-specific immutable threshold-profile versions
- Threshold validation and duplicate-content suppression
- Active threshold profile selection
- Business screening helper
- Mandatory non-disableable engineering controls
- Threshold profile template and automated tests

### Preserved
- Existing `app.py`, dashboard, and upload workflows
- Persistence schema and immutable-history triggers
- Analytical, risk, scenario, and recommendation engines
- Engineering-validation and non-autonomous-approval controls
- Draft integration-contract status
- AI Procurement Copilot repository separation

### Excluded
- Scenario execution
- Recommendation-engine modification
- Decision-history interface
- Authentication and external database
- Supplier workflow and ERP integration
- AI approval and new packaging categories

### Scope Boundary
PVE-1.0.4 adds business threshold creation, validation, selection, and versioning only. Business thresholds cannot disable engineering validation, technical qualification, evidence, critical-risk, or approval controls.

## [1.0.3-upload-validation] — Completed

### Added
- Canonical UTF-8 JSON upload with a 2 MB limit
- Limited template-based CSV upload using exactly `project.csv` and `alternatives.csv`
- Canonical normalization for JSON and CSV inputs
- Active-project binding and user-upload validation profile
- Field-level validation issue reporting
- Dynamically generated JSON and CSV templates
- Save-only-when-valid workflow
- Immutable dataset-version storage
- Duplicate canonical-content detection across JSON and CSV
- Archived-project upload prohibition
- Upload design and QA documentation
- Upload, validation, persistence, and scope tests

### Completed
- PR #19 merged and closed
- Squash merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Effort used: 16.5 hours
- Program budget remaining: 47.5 hours
- Source branch deleted

### Preserved
- Existing deterministic analytical engines
- Existing `app.py` workflow and project dashboard
- Engineering-validation and non-autonomous-approval controls
- Synthetic-data and non-production disclaimers
- Draft integration-contract status
- AI Procurement Copilot repository separation
- Existing database schema and immutable-history triggers

### Excluded
- Configurable thresholds
- Scenario execution
- Decision-history interface
- Authentication and external database
- PDF, Excel, OCR, and unstructured-document extraction
- ERP, supplier workflow, AI approval, and new-category capabilities

### Scope Boundary
PVE-1.0.3 adds controlled ingestion only. Uploaded data cannot pre-approve a packaging decision, invalid uploads are not stored, and incomplete technical evidence remains eligible for an `insufficient_data` outcome.

## [1.0.2-project-dashboard] — Completed

### Added
- Streamlit multi-project dashboard page
- Portfolio summary metrics for projects, dataset versions, and saved decisions
- Project creation
- Explicit active workspace selection and current-workspace display
- Metadata-only project duplication
- Project archiving and separate archived-project view
- Runtime SQLite service factory
- Runtime database Git exclusion
- Project dashboard design and QA documentation
- Fifteen dashboard and application-service tests

### Corrected
- Archived projects can no longer become or overwrite the active workspace.
- Project selectboxes no longer mutate active workspace session state automatically.
- Active workspace changes now require the explicit `Select as active workspace` action.
- Archiving the active project clears the active workspace safely.

### Completed
- PR #18 merged and closed
- Squash merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors
- Source branch deleted

### Preserved
- Existing deterministic analytical engines
- Existing `app.py` decision workflow
- Engineering-validation and non-autonomous-approval controls
- Synthetic-data and non-production disclaimers
- Draft integration-contract status
- AI Procurement Copilot repository separation
- Immutable historical evidence

### Excluded
- Upload and parsing workflows
- Configurable threshold UI
- Scenario execution from the dashboard
- Decision-history UI
- Authentication and external database
- ERP, supplier, AI approval, PDF, Excel, and new-category capabilities

### Scope Boundary
PVE-1.0.2 adds project portfolio navigation only. Dashboard metrics do not represent realized savings, approved packaging changes, or supplier allocation. SQLite remains demonstration persistence.

## [1.0.1-foundation-persistence] — Completed

### Added
- SQLite database connection manager with foreign-key enforcement
- Schema initialization with version recording
- Repository modules for projects, datasets, threshold profiles, scenarios, decision snapshots, and export records
- Immutable database triggers for datasets, threshold profiles, scenarios, and decision snapshots
- Project lifecycle application service
- Cross-project integrity validation for scenario and decision links
- Temporary isolated database support for automated tests
- Comprehensive persistence, immutability, and project-integrity test coverage

### Completed
- PR #17 merged and closed
- Squash merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors
- Source branch deleted

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
- Streamlit demonstration UI
- Deterministic cost, material, qualification, risk, scenario, recommendation, and export modules
- JSON and Markdown decision-package exports
- Interview demonstration guide
- Final release checklist
- Recovery manifest
- PVE-0.7 QA report

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
