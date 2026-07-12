# Changelog

## [Unreleased]

### Planned
- PVE-0.3 — Cost and Material Engine

## [0.2.0-data-model] — PVE-0.2 Data Model and Demo Data

### Added
- Canonical data model covering fourteen entity groups
- Synthetic corrugated shipping-case demo dataset with one baseline and three alternatives
- Invalid and partial-data examples
- Deterministic Python data-validation module
- Automated data-validation test suite
- Expanded PVE CI workflow
- PVE-0.2 QA report

### Completed
- PR #3 merged and closed
- Squash merge commit: `33b4319c3b74d8caaad6bc03cb85cb6ebf1727ff`
- Stable branch: `main`
- Original feature branch: Deleted
- Final validated CI: PVE CI #68, run ID `29180955427`
- Tests: 10 passed, 0 failed, 0 errors
- QA result: Pass

### Scope Boundary
PVE-0.2 includes data structures and validation only. It does not include UI, cost calculations, savings calculations, material optimization, recommendation scoring, supplier ranking, allocation, or technical approval automation. The integration contract remains draft.

## [0.1.0-foundation] — PVE-0.1 Repository Foundation

### Added
- Independent Packaging Value Engineering repository
- GitHub-first governance and recovery framework
- Build numbering and scope options
- Explicit product boundary with AI Procurement Copilot
- Integration-contract draft and dedicated integration paths
- Source, data, test, documentation, and QA foundations
- Foundation CI workflow
- Build-specific QA report

### Fixed
- Corrected case-sensitive CI validation
- Added integration export and sample paths
- Synchronized post-merge governance records

### Completed
- PVE-0.1 and closure merged to stable `main`
