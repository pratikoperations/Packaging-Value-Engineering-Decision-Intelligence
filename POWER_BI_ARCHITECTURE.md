# Power BI Edition Architecture

## Architecture Decision
Use a shared SQL reporting database between the existing PVE application and Power BI.

## Logical Flow
1. Users continue to operate PVE through Streamlit.
2. Existing Python services remain authoritative for validation, scenario execution, qualification, risk, recommendations, and decision snapshots.
3. Approved reporting integration writes or projects governed data into SQL reporting tables.
4. Power BI reads reporting views in read-only mode.
5. Power BI presents executive analysis; it does not create, approve, or modify operational evidence.

## Component Boundaries
### Streamlit and Python
- project and dataset workflows
- scenario execution
- technical and risk controls
- immutable decision evidence
- operational validation

### Shared SQL Database
- governed source for reporting
- normalized operational references
- reporting facts and dimensions
- audit timestamps and source identifiers

### Power BI
- semantic model
- measures and KPIs
- executive dashboards
- drill-through and decision history

## Preservation Rules
- The current Streamlit deployment and sharing link remain active.
- Existing application logic is not rewritten for Power BI.
- Existing repository remains canonical.
- Power BI is read-only against reporting views.
- Python calculations remain authoritative; DAX must not recreate conflicting business logic.

## Deferred Scope
API layer, Power Apps, ERP integration, supplier portal, autonomous approval, real-time streaming, and enterprise-wide deployment.