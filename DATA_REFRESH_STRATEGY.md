# Data Refresh Strategy

## Objective
Provide reliable Power BI refresh without affecting the active Streamlit application.

## Recommended Initial Mode
Power BI Import mode with scheduled refresh from approved SQL reporting views.

## Refresh Layers
1. PVE operational data remains authoritative.
2. A controlled reporting load updates SQL reporting tables.
3. Reconciliation runs before a load is marked successful.
4. Power BI refresh starts only after a successful reporting load.

## Proposed Cadence
- Portfolio demonstration: on demand
- Controlled pilot: daily or after approved scenario batches
- Departmental production: scheduled refresh with documented service-level expectations

## Failure Controls
- retain the last successful reporting dataset
- log load start, end, status, row counts, and source versions
- prevent partial loads from becoming visible
- alert on reconciliation variance or failed refresh
- never delete immutable source evidence to repair reporting

## Gateway Decision
A gateway is required only when Power BI Service cannot directly reach the selected SQL environment. The implementation phase must confirm hosting and licensing before selecting a gateway.

## Deferred
DirectQuery, real-time streaming, incremental refresh, and event-driven refresh are deferred until data volume and business need justify them.