# Recovery Manifest

## Purpose
Enable complete project recovery from GitHub without relying on chat history.

## Project Identity
- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Current build: PVE-0.1 — Repository Foundation
- Working branch: `agent/pve-0.1-repository-foundation`

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
1. Confirm current branch and latest commit.
2. Identify the current build and pending exit criteria.
3. Review open pull requests and CI status.
4. Resume only the next incomplete build unit.
5. After changes, run tests, update governance records, commit, push, verify GitHub, and store QA evidence.

## Separation Rule
This repository never stores AI Procurement Copilot source files. Cross-project communication uses versioned integration packages only.
