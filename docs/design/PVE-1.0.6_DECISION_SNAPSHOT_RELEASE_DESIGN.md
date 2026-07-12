# PVE-1.0.6 Decision Snapshot and Final Release Design

## Objective
Complete PVE 1.0 by converting a saved controlled scenario into an immutable, explainable decision snapshot and exposing project-scoped read-only decision history.

## Workflow

```text
Active Project
  → Select Saved Immutable Scenario
  → Reuse Exact Dataset and Threshold References
  → Rank Proposed Alternatives Deterministically
  → Apply Scenario Control Status
  → Record Recommendation-for-Review Status
  → Preserve Technical, Risk, Threshold, and Control Evidence
  → Save Immutable Decision Snapshot
  → Review Project-Scoped Decision History
```

## Recommendation Statuses
- `recommended_for_engineering_review`
- `conditionally_recommended_for_engineering_review`
- `not_recommended_business_threshold_failed`
- `insufficient_data`
- `blocked`

These statuses are decision-support classifications only. None represents engineering approval, commercial authorization, supplier allocation, or autonomous approval.

## Deterministic Selection
Only proposed alternatives are considered. Alternatives are ranked by:
1. controlled scenario status
2. annual savings versus baseline
3. material reduction
4. stable alternative identifier

Baseline records cannot become the preferred alternative.

## Exact Reference Preservation
Every snapshot preserves:
- project ID
- scenario ID
- dataset version ID
- threshold-profile version ID
- preferred alternative, when eligible
- engine version and source marker
- recommendation evidence
- technical, risk, threshold, and mandatory-control evidence

The existing repository layer revalidates project, scenario, dataset, and threshold consistency before insertion.

## Decision History
History is:
- project-scoped
- read-only
- available for archived projects
- backed by immutable snapshot records
- explainable at recommendation and gate-result level

Archived projects cannot create new snapshots.

## Scope Exclusions
- autonomous approval
- supplier ranking or allocation
- authentication
- external database
- ERP integration
- recommendation-engine modification
- new packaging categories
