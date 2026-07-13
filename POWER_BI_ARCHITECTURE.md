# Power BI Edition Architecture

## Architecture Decision
Use PostgreSQL as a read-only reporting mirror between the existing PVE application and Power BI.

## Fixed Boundaries
- Streamlit remains the active, shareable operational workflow layer.
- Current SQLite operational persistence remains unchanged and authoritative.
- Existing Python services remain authoritative for validation, scenario execution, qualification, risk, recommendations, and immutable decision snapshots.
- PostgreSQL receives governed reporting projections only; it is not an operational write store.
- Power BI connects to approved PostgreSQL reporting views in Import mode and remains read-only.
- No operational persistence migration is included.
- No API, Power Apps, ERP integration, real-time streaming, or enterprise deployment is included.

## Logical Flow
1. Users continue to operate PVE through Streamlit.
2. Existing Python and SQLite workflows create authoritative operational evidence.
3. A controlled reporting-load process projects approved data into PostgreSQL.
4. Reconciliation validates counts, values, statuses, versions, and source identifiers.
5. Power BI imports data only from approved read-only views.
6. Power BI presents executive analysis but cannot create, approve, or modify operational evidence.

## Component Responsibilities
### Streamlit and Python
- project and dataset workflows
- scenario execution
- technical and risk controls
- recommendations for review
- immutable decision evidence
- operational validation

### SQLite
- current authoritative operational persistence
- unchanged by this edition

### PostgreSQL Reporting Mirror
- read-optimized dimensions and facts
- reporting views
- lineage, load, and reconciliation records
- no operational write authority

### Power BI
- semantic model
- aggregation measures
- executive dashboards
- drill-through and decision history
- no recreation of authoritative qualification, risk, eligibility, or recommendation logic

## Preservation Rules
- The current Streamlit deployment and public sharing link remain active.
- Existing application, persistence, analytical logic, tests, deployment, controls, and governance are not modified during planning.
- GitHub remains canonical.
- Python calculations remain authoritative.
- DAX may aggregate stored outcomes but must not create conflicting business logic.

## Initial Technical Target
- SQL platform: PostgreSQL
- Power BI mode: Import
- Refresh: on demand for portfolio use
- Gateway: deferred unless selected hosting requires it

## Deferred Scope
API layer, Power Apps, operational persistence migration, ERP integration, supplier portal, autonomous approval, real-time streaming, gateway deployment unless required, and enterprise-wide deployment.