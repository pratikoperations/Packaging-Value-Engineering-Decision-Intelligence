# PVE-1.0.2 Project Dashboard Design

## Objective
Add a portfolio-level Streamlit dashboard for creating, selecting, duplicating, archiving, and reviewing packaging value-engineering projects without adding upload, analysis, threshold, or history workflows.

## User Flow
1. Open Project Dashboard.
2. Review portfolio metrics.
3. Create a corrugated packaging project.
4. Select an active project as the current session workspace.
5. Duplicate project metadata when a similar project is required.
6. Archive completed or inactive projects without deleting evidence.
7. Review archived projects in read-only form.

## Dashboard Metrics
- Total projects
- Active projects
- Archived projects
- Dataset versions
- Saved decision snapshots

These metrics describe stored project records and evidence only. They do not represent realized savings, approved packaging changes, or supplier allocation.

## Architecture

```text
Streamlit Project Dashboard
        ↓
ProjectService
        ↓
ProjectRepository
        ↓
SQLite demonstration persistence
```

The Streamlit page does not execute SQL directly. Project lifecycle and dashboard queries remain behind the application-service and repository boundaries.

## Project Operations
- Create project
- Select active project in Streamlit session state
- Duplicate project metadata only
- Archive project
- List active projects
- List archived projects

Duplication does not copy datasets, scenarios, decisions, or export records.

## Scope Controls
- Existing corrugated category only
- No upload or parsing
- No configurable threshold UI
- No scenario execution
- No decision-history UI
- No authentication or permissions
- No production-database claim
- No supplier workflow
- No AI approval

## Persistence Boundary
The dashboard stores records in `runtime/pve_portfolio.sqlite3`. Runtime SQLite files are excluded from Git. Public Streamlit persistence is demonstration-only and may reset after restart or redeployment.

## Acceptance Criteria
- Empty portfolio state renders safely.
- Projects can be created and selected.
- Duplicate codes are rejected.
- Project metadata can be duplicated without copying evidence.
- Projects can be archived without deleting history.
- Active and archived lists remain separate.
- Dashboard counts reconcile with repository records.
- No realized-savings claim is shown.
- Existing single-project demonstration remains unchanged.
