# PVE 1.1 Release Checklist

## Functional acceptance
- [x] Eight packaging categories support project creation.
- [x] Objectives and category-specific change types are available.
- [x] Category input and document guidance is configuration-driven.
- [x] Eight category-specific Excel templates are generated.
- [x] Excel uploads are parsed, normalized, and validated.
- [x] Missing mandatory values and blocking issues are shown.
- [x] Transparent readiness percentage and stage are produced.
- [x] Available and unavailable outputs include reasons.
- [x] Commercial savings, ROI, payback, and material reduction are supported.
- [x] Category testing checklists are generated.
- [x] JSON and Markdown executive summaries are available.

## Governance acceptance
- [x] Source classification is retained.
- [x] Supplier-declared and predicted values are not presented as tested.
- [x] Engineering validation remains mandatory.
- [x] Human approval remains mandatory.
- [x] Percentage readiness cannot approve a project.
- [x] Critical blockers override commercial attractiveness and percentage scores.
- [x] Archived projects remain read-only.
- [x] Dataset versions and historical decision snapshots remain immutable.
- [x] Project isolation remains enforced.

## QA acceptance
- [x] One synthetic sample exists for each category.
- [x] Three detailed release cases exist.
- [x] New release QA tests are included.
- [ ] Final Build 9 CI succeeds with zero failures and zero errors.
- [ ] PR #25 receives separate merge authorization.

## Release state
Build 9 may be marked complete only after final-head CI passes. Completion does not authorize deployment, pilot, production use, or merge.
