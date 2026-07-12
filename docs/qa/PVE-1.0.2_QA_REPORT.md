# PVE-1.0.2 QA Report

## Build
PVE-1.0.2 — Project Dashboard

## Status
Corrective branch validation pending

## Objective
Add a controlled multi-project Streamlit dashboard without introducing upload, threshold, analysis, history, authentication, supplier, or AI approval workflows.

## Changed Capability
- Portfolio summary metrics
- Project creation
- Explicit active workspace selection
- Current active workspace display
- Project metadata duplication
- Project archiving
- Active and archived project lists
- Read-only archived project presentation
- Runtime SQLite service initialization

## Architecture
- Streamlit page: `pages/01_Project_Dashboard.py`
- Application boundary: `ProjectService`
- Repository boundary: `ProjectRepository`
- Runtime factory: `src/application/runtime.py`
- Demonstration database: `runtime/pve_portfolio.sqlite3`

The page does not execute SQL directly.

## Active Workspace Correction
- A selectbox no longer changes `active_project_id` automatically.
- Active projects require an explicit `Select as active workspace` button.
- Archived projects cannot write to `active_project_id`.
- Rendering the archived tab cannot overwrite an existing active workspace.
- The currently active workspace is shown clearly.
- Archiving the active project clears the active workspace safely.

## Scope Controls
- Existing corrugated category only
- Duplication copies project metadata only
- Historical datasets and decisions are not copied
- Archiving preserves historical evidence
- Dashboard metrics do not claim realized savings
- Existing `app.py` workflow remains unchanged
- SQLite remains demonstration persistence

## Test Coverage Added
- empty portfolio summary
- project-code and currency normalization
- metadata-only duplication
- duplicate-code rejection
- archive separation
- dashboard related-record counts
- portfolio summary counts
- runtime database initialization
- static dashboard contract
- realized-savings claim prohibition
- active project explicit selection
- archived project selection rejection
- archived selection does not overwrite active workspace
- archived project read-only source contract
- future workflow scope exclusion

## Expected Test Baseline
- Previous total: 85
- Dashboard tests: 15
- Expected total: 100

## Budget
- Program budget before build: 75.5 hours
- PVE-1.0.2 planned allocation: 11 hours
- Revised estimated effort used: 11.5 hours
- Estimated remaining program budget: 64.0 hours

## Preserved Controls
- deterministic analytical engines
- engineering validation requirement
- no autonomous approval
- synthetic-data disclaimer
- non-production disclaimer
- draft integration contract
- AI Procurement Copilot separation
- existing Streamlit decision workflow

## Explicit Exclusions
No upload, JSON parsing, CSV parsing, configurable thresholds, scenario execution, decision-history interface, authentication, external database, supplier workflow, ERP integration, AI approval, or new packaging category.

## CI Evidence
To be completed after the final corrective branch-head CI run.

## QA Result
Pending CI and complete diff review.

## Merge Rule
Keep the pull request as draft. Do not merge automatically.
