# E1 Milestones

## Governance Baseline

Frozen baseline SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`

## Milestone Register

### M1 — Initialization Complete

Target outcomes:
- `e1-development` exists from the frozen baseline.
- All five E1 planning documents exist.
- No production functionality is modified.

Acceptance evidence:
- Branch ancestry confirms the frozen baseline as the starting commit.
- Changed-file review contains planning documents only.

### M2 — Scope and Architecture Approved

Target outcomes:
- E1 feature scope is explicit.
- Protected subsystems and non-goals are recorded.
- Acceptance criteria and affected components are mapped.

Acceptance evidence:
- TSG architecture decision.
- Approved implementation authorization.

### M3 — Authorized Feature Slices Complete

Target outcomes:
- Each approved E1 slice is implemented independently.
- Focused unit and integration tests accompany every slice.
- Existing deterministic and governance controls remain intact.

Acceptance evidence:
- Reviewed pull requests.
- Focused test results and traceability matrix.

### M4 — Integration and Regression Complete

Target outcomes:
- Complete automated suite passes.
- State, persistence, export, error, and cross-device behaviour is validated.
- No unresolved critical or high-severity defects remain.

Acceptance evidence:
- CI run and artifacts.
- QA and governance sign-off.

### M5 — Release Candidate Approved

Target outcomes:
- Release-candidate branch or PR is frozen for review.
- Hosted acceptance evidence is complete.
- Product-owner approval is recorded.

Acceptance evidence:
- Exact head SHA.
- Successful CI.
- Hosted screenshots or recording and deployment logs.

### M6 — E1 Released and Frozen

Target outcomes:
- Approved release is merged using the authorized method.
- Post-merge CI passes on the exact main SHA.
- Hosted deployment is verified.
- E1 release SHA is declared permanently frozen.

Acceptance evidence:
- Merge commit or release SHA.
- Post-merge CI run.
- Hosted acceptance record.

## Indicative Effort

| Milestone | Estimated effort |
|---|---:|
| M1 | 2–4 hours |
| M2 | 8–12 hours |
| M3 | 35–50 hours |
| M4 | 18–24 hours |
| M5 | 8–12 hours |
| M6 | 4–6 hours |
| **Total E1** | **75–108 hours** |

Effort will be re-baselined after M2 because the authoritative feature specification controls implementation complexity.
