# Architecture Decision Record

## Decision
Adopt PostgreSQL as a read-only reporting mirror for the PVE Power BI Executive Reporting Edition.

## Context
The completed PVE application already uses Streamlit, Python, and SQLite for operational workflows and governed decision evidence. The Power BI edition must add executive reporting without destabilizing the existing application or replacing its persistence layer.

## Chosen Architecture
- Streamlit remains the active and shareable operational interface.
- SQLite remains the authoritative operational persistence layer.
- Existing Python logic remains authoritative for all calculations, qualifications, risks, thresholds, recommendations, and decision snapshots.
- PostgreSQL receives controlled reporting projections only.
- Power BI uses Import mode against approved PostgreSQL views.
- Power BI is read-only.
- Refresh is on demand for portfolio use.
- Gateway is deferred unless the selected hosting topology requires it.

## Rejected Alternatives
### Replace SQLite with PostgreSQL
Rejected for this edition because it would change operational persistence, increase regression risk, and exceed the approved reporting scope.

### Power BI DirectQuery
Deferred because Import mode is simpler, faster for portfolio use, and easier to reconcile.

### API-first integration
Rejected because it adds unnecessary backend complexity for the reporting use case.

### File-only integration
Rejected as the final target because it provides weaker governance, traceability, and refresh architecture.

## Consequences
### Positive
- preserves current Streamlit functionality and sharing
- protects completed application logic
- creates a professional SQL and Power BI architecture
- supports traceability and reconciliation
- keeps implementation within the planned portfolio scope

### Trade-offs
- introduces a controlled data-load process
- creates two stores with different responsibilities
- requires explicit lineage and reconciliation
- Power BI may not show the latest operational data until an on-demand refresh completes

## Scope Boundary
No operational migration, API, ERP integration, supplier portal, autonomous approval, real-time streaming, or enterprise deployment is authorized.

## Status
Accepted for planning. Implementation remains unauthorized until PR #23 receives final approval and a separate build is started.