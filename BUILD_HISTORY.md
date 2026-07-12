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
**Status:** Implementation complete — CI and final QA pending

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

### Scope Exclusions
- Application UI
- Technical qualification and risk
- Logistics optimization
- Scenario and sensitivity analysis
- Recommendation scoring
- Supplier ranking or allocation
- Autonomous technical approval
- Integration-contract finalization

### Exit Criteria
- Existing PVE-0.2 tests continue to pass
- Eight PVE-0.3 engine tests pass
- Total automated test count is 18
- Full branch diff is reviewed
- PVE CI passes
- QA report is finalized
- Draft PR is opened

### Next Build
PVE-0.4 — Technical Qualification and Risk, only after PVE-0.3 is merged into `main`.
