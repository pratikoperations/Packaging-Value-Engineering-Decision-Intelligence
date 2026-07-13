# PVE 1.0 Final Release Checklist

## Functional Acceptance
- [x] Multi-project dashboard works with explicit active selection
- [x] Archived projects remain read-only
- [x] JSON and limited CSV uploads normalize canonically
- [x] Invalid and duplicate uploads are rejected
- [x] Dataset and threshold versions remain immutable
- [x] Controlled scenarios bind exact dataset and threshold versions
- [x] Scenario assumptions remain explicit and bounded
- [x] Existing deterministic engines remain authoritative
- [x] Scenario records remain immutable
- [x] Decision snapshots preserve exact project, scenario, dataset, and threshold references
- [x] Dataset-defined baseline is excluded from preferred recommendations
- [x] Decision history is project-scoped and read-only
- [x] Archived projects cannot create new snapshots at repository level
- [x] History created before archival remains readable
- [x] Decision snapshots remain immutable

## Control Acceptance
- [x] Engineering validation remains mandatory
- [x] Human approval remains mandatory
- [x] Autonomous approval is prohibited
- [x] Critical risk remains blocking
- [x] Not-qualified alternatives remain blocked
- [x] Insufficient data cannot become recommended
- [x] Business thresholds cannot override engineering controls
- [x] Project isolation remains enforced

## Scope Acceptance
- [x] No authentication
- [x] No external database claim
- [x] No ERP integration
- [x] No supplier ranking or allocation
- [x] No autonomous packaging approval
- [x] No analytical-engine modification
- [x] No recommendation-engine modification
- [x] No new packaging category
- [x] AI Procurement Copilot remains separate
- [x] Integration contract remains draft

## Quality Acceptance
- [x] Full automated suite passes — 179 passed, 0 failed, 0 errors
- [x] Final CI passes — PVE CI #507, run ID `29221779591`
- [x] Governance records identify PVE-1.0.6 correctly
- [x] Final interview guide is current
- [x] Final QA report is current
- [ ] Complete changed-file review passes
- [ ] PR #22 is squash merged
- [ ] Source branch is deleted after merge
- [ ] Post-merge governance closure is completed

## Budget Acceptance
- [x] PVE-1.0.5 effort: 17.5 hours
- [x] PVE-1.0.6 actual effort: 17.0 hours
- [x] Cumulative effort: 89.5 hours
- [x] Remaining program budget: 0.5 hours

## Release Boundary
PVE 1.0 records explainable decision-support evidence and recommendation-for-review statuses. It does not grant engineering approval, commercial authorization, supplier allocation, or autonomous approval.