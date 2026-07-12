# Build History

## PVE-0.1 — Repository Foundation
**Status:** Completed and merged

- Stable closure merge commit: `d4672eadc23f23ba5528a44ff91fba649e6eff68`
- Foundation QA: Pass

## PVE-0.2 — Data Model and Demo Data
**Status:** Completed and merged

- Merge commit: `33b4319c3b74d8caaad6bc03cb85cb6ebf1727ff`
- Closure merge commit: `6a6f5d080f906f3a6b01b73cd04465db7da356ef`
- QA: Pass
- Tests: 10 passed, 0 failed, 0 errors

## PVE-0.3 — Cost and Material Engine
**Status:** Ready for review and merge

### Objective
Create deterministic, transparent cost and material calculations using the canonical PVE-0.2 dataset.

### Completed Scope
- Material-component aggregation by alternative
- Component-to-case weight variance
- Annual material mass calculation
- Material change in grams and percentage versus baseline
- Unit-cost aggregation by alternative
- Annual cost calculation
- Unit and annual savings versus baseline
- Cost change percentage versus baseline
- Input guards for baseline, identifiers, units, currencies, volumes, weights, and missing records
- Eight new automated tests

### Validated CI Evidence
- Workflow: PVE CI
- Run number: 98
- Run ID: `29181336986`
- Validated commit: `da769f756cd6a5edfd38e61fc8176642c51c41d9`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 18 run, 18 passed, 0 failed, 0 errors

### Scope Exclusions
- Application UI
- Technical qualification and risk
- Logistics optimization
- Scenario and sensitivity analysis
- Recommendation scoring
- Supplier ranking or allocation
- Autonomous technical approval
- Integration-contract finalization

### Exit Criteria Result
- Existing PVE-0.2 tests continue to pass: Pass
- Eight PVE-0.3 engine tests pass: Pass
- Total automated test count is 18: Pass
- Full branch diff reviewed: Pass
- PVE CI passes: Pass
- QA report finalized: Pass
- Draft PR opened: Pass

### Next Build
PVE-0.4 — Technical Qualification and Risk, only after PVE-0.3 is merged into `main`.
