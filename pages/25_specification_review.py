from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.application.runtime import (
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
    build_specification_review_read_model,
)
from src.application.specification_review_service import SpecificationReviewError
from src.domain.specification_review import DatasetRole, ReviewStatus
from src.ui.specification_review_ui import (
    ReviewActionRequest,
    assigned_dataset_from_record,
    comparison_rows,
    discover_reviewable_fields,
    execute_once,
    history_rows,
    review_summary_label,
)

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))
REVIEW_ID_KEY = "active_specification_review_id"
PROJECT_ID_KEY = "active_specification_review_project_id"
MODE_KEY = "specification_review_mode"


def _dataset_label(record: dict[str, object]) -> str:
    filename = record.get("original_filename") or record.get("source_type") or "dataset"
    return f"v{record['version_number']} — {filename} — {record['validation_status']}"


def _render_error(error: Exception) -> None:
    if isinstance(error, SpecificationReviewError):
        st.error(error.message)
    elif isinstance(error, KeyError):
        st.error("The selected project, dataset, or review is no longer available.")
    else:
        st.error("The review action could not be completed safely. No partial action was saved.")


def _clear_selection() -> None:
    st.session_state.pop(REVIEW_ID_KEY, None)
    st.session_state.pop(PROJECT_ID_KEY, None)


def _initialize_review(project_id: str, existing_id: str, proposed_id: str, actor: str) -> None:
    datasets = build_dataset_repository(DATABASE_PATH)
    service = build_persistent_specification_review_service(DATABASE_PATH)
    existing = assigned_dataset_from_record(datasets.get(existing_id), DatasetRole.EXISTING)
    proposed = assigned_dataset_from_record(datasets.get(proposed_id), DatasetRole.PROPOSED)
    fields = discover_reviewable_fields(existing, proposed)
    if not fields:
        raise SpecificationReviewError("no_reviewable_fields", "No scalar specification fields were available for comparison.")
    request = ReviewActionRequest("initialize", f"new:{project_id}:{existing_id}:{proposed_id}", 0)
    executed, review = execute_once(
        st.session_state,
        request,
        lambda: service.initialize_and_save(existing=existing, proposed=proposed, fields=fields, actor_reference=actor),
    )
    if executed and review is not None:
        st.session_state[REVIEW_ID_KEY] = review.review_id
        st.session_state[PROJECT_ID_KEY] = project_id
        st.session_state[MODE_KEY] = "resume"
        st.success("Specification review created and persisted.")
        st.rerun()


def _apply_action(review, action: str, field_key: str | None, actor: str, reason: str, corrected: str) -> None:
    service = build_persistent_specification_review_service(DATABASE_PATH)
    request = ReviewActionRequest(action, review.review_id, review.revision_number, field_key, corrected if action == "correct" else None, reason or None)

    def operation():
        if action == "confirm_baseline":
            return service.confirm_and_save(review.review_id, dataset_id=review.state.existing_dataset_id, actor_reference=actor)
        if action == "accept" and field_key:
            return service.accept_and_save(review.review_id, field_key=field_key, actor_reference=actor)
        if action == "reject" and field_key:
            return service.reject_and_save(review.review_id, field_key=field_key, actor_reference=actor, action_reason=reason)
        if action == "correct" and field_key:
            return service.correct_and_save(review.review_id, field_key=field_key, corrected_value=corrected, actor_reference=actor, action_reason=reason)
        raise SpecificationReviewError("invalid_ui_action", "Select a valid review action.")

    executed, _ = execute_once(st.session_state, request, operation)
    if executed:
        st.success("Review action saved as a new immutable revision.")
        st.rerun()


def _render_create(project_id: str, valid_records: list[dict[str, object]], actor: str) -> None:
    if len(valid_records) < 2:
        st.warning("This project needs at least two valid dataset versions for Existing-versus-Proposed review.")
        return
    record_by_id = {str(row["dataset_id"]): row for row in valid_records}
    dataset_ids = list(record_by_id)
    existing_id = st.selectbox("Existing dataset", dataset_ids, format_func=lambda value: _dataset_label(record_by_id[value]))
    proposed_id = st.selectbox("Proposed dataset", [value for value in dataset_ids if value != existing_id], format_func=lambda value: _dataset_label(record_by_id[value]))
    if st.button("Initialize persisted review", type="primary", disabled=not actor.strip()):
        _initialize_review(project_id, existing_id, proposed_id, actor.strip())


