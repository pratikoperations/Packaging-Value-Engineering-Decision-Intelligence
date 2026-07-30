# E1.4 Persisted Specification Review UI Contract

## Scope

E1.4 exposes one current-session persisted specification review through Streamlit. Review discovery, history browsing, resumption across sessions, snapshot creation, scenario changes, exports, deployment, and main-branch changes remain out of scope.

## File manifest

- `app.py`
- `pages/25_specification_review.py`
- `src/application/runtime.py`
- `src/ui/specification_review_ui.py`
- `tests/test_specification_review_ui.py`
- `docs/e1-4-specification-review-ui-contract.md`

## Interaction contract

1. The user selects one active project.
2. Only valid datasets belonging to that project are selectable.
3. Existing and Proposed selections must be distinct.
4. A non-empty actor reference is required before any write action is enabled.
5. Review initialization persists revision 1 through `PersistentSpecificationReviewService`.
6. Baseline confirmation, Accept, Reject, and Correct each append one immutable revision.
7. Reject and Correct require a non-empty rationale.
8. Correct additionally requires a corrected value.
9. The current revision and eligibility blockers are reloaded from persistence after every successful action.
10. The UI never creates a snapshot or invokes scenario, decision, or export services.

## Streamlit rerun-safety contract

Every write is represented by a deterministic action token containing the review identity, source revision, action, field, corrected value, and rationale. The token is placed in session state before the operation and committed only after success.

- A pending or committed token cannot execute again during a rerun.
- A failed operation clears its pending token and may be retried.
- A later revision generates a different token.
- No write occurs merely because the page reruns.

## Acceptance tests

- Canonical dataset JSON is decoded into governed assigned datasets.
- Scalar nested fields are discovered deterministically; list-valued structures are excluded.
- Action tokens are deterministic and revision-sensitive.
- Successful actions execute once.
- Duplicate rerun submissions are blocked.
- Failed operations can be retried.
- Runtime builders share one persisted database.
- A complete initialize/confirm/accept flow reaches eligibility.
- Existing full-suite tests remain green through CI.
