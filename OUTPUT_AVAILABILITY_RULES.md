# PVE 1.1 Output Availability Rules

## Always available

- Document completeness status
- Category-specific test requirement checklist

These outputs describe recorded intake information only.

## Conditionally available

### Commercial analysis

Available when annual volume, current unit cost, and proposed unit cost are present and valid. Missing inputs are returned as explicit reasons rather than replaced by hidden assumptions.

## Unavailable in PVE 1.1

### Final technical feasibility

Unavailable because PVE 1.1 provides intake and validation readiness, not complete engineering calculation or validation across all categories. Blockers and missing technical evidence are reported as reasons.

### Approval decision

Unavailable because engineering validation and human approval remain mandatory. Readiness percentage cannot approve, reject, or conditionally approve a project.

## Rule behavior

Each output contains:

- output name
- availability flag
- one or more reasons when unavailable

Blocking issues override readiness stages but do not suppress useful non-technical outputs such as document completeness and testing checklists.

## Governance

Commercial attractiveness never overrides technical or compliance blockers. Supplier-declared, predicted, and assumed values retain their source classification and are not represented as laboratory-tested or verified facts.
