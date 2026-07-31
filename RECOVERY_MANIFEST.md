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

## E1.7 Governance-Closed Recovery Point
- Milestone: E1.7 — Governed Approved Specification Consumption Contract.
- Status: completed, verified, merge-committed into `e1-development`, and governance-closed.
- Recovery branch: `e1-development`.
- Recovery SHA: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Retained feature branch: `e1/governed-approved-specification-consumption`.
- Retained feature SHA: `b08bf9d92dcda173ce4ecd2f913e0d3f9f1b5940`.
- Pull request: PR #68 merged and closed by merge commit.
- Scope evidence: 10 commits; 15 changed files; 2,907 additions; 0 deletions.
- Validation evidence: workflow run `30628727103`, job `91149911990`; 656 tests passed; 0 failures; 0 errors.
- Artifact evidence: `8792456475`; SHA-256 `69635bdcf5125aed1e1e5e4c846cd31ccf8fad866daed4d2a5d702b3b62bd771`.
- Frozen `main` remains `300054cceb255e8e1273e8012a3ba0c0a236556d`.

## E1.7 Recovery and Claim Rules
- Resume E1 development only from `e1-development` at or after `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7` unless a later governance-closed SHA is explicitly approved.
- Preserve the retained feature branch until separate deletion authorization.
- E1.7 prepares governed approved-specification consumption envelopes and records purpose-specific authorizations.
- E1.7 does not execute cost, scenario, risk, material, sourcing, recommendation, or award engines.
- E1.7 does not approve a downstream business decision.
- Any downstream analytical consumer, release-candidate audit, promotion toward `main`, deployment, release, or tag requires separate authorization.
