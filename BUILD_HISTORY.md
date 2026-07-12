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
**Status:** Completed and merged

- Merge commit: `de9d18a428274bfafd369e7509f88b20bc33db89`
- Closure merge commit: `eb32194e2eaf57c8972e12bf12ca5535fad22b2f`
- QA: Pass
- Tests: 18 passed, 0 failed, 0 errors

## PVE-0.4 — Technical Qualification and Risk
**Status:** Implementation complete — CI and final QA pending

### Objective
Create deterministic technical qualification and explicit quality, supply, and implementation risk indicators using the canonical dataset.

### Completed Scope
- Requirement-by-alternative technical status aggregation
- Failure precedence
- Conditional qualification handling
- Missing-result and missing-evidence handling
- Validation-required outputs
- Quality, supply, and implementation risk indicators
- Probability-based effective severity
- Explicit risk-data completeness
- High and critical mitigation requirements
- Twelve new automated tests

### Scope Exclusions
- Application UI
- Recommendation scoring
- Supplier ranking or allocation
- Scenario and sensitivity analysis
- Autonomous technical approval
- Final integration contract
- PVE-0.5 functionality

### Exit Criteria
- Existing 18 tests continue to pass
- Twelve PVE-0.4 tests pass
- Total automated test count is 30
- Full branch diff is reviewed
- PVE CI passes
- QA report is finalized
- Draft PR is opened

### Next Build
PVE-0.5 — Scenario and Recommendation UI, only after PVE-0.4 is merged into `main`.
