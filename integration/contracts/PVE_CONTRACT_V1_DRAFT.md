# PVE Contract v1.0 — Draft

## Purpose
Define the read-only decision package exported by PVE and consumed by AI Procurement Copilot.

## Planned Package
`pve_decision_package.json`

## Mandatory Metadata
- `contract_version`
- `source_repository`
- `source_commit`
- `generated_at`
- `project_id`
- `packaging_category`

## Baseline and Alternatives
- `baseline_specification`
- `alternatives`
- `annual_volume`
- `currency`
- `units`

## Decision Outputs
- `technical_status`
- `target_unit_cost`
- `gross_annual_savings`
- `risk_adjusted_savings`
- `confidence_score`
- `data_gaps`
- `risks`
- `validation_requirements`
- `implementation_constraints`
- `recommended_option`

## Status Values
- `recommended`
- `conditionally_recommended`
- `not_recommended`
- `insufficient_data`

## Ownership Rule
PVE owns the exported technical-commercial decision. Procurement Copilot consumes but does not edit the source package.

## Freeze Rule
This draft becomes `PVE-CONTRACT-v1.0` only after PVE-0.6 compatibility tests pass.
