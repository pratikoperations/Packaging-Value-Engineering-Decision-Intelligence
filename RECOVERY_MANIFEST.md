# Recovery Manifest

## Stable release
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`
- Stable release: PVE 1.0.6
- Stable merge: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`
- Stable CI: PVE CI #520, run `29223657516`
- Stable tests: 179 passed

## Active PVE 1.1 recovery point
- Branch: `feature/pve-1.1-all-category-intake`
- Pull request: PR #25
- PR state: open, draft, unmerged
- Hold removed: 2026-07-14
- Builds 1 through 9: complete
- Total consumed: 80 hours
- Remaining allocation: 0 hours

## Final validation evidence
- Build 9 implementation validation: PVE CI #725
- Run ID: `29302736072`
- Validated implementation head: `f2cd981fdb2d8173569b138c8bedd399e7bb1c0d`
- Complete suite: 221 passed
- Focused report tests: 4 passed
- Total executions: 225
- Failures: 0
- Errors: 0

## Release evidence
- Eight synthetic category samples are stored in `data/demo/pve_1_1_release_cases.json`.
- Three detailed demonstration cases cover ready, blocked, and critical-data-missing outcomes.
- Final QA plan, QA report, release checklist, and interview demo are present.

## Recovery rule
Resume only for final-head validation, merge review, or governance closure after explicit authorization. Do not start another PVE 1.1 development increment because the 80-hour cap is fully consumed.

## Scope boundary
Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, and autonomous approval remain excluded.
