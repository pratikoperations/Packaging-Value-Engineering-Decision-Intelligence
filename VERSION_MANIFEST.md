# Version Manifest

## Current Version
- Project version: `0.7.0-qa-interview-release`
- Build: `PVE-0.7`
- Status: Release implementation complete — CI and QA pending
- Stable branch: `main`
- Working branch: `agent/pve-0.7-qa-interview-release`
- Base commit: `1b3a6f0250f3645df08e908b3be30d75b99294e7`

## Completed Foundation
- PVE-0.6 status: `0.6.0-decision-package-export completed`
- Canonical data-model version: `0.2.0`
- Automated test baseline before PVE-0.7: 52

## Current Deliverables
- Final README: `README.md`
- Interview demo guide: `docs/INTERVIEW_DEMO_GUIDE.md`
- Final release checklist: `docs/FINAL_RELEASE_CHECKLIST.md`
- Release QA report: `docs/qa/PVE-0.7_QA_REPORT.md`
- End-to-end release tests: `tests/release/test_end_to_end_release.py`
- Recovery manifest: `RECOVERY_MANIFEST.md`

## Release Scope
- End-to-end deterministic QA
- Static UI smoke validation
- Interview-demo workflow
- Final user guidance
- Release and recovery acceptance criteria
- CI enforcement for final release files

## Expected Test Baseline
- Existing tests: 52
- New PVE-0.7 release tests: 6
- Expected total: 58

## Scope Boundary
No new analytical engine, supplier ranking, supplier allocation, autonomous technical approval, final integration contract, external system integration, or production deployment capability is included. The integration contract remains draft.

## Release Rule
Version `0.7.0-qa-interview-release` becomes completed only after all 58 tests pass, PVE CI succeeds, the release PR is reviewed and merged, and post-merge governance closure is recorded.
