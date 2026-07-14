# Recovery Manifest

## Repository
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`

## Stable Release Recovery Points

### PVE 1.0.6
- Status: complete and governance-closed.
- Merge commit: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`.
- Final CI: PVE CI #520, run `29223657516`.
- Tests: 179 passed.

### PVE 1.1
- Release: All-Category Project Intake and Validation Readiness.
- Status: complete, validated, squash-merged, and governance-closed.
- Pull request: PR #25, merged and closed.
- Final feature head: `dc85db49afee46bde3118684761c0a176dd32194`.
- Squash merge commit: `37f4ae58e0d57c4531293371e423d771ada7ae50`.
- Final pre-merge CI: PVE CI #735.
- Run ID: `29302903427`.
- Complete unittest suite: 221 passed.
- Focused report tests: 4 passed.
- Total executions: 225.
- Failures: 0.
- Errors: 0.
- Total consumed: 80 hours.
- Remaining allocation: 0 hours.

## Release Evidence
- Eight synthetic category samples are stored in `data/demo/pve_1_1_release_cases.json`.
- Three detailed demonstration cases cover ready, blocked, and critical-data-missing outcomes.
- Final QA plan, QA report, release checklist, and interview demonstration are present.
- Engineering validation and human approval remain mandatory.
- Autonomous approval remains prohibited.
- Historical evidence and decision snapshots remain immutable.
- Archived projects remain read-only.
- Project isolation remains enforced.

## Recovery Rule
Resume from `main` at or after merge commit `37f4ae58e0d57c4531293371e423d771ada7ae50`. PVE 1.1 is closed; do not resume feature development on PR #25. Any PVE 1.2 work requires a new explicit authorization, scope, budget, branch, and pull request.

## Scope Boundary
Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, and autonomous approval remain excluded.
