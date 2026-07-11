# Build History

## PVE-0.1 — Repository Foundation
**Status:** Completed and merged

- Stable closure merge commit: `d4672eadc23f23ba5528a44ff91fba649e6eff68`
- Foundation QA: Pass

## PVE-0.2 — Data Model and Demo Data
**Status:** Implementation complete — final QA pending

### Objective
Create a canonical, explicit, testable data foundation for packaging value engineering before implementing calculation or recommendation engines.

### Completed Scope
- Fourteen canonical entity groups
- Explicit field dictionary with units, allowed values, default rules, validation rules, and evidence requirements
- Synthetic corrugated shipping-case dataset with one baseline and three alternatives
- Synthetic cost, logistics, technical, risk, sustainability, validation, evidence, and export records
- Invalid and partial-data fixtures
- Standard-library Python validation module
- Automated validation tests
- CI validation for JSON syntax, synthetic labelling, mandatory files, and tests

### Scope Exclusions
- Cost and material calculations
- Savings calculations
- Recommendation scoring
- Application UI
- Supplier ranking or allocation
- Autonomous technical approval

### Exit Criteria
- Valid demo dataset passes validation
- Required negative tests pass
- All demo data is explicitly synthetic
- Every schema field declares a unit or unitless state
- No hidden defaults exist
- Full diff is reviewed
- CI passes
- QA report is finalized
- Draft PR is opened

### Next Build
PVE-0.3 — Cost and Material Engine, only after PVE-0.2 is merged into `main`.
