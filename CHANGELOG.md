# Changelog

## [1.0.6-decision-snapshot-final-release] — Final Review Pending

### Added
- Immutable decision snapshots from saved scenarios
- Exact project, scenario, dataset, and threshold references
- Dataset-defined baseline exclusion
- Recommendation-for-review statuses without autonomous approval
- Project-scoped read-only decision history
- Archived-project repository write protection
- Final interview guide, QA report, and release checklist

### Validation
- PR #22
- Final CI: PVE CI #507
- Run ID: `29221779591`
- Tests: 179 passed, 0 failed, 0 errors
- Actual effort: 17.0 hours
- Remaining program budget: 0.5 hours

### Mandatory Controls Preserved
- Engineering validation required
- Human approval required
- Autonomous approval prohibited
- Critical risk and not-qualified outcomes blocked
- Insufficient data cannot become recommended
- Snapshots immutable
- Project isolation enforced

### Excluded
- Authentication
- External database
- ERP integration
- Supplier ranking or allocation
- Autonomous approval
- Analytical-engine modification
- Recommendation-engine modification
- New packaging category

## [1.0.5-controlled-scenario-execution] — Completed
- PR #21 merged and closed
- Merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Tests: 160 passed, 0 failed, 0 errors
- Effort used: 17.5 hours
- Program budget remaining: 17.5 hours
- Source branch deleted
- Added controlled deterministic scenario execution, immutable scenario records, exact dataset and threshold binding, business-threshold explanations, and mandatory engineering controls.

## [1.0.4-configurable-thresholds] — Completed
- PR #20 merged and closed
- Merge commit: `301a0d92d41f46a15e37c5bd059e8673c3f666a6`
- Tests: 143 passed, 0 failed, 0 errors
- Effort used: 12.5 hours

## [1.0.3-upload-validation] — Completed
- PR #19 merged and closed
- Merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Effort used: 16.5 hours

## [1.0.2-project-dashboard] — Completed
- PR #18 merged and closed
- Merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors

## [1.0.1-foundation-persistence] — Completed
- PR #17 merged and closed
- Merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors

## [0.7.2-live-demo-streamlit-compatibility] — Completed
- PR #16 merged and closed
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors

## [0.7.1-streamlit-deployment-disclaimer] — Completed
- PR #15 merged and closed
- Merge commit: `c3bc5fb291c7c087c2a4ab054b297841a7b5e73a`
- Tests: 59 passed, 0 failed, 0 errors

## [0.7.0-qa-interview-release] — Completed
- PR #13 merged and closed
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Tests: 58 passed, 0 failed, 0 errors

## Prior Releases
- `0.6.0-decision-package-export` — Completed
- `0.5.0-scenario-recommendation-ui` — Completed
- `0.4.0-technical-risk` — Completed
- `0.3.0-cost-material-engine` — Completed
- `0.2.0-data-model` — Completed
- `0.1.0-foundation` — Completed