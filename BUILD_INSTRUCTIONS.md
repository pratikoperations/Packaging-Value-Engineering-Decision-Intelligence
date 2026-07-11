# Build Instructions

## Mandatory Start Sequence
1. Read `PROJECT_STATUS.md`.
2. Read `RECOVERY_MANIFEST.md`.
3. Read the latest entries in `ACTIVITY_LOG.md`, `BUILD_HISTORY.md`, `CHANGELOG.md`, and `DECISION_LOG.md`.
4. Read the latest QA report in `docs/qa/`.
5. Confirm branch, build ID, scope, acceptance criteria, dependencies, and last known stable commit.

## Build Rules
- Work on one coherent build unit at a time.
- Keep deterministic calculations separate from AI-generated text.
- Do not silently change formulas, units, thresholds, assumptions, or defaults.
- Add or update tests with every logic change.
- Keep all PVE files in this repository only.
- Never write directly into the AI Procurement Copilot repository.

## Completion Workflow
1. Implement the approved scope.
2. Run applicable tests and checks.
3. Inspect the full diff.
4. Update governance records.
5. Commit using `PVE-x.x: concise outcome`.
6. Push the branch.
7. Re-fetch the GitHub commit and verify file placement.
8. Check CI or document why it is not applicable.
9. Store QA evidence before marking the build complete.

## Failure Rule
Preserve the last known stable state, log the failure, document limitations, and use a corrective build rather than hiding failed work.

## Source-of-Truth Rule
When chat and GitHub conflict, the latest quality-checked GitHub record governs.
