# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current completed build: PVE-0.1 — Repository Foundation
- Stable branch: `main`
- Stable merge commit: `3a0ac16d1808311a10d2be1986ca853085f67efe`
- Current closure branch: `agent/pve-0.1-post-merge-closure`

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
1. Confirm latest `main`, open pull requests, and CI status.
2. Confirm PVE-0.1 is completed and merged.
3. If the post-merge closure PR is open, finish only closure corrections there.
4. After closure merge, create a new branch from updated `main` for PVE-0.2.
5. Resume only the next approved build unit.
6. After changes, run tests, update governance records, commit, push, verify GitHub, and store QA evidence.

## Next Approved Build
PVE-0.2 — Data Model and Demo Data

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
