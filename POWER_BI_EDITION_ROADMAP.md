# PVE Power BI Executive Reporting Edition Roadmap

## Status
Planning only. No implementation is authorized by this document.

## Objective
Add Power BI as an executive reporting layer while preserving the completed Streamlit application, current sharing link, GitHub repository, operational workflows, decision logic, tests, immutability, and governance controls.

## Approved Architecture
- Streamlit remains the operational workflow layer.
- A shared SQL database becomes the governed reporting source.
- Power BI consumes reporting-ready tables and views.
- No API-first architecture.
- API work is deferred.

## 180-Hour Plan
1. Architecture and reporting requirements — 20 hours
2. SQL reporting schema and migration design — 35 hours
3. Python-to-SQL reporting integration — 35 hours
4. Power BI semantic model and DAX — 35 hours
5. Executive dashboard development — 35 hours
6. QA, reconciliation, documentation, and interview demo — 20 hours

## Stage Gates
- Gate 1: reporting requirements and KPI dictionary approved
- Gate 2: SQL schema and data ownership approved
- Gate 3: reconciliation proves Power BI totals match PVE outputs
- Gate 4: security and refresh design approved
- Gate 5: interview demo accepted

## Non-Goals
No replacement of Streamlit, no changes to analytical logic, no autonomous approval, no ERP integration, no supplier allocation, no production deployment, and no API implementation.

## Completion Definition
Planning is complete when all ten planning documents are reviewed and the implementation backlog is approved. Implementation must start under a separate build authorization.