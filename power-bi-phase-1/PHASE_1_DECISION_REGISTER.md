# Phase 1 Decision Register

## Status Legend
- **Fixed** — approved and not open for redesign in Phase 1
- **Confirm** — evidence is required before Phase 1 closure
- **Deferred** — outside Phase 1 or later scope

| Decision | Status | Current Position | Required Evidence |
|---|---|---|---|
| Operational interface | Fixed | Streamlit retained | Confirm current deployment remains reachable |
| Operational persistence | Fixed | SQLite remains authoritative | Confirm no schema migration is introduced |
| Reporting database role | Fixed | PostgreSQL read-only reporting mirror | Use local PostgreSQL for portfolio implementation; no cloud hosting in initial build |
| Power BI mode | Fixed | Import | Power BI Desktop on Windows is required for report development; Android app is viewer-only for this project |
| Refresh cadence | Fixed | On demand for portfolio use | Project maintainer triggers load and refresh before demos |
| Gateway | Deferred | Not required for local PostgreSQL + Desktop-only demonstration | Revisit only if Power BI Service is later authorized |
| Power BI Service | Deferred | Not required for initial implementation | Current free Android access is insufficient evidence of publish/share rights; Service publishing is optional future scope |
| Public sharing | Fixed | Streamlit remains the public operational demo | Power BI fallback is Desktop screen share or recorded walkthrough |
| Data classification | Fixed | Synthetic data only for portfolio edition | Confidential supplier, company, personal, pricing, contract, and production data prohibited |
| KPI definitions | Confirm | Existing KPI dictionary is baseline | Freeze currency, precision, rounding, filters, and owners |
| Source mapping | Confirm | Existing mapping is baseline | Validate against actual SQLite/Python fields without code changes |
| Row-level security | Deferred | Not required for synthetic local demo | Required before real departmental sharing |
| API | Deferred | Excluded | None |
| Enterprise deployment | Deferred | Excluded | None |

## User Environment Decision
- Current access: Power BI Android app, free version.
- Initial development target: Power BI Desktop on a Windows computer.
- Initial sharing target: local demonstration and recorded walkthrough only.
- Initial database target: local PostgreSQL.
- Initial data target: synthetic portfolio data only.
- Streamlit remains the only public interactive link.

## Phase Boundary
No implementation artifact from Phase 2 onward may be created under this branch. This includes PostgreSQL DDL, migration scripts, ETL/load code, Power BI files, DAX implementation, deployment configuration, or gateway installation.
