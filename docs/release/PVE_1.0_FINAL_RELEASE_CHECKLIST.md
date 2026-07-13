# PVE 1.0 Final Release Checklist

## Functional Acceptance
- [x] Multi-project dashboard works with explicit active selection
- [x] Archived projects remain read-only
- [x] JSON and limited CSV uploads normalize canonically
- [x] Invalid and duplicate uploads are rejected
- [x] Dataset versions are immutable
- [x] Controlled default and project threshold profiles are available
- [x] Threshold profiles are immutable and project-scoped
- [x] Controlled scenarios bind exact dataset and threshold versions
- [x] Scenario assumptions are explicit and bounded
- [x] Existing deterministic engines remain authoritative
- [x] Scenario records are immutable
- [x] Decision snapshots preserve exact project, dataset, threshold, and scenario references
- [x] Decision history is project-scoped and read-only
- [x] Decision snapshots are immutable

## Control Acceptance
- [x] Engineering validation remains mandatory
- [x] No autonomous approval is allowed
- [x] Critical risk remains blocking
- [x] Not-qualified alternatives remain blocked
- [x] Insufficient technical or risk data cannot become eligible
- [x] Business thresholds cannot override engineering controls
- [x] Baseline alternatives cannot become preferred recommendations
- [x] Archived projects cannot create new evidence records

## Scope Acceptance
- [x] No authentication
- [x] No external database claim
- [x] No ERP integration
- [x] No supplier ranking or allocation
- [x] No autonomous packaging approval
- [x] No new packaging category
- [x] AI Procurement Copilot remains separate
- [x] Integration contract remains draft

## Quality Acceptance
- [x] Full automated test suite passes — 177 passed, 0 failed, 0 errors
- [x] Corrective CI passes — PVE CI #483, run ID `29220919849`
- [x] Final implementation-and-evidence CI passes — PVE CI #499, run ID `29221086243`
- [ ] Complete changed-file review passes
- [x] No unresolved review threads at validation
- [x] Governance files identify PVE-1.0.6 and final closure correctly
- [x] Interview demonstration guide is current
- [ ] Source branch is deleted after squash merge

## Repair Evidence
- Initial failure: PVE CI #479, run ID `29202005257`
- Root cause: incomplete constructor wiring after adding dataset-aware baseline protection to `DecisionSnapshotService`
- Corrective files: `src/application/runtime.py` and `tests/decision_snapshots/test_decision_snapshots.py`
- Safeguards preserved: dataset-defined baseline exclusion, project isolation, repository revalidation, immutability, engineering validation, and non-autonomous approval

## Release Boundary
PVE 1.0 is a portfolio-quality decision-support system. It records evidence and recommendation-for-review statuses, but it does not grant engineering approval, commercial authorization, or supplier allocation.
