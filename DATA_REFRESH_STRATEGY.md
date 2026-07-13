# Data Refresh Strategy

## Objective
Provide reliable Power BI refresh without affecting the active Streamlit application or SQLite operational persistence.

## Initial Mode
- Power BI Import mode
- PostgreSQL reporting views
- on-demand refresh for portfolio use
- gateway deferred unless hosting requires it

## Refresh Sequence
1. Streamlit and SQLite remain authoritative and operationally unchanged.
2. An authorized reporting-load process reads approved SQLite outcomes.
3. The process writes an idempotent reporting projection to PostgreSQL.
4. Reconciliation validates row counts, values, statuses, source IDs, and versions.
5. Only a successful reconciled load is marked reportable.
6. Power BI Import refresh runs after the successful load.

## Failure Controls
- retain the last successful reporting dataset
- log load start, end, status, row counts, source versions, and errors
- prevent partial loads from becoming visible
- reject duplicate or inconsistent loads
- block Power BI refresh when reconciliation fails
- never delete or modify immutable SQLite evidence to repair reporting

## Portfolio Operating Model
- refresh owner: project maintainer
- cadence: on demand before demonstration or review
- acceptable staleness: latest successful manually initiated load
- failure response: preserve prior successful dataset, investigate, correct mapping or connectivity, rerun load, then refresh Power BI

## Gateway Rule
A gateway is introduced only if Power BI Service cannot directly reach the selected PostgreSQL host. Desktop-only demonstration does not require a gateway.

## Deferred
Scheduled departmental refresh, service-level targets, production alerting, DirectQuery, incremental refresh, real-time streaming, and event-driven refresh.