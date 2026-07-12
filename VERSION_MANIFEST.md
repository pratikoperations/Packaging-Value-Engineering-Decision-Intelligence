# Version Manifest

## Current Program Version
- Program: `PVE 1.0 Controlled Build`
- Current build: `PVE-1.0.1`
- Working version: `1.0.1-foundation-persistence`
- Status: Draft PR preparation and validation
- Stable branch: `main`
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
- Immutable dataset repository
- Immutable threshold-profile repository
- Immutable scenario repository
- Immutable decision-snapshot repository
- Export-record repository
- Isolated temporary-database test fixtures

## Stable Public Release
- Project version: `0.7.0-qa-interview-release`
- Stable public deployment: https://packaging-value-engineering-decision-intelligence.streamlit.app/
- Latest stable maintenance commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Stable tests: 60 passed, 0 failed, 0 errors

## Scope Boundary
PVE-1.0.1 adds persistence infrastructure only. It excludes UI expansion, uploads, CSV parsing, configurable threshold UI, history UI, authentication, external databases, enterprise integration, supplier workflows, AI approval, and additional packaging categories.
