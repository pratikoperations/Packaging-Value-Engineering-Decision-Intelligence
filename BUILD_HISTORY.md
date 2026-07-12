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

- Merge commit: `930a4e25d3392b7107616ec498501ef48aa72a8e`
- Closure merge commit: `47ad5730699e49ab64accb41b19e488ebc166ffa`
- QA: Pass
- Tests: 42 passed, 0 failed, 0 errors

## PVE-0.6 — Decision Package Export
**Status:** Completed and merged

### Objective
Create a deterministic, read-only executive decision package with machine-readable and human-readable exports.

### Completed Scope
- Structured executive summary
- Explicit project and scenario metadata
- Baseline and proposed-alternative comparison
- Cost and material results
- Technical qualification outcomes and evidence gaps
- Quality, supply, and implementation risk outcomes
- Recommendation rationale, constraints, and validation requirements
- Deterministic JSON export
- Deterministic Markdown executive report
- Streamlit download controls
- Ten new automated tests

### Validation Controls
- Mandatory top-level sections
- Required identity and provenance metadata
- Positive annual volume
- Single valid baseline
- Complete scenario, qualification, risk, and recommendation coverage
- Unique exported alternative identifiers
- Fixed read-only, no-approval, no-allocation, no-integration controls

### Completion Record
- Pull request: PR #11
- PR status: Merged and closed
- Merge method: Squash merge
- Merge commit: `70dd9dcbf60ab0896e4e38aedf8e20dc65c40985`
- Stable branch: `main`
- Original feature branch: Deleted

### Validated CI Evidence
- Workflow: PVE CI
- Run number: 227
- Run ID: `29183476545`
- Validated PR commit: `55b5294c6c1a4924dca681a47680af70be551b4d`
- Job: `validate-repository`
- Conclusion: Success
- Tests: 52 passed, 0 failed, 0 errors

### Scope Exclusions
- Autonomous technical approval
- Supplier allocation
- Final integration contract
- External system integration
- PVE-0.7 release packaging

### Exit Criteria Result
- Existing 42 tests continue to pass: Pass
- Ten PVE-0.6 tests pass: Pass
- Total automated test count is 52: Pass
- Full branch diff reviewed: Pass
- PVE CI passes: Pass
- QA report finalized: Pass
- PR merged: Pass

### Next Approved Build
PVE-0.7 — QA and Interview Release, after the post-merge closure PR is merged into `main`.
