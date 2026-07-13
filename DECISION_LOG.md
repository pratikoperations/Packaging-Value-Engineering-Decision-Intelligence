# Decision Log

## Existing Decisions
DEC-PVE-001 through DEC-PVE-029 remain in force, including separate repositories, GitHub as canonical record, deterministic logic, immutable evidence, project isolation, controlled thresholds, explicit scenario assumptions, and prohibition of autonomous approval.

## DEC-PVE-030 — Decision Snapshots Originate From Saved Scenarios
PVE-1.0.6 creates decision snapshots only from saved immutable scenarios and preserves exact project, scenario, dataset, and threshold-profile references.

## DEC-PVE-031 — Dataset-Defined Baseline Is Excluded
The baseline alternative is identified from the immutable dataset rather than a hard-coded identifier and cannot become the preferred recommendation.

## DEC-PVE-032 — Recommendation Status Means Review Readiness
Decision statuses communicate engineering-review readiness only. Engineering validation and human approval remain mandatory, and autonomous approval remains prohibited.

## DEC-PVE-033 — Decision History Is Project-Scoped and Read-Only
Decision history is limited to the selected project and exposes immutable recommendation, technical, risk, threshold, and mandatory-control evidence.

## DEC-PVE-034 — Archived Projects Retain History but Reject Writes
Archived projects may view existing decision history. `DecisionRepository` rejects creation of new decision snapshots after archival.

## DEC-PVE-035 — PVE-1.0.6 Final Scope
PVE-1.0.6 adds immutable decision snapshots, decision history, final interview guidance, QA, release checklist, and governance alignment. It does not add authentication, external databases, ERP integration, supplier ranking or allocation, autonomous approval, analytical-engine changes, recommendation-engine changes, or new packaging categories.

## DEC-PVE-036 — Final Release Budget
PVE-1.0.6 uses 17.0 hours. Cumulative PVE 1.0 effort is 89.5 hours, leaving 0.5 hours of the 90-hour program budget.

## DEC-PVE-037 — Final Review Gate
PR #22 remains draft until final branch-head CI, complete diff review, and governance alignment pass. Final closure occurs only after squash merge and source-branch deletion.