# Final Release Checklist

## Release Candidate
PVE-0.7 — QA and Interview Release

## Acceptance Criteria

### Repository and governance
- [x] `main` remains the stable branch.
- [x] PVE-0.1 through PVE-0.6 are recorded as completed and merged.
- [x] PVE-0.7 scope is limited to QA, documentation, interview demonstration, recovery, and release hardening.
- [x] Integration contract remains draft.
- [x] AI Procurement Copilot source code is absent.

### Functional flow
- [x] Synthetic demo data passes canonical validation.
- [x] Cost and material engines produce results for every alternative.
- [x] Technical qualification covers every alternative.
- [x] Quality, supply, and implementation risk are surfaced.
- [x] Scenario assumptions are explicit.
- [x] Recommendation rationale, constraints, and validation requirements are visible.
- [x] JSON and Markdown decision-package exports validate and render.

### UI smoke validation
- [x] Application imports are syntactically valid through the automated release suite.
- [x] Scenario input controls are present.
- [x] Comparison and preferred-alternative sections are present.
- [x] Recommendation rationale and validation sections are present.
- [x] JSON and Markdown download controls are present.
- [x] Engineering-approval disclaimer is present.

### Automated QA
- [x] All historical automated tests pass.
- [x] PVE-0.7 end-to-end release tests pass.
- [x] PVE CI reports zero failures and zero errors.
- [x] Full PR diff contains no new analytical engine or product-scope expansion.

### Interview readiness
- [x] README contains setup, execution, architecture, scope, and limitations.
- [x] Interview demo guide is complete.
- [x] Demo workflow is designed for 8–12 minutes.
- [x] Synthetic-data status is disclosed.
- [x] Business value and production limitations are explained.

### Recovery readiness
- [x] Recovery manifest lists current files in the correct reading order.
- [x] Test and application commands are documented.
- [x] Stable base commit, validated CI, validated commit, and release status are recorded before final merge.

## Validated Release Evidence
- Workflow: PVE CI
- Run number: 256
- Run ID: `29184311901`
- Validated commit: `9e42a605598f364604ec6b418ee0b2a0c37f747f`
- Tests: 58 passed, 0 failed, 0 errors
- Full diff review: Pass
- QA status: Pass

## Remaining Release Actions
- [ ] Final QA commit passes PVE CI.
- [ ] PR #13 is reviewed and merged.
- [ ] Post-merge governance closure is recorded.

## Release Gate
PVE-0.7 is ready for review after the final QA commit passes PVE CI. It becomes completed only after PR #13 is merged and post-merge governance closure is recorded.
