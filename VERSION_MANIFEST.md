# Version Manifest

## Final Version
- Project version: `0.7.0-qa-interview-release`
- Build: `PVE-0.7`
- Status: `0.7.0-qa-interview-release completed`
- Stable branch: `main`
- Release PR: PR #13 merged and closed
- Release merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Original feature branch: Deleted

## Final Validation Evidence
- Workflow: PVE CI
- Run number: 268
- Run ID: `29184423320`
- Validated commit: `d6ae2079e332a33edcc71d0011d642f0ae1eb5f9`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 58 passed, 0 failed, 0 errors

## Final Deliverables
- Interview-ready README
- Streamlit demonstration UI
- Deterministic cost, material, qualification, risk, scenario, recommendation, and export modules
- JSON and Markdown decision-package exports
- Interview demonstration guide
- Final release checklist
- Recovery manifest
- PVE-0.7 QA report

## Scope Boundary
The release excludes autonomous technical approval, supplier ranking, supplier allocation, final integration contract, external integration, and production deployment capability. The integration contract remains draft.

## Version State
This is the completed Lean Interview Project release after the final governance closure PR is merged.

## PVE-0.7.1 Maintenance Record
- Build: `PVE-0.7.1`
- Pull request: PR #15 merged and closed
- Merge commit: `c3bc5fb291c7c087c2a4ab054b297841a7b5e73a`
- Tests: 59 passed, 0 failed, 0 errors

## PVE-0.7.2 Maintenance Record
- Build: `PVE-0.7.2`
- Pull request: PR #16 merged and closed
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors
- Public application: https://packaging-value-engineering-decision-intelligence.streamlit.app/

## PVE 1.0 Working Version
- Program: `PVE 1.0 Controlled Build`
- Current build: `PVE-1.0.1`
- Working version: `1.0.1-foundation-persistence`
- Status: draft PR correction and validation
- Feature branch: `agent/pve-1.0.1-foundation-persistence`
- Stable base commit: `a45cabc37aada9e57febe7687617146d2da65fd0`

## Approved Program Budget
- Working budget: 90 hours
- Hard ceiling: 110 hours
- PVE-1.0.1 planned allocation: 13 hours
- Revised estimated effort used: 14.5 hours
- Estimated remaining program budget: 75.5 hours

## PVE-1.0.1 Deliverables
- SQLite connection and transaction manager
- Schema initialization with version recording
- Foreign-key enforcement
- Project repository and application service
- Immutable dataset, threshold, scenario, and decision repositories
- Cross-project integrity validation for scenarios and decisions
- Export-record repository
- Isolated temporary-database test fixtures

## PVE-1.0.1 Scope Boundary
PVE-1.0.1 excludes dashboard UI, uploads, CSV parsing, threshold UI, history UI, authentication, external databases, enterprise integrations, supplier workflows, AI approval, document extraction, and additional packaging categories.
