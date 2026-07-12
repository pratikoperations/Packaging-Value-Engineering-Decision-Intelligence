# Build History

## PVE-0.1 — Repository Foundation
**Status:** Completed and merged

- Stable closure merge commit: `d4672eadc23f23ba5528a44ff91fba649e6eff68`
- Foundation QA: Pass

## PVE-0.2 — Data Model and Demo Data
**Status:** Ready for review and merge

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

### Validated CI Evidence
- Workflow: PVE CI
- Run number: 58
- Run ID: `29180838040`
- Validated commit: `436820a54ff066b2c2265403bda628c78107962d`
- Job: `validate-repository`
- Conclusion: success
- Tests: 10 run, 10 passed, 0 failed, 0 errors

### Scope Exclusions
- Cost and material calculations
- Savings calculations
- Recommendation scoring
- Application UI
- Supplier ranking or allocation
- Autonomous technical approval
- Final integration contract; it remains draft

### Exit Criteria Result
- Valid demo dataset passes validation: Pass
- Required negative tests pass: Pass
- All demo data is explicitly synthetic: Pass
- Every schema field declares a unit or unitless state: Pass
- No hidden defaults exist: Pass
- Full diff reviewed: Pass
- CI passes: Pass
- QA report finalized: Pass
- Draft PR opened: Pass

### Next Build
PVE-0.3 — Cost and Material Engine, only after PVE-0.2 is merged into `main`.
