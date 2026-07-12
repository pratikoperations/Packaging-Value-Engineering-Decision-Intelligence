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
- Merge method: Squash merge
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Stable branch: `main`

### Final Validation
- PVE CI #268, run ID `29184423320`
- Tests: 58 passed, 0 failed, 0 errors
- QA result: Pass

## PVE-0.7.1 — Streamlit Deployment Disclaimer
**Status:** Completed and merged through PR #15

## PVE-0.7.2 — Live Demo and Streamlit Compatibility
**Status:** Completed and merged through PR #16
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Stable tests: 60 passed, 0 failed, 0 errors
- Public demo: https://packaging-value-engineering-decision-intelligence.streamlit.app/

---

## PVE-1.0.1 — Foundation and Persistence
**Status:** In progress — draft PR preparation

### Objective
Create the persistence and application-service foundation for the approved PVE 1.0 controlled multi-project platform.

### Implemented Scope
- SQLite connection and transaction management
- Schema initialization and migration tracking
- Foreign-key enforcement
- Project lifecycle repository and service
- Immutable project dataset versions
- Immutable threshold-profile versions
- Immutable scenarios
- Immutable decision snapshots
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

### Budget
- Approved build allocation: 13 hours
- Program budget before build: 90 hours
- Estimated program budget after build: 77.5 hours

### Scope Exclusions
No dashboard UI, uploads, CSV parsing, threshold UI, history UI, authentication, external database, PDF or Excel extraction, ERP integration, supplier workflow, AI approval, or new category.

### Merge Gate
Full test suite and complete diff must pass review before squash merge. Do not merge automatically.
