# Version Manifest

## Stable Public Version
- Project version: `0.7.0-qa-interview-release`
- Build: `PVE-0.7`
- Status: completed and publicly deployed
- Stable branch: `main`
- Release PR: PR #13 merged and closed
- Release merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Latest maintenance commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Public application: https://packaging-value-engineering-decision-intelligence.streamlit.app/

## Stable Validation Evidence
- PVE CI baseline: success
- Tests after PVE-0.7.2: 60 passed, 0 failed, 0 errors

## Stable Deliverables
- Interview-ready README
- Streamlit demonstration UI
- Deterministic cost, material, qualification, risk, scenario, recommendation, and export modules
- JSON and Markdown decision-package exports
- Interview demonstration guide
- Release checklist and recovery manifest

## PVE 1.0 Working Version
- Program: `PVE 1.0 Controlled Build`
- Current build: `PVE-1.0.1`
- Working version: `1.0.1-foundation-persistence`
- Status: draft PR preparation and validation
- Feature branch: `agent/pve-1.0.1-foundation-persistence`
- Stable base commit: `a45cabc37aada9e57febe7687617146d2da65fd0`

## Approved Program Budget
- Working budget: 90 hours
- Hard ceiling: 110 hours
- PVE-1.0.1 allocation: 13 hours

## PVE-1.0.1 Deliverables
- SQLite connection and transaction manager
- Schema migration version tracking
- Foreign-key enforcement
- Project repository and application service
- Immutable dataset, threshold, scenario, and decision repositories
- Export-record repository
- Isolated temporary-database test fixtures

## Scope Boundary
The stable release and PVE-1.0.1 exclude autonomous approval, supplier ranking or allocation, final integration contracts, production infrastructure, authentication, external databases, enterprise integrations, document extraction, and additional packaging categories.
