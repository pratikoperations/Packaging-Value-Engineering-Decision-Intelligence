# PVE Power BI Executive Reporting Edition — Phase 1 Kickoff

## Authorization
Phase 1 only is authorized. No Phase 2 schema build, PostgreSQL deployment, reporting-load code, Power BI model, dashboard build, or production infrastructure is authorized.

## Phase 1 Objective
Finalize architecture and reporting requirements for the approved Power BI executive reporting edition while preserving the completed Streamlit application and SQLite operational persistence.

## Fixed Boundaries
- Streamlit remains active and shareable.
- Existing public Streamlit link remains preserved.
- SQLite remains the authoritative operational persistence layer.
- PostgreSQL remains a planned read-only reporting mirror.
- Power BI remains a read-only executive reporting layer.
- Python remains authoritative for analytical and decision logic.
- No operational persistence migration.
- No API, ERP integration, Power Apps, autonomous approval, or enterprise rollout.

## Phase 1 Budget
20 hours maximum under the approved 180-hour base plan.

## Phase 1 Deliverables
1. Confirmed stakeholder and report audience matrix.
2. Frozen KPI dictionary and ownership matrix.
3. Validated source-to-target mapping at planning level.
4. PostgreSQL hosting decision.
5. Power BI account, licence, workspace, and sharing decision.
6. Data classification and demonstration-data decision.
7. Refresh ownership and operating model.
8. Phase 1 acceptance evidence and recommendation for Phase 2.

## Exit Gate
Phase 1 is complete only when every item in `PHASE_1_ACCEPTANCE_EVIDENCE.md` is resolved and recorded. Phase 2 requires separate authorization.