def _render_review(project_id: str, review_id: str, actor: str) -> None:
    read_model = build_specification_review_read_model(DATABASE_PATH)
    review = read_model.load_latest(review_id, project_id=project_id)
    history = read_model.list_history(review_id, project_id=project_id)
    left, middle, right = st.columns(3)
    left.metric("Review", review.review_id)
    middle.metric("Current revision", review.revision_number)
    right.metric("Eligibility", "Eligible" if review.state.eligibility and review.state.eligibility.eligible else "Blocked")
    st.dataframe(comparison_rows(review), width="stretch", hide_index=True)
    eligibility = review.state.eligibility
    if eligibility and eligibility.eligible:
        st.success("All review gates are satisfied. Snapshot creation remains deferred to E1.6.")
    else:
        st.warning("Snapshot eligibility is blocked.")
        for blocker in eligibility.blockers if eligibility else ():
            st.write(f"- {blocker}")
    if not review.state.existing_baseline or not review.state.existing_baseline.confirmed:
        if st.button("Confirm Existing dataset as baseline", disabled=not actor.strip()):
            _apply_action(review, "confirm_baseline", None, actor.strip(), "", "")
    pending = [item for item in review.state.comparisons if item.candidate.status is ReviewStatus.PENDING]
    if pending:
        field_key = st.selectbox("Field", [item.field_key for item in pending])
        action = st.radio("Action", ["accept", "reject", "correct"], horizontal=True)
        reason = st.text_area("Rationale", disabled=action == "accept")
        corrected = st.text_input("Corrected value", disabled=action != "correct")
        disabled = not actor.strip() or (action in {"reject", "correct"} and not reason.strip()) or (action == "correct" and not corrected.strip())
        if st.button("Save field action", type="primary", disabled=disabled):
            _apply_action(review, action, field_key, actor.strip(), reason.strip(), corrected)
    else:
        st.success("Every changed field has a terminal review status.")
    with st.expander("Immutable revision history", expanded=False):
        st.dataframe(history_rows(history), width="stretch", hide_index=True)
    if st.button("Return to review selection"):
        _clear_selection()
        st.rerun()


def main() -> None:
    st.title("Specification Review")
    st.caption("Governed Existing-versus-Proposed comparison with append-only audit provenance.")
    st.info("E1.5 supports project-scoped review discovery, latest-state resumption, and read-only immutable history.")
    projects = build_project_repository(DATABASE_PATH).list(archived=False)
    if not projects:
        st.warning("Create an active project before starting or resuming a review.")
        return
    project_options = {f"{row['project_code']} — {row['project_name']}": row for row in projects}
    selected_project_label = st.selectbox("Project", list(project_options))
    project_id = str(project_options[selected_project_label]["project_id"])
    if st.session_state.get(PROJECT_ID_KEY) not in {None, project_id}:
        _clear_selection()
    actor = st.text_input("Actor reference", help="Required for every persisted review revision.")
    read_model = build_specification_review_read_model(DATABASE_PATH)
    summaries = read_model.list_reviews_for_project(project_id)
    mode_options = ["Create new review"] + (["Resume persisted review"] if summaries else [])
    mode = st.radio("Mode", mode_options, horizontal=True)
    records = build_dataset_repository(DATABASE_PATH).list_for_project(project_id)
    valid_records = [row for row in records if row["validation_status"] == "valid"]
    if mode == "Create new review":
        _clear_selection()
        _render_create(project_id, valid_records, actor)
        return
    summary_by_id = {summary.review_id: summary for summary in summaries}
    selected_review_id = st.selectbox("Persisted review", list(summary_by_id), format_func=lambda value: review_summary_label(summary_by_id[value]))
    st.session_state[REVIEW_ID_KEY] = selected_review_id
    st.session_state[PROJECT_ID_KEY] = project_id
    try:
        _render_review(project_id, selected_review_id, actor)
    except Exception as error:
        _clear_selection()
        _render_error(error)


main()
