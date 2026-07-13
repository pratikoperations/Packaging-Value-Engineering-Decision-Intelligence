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
- Build 8 starting head: `4de563c08178ca2c0e406fce2fa4e7347938119b`
- Build 8 implementation: complete
- Final-head validation: pending

## Build state
- Builds 1 through 7: complete and validated, 61 hours consumed.
- Build 8: implementation complete, 8 hours consumed, final CI required.
- Total consumed: 69 hours.
- Remaining under the 80-hour cap: 11 hours.

## Build 8 recovery evidence
- Guided category Excel, JSON, and CSV intake workflow.
- Readiness, blockers, output availability, source traceability, commercial estimates, testing evidence, and report export.
- JSON and Markdown executive summaries include unavailable-output reasons and approval limitations.
- Focused report tests and Build 8 QA record added.

## Next increment
Build 9 is not authorized. Stop after Build 8 final validation and report the authorization gate.

## Recovery rule
Resume only from the active branch and PR. Keep PR #25 draft and unmerged. Do not begin Build 9 without explicit authorization.

## Scope boundary
Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, and autonomous approval remain excluded.
