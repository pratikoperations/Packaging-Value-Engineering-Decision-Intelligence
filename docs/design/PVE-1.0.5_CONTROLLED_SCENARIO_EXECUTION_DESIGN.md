# PVE-1.0.5 Controlled Scenario Execution Design

## Objective
Connect immutable dataset and threshold-profile versions to the existing deterministic scenario, technical-qualification, and risk engines, then save an immutable scenario evidence record.

## Workflow

```text
Active Project
  → Select Project Dataset Version
  → Select Global or Project Threshold Version
  → Enter Explicit Bounded Assumptions
  → Run Existing Deterministic Scenario Engine
  → Evaluate Technical Qualification and Risk
  → Evaluate Explainable Business Thresholds
  → Apply Mandatory Engineering Controls
  → Review Alternative-Level Results
  → Save Immutable Scenario Record
```

## Controlled Assumptions
- Annual volume must be greater than zero.
- Unit-cost adjustment is explicit by alternative and bounded from -50% to +100%.
- Material-weight adjustment is explicit by alternative and bounded from -50% to +100%.
- No forecasting, optimization, hidden defaults, probability weighting, or AI-generated assumptions are used.

## Version Binding
Every saved scenario references:
- one immutable project dataset version
- one immutable threshold-profile version
- the active project
- explicit scenario assumptions
- deterministic results

The service and repository both prevent cross-project dataset or threshold use. Global controlled thresholds remain valid for every project.

## Mandatory Control Outcomes
Alternative results use controlled statuses:
- `blocked`
- `insufficient_data`
- `business_threshold_failed`
- `conditionally_eligible_for_review`
- `eligible_for_engineering_review`

None of these statuses is an autonomous approval. Engineering validation and human approval remain mandatory.

## Explainability
Each alternative records:
- cost and material results
- technical status and reasons
- technical validation activities
- risk level, completeness, and reasons
- business-threshold pass/fail and reasons
- mandatory-control status and reasons
- engineering-validation requirement
- autonomous-approval prohibition

## Persistence
Scenario records are append-only under the existing PVE-1.0.1 SQLite trigger controls. This build does not create decision snapshots or decision-history UI.

## Scope Exclusions
- Decision snapshots and decision history
- Recommendation-engine modification
- Autonomous approval
- Supplier ranking or allocation
- Authentication
- External database
- ERP integration
- New packaging category
