# PVE-0.2 QA Report

## Build
PVE-0.2 — Data Model and Demo Data

## Scope
Canonical field dictionary, synthetic corrugated shipping-case data, invalid-data fixtures, deterministic validation, automated tests, and CI expansion.

## Acceptance Criteria
- All committed demo data is explicitly synthetic
- One baseline and at least three alternatives exist
- Every field defines a unit or unitless state
- No hidden defaults are allowed
- Required, numeric, unit, enum, currency, ID, evidence, dimension, weight, percentage, and reference validation exists
- Partial technical data can trigger insufficient-data eligibility
- Data model aligns with the draft PVE integration contract
- No UI, cost calculation, savings calculation, or recommendation scoring is introduced

## Implemented Checks
- Required-field validation
- Positive and non-negative numeric validation
- Supported units and currency consistency
- Allowed status and category values
- Duplicate identifiers
- Cross-record references
- Evidence references
- Dimensions, weights, and percentages
- Exact baseline count
- Synthetic dataset labelling
- Draft integration-contract marker
- Insufficient-data eligibility

## Automated Tests
Ten standard-library `unittest` cases cover:
1. Valid complete dataset
2. Missing mandatory field
3. Negative value
4. Duplicate ID
5. Unsupported unit
6. Invalid enum value
7. Missing evidence
8. Invalid percentage
9. Partial dataset and insufficient-data eligibility
10. Currency consistency

## CI
PVE CI validates mandatory files, JSON syntax, synthetic labelling, build identity, draft-contract status, and all tests.

## Known Limitations
- Cost values are inputs only; no cost calculation is performed
- Material weights are inputs only; no optimization calculation is performed
- Recommendation is a non-scored placeholder
- Technical results are synthetic and incomplete by design
- No UI, database, API, or production-data integration exists
- Contract remains draft until PVE-0.6

## QA Status
**Conditional Pass** — implementation is complete; final status depends on complete diff inspection and successful CI on the final branch commit.

## Release Recommendation
Open a draft PR after final verification. PVE-0.3 begins only after PVE-0.2 passes QA and is merged.
