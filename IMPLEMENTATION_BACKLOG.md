# Implementation Backlog

## Planning Status
Backlog defined; implementation not started.

## Phase 1 — Architecture and Requirements (20h)
- confirm audience, KPIs, data sources, hosting, licensing, and sharing
- freeze KPI dictionary and dashboard page scope
- decide SQL platform and reporting-load pattern

## Phase 2 — SQL Reporting Layer (35h)
- create dimensions, facts, audit tables, and reporting views
- preserve source identifiers and project isolation
- add lineage, load status, and reconciliation records

## Phase 3 — Python Reporting Integration (35h)
- map authoritative PVE outputs to reporting entities
- implement idempotent controlled loads
- add validation and failure rollback
- do not change analytical outcomes

## Phase 4 — Power BI Semantic Model (35h)
- relationships, date model, measures, calculation groups only if justified
- row-level-security design
- data dictionary and measure documentation

## Phase 5 — Dashboard Build (35h)
- eight approved report pages
- drill-through, tooltips, filters, and executive navigation
- synthetic-data and non-approval disclosures

## Phase 6 — QA and Demo (20h)
- numerical reconciliation
- refresh testing
- access testing
- performance review
- documentation and seven-minute interview demonstration

## Priority Order
1. Traceability and reconciliation
2. Data model stability
3. Executive usefulness
4. Security and sharing
5. Visual polish

## Deferred Backlog
API, Power Apps, ERP integration, supplier portal, real-time streaming, autonomous approval, and enterprise rollout.