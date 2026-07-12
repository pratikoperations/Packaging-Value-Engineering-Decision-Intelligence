# PVE-1.0.2 QA Report

## Build
PVE-1.0.2 — Project Dashboard

## Status
Draft PR validation pending

## Objective
Add a controlled multi-project Streamlit dashboard without introducing upload, threshold, analysis, history, authentication, supplier, or AI approval workflows.

## Changed Capability
- Portfolio summary metrics
- Project creation
- Active project selection in Streamlit session state
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

## Expected Test Baseline
- Previous total: 85
- New dashboard tests: 10
- Expected total: 95

## Budget
- Program budget before build: 75.5 hours
- PVE-1.0.2 planned allocation: 11 hours
- Estimated effort used: 10.5 hours
- Estimated remaining program budget: 65.0 hours

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
To be completed after the final branch-head CI run.

## QA Result
Pending CI and complete diff review.

## Merge Rule
Keep the pull request as draft. Do not merge automatically.
