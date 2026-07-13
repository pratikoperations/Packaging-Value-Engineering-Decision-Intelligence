# Phase 1 Decision Register

## Status Legend
- **Fixed** — approved and not open for redesign in Phase 1
- **Confirm** — evidence is required before Phase 1 closure
- **Deferred** — outside Phase 1 or later scope

| Decision | Status | Current Position | Required Evidence |
|---|---|---|---|
| Operational interface | Fixed | Streamlit retained | Confirm current deployment remains reachable |
| Operational persistence | Fixed | SQLite remains authoritative | Confirm no schema migration is introduced |
| Reporting database role | Fixed | PostgreSQL read-only reporting mirror | Confirm hosting option and connectivity pattern |
| Power BI mode | Fixed | Import | Confirm Desktop and optional Service path |
| Refresh cadence | Fixed | On demand for portfolio use | Confirm named refresh owner and runbook |
| Gateway | Confirm | Deferred unless topology requires it | Record reachability result after hosting choice |
| Power BI Service | Confirm | Optional | Confirm account, entitlement, tenant, workspace, and sharing rights |
| Public sharing | Confirm | Streamlit remains public operational demo | Confirm Power BI fallback is Desktop/recorded walkthrough |
| Data classification | Confirm | Synthetic data preferred for portfolio | Record prohibited data categories |
| KPI definitions | Confirm | Existing KPI dictionary is baseline | Freeze currency, precision, rounding, filters, and owners |
| Source mapping | Confirm | Existing mapping is baseline | Validate against actual SQLite/Python fields without code changes |
| Row-level security | Deferred | Not required for synthetic local demo | Required before real departmental sharing |
| API | Deferred | Excluded | None |
| Enterprise deployment | Deferred | Excluded | None |

## Phase Boundary
No implementation artifact from Phase 2 onward may be created under this branch. This includes PostgreSQL DDL, migration scripts, ETL/load code, Power BI files, DAX implementation, deployment configuration, or gateway installation.
