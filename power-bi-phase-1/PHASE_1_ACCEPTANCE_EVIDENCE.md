# Phase 1 Acceptance Evidence

## Purpose
Record the evidence required to close the 20-hour architecture and requirements phase.

## Acceptance Checklist

| Requirement | Evidence Needed | Status |
|---|---|---|
| Streamlit preserved | Current deployment and public sharing route confirmed | Open |
| SQLite preserved | No operational schema or persistence change in branch diff | Open |
| Audience confirmed | Procurement, packaging, procurement excellence, and executive audiences accepted | Passed |
| Dashboard scope frozen | Eight approved pages accepted without expansion | Passed |
| KPI dictionary frozen | Definitions, units, currency, precision, rounding, filters, exclusions, and owners recorded | Open |
| Source mapping validated | Planning mapping checked against actual authoritative entities and fields | Open |
| PostgreSQL hosting selected | Local PostgreSQL selected; local connection, zero hosting cost, local credentials, and portfolio-only backup boundary recorded | Passed |
| Power BI development route confirmed | Power BI Desktop on Windows selected; installation still required on a Windows computer | Conditional |
| Power BI Service route confirmed | Service publishing deferred; current free Android app does not establish publish/share entitlement; Desktop/recorded-demo fallback fixed | Passed |
| Gateway decision recorded | Not required for local PostgreSQL and Desktop-only demonstration | Passed |
| Data classification fixed | Synthetic portfolio data only; confidential supplier, company, personal, contract, pricing, and production data prohibited | Passed |
| Refresh operating model fixed | Project maintainer triggers on-demand reporting load and Power BI refresh before demos; last successful dataset retained on failure | Passed |
| Scope preservation verified | No API, ERP, Power Apps, migration, enterprise rollout, or decision-logic changes | Open |
| Phase 1 review complete | Review records no unresolved critical gaps | Open |

## Current Environment Evidence
- User currently has the Power BI Android application using the free version.
- Android is treated as a viewing environment, not the report-development environment.
- Initial report development requires Power BI Desktop on Windows.
- Initial sharing is local screen share or recorded walkthrough.
- Existing Streamlit remains the public interactive demonstration.

## Closure Blocker
Phase 1 cannot close until Power BI Desktop availability is confirmed on a Windows computer, KPI definitions and source mapping are frozen, scope preservation is verified, and the final Phase 1 review passes.

## Closure Rule
All rows must be marked Passed with referenced evidence before Phase 1 can be closed. Completion of this file does not authorize Phase 2.
