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

## Historical Release Evidence
- Eight synthetic category samples are stored in `data/demo/pve_1_1_release_cases.json`.
- Three detailed demonstration cases cover ready, blocked, and critical-data-missing outcomes.
- Final QA plan, QA report, release checklist, and interview demonstration are present.
- Engineering validation and human approval remain mandatory.
- Autonomous approval remains prohibited.
- Historical evidence and decision snapshots remain immutable.
- Archived projects remain read-only.
- Project isolation remains enforced.

## Historical PVE 1.1 Recovery Rule
Resume the PVE 1.1 historical release from `main` at or after merge commit `37f4ae58e0d57c4531293371e423d771ada7ae50`. PVE 1.1 is closed; do not resume feature development on PR #25.

## E1.7 Governance-Closed Recovery Point — Historical
- Milestone: E1.7 — Governed Approved Specification Consumption Contract.
- Status: completed, verified, merge-committed into `e1-development`, and governance-closed.
- Historical implementation SHA: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Retained feature branch: `e1/governed-approved-specification-consumption`.
- Retained feature SHA: `b08bf9d92dcda173ce4ecd2f913e0d3f9f1b5940`.
- Pull request: PR #68 merged and closed by merge commit.
- Scope evidence: 10 commits; 15 changed files; 2,907 additions; 0 deletions.
- Validation evidence: workflow run `30628727103`, job `91149911990`; 656 tests passed; 0 failures; 0 errors.
- Artifact evidence: `8792456475`; SHA-256 `69635bdcf5125aed1e1e5e4c846cd31ccf8fad866daed4d2a5d702b3b62bd771`.
- At this historical milestone, `main` remained `300054cceb255e8e1273e8012a3ba0c0a236556d`.

## E1.7 Historical Recovery and Claim Rules
- Preserve the E1.7 implementation lineage unless a later governed recovery record explicitly supersedes it.
- E1.7 prepares governed approved-specification consumption envelopes and records purpose-specific authorizations.
- E1.7 does not execute cost, scenario, risk, material, sourcing, recommendation, or award engines.
- E1.7 does not approve a downstream business decision.

## E1 Release-Candidate Recovery Point — Historical
- Status: E1.1 through E1.7 completed; final E1 merge exact-SHA validated and governed as the release-candidate product baseline.
- Governed product baseline SHA: `45f795370a60654050b5dca1ff4789487b3f049e`.
- E1.7 implementation PR #68 and governance-closure PR #69 are merged and closed.
- The earlier SHA `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7` remains preserved as implementation lineage.
- Exact-SHA validation: workflow run `30640190796`, job `91187867871`, success.
- Focused report tests: 4 passed.
- Full repository suite: 656 passed; 0 failures; 0 errors.
- Retained artifact: `8797098203`; SHA-256 `5697d07b0b4664810bbad29615e04892528aa232ff18353d1e00f611b023b384`.
- At this historical milestone, `main` remained `300054cceb255e8e1273e8012a3ba0c0a236556d` and promotion still required separate authorization.

## E1 Promotion Recovery Point — Current
- Promotion PR: #71 merged and closed.
- Merge method: merge commit.
- Original pre-E1 rollback `main` SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- E1.7 implementation lineage: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Governed E1 product baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- Final pre-promotion and retained `e1-development` SHA: `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- Current promoted `main` recovery SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Post-merge workflow run: `30656143928`.
- Validation job: `91240891645`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Retained artifact: `8803331290`.
- Artifact SHA-256: `943cad0adb2f8f4d20c5c9b0f2e1520655043c2224cfb079ee67d4e5d28e2d39`.

## Current Recovery Rule
1. Use `main` at `a6803b6156b591ec1fe9587469f6fe7c00ed97f4` to reconstruct the promoted E1 stable source baseline.
2. Use `300054cceb255e8e1273e8012a3ba0c0a236556d` only as the original pre-E1 rollback point.
3. Preserve `16fe5f...`, `45f795...`, and `9a3379...` as historical implementation, governed product-baseline, and pre-promotion development lineage respectively.
4. Do not rewrite or delete retained branches or historical evidence without separate authorization.
5. Any future build must start from its explicitly authorized exact validated baseline.

## Current-State Correction
Earlier records stating that `main` remained at `300054cceb255e8e1273e8012a3ba0c0a236556d`, or that E1 promotion remained unauthorized, are preserved as historical pre-promotion milestones. They are superseded as current-state instructions by the validated promoted baseline `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.

## Mandatory Scope Boundary
- Recovery records do not authorize deployment, release, tagging, live organizational data, pilot, activation, production use, or production-readiness claims.
- Human authorization remains mandatory.
- Autonomous approval and autonomous execution of engineering, commercial, sourcing, supplier-award, cost, scenario, risk, material, recommendation, deployment, release, or production decisions remain prohibited.

## Showcase and Handoff Build 1 Recovery
- Integration branch: `showcase-handoff-development`, created from `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Feature branch: `showcase/build-1-governance-closure`, created from the same SHA.
- If Build 1 is rejected, retain the integration branch at the exact promoted baseline and do not merge the feature branch.
- Builds 2–6 require separate authorization.
