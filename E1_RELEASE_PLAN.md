# E1 Release Plan

## Governance Baseline

- Permanently frozen baseline SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`
- E1 development branch: `e1-development`
- The baseline release remains immutable throughout E1.

## Release Model

E1 will be delivered through controlled, reviewable pull requests. Feature work must not be committed directly to `main`. The final release must be tied to an exact reviewed head SHA and verified again after merge.

## Release Stages

### 1. Planning Approval

Required evidence:
- E1 roadmap, milestones, risk register, test strategy, and release plan approved.
- Authoritative feature specification and non-goals recorded.

Gate:
- Explicit TSG implementation authorization.

### 2. Feature Development

Requirements:
- Small, independently reviewable feature slices.
- Tests and documentation included with each slice.
- No weakening of frozen-release controls.
- Expected-head protection used for authorized merges.

Gate:
- Focused tests and full regression suite pass.

### 3. Integration Freeze

Actions:
- Stop scope additions.
- Resolve open defects and review comments.
- Produce release-candidate SHA.
- Confirm changed files match approved scope.

Gate:
- No unresolved critical or high-severity defect.

### 4. Release Candidate Verification

Required evidence:
- CI workflow name, trigger, run number, run ID, job ID, checked-out ref, checked-out SHA, test totals, and artifact details.
- Hosted application startup and deployment logs.
- Desktop, tablet, and mobile navigation evidence.
- Full authorized workflow evidence, including governance blocking and snapshot eligibility.
- Confirmation that no traceback, raw exception class, internal module names, or raw JSON is exposed.

Gate:
- TSG decision: MERGE READY.

### 5. Production Merge

Actions:
- Reconfirm base SHA and expected head SHA.
- Merge only through the approved method.
- Do not force-push or rewrite history.
- Record the resulting main SHA.

Gate:
- Merge result matches authorized head and method.

### 6. Post-Merge Verification

Required evidence:
- CI executed against the exact resulting main SHA.
- All tests pass with zero failures and zero errors.
- Hosted application deploys from the approved branch/SHA.
- Smoke test and governed workflow acceptance pass.

Gate:
- TSG decision: POST-MERGE VERIFIED.

### 7. Release Freeze

Actions:
- Declare the E1 main SHA frozen.
- Record release date, CI evidence, deployment evidence, and known limitations.
- Begin subsequent work only in a new version or authorized branch.

Gate:
- TSG decision: FREEZE.

## Rollback Strategy

Rollback is required when a critical release defect is confirmed.

Procedure:
1. Preserve evidence and stop further deployment changes.
2. Identify the last verified frozen release SHA.
3. Revert through a reviewed pull request unless immediate operational risk requires the repository's authorized emergency process.
4. Run full CI against the rollback result.
5. Verify hosted deployment and workflow behaviour.
6. Document root cause and corrective action before resuming E1.

The frozen baseline SHA remains the ultimate known reference but must not be rewritten or modified.

## Release Communications

The release record must state:
- Release SHA and branch.
- Implemented scope.
- Test totals and CI identifiers.
- Hosted verification evidence.
- Data and evidence limitations.
- Human approval requirements.
- Known residual risks.

## Completion Criteria

E1 is complete only when implementation, testing, documentation, release verification, and final freeze are all complete. A successful pre-merge CI run alone does not constitute a release.
