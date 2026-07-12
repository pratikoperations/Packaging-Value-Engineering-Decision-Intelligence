# Changelog

## [Unreleased]

### Added
- Deterministic material engine
- Deterministic cost engine
- Material and cost analysis dataclasses
- Eight new engine tests
- PVE-0.3 QA report
- CI coverage for PVE-0.3 files and all tests

### Calculations
- Component-weight aggregation
- Component-to-case weight variance
- Annual material mass
- Material change versus baseline
- Unit and annual cost
- Unit and annual savings versus baseline
- Cost change percentage versus baseline

### Scope Boundary
PVE-0.3 does not include UI, technical qualification, risk, recommendation scoring, supplier ranking, allocation, scenario analysis, autonomous approval, or PVE-0.4 functionality. The integration contract remains draft.

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
- Post-merge closure commit: `6a6f5d080f906f3a6b01b73cd04465db7da356ef`
- Stable branch: `main`
- Tests: 10 passed, 0 failed, 0 errors
- QA result: Pass

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
