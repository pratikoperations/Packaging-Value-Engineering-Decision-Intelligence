# Final Release Checklist

## Release Candidate
PVE-0.7 — QA and Interview Release

## Acceptance Criteria

### Repository and governance
- [ ] `main` remains the stable branch.
- [ ] PVE-0.1 through PVE-0.6 are recorded as completed and merged.
- [ ] PVE-0.7 scope is limited to QA, documentation, interview demonstration, recovery, and release hardening.
- [ ] Integration contract remains draft.
- [ ] AI Procurement Copilot source code is absent.

### Functional flow
- [ ] Synthetic demo data passes canonical validation.
- [ ] Cost and material engines produce results for every alternative.
- [ ] Technical qualification covers every alternative.
- [ ] Quality, supply, and implementation risk are surfaced.
- [ ] Scenario assumptions are explicit.
- [ ] Recommendation rationale, constraints, and validation requirements are visible.
- [ ] JSON and Markdown decision-package exports validate and render.

### UI smoke validation
- [ ] Application imports are syntactically valid.
- [ ] Scenario input controls are present.
- [ ] Comparison and preferred-alternative sections are present.
- [ ] Recommendation rationale and validation sections are present.
- [ ] JSON and Markdown download controls are present.
- [ ] Engineering-approval disclaimer is present.

### Automated QA
- [ ] All historical automated tests pass.
- [ ] PVE-0.7 end-to-end release tests pass.
- [ ] PVE CI reports zero failures and zero errors.
- [ ] Full PR diff contains no new analytical engine or product-scope expansion.

### Interview readiness
- [ ] README contains setup, execution, architecture, scope, and limitations.
- [ ] Interview demo guide is complete.
- [ ] Demo can be delivered in 8–12 minutes.
- [ ] Synthetic-data status is disclosed.
- [ ] Business value and production limitations are explained.

### Recovery readiness
- [ ] Recovery manifest lists current files in the correct reading order.
- [ ] Test and application commands are documented.
- [ ] Stable commit, validated CI, and release status are recorded before final merge.

## Release Gate
PVE-0.7 may be marked ready for review only when all automated tests and PVE CI pass. It may be marked completed only after the release PR is merged and governance closure is recorded.
