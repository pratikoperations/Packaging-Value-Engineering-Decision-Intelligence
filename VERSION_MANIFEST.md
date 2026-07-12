# Version Manifest

## Current Version
- Project version: `0.7.0-qa-interview-release`
- Build: `PVE-0.7`
- Status: `0.7.0-qa-interview-release ready`
- Stable branch: `main`
- Working branch: `agent/pve-0.7-qa-interview-release`
- Base commit: `1b3a6f0250f3645df08e908b3be30d75b99294e7`

## Validation Evidence
- Workflow: PVE CI
- Run number: 256
- Run ID: `29184311901`
- Validated commit: `9e42a605598f364604ec6b418ee0b2a0c37f747f`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 58 run, 58 passed, 0 failed, 0 errors

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

## Final Test Baseline
- Existing tests: 52
- New PVE-0.7 release tests: 6
- Total: 58

## Scope Boundary
No new analytical engine, supplier ranking, supplier allocation, autonomous technical approval, final integration contract, external system integration, or production deployment capability is included. The integration contract remains draft.

## Release Rule
Version `0.7.0-qa-interview-release` becomes completed only after the final QA commit passes PVE CI, PR #13 is reviewed and merged, and post-merge governance closure is recorded.
