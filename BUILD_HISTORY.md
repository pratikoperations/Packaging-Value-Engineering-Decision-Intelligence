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

- Merge commit: `70dd9dcbf60ab0896e4e38aedf8e20dc65c40985`
- Closure merge commit: `1b3a6f0250f3645df08e908b3be30d75b99294e7`
- QA: Pass
- Tests: 52 passed, 0 failed, 0 errors

## PVE-0.7 — QA and Interview Release
**Status:** Release implementation complete — CI and final QA pending

### Objective
Convert the completed analytical application into a recoverable, interview-ready release with end-to-end evidence and clear operating boundaries.

### Completed Scope
- Final README and local-run guidance
- End-to-end dataset-to-export QA
- Static Streamlit UI smoke validation
- Interview demonstration guide
- Final release checklist and acceptance criteria
- Recovery-readiness updates
- Six final-release automated tests
- CI enforcement for release documentation and PVE-0.7 identity

### Acceptance Criteria
- Canonical synthetic data validates.
- All alternatives receive cost, material, qualification, and risk outputs.
- All proposed alternatives receive recommendation outputs.
- JSON and Markdown exports are deterministic and readable.
- Human approval and project-boundary controls remain fixed.
- UI source includes scenario, comparison, recommendation, export, and disclaimer controls.
- README, demo guide, checklist, and recovery instructions are complete.
- Integration contract remains draft.

### Expected Test Result
- Existing tests: 52
- New PVE-0.7 release tests: 6
- Expected total: 58

### Scope Exclusions
- New analytical engines
- Supplier ranking or allocation
- Autonomous technical approval
- Final integration contract
- External system integration
- Production security, workflow, or deployment implementation

### Exit Criteria
- All 58 tests pass
- Full PR diff is reviewed
- PVE CI passes
- QA report is finalized
- Draft PR is opened and later marked ready only after final CI
