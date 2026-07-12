# PVE 1.0 Final Release Checklist

## Functional Acceptance
- [ ] Multi-project dashboard works with explicit active selection
- [ ] Archived projects remain read-only
- [ ] JSON and limited CSV uploads normalize canonically
- [ ] Invalid and duplicate uploads are rejected
- [ ] Dataset versions are immutable
- [ ] Controlled default and project threshold profiles are available
- [ ] Threshold profiles are immutable and project-scoped
- [ ] Controlled scenarios bind exact dataset and threshold versions
- [ ] Scenario assumptions are explicit and bounded
- [ ] Existing deterministic engines remain authoritative
- [ ] Scenario records are immutable
- [ ] Decision snapshots preserve exact project, dataset, threshold, and scenario references
- [ ] Decision history is project-scoped and read-only
- [ ] Decision snapshots are immutable

## Control Acceptance
- [ ] Engineering validation remains mandatory
- [ ] No autonomous approval is allowed
- [ ] Critical risk remains blocking
- [ ] Not-qualified alternatives remain blocked
- [ ] Insufficient technical or risk data cannot become eligible
- [ ] Business thresholds cannot override engineering controls
- [ ] Baseline alternatives cannot become preferred recommendations
- [ ] Archived projects cannot create new evidence records

## Scope Acceptance
- [ ] No authentication
- [ ] No external database claim
- [ ] No ERP integration
- [ ] No supplier ranking or allocation
- [ ] No autonomous packaging approval
- [ ] No new packaging category
- [ ] AI Procurement Copilot remains separate
- [ ] Integration contract remains draft

## Quality Acceptance
- [ ] Full automated test suite passes
- [ ] CI passes on final branch head
- [ ] Complete changed-file review passes
- [ ] No unresolved review threads
- [ ] Governance files identify PVE-1.0.6 and final closure correctly
- [ ] Interview demonstration guide is current
- [ ] Source branch is deleted after squash merge

## Release Boundary
PVE 1.0 is a portfolio-quality decision-support system. It records evidence and recommendation-for-review statuses, but it does not grant engineering approval, commercial authorization, or supplier allocation.
