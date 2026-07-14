# PVE 1.1 Commercial and ROI Logic

## Purpose

Build 7 provides common, deterministic commercial opportunity calculations across all eight packaging categories. These calculations support business screening only and do not override readiness blockers, engineering validation, compliance requirements, or human approval.

## Calculations

- Saving per unit = current unit cost − proposed unit cost
- Annual gross saving = saving per unit × annual volume
- Expected realized saving = annual gross saving × realization percentage
- First-year net benefit = expected realized saving − testing cost − tooling cost − implementation cost − qualification cost
- Payback period in months = total implementation investment ÷ monthly realized saving
- Material reduction per unit = current material weight − proposed material weight
- Annual material reduction = material reduction per unit × annual volume
- Percentage cost reduction = saving per unit ÷ current unit cost × 100
- Percentage material reduction = material reduction per unit ÷ current material weight × 100

## Validation

- Monetary, volume, investment, and material-weight inputs must be non-negative.
- Realization percentage must be between 0 and 100.
- Current and proposed material weights must be provided together.
- Payback is unavailable when monthly realized saving is not positive.
- Cost and material percentages use zero when the corresponding current baseline is zero.

## Estimates and assumptions

Every result includes explicit estimate labels. User-supplied assumptions are retained with the result. No hidden realization, volume, cost, engineering, or technical-performance assumption is introduced.

## Governance

- Commercial attractiveness never removes a readiness blocker.
- Technical and compliance evidence remain mandatory where applicable.
- Supplier-declared, predicted, and assumed values retain their source classification.
- These calculations do not approve, reject, or conditionally approve a packaging design.
