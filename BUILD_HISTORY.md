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
**Status:** Completed and merged

- Merge commit: `ced6c5542faa700a43101f8f9fc702d15d78f0ca`
- Closure merge commit: `e28299d5ad5bf127aee16cf479ccf3576cf85ea8`
- QA: Pass
- Tests: 30 passed, 0 failed, 0 errors

## PVE-0.5 — Scenario and Recommendation UI
**Status:** Completed and merged

### Objective
Create explicit scenario assumptions, transparent packaging-alternative comparison, explainable recommendations, and a lightweight interview-demo UI.

### Completed Scope
- Annual-volume scenario input
- Alternative-level cost and material adjustments
- Reuse of deterministic cost and material engines
- Assumption disclosure for every scenario result
- Qualification- and risk-gated recommendation statuses
- Transparent preferred-alternative ordering without opaque scoring
- User-visible rationale, constraints, and validation requirements
- Streamlit comparison UI
- Twelve new automated tests

### Completion Record
- Pull request: PR #9
- PR status: Merged and closed
- Merge method: Squash merge
- Merge commit: `930a4e25d3392b7107616ec498501ef48aa72a8e`
- Stable branch: `main`
- Original feature branch: Deleted

### Validated CI Evidence
- Workflow: PVE CI
- Run number: 190
- Run ID: `29182740157`
- Validated PR commit: `252bf329fcb50c9d3c7c7fb1392309599356eb54`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 42 passed, 0 failed, 0 errors

### Scope Exclusions
- Supplier ranking
- Supplier allocation
- Autonomous technical approval
- Final integration contract
- Decision-package export
- PVE-0.6 functionality

### Exit Criteria Result
- Existing 30 tests continue to pass: Pass
- Twelve PVE-0.5 tests pass: Pass
- Total automated test count is 42: Pass
- Full branch diff reviewed: Pass
- PVE CI passes: Pass
- QA report finalized: Pass
- PR merged: Pass

### Next Approved Build
PVE-0.6 — Decision Package Export, after the post-merge closure PR is merged into `main`.
