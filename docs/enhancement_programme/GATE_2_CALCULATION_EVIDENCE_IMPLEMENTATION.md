# Gate 2 Independent Calculation Evidence Implementation

## Status

Implementation candidate. Exact-head CI and governed acceptance remain required.

## Baseline

- Programme branch: `enhancement/browser-data-calculation-programme`
- Required programme SHA: `97df0c7bfb2696958ccf3df1ac78087012d465cc`
- Feature branch: `enhancement/independent-calculation-evidence`
- Frozen showcase branch: `showcase-handoff-development`
- Required frozen SHA: `2954c293ca09882cadd7f23b5862f50334170a11`

## Scope implemented

- exactly 16 independently implemented numeric formula contracts;
- six separately classified rule-lineage records;
- independently owned formula, tolerance and assumption registries;
- Decimal conversion through `Decimal(str(raw_value))`;
- explicit `ROUND_HALF_EVEN` output quantization;
- combined absolute and relative tolerance policies;
- reconciliation states `matched`, `matched_within_tolerance`, `mismatch`, `insufficient_evidence` and `unsupported`;
- INR-only currency support;
- zero-denominator, sign, range, missing-input, non-finite and unsupported-currency controls;
- stable assumption IDs for the 25 g adhesive-and-ink split and 650 km synthetic freight distance;
- independent fixtures, mutation detection and static dependency-boundary tests;
- Calculation Evidence route integration;
- additive JSON and Markdown decision-package evidence sections.

## Independence boundary

The independent evidence modules do not import or execute:

- `src.cost_engine`;
- `src.material_engine`;
- `src.scenario_engine`;
- `src.technical_qualification`;
- `src.risk_engine`;
- `src.recommendation`.

Primary outputs enter only through the reconciliation boundary after independent arithmetic completes.

## Primary engines preserved

Gate 2 does not modify:

- `src/cost_engine/engine.py`;
- `src/material_engine/engine.py`;
- `src/scenario_engine/engine.py`;
- `src/technical_qualification/engine.py`;
- `src/risk_engine/engine.py`;
- `src/recommendation/engine.py`;
- `src/synthetic_data/compatibility_adapter.py`.

## Calculation catalogue

### Cost

- `CALC-COST-001` unit-cost aggregation;
- `CALC-COST-002` annual cost;
- `CALC-COST-003` unit savings versus baseline;
- `CALC-COST-004` annual savings versus baseline;
- `CALC-COST-005` cost variance percentage.

### Material

- `CALC-MAT-001` component-weight aggregation;
- `CALC-MAT-002` component variance;
- `CALC-MAT-003` annual material;
- `CALC-MAT-004` material change versus baseline;
- `CALC-MAT-005` material variance percentage.

### Scenario

- `CALC-SCN-001` adjustment factor;
- `CALC-SCN-002` adjusted cost input;
- `CALC-SCN-003` adjusted case weight;
- `CALC-SCN-004` adjusted component weight.

### Compatibility assumptions

- `CALC-ADP-001` board component derivation;
- `CALC-ADP-002` component reconciliation.

## Rule lineage

- `RULE-RISK-001` probability-to-risk band;
- `RULE-RISK-002` declared-versus-probability severity;
- `RULE-RISK-003` overall risk maximum;
- `RULE-QUAL-001` qualification-status precedence;
- `RULE-REC-001` recommendation gate;
- `RULE-REC-002` preferred-alternative ordering.

These records describe decision paths. They are not represented as Decimal financial formulas.

## Evidence limitations

- Synthetic demonstration data only.
- Arithmetic matching is not supplier, engineering, regulatory, production or realized-savings validation.
- Missing primary intermediate outputs remain `insufficient_evidence`; the independent engine does not fabricate primary values.
- Live foreign-exchange conversion is unsupported.
- The evidence section supplements rather than replaces primary decision-package results.

## Effort control

- Gate 0 actual: 6 hours.
- Gate 1 actual: 18 hours.
- Cumulative before Gate 2: 24 hours.
- Gate 2 authorized forecast: 32 hours.
- Forecast cumulative: 56 hours.
- Gate 2 ceiling: 68 hours.
- Actual Gate 2 effort: pending confirmation after CI and correction closure.

## Acceptance required

- exact-head workflow success;
- focused Gate 2 tests pass;
- complete repository regression passes;
- mutation tests pass;
- independence-boundary tests pass;
- artifact ID and digest recorded;
- draft PR remains unmerged until separate disposition authorization.
