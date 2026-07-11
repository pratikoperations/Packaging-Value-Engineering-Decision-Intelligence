# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current build: PVE-0.1 — Repository Foundation
- Status: Ready for review and merge
- Working branch: `agent/pve-0.1-repository-foundation`
- Pull request: `#1`

## Mandatory Reading Order
1. `PROJECT_STATUS.md`
2. `BUILD_INSTRUCTIONS.md`
3. `VERSION_MANIFEST.md`
4. `ACTIVITY_LOG.md`
5. `BUILD_HISTORY.md`
6. `CHANGELOG.md`
7. `DECISION_LOG.md`
8. `docs/MASTER_ARCHITECTURE.md`
9. `docs/MASTER_BUILD_PLAN.md`
10. Latest report in `docs/qa/`

## Recovery Procedure
1. Confirm the latest commit, current branch, PR state, and CI result.
2. Identify the current build and its completion status.
3. Review open pull requests and any unresolved QA items.
4. If PR #1 is not merged, continue only PVE-0.1 corrections on its branch.
5. If PR #1 is merged, begin PVE-0.2 from updated `main` on a new branch.
6. After changes, run tests, update governance records, commit, push, verify GitHub, and store QA evidence.

## Current Next Action
Confirm the final Foundation CI pass and review PR #1. Do not merge automatically without explicit instruction.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
