# PVE-1.0.4 QA Report

## Build
PVE-1.0.4 — Configurable Business Thresholds

## Status
Draft PR validation pending

## Objective
Add immutable configurable business threshold profiles without weakening engineering validation, technical qualification, risk blocks, evidence controls, or human approval.

## Implemented Capability
- Controlled global default threshold profile
- Project-specific threshold profiles
- Immutable profile versioning
- Duplicate-content suppression
- Profile validation
- Active threshold profile selection
- Threshold template
- Business screening helper
- Non-disableable engineering control display

## Configurable Fields
- `minimum_annual_savings`
- `minimum_material_reduction_percent`
- `maximum_business_risk`
- `require_positive_savings_or_material_reduction`

## Mandatory Controls
- Engineering validation required
- Autonomous approval prohibited
- Critical risk blocked
- Not-qualified alternatives blocked
- Insufficient data cannot be recommended

These controls are constants outside the editable profile schema.

## Expected Test Baseline
- Previous total: 126
- New threshold tests: 17
- Expected total: 143

## Budget
- Program budget before build: 47.5 hours
- Planned allocation: 13 hours
- Estimated effort used: 12.5 hours
- Estimated remaining program budget: 35.0 hours

## Preserved Controls
- Existing `app.py`
- Project dashboard and upload workflow
- Persistence schema
- Analytical and recommendation engines
- Engineering-validation requirement
- Synthetic-data and non-production disclaimers
- Draft integration contract
- AI Procurement Copilot separation

## Explicit Exclusions
No scenario execution, recommendation-engine modification, decision-history UI, authentication, external database, supplier workflow, ERP integration, AI approval, or new packaging category.

## CI Evidence
To be completed after the final branch-head CI run.

## QA Result
Pending CI and complete diff review.

## Merge Rule
Keep the pull request as draft. Do not merge automatically.
