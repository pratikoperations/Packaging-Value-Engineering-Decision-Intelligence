# Build History

## PVE-0.1 through PVE-0.7.2
**Status:** Completed, validated, merged, and publicly deployed.

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
- Expected program budget after build: 77 hours

### Scope Exclusions
No dashboard UI, uploads, CSV parsing, threshold UI, history UI, authentication, external database, PDF or Excel extraction, ERP integration, supplier workflow, AI approval, or new category.

### Merge Gate
Full test suite and complete diff must pass review before squash merge. Do not merge automatically.
