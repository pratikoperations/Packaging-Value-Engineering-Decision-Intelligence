# Phase Acceptance Criteria

## Purpose
Define measurable exit gates for the 180-hour base implementation plan.

## Phase 1 — Architecture and Requirements
Accepted only when:
- architecture decision record is approved
- KPI dictionary is frozen
- source-to-target mapping is complete
- PostgreSQL hosting and Power BI sharing approach are documented
- Streamlit, SQLite, public sharing, and no-migration boundaries are confirmed

## Phase 2 — PostgreSQL Reporting Layer
Accepted only when:
- dimensions, facts, audit tables, and approved views exist
- foreign keys and project isolation tests pass
- authoritative source IDs are preserved
- Power BI role has SELECT-only access to approved views
- sample load does not change SQLite or Streamlit behavior

## Phase 3 — Reporting Load Integration
Accepted only when:
- on-demand load is idempotent
- duplicate loads are rejected or safely ignored
- partial failure preserves the last successful dataset
- load audit and lineage are complete
- reconciliation blocks publication of inconsistent data

## Phase 4 — Power BI Semantic Model
Accepted only when:
- Import model has no ambiguous relationships
- all approved KPIs are documented
- DAX aggregates stored outcomes and does not recreate decision logic
- project, scenario, dataset, threshold, and alternative traceability is available
- deterministic totals and statuses exactly match Python and PostgreSQL

## Phase 5 — Dashboard Build
Accepted only when:
- all eight approved pages are complete
- navigation, filters, tooltips, and drill-through work
- baseline is never shown as the preferred recommendation
- archived history remains visible and read-only
- synthetic-data and non-approval disclosures are present

## Phase 6 — QA and Demo
Accepted only when:
- zero unresolved deterministic variances remain
- at least five representative scenarios pass manual reconciliation
- refresh failure and recovery are tested
- read-only permissions are verified
- known limitations are documented
- seven-minute interview demo is accepted

## Contingency Rule
The separate 20-hour reserve may address documented hosting, licensing, gateway, connectivity, or reconciliation issues only. It cannot fund new scope.

## Release Rule
No phase may be treated as complete without recorded evidence. No implementation release may proceed until all phase gates pass.