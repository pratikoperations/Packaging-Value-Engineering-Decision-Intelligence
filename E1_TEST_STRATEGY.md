# E1 Test Strategy

## Governance Baseline

Frozen baseline SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`

The existing automated suite is the minimum regression floor. E1 tests must extend coverage without deleting, weakening, skipping, or rewriting existing assertions merely to obtain a passing result.

## Test Objectives

1. Preserve deterministic decision outputs.
2. Verify all authorized E1 behaviour and state transitions.
3. Protect persistence, auditability, procurement traceability, and human-review controls.
4. Prevent internal errors or implementation details from reaching the user interface.
5. Confirm usable desktop, tablet, and mobile operation.
6. Tie release evidence to exact commit SHAs.

## Test Layers

### Unit Tests

Cover:
- Pure domain rules and calculations.
- Data normalization and validation.
- Role assignment and review-state transitions.
- Snapshot eligibility and blocking logic.
- Presentation-safe error mapping.

Requirements:
- Deterministic inputs and outputs.
- Boundary and invalid-input cases.
- No external service dependency.

### Integration Tests

Cover:
- Application services with persistence.
- Upload-to-validation-to-review workflow.
- Existing and Proposed candidate handling.
- Decision records, snapshots, and exports.
- Archived/read-only behaviour where applicable.

Requirements:
- Isolated temporary storage.
- Repeatable fixtures.
- Idempotency and transaction behaviour where relevant.

### Regression Tests

- Run the full existing test suite on every E1 pull request.
- Maintain representative golden cases for frozen-release behaviour.
- Compare key outputs with the frozen baseline when implementation can affect decisions.
- Treat unexplained output changes as release blockers.

### UI and Acceptance Tests

Verify:
- Application startup.
- Desktop sidebar navigation.
- Tablet navigation.
- Mobile navigation.
- Data Upload page.
- Existing and Proposed role assignment.
- Existing approved-baseline confirmation.
- Pending Proposed candidate review.
- Blocked downstream state while reviews remain unresolved.
- Snapshot visibility only after all Proposed candidates are resolved.
- Clear user-facing errors without traceback, exception class, internal module name, parser detail, or raw JSON exposure.

### Export and Audit Tests

Verify:
- Export content is deterministic and complete.
- Record identifiers and timestamps are traceable.
- Snapshot content cannot be silently mutated.
- Synthetic-data and human-approval limitations remain visible.

### Performance and Reliability Checks

- Record startup time and critical workflow response time.
- Test representative larger datasets within the supported envelope.
- Verify repeated operations do not duplicate immutable records unexpectedly.
- Verify graceful handling of malformed or unsupported uploads.

## CI Requirements

Every implementation PR must provide:
- Focused test results for changed behaviour.
- Full-suite result.
- Zero failures and zero errors.
- Explicit skipped-test explanation, if any.
- Uploaded full-suite diagnostic artifact.
- Checked-out ref and SHA.

## Release Acceptance Gates

A release candidate is acceptable only when:
- All existing and new automated tests pass.
- No critical or high-severity defect remains open.
- Hosted acceptance evidence covers the approved workflow.
- Deployed branch or commit is identifiable.
- Post-merge CI runs successfully against the exact release SHA.

## Defect Severity

- Critical: corrupted data, incorrect decision, frozen-baseline violation, deployment failure, or bypassed governance control.
- High: major workflow unavailable, auditability lost, unresolved review bypassed, or sensitive implementation detail exposed.
- Medium: material usability or compatibility defect with a workaround.
- Low: cosmetic or minor documentation issue without decision impact.
