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
- Build 7 closure commit: `4de563c08178ca2c0e406fce2fa4e7347938119b`
- Build 8 final activity commit before reconciliation: `ecc9b7083062dd5313b70cdd421ae06f1ea55905`
- Current recovery head after status reconciliation: `a2ea9bcaace5e743c9d6d4c2c3a94afc723a387c`

## Authoritative build state
- Builds 1 through 7: complete and validated, 61 hours consumed.
- Build 8: complete and validated, 8 hours consumed.
- Total consumed: 69 hours.
- Remaining under the 80-hour cap: 11 hours.

## Build 7 evidence
- Authorized ceiling recorded: 5 hours.
- Closure commit: `4de563c08178ca2c0e406fce2fa4e7347938119b`.
- Validation recorded: PVE CI #649 / run `29256159775`, success.
- Core files present by closure: `src/commercial/__init__.py`, `src/commercial/savings_engine.py`, `tests/commercial/__init__.py`, `tests/commercial/test_savings_engine.py`, `COMMERCIAL_ROI_LOGIC.md`.

## Build 8 evidence
- Authorized ceiling recorded: 8 hours.
- Starting head: `4de563c08178ca2c0e406fce2fa4e7347938119b`.
- Final validated activity commit: `ecc9b7083062dd5313b70cdd421ae06f1ea55905`.
- The branch advanced by 28 commits during Build 8.
- Files added in that interval: `pages/03_PVE_1_1_Guided_Workflow.py`, `src/application/intake_workflow.py`, `src/reports/__init__.py`, `src/reports/executive_summary.py`, `tests/build8_executive_summary.py`, `docs/qa/PVE_1.1_BUILD_8_QA_REPORT.md`.
- File modified in that interval: `pages/02_Upload_Validate.py`.
- Validation: PVE CI #699 / run `29278878816`, success.
- Focused report tests: 4 passed.
- Complete automated suite: 213 passed.
- Total test executions: 217; zero failures and errors.

## Authorization reconciliation
- Branch governance records support Build 7 authorization at 5 hours and Build 8 authorization at 8 hours.
- The connector-visible PR comments do not expose separate user-authored authorization comments for Build 7 or Build 8.
- Recovery therefore relies on the accepted build plan, branch governance records, and validated closure commits.

## Next increment
Build 9 is not authorized. Stop at the Build 9 authorization gate.

## Recovery rule
Resume only from the active branch and PR. Keep PR #25 draft and unmerged. Do not begin Build 9 without explicit authorization.

## Scope boundary
Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, and autonomous approval remain excluded.