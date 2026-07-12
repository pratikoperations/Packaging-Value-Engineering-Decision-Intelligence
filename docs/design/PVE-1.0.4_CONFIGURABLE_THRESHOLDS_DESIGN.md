# PVE-1.0.4 Configurable Business Thresholds Design

## Objective
Add versioned commercial screening thresholds while preserving non-disableable engineering qualification, risk, evidence, and human-approval controls.

## Configurable Business Fields
- Minimum annual savings
- Minimum material reduction percent
- Maximum acceptable business risk
- Require positive savings or material reduction

## Mandatory Controls
These controls are not part of the editable profile:
- Engineering validation remains required
- Autonomous approval remains prohibited
- Critical risk remains blocking
- Not-qualified alternatives remain blocked
- Insufficient data cannot become recommended

## Profile Types
- Controlled global default: read-only, available to all projects
- Project-specific profile: immutable versioned record

## Workflow

```text
Active Project
    ↓
Load Controlled Default + Project Profiles
    ↓
Select Active Threshold Profile
    ↓
Create Project-Specific Version
    ↓
Validate Business Fields
    ↓
Store Immutable Threshold Version
```

## Versioning
Threshold profiles are append-only. Editing creates a new version under the same project and profile name. Identical content returns the existing version rather than creating duplicate history.

## Application Boundary
The Streamlit page uses `ThresholdService`, which uses `ThresholdRepository`. No page-level SQL is allowed.

## Scope Exclusions
No scenario execution, recommendation-engine modification, decision-history UI, authentication, external database, supplier workflow, ERP integration, AI approval, or new packaging category.
