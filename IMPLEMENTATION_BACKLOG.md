# Implementation Backlog

## Planning Status
Backlog defined; implementation not started.

## Base Plan — 180 Hours

### Phase 1 — Architecture and Requirements (20h)
- confirm audience, KPIs, PostgreSQL hosting, Power BI account, licence, workspace, and sharing method
- approve KPI dictionary and source-to-target mapping
- confirm reporting-mirror boundary and no SQLite migration

**Exit evidence:** architecture decision approved; KPI dictionary frozen; hosting and sharing decision recorded.

### Phase 2 — PostgreSQL Reporting Layer (35h)
- create dimensions, facts, audit tables, and read-only reporting views
- preserve authoritative source identifiers and project isolation
- add lineage, load status, reconciliation, and error records

**Exit evidence:** schema review passed; foreign keys and read-only role tested; sample data loaded without changing SQLite.

### Phase 3 — Python Reporting Integration (35h)
- map authoritative PVE outputs to reporting entities
- implement idempotent on-demand loads
- add validation, rollback, and last-successful-load protection
- do not change analytical outcomes or operational persistence

**Exit evidence:** duplicate-load prevention and failure recovery demonstrated; source-to-target reconciliation passed.

### Phase 4 — Power BI Semantic Model (35h)
- build relationships, date model, measures, and metadata
- use Import mode
- aggregate stored outcomes only
- document measures and access assumptions

**Exit evidence:** model validates with no ambiguous relationships; KPI results exactly match Python and PostgreSQL.

### Phase 5 — Executive Dashboard Build (35h)
- build eight approved report pages
- add drill-through, tooltips, filters, navigation, version context, and disclosures

**Exit evidence:** every page meets dashboard acceptance criteria and shows no approval overclaim.

### Phase 6 — QA and Demo (20h)
- numerical reconciliation
- refresh and failure testing
- read-only access testing
- performance review
- documentation and seven-minute interview demo

**Exit evidence:** zero unresolved deterministic variances; known limitations recorded; demo accepted.

## Contingency Reserve — 20 Hours
Separate from the 180-hour base plan. May be used only for documented PostgreSQL hosting, Power BI licensing, gateway, connectivity, or reconciliation issues. It does not authorize new scope.

## Priority Order
1. Traceability and reconciliation
2. Preservation of Streamlit and SQLite
3. Data model stability
4. Executive usefulness
5. Security and sharing
6. Visual polish

## Deferred Backlog
API, Power Apps, ERP integration, supplier portal, real-time streaming, operational persistence migration, autonomous approval, and enterprise rollout.