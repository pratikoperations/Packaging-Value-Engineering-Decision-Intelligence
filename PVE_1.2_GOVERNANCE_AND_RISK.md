# PVE 1.2 Governance, Risk and Acceptance Controls

## Release status
PVE 1.2 Builds 1–8 are complete on draft PR #26.

- Completed effort: 74 of 74 planned hours.
- Completion: 100%.
- Pending planned work: 0 hours, 0%.
- Contingency used: 0 of 2 hours.
- Functional validation: PVE CI #849, run `29309701227`, 300 tests passed, 0 failures, 0 errors.
- Final documented-head CI is required before the PR record is updated for Build 8 closure.

## Mandatory governance controls
- Engineering validation remains mandatory.
- Explicit human approval remains mandatory.
- Autonomous approval is prohibited.
- Approved, Rejected, and Conditional are not generated automatically.
- Readiness percentage cannot become a technical or approval decision.
- Evidence confidence is not probability of technical success.
- Technical, safety, compliance, evidence, pallet, environment, and line-compatibility blockers override commercial attractiveness.
- Commercial outputs disclose inputs, limitations, assumptions, source classifications, and blocking conditions.
- Archived projects remain read-only.
- Cross-project references are rejected.
- Datasets, scenarios, thresholds, readiness assessments, decision snapshots, and technical assessments remain immutable.
- Technical assessments are append-only.

## Calculation and output classes

### Deterministic comparison
Direct comparison of supplied or governed values, such as laboratory-tested BCT against an explicit project requirement.

### Deterministic formula
A transparent formula using explicit inputs, units, assumptions, and source records, such as expected annual failure cost or annual pallet movements.

### Configuration-driven rule
A project or category rule with traceable source, applicability, version, and validation status.

### Checklist
A structured compatibility or completeness check, such as supplier capability, artwork change, or packing-line compatibility.

### Unavailable or blocked output
An output that cannot be responsibly calculated because a required input, governed factor, evidence item, or validation step is absent, or because a critical technical blocker remains unresolved.

No class may silently convert supplier declarations, predictions, assumptions, or synthetic demonstration data into laboratory-tested or production facts.

## Threshold and source controls
- Thresholds and factors are not embedded as unexplained constants.
- Every threshold or factor retains source, version, applicability, and validation status.
- Project-specific overrides identify authority and reason and remain append-only.
- Expired, superseded, mismatched, or invalid evidence cannot satisfy requirements.
- Source classifications remain distinct: uploaded fact, manually entered fact, supplier-declared value, laboratory-tested value, predicted value, and assumption.
- Synthetic demonstration records are explicitly labelled and cannot be represented as external fact.

## Recommendation and approval controls
A positive engineering-review recommendation requires:
- no critical blocker;
- matched mandatory evidence;
- project-defined requirements met;
- source classifications preserved;
- assumptions and limitations visible;
- required laboratory, packing-line, or transport trials identified;
- technical and commercial outputs separated.

A positive financial, material, pallet, logistics, or sustainability result does not authorize implementation.

## Persistence and isolation controls
- Schema version 4 is additive.
- Migration from schema versions 1, 2, and 3 is tested.
- Technical assessments reject update and delete through repository methods and database triggers.
- Existing immutable record families retain update/delete triggers.
- Archived-project writes are rejected.
- Dataset, readiness, threshold, evidence, and assessment references must belong to the same project unless a governed global threshold is explicitly permitted.
- Historical datasets, thresholds, scenarios, readiness assessments, and decision snapshots remain unchanged when technical assessments are created.

## Controlled contingency
The two-hour contingency remains unused. It may only cover:
- unexpected regression;
- CI-only failure;
- migration compatibility repair;
- cross-module integration defect;
- release-evidence reconciliation.

It cannot fund new functionality, additional categories, deployment, or scope expansion.

## Principal residual risks and controls

### False technical authority — High
Risk: Screening appears to be engineering approval.  
Control: Review-only outcomes, explicit limitations, human-only approval, and mandatory engineering validation.

### Unsourced engineering or commercial inputs — High
Risk: Hidden constants or inferred prices create false precision.  
Control: Explicit sourced inputs; unavailable output when required inputs are absent.

### Evidence mismatch — High
Risk: Evidence belongs to another supplier, site, structure, batch, or specification.  
Control: Multi-field evidence matching, validity checks, conflict detection, and cross-project isolation.

### Compression overclaim — High
Risk: Simplified prediction is represented as universally reliable.  
Control: No universal BCT prediction, McKee model, or hidden ECT-to-BCT conversion.

### Commercial override — High
Risk: Savings conceal technical or operational failure.  
Control: Technical and evidence blockers have higher precedence than every commercial or sustainability output.

### Pallet optimization overclaim — Medium
Risk: Two simple rectangular orientations are presented as global optimisation.  
Control: Outputs are labelled simple comparisons; mixed-SKU and 3D optimisation remain excluded.

### Damage and economic scenario misuse — Medium
Risk: Assumptions are interpreted as forecasts.  
Control: Source classifications, references, assumptions, and scenario language are retained.

### Supplier-boundary drift — Medium
Risk: Capability checks become supplier ranking.  
Control: Compatible, incompatible, or evidence missing only; no scoring, ranking, or allocation.

### Sustainability overclaim — Medium
Risk: Physical indicators become unsupported carbon claims.  
Control: Carbon remains unavailable without separately governed and authorized methodology.

### Synthetic-data misuse — Medium
Risk: Demonstration values are treated as real supplier or laboratory evidence.  
Control: Dataset-level and case-level synthetic labels, QA assertions, and documentation warnings.

## Build 8 acceptance evidence
- Eight governed synthetic cases exist and are uniquely identified.
- End-to-end intake-to-immutable-assessment regression passes.
- Migration from schema versions 1, 2, and 3 to version 4 passes.
- All immutable record families retain update/delete triggers.
- Archived-project protection and cross-project isolation pass.
- JSON and CSV-compatible normalization and Excel-template regression pass.
- Approved, Rejected, and Conditional are absent from automatic outcomes.
- Functional full suite passes with 300 tests and zero failures or errors.
- Release QA report, checklist, notes, status, build plan, README, architecture, and governance records are reconciled.

## Release control
Build 8 completion does not authorize marking PR #26 ready for review, merging, deployment, pilot, activation, or production use. PR #26 must remain draft and unmerged until separately authorized.
