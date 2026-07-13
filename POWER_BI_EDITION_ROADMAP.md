# PVE Power BI Executive Reporting Edition Roadmap

## Status
Planning only. No implementation is authorized by this document.

## Objective
Add Power BI as an executive reporting layer while preserving the completed Streamlit application, public sharing link, GitHub repository, operational workflows, SQLite persistence, decision logic, tests, immutability, and governance controls.

## Fixed Architecture
- Streamlit remains active and shareable.
- SQLite remains the authoritative operational persistence layer.
- PostgreSQL is a read-only reporting mirror.
- Power BI consumes approved PostgreSQL views in Import mode.
- Refresh is on demand for portfolio use.
- Gateway is deferred unless hosting requires it.
- API, operational persistence migration, and enterprise deployment are excluded.

## 180-Hour Base Plan
1. Architecture and reporting requirements — 20 hours
2. PostgreSQL reporting schema — 35 hours
3. Python-to-PostgreSQL reporting integration — 35 hours
4. Power BI semantic model and DAX — 35 hours
5. Executive dashboard development — 35 hours
6. QA, reconciliation, documentation, and interview demo — 20 hours

## Contingency
A separate 20-hour reserve may be used only for documented licensing, PostgreSQL hosting, gateway, connectivity, or reconciliation problems. It does not expand scope.

## Stage Gates
- **Gate 1:** architecture decision, hosting, sharing approach, KPI dictionary, and source mapping approved
- **Gate 2:** PostgreSQL schema, ownership, read-only permissions, and lineage approved
- **Gate 3:** controlled load is idempotent and failure-safe
- **Gate 4:** Power BI totals and statuses exactly match authoritative PVE outputs
- **Gate 5:** dashboards, disclosures, traceability, and interview demo accepted

## Non-Goals
No Streamlit replacement, SQLite migration, analytical-logic change, autonomous approval, ERP integration, supplier allocation, API implementation, production gateway unless required, or enterprise rollout.

## Completion Definition
Planning is complete when all fifteen planning documents are reviewed, fixed decisions are consistent across files, and the implementation backlog is explicitly approved. Implementation must start under a separate build authorization.