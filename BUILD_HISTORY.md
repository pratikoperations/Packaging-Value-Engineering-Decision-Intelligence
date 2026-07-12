# Build History

## PVE-0.1 — Repository Foundation
**Status:** Completed and merged

## PVE-0.2 — Data Model and Demo Data
**Status:** Completed and merged

## PVE-0.3 — Cost and Material Engine
**Status:** Completed and merged

## PVE-0.4 — Technical Qualification and Risk
**Status:** Completed and merged

## PVE-0.5 — Scenario and Recommendation UI
**Status:** Completed and merged

## PVE-0.6 — Decision Package Export
**Status:** Completed and merged

## PVE-0.7 — QA and Interview Release
**Status:** Completed and merged

### Completion Record
- Pull request: PR #13
- PR status: Merged and closed
- Merge method: Squash merge
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Stable branch: `main`
- Original feature branch: Deleted

### Final Validated CI Evidence
- Workflow: PVE CI
- Run number: 268
- Run ID: `29184423320`
- Validated commit: `d6ae2079e332a33edcc71d0011d642f0ae1eb5f9`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 58 passed, 0 failed, 0 errors

### Final Acceptance Result
- End-to-end deterministic flow: Pass
- Static UI smoke validation: Pass
- Interview guidance: Pass
- Release checklist: Pass
- Recovery verification: Pass
- Full diff review: Pass
- QA report: Pass
- PR merge: Pass

## Final Project State
All seven planned builds are completed and merged. The project becomes fully governance-closed after the final closure PR is merged.

## PVE-0.7.1 — Streamlit Deployment Disclaimer
**Status:** Completed and merged through PR #15

## PVE-0.7.2 — Live Demo and Streamlit Compatibility
**Status:** Completed and merged through PR #16
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Stable tests: 60 passed, 0 failed, 0 errors
- Public demo: https://packaging-value-engineering-decision-intelligence.streamlit.app/

---

## PVE-1.0.1 — Foundation and Persistence
**Status:** Completed and merged through PR #17

### Objective
Create the persistence and application-service foundation for the approved PVE 1.0 controlled multi-project platform.

### Implemented Scope
- SQLite connection and transaction management
- Schema initialization with version recording
- Foreign-key enforcement
- Project lifecycle repository and service
- Immutable project dataset versions
- Immutable threshold-profile versions
- Immutable scenarios
- Immutable decision snapshots
- Cross-project scenario and decision integrity validation
- Export-record persistence
- Isolated temporary test databases

### Database Tables
- `schema_migrations`
- `projects`
- `project_datasets`
- `threshold_profiles`
- `scenarios`
- `decision_snapshots`
- `export_records`

### Completion Record
- Pull request: PR #17
- Merge method: Squash merge
- Merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors
- Source branch: Deleted

### Budget
- Revised effort used: 14.5 hours
- Program budget after build: 75.5 hours

### Scope Exclusions
No dashboard UI, uploads, CSV parsing, threshold UI, history UI, authentication, external database, PDF or Excel extraction, ERP integration, supplier workflow, AI approval, or new category.

---

## PVE-1.0.2 — Project Dashboard
**Status:** Completed and merged through PR #18

### Objective
Add a controlled project portfolio dashboard using the PVE-1.0.1 persistence foundation.

### Implemented Scope
- Portfolio summary metrics
- Project creation
- Explicit active workspace selection
- Current active workspace display
- Metadata-only project duplication
- Project archiving
- Active and archived project views
- Runtime SQLite service initialization
- Demonstration persistence disclosure

### Design Rules
- Dashboard uses `ProjectService` and `ProjectRepository`; no page-level SQL
- Project duplication does not copy datasets, scenarios, decisions, or exports
- Archived projects remain read-only and retain evidence
- Dashboard metrics do not represent realized savings
- Existing `app.py` decision workflow remains unchanged

### Completion Record
- Pull request: PR #18
- Merge method: Squash merge
- Merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors
- Source branch: Deleted

### Budget
- Revised effort used: 11.5 hours
- Program budget after build: 64.0 hours

### Scope Exclusions
No upload, JSON or CSV parsing, threshold UI, scenario execution, decision-history UI, authentication, external database, supplier workflow, ERP integration, AI approval, or new packaging category.

---

## PVE-1.0.3 — Upload and Validation
**Status:** Completed and merged through PR #19

### Objective
Add controlled user-data ingestion for the active corrugated packaging project.

### Implemented Scope
- Canonical JSON upload with encoding and size controls
- Limited `project.csv` and `alternatives.csv` parsing
- Canonical normalization
- Active-project binding
- User-upload validation profile
- Field-level issue reporting
- Downloadable templates
- Save-only-when-valid workflow
- Immutable dataset-version storage
- Canonical duplicate detection across JSON and CSV
- Archived-project upload prohibition

### Design Rules
- JSON remains canonical
- CSV is limited to exactly two documented templates
- Invalid uploads are never stored
- Uploaded recommendations cannot pre-approve a decision
- Incomplete technical evidence can remain structurally valid but must remain eligible for `insufficient_data`
- Existing analytical engines and persistence schema remain unchanged

### Completion Record
- Pull request: PR #19
- Merge method: Squash merge
- Merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Source branch: Deleted

### Budget
- Effort used: 16.5 hours
- Program budget after build: 47.5 hours

### Scope Exclusions
No configurable thresholds, scenario execution, decision-history UI, authentication, external database, PDF or Excel extraction, OCR, ERP integration, supplier workflow, AI approval, or new packaging category.

---

## PVE-1.0.4 — Configurable Business Thresholds
**Status:** In progress — draft PR validation pending

### Objective
Add immutable configurable business threshold profiles without weakening mandatory engineering controls.

### Implemented Scope
- Controlled global default profile
- Project-specific immutable profile versions
- Threshold validation
- Duplicate-content suppression
- Active threshold profile selection
- Business screening helper
- Mandatory non-disableable engineering controls
- Threshold template and automated tests

### Design Rules
- Business thresholds remain separate from engineering controls
- Engineering validation remains mandatory
- Autonomous approval remains prohibited
- Critical risk remains blocking
- Not-qualified alternatives remain blocked
- Insufficient data cannot become recommended
- Threshold changes create immutable versions
- Identical content does not duplicate history

### Budget
- Planned allocation: 13 hours
- Estimated effort used: 12.5 hours
- Program budget before build: 47.5 hours
- Estimated program budget after build: 35.0 hours

### Scope Exclusions
No scenario execution, recommendation-engine modification, decision-history UI, authentication, external database, supplier workflow, ERP integration, AI approval, or new packaging category.

### Merge Gate
Full CI and complete diff review must pass before squash merge. Do not merge automatically.
