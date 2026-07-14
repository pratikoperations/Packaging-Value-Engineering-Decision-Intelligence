# PVE 1.2 Governance, Risk and Acceptance Controls

## Mandatory governance controls

- Engineering validation remains mandatory.
- Human approval remains mandatory.
- Autonomous approval is prohibited.
- Readiness percentage cannot become a technical or approval decision.
- Technical, safety, compliance, evidence, and line-compatibility blockers override commercial attractiveness.
- Commercial outputs must disclose missing inputs, limitations, and assumptions.
- Archived projects remain read-only.
- Project isolation remains enforced.
- Existing datasets, scenarios, thresholds, readiness assessments, and decision snapshots remain immutable.
- Future PVE 1.2 technical assessments must be append-only and immutable.

## Calculation classes

### Deterministic comparison

Direct comparison of supplied or governed values, such as laboratory-tested BCT against a project-defined BCT requirement.

### Deterministic formula

A transparent formula using explicit inputs, units, assumptions, and formula version, such as annual expected damage-cost scenario or annual pallet movements.

### Configuration-driven rule

A project or category rule with a traceable source and version, such as a mandatory line trial when a box style changes.

### Checklist

A structured compatibility or completeness check, such as supplier converting capability or artwork-change impact.

### Unavailable output

An output that cannot be responsibly calculated because a required input, governed coefficient, evidence item, or validation module is absent.

No class may silently convert supplier declarations, predictions, or assumptions into laboratory-tested facts.

## Threshold and override controls

- Thresholds must not be embedded as unexplained constants.
- Every threshold must retain source, version, applicability, and validation status.
- Project-specific overrides must identify the approving authority and reason.
- Overrides are append-only and must not rewrite historical assessments.
- An expired or inapplicable threshold cannot be used as valid decision evidence.
- Conflicting thresholds require explicit engineering resolution.

## Recommendation and approval controls

The engine may produce technical screening statuses and an engineering recommendation for review. It must not produce Approved, Rejected, or Conditional without explicit human decision input.

A positive engineering-review recommendation requires:

- no critical blocker;
- required evidence matched to the proposed specification;
- project-defined requirements met;
- source classifications preserved;
- assumptions and limitations visible;
- required laboratory, packing-line, and transport trials identified;
- technical and commercial outputs separated.

## Controlled contingency

The two-hour contingency requires an explicit recorded reason. Permitted reasons:

- unexpected regression caused by authorized Build 1 changes;
- CI-only failure requiring repository correction;
- migration compatibility repair in a later authorized build;
- cross-module integration defect;
- release-evidence reconciliation.

The contingency cannot be used for scope expansion.

## Principal risks and controls

### False technical authority — High

Risk: Screening appears to be engineering approval.

Control: Human-only approval statuses, explicit limitations, and mandatory engineering validation.

### Unsourced engineering thresholds — High

Risk: Universal constants create false precision.

Control: Sourced, versioned, applicable thresholds; unavailable output when governed inputs are absent.

### Evidence mismatch — High

Risk: Test evidence belongs to another supplier, site, structure, batch, or specification.

Control: Multi-field evidence matching and evidence-conflict blockers.

### Compression overclaim — High

Risk: Simplified ECT-to-BCT logic is represented as universally reliable.

Control: No advanced BCT prediction in PVE 1.2; compare supplied evidence with supplied requirements and require laboratory validation.

### Commercial override — High

Risk: Savings conceal technical or operational failure.

Control: Critical blockers override recommendation regardless of financial benefit.

### Pallet optimization overclaim — Medium

Risk: Simple orientations are presented as globally optimized patterns.

Control: Label as simple pattern comparison and permit engineering-validated manual patterns.

### Damage scenario misuse — Medium

Risk: Assumptions are interpreted as forecasts.

Control: Source classification, explicit assumptions, and scenario language in every output.

### Supplier-boundary drift — Medium

Risk: Capability checks become supplier rankings.

Control: Compatible, incompatible, or evidence missing only; no scoring, ranking, or allocation.

### Sustainability overclaim — Medium

Risk: Physical material indicators become unsupported carbon claims.

Control: Carbon remains unavailable without governed factor data.

### QA compression — Medium

Risk: Six-hour final QA becomes insufficient.

Control: Tests are written continuously in each build; contingency can cover regression or CI repair only.

## Build 1 acceptance criteria

- Architecture and scope documents exist.
- Release budget and contingency governance are explicit.
- Stable PVE 1.1 remains unchanged and governance-closed.
- README identifies current stable and active planning states accurately.
- No production technical code, formulas, migration, persistence table, or Build 2 schema exists.
- Complete existing tests pass.
- Current-head CI succeeds.
- Draft PR remains open and unmerged.
