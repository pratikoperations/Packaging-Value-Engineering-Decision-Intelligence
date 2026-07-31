from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.application.approved_specification_snapshot_service import (
    ApprovedSpecificationSnapshotError,
)
from src.application.runtime import (
    build_approved_specification_read_model,
    build_approved_specification_snapshot_service,
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
    build_specification_review_read_model,
)
from src.application.specification_review_service import SpecificationReviewError
from src.domain.specification_review import DatasetRole, ReviewStatus
from src.ui.specification_review_ui import (
    ReviewActionRequest,
    SnapshotActionRequest,
    assigned_dataset_from_record,
    business_blocker_message,
    comparison_rows,
    discover_reviewable_fields,
    execute_once,
    execute_snapshot_once,
    history_rows,
    review_summary_label,
    snapshot_identity_rows,
    snapshot_metrics,
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
    if isinstance(error, (SpecificationReviewError, ApprovedSpecificationSnapshotError)):
        st.error(error.message)
    elif isinstance(error, KeyError):
        st.error("The selected project, dataset, review, or snapshot is no longer available.")
    else:
        st.error("The governed action could not be completed safely. No partial action was saved.")


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
        raise SpecificationReviewError(
            "no_reviewable_fields",
            "No scalar specification fields were available for comparison.",
        )
    request = ReviewActionRequest(
        "initialize", f"new:{project_id}:{existing_id}:{proposed_id}", 0
    )
    executed, review = execute_once(
        st.session_state,
        request,
        lambda: service.initialize_and_save(
            existing=existing,
            proposed=proposed,
            fields=fields,
            actor_reference=actor,
        ),
    )
    if executed and review is not None:
        st.session_state[REVIEW_ID_KEY] = review.review_id
        st.session_state[PROJECT_ID_KEY] = project_id
        st.session_state[MODE_KEY] = "resume"
        st.success("Specification review created and persisted.")
        st.rerun()


def _apply_action(
    review,
    action: str,
    field_key: str | None,
    actor: str,
    reason: str,
    corrected: str,
) -> None:
    service = build_persistent_specification_review_service(DATABASE_PATH)
    request = ReviewActionRequest(
        action,
        review.review_id,
        review.revision_number,
        field_key,
        corrected if action == "correct" else None,
        reason or None,
    )

    def operation():
        if action == "confirm_baseline":
            return service.confirm_and_save(
                review.review_id,
                dataset_id=review.state.existing_dataset_id,
                actor_reference=actor,
            )
        if action == "accept" and field_key:
            return service.accept_and_save(
                review.review_id,
                field_key=field_key,
                actor_reference=actor,
            )
        if action == "reject" and field_key:
            return service.reject_and_save(
                review.review_id,
                field_key=field_key,
                actor_reference=actor,
                action_reason=reason,
            )
        if action == "correct" and field_key:
            return service.correct_and_save(
                review.review_id,
                field_key=field_key,
                corrected_value=corrected,
                actor_reference=actor,
                action_reason=reason,
            )
        raise SpecificationReviewError(
            "invalid_ui_action", "Select a valid review action."
        )

    executed, _ = execute_once(st.session_state, request, operation)
    if executed:
        st.success("Review action saved as a new immutable revision.")
        st.rerun()


def _render_create(
    project_id: str,
    valid_records: list[dict[str, object]],
    actor: str,
) -> None:
    if len(valid_records) < 2:
        st.warning(
            "This project needs at least two valid dataset versions for "
            "Existing-versus-Proposed review."
        )
        return
    record_by_id = {str(row["dataset_id"]): row for row in valid_records}
    dataset_ids = list(record_by_id)
    existing_id = st.selectbox(
        "Existing dataset",
        dataset_ids,
        format_func=lambda value: _dataset_label(record_by_id[value]),
    )
    proposed_id = st.selectbox(
        "Proposed dataset",
        [value for value in dataset_ids if value != existing_id],
        format_func=lambda value: _dataset_label(record_by_id[value]),
    )
    if st.button(
        "Initialize persisted review",
        type="primary",
        disabled=not actor.strip(),
    ):
        _initialize_review(project_id, existing_id, proposed_id, actor.strip())


def _render_existing_snapshot(snapshot) -> None:
    st.subheader("Approved Specification Snapshot")
    st.caption(
        "Read-only human-authorized controlled snapshot. "
        "This record does not constitute autonomous engineering approval."
    )
    st.dataframe(snapshot_identity_rows(snapshot), width="stretch", hide_index=True)

    metrics = snapshot_metrics(snapshot)
    first = st.columns(3)
    first[0].metric("Approved fields", metrics["approved_field_count"])
    first[1].metric("Accepted", metrics["accepted_field_count"])
    first[2].metric("Corrected", metrics["corrected_field_count"])
    second = st.columns(3)
    second[0].metric("Retained baseline", metrics["retained_baseline_count"])
    second[1].metric("Unchanged", metrics["unchanged_field_count"])
    second[2].metric("Optional exclusions", metrics["optional_exclusion_count"])

    with st.expander("Snapshot audit details", expanded=False):
        st.text(f"Content hash: {snapshot.content_hash}")
        st.text(f"Schema version: {snapshot.snapshot_schema_version}")
        st.text(f"Approval rationale: {snapshot.approval_reason}")


def _create_snapshot(project_id: str, review, actor: str, reason: str) -> None:
    datasets = build_dataset_repository(DATABASE_PATH)
    existing = assigned_dataset_from_record(
        datasets.get(review.state.existing_dataset_id),
        DatasetRole.EXISTING,
    )
    proposed = assigned_dataset_from_record(
        datasets.get(review.state.proposed_dataset_id),
        DatasetRole.PROPOSED,
    )
    fields = discover_reviewable_fields(existing, proposed)
    if not fields:
        raise ApprovedSpecificationSnapshotError(
            "no_governed_fields",
            "No governed scalar fields are available for snapshot creation.",
        )
    request = SnapshotActionRequest(
        project_id=project_id,
        review_id=review.review_id,
        source_review_revision_id=review.review_revision_id,
        actor_reference=actor,
        approval_reason=reason,
    )
    service = build_approved_specification_snapshot_service(DATABASE_PATH)
    executed, snapshot = execute_snapshot_once(
        st.session_state,
        request,
        lambda: service.create_snapshot(
            project_id=project_id,
            review_id=review.review_id,
            source_review_revision_id=review.review_revision_id,
            actor_reference=actor,
            approval_reason=reason,
            fields=fields,
        ),
    )
    if executed and snapshot is not None:
        st.success("Immutable approved specification snapshot created.")
        st.rerun()


def _render_snapshot_control(project_id: str, review, actor: str) -> None:
    approved_read_model = build_approved_specification_read_model(DATABASE_PATH)
    existing_snapshot = approved_read_model.get_snapshot_for_review(
        review.review_id,
        project_id=project_id,
    )
    if existing_snapshot is not None:
        _render_existing_snapshot(existing_snapshot)
        return

    eligibility = review.state.eligibility
    if not eligibility or not eligibility.eligible:
        return

    st.subheader("Create Approved Specification Snapshot")
    st.info(
        "This creates one immutable, project-scoped record from the latest "
        "eligible review revision. It records a human authorization and does "
        "not autonomously approve engineering specifications."
    )
    reason = st.text_area(
        "Snapshot approval rationale",
        key=f"snapshot_reason_{review.review_id}",
        help="Required. State why this governed review output may be frozen.",
    )
    confirmed = st.checkbox(
        "I confirm this is the latest eligible review and authorize creation "
        "of one immutable approved specification snapshot.",
        key=f"snapshot_confirmation_{review.review_id}",
    )
    disabled = not actor.strip() or not reason.strip() or not confirmed
    if st.button(
        "Create immutable approved specification snapshot",
        type="primary",
        disabled=disabled,
        key=f"create_snapshot_{review.review_revision_id}",
    ):
        _create_snapshot(
            project_id,
            review,
            actor.strip(),
            reason.strip(),
        )


def _render_review(project_id: str, review_id: str, actor: str) -> None:
    read_model = build_specification_review_read_model(DATABASE_PATH)
    review = read_model.load_latest(review_id, project_id=project_id)
    history = read_model.list_history(review_id, project_id=project_id)

    left, middle, right = st.columns(3)
    left.metric("Review", review.review_id)
    middle.metric("Current revision", review.revision_number)
    right.metric(
        "Snapshot eligibility",
        (
            "Eligible"
            if review.state.eligibility and review.state.eligibility.eligible
            else "Blocked"
        ),
    )
    st.dataframe(comparison_rows(review), width="stretch", hide_index=True)

    eligibility = review.state.eligibility
    if eligibility and eligibility.eligible:
        st.success(
            "All governed review gates are satisfied for the latest persisted revision."
        )
    else:
        st.warning("Approved snapshot creation is blocked.")
        for blocker in eligibility.blockers if eligibility else ():
            st.write(f"- {business_blocker_message(blocker)}")

    if not review.state.existing_baseline or not review.state.existing_baseline.confirmed:
        if st.button(
            "Confirm Existing dataset as baseline",
            disabled=not actor.strip(),
        ):
            _apply_action(
                review,
                "confirm_baseline",
                None,
                actor.strip(),
                "",
                "",
            )

    pending = [
        item
        for item in review.state.comparisons
        if item.candidate.status is ReviewStatus.PENDING
    ]
    if pending:
        field_key = st.selectbox("Field", [item.field_key for item in pending])
        action = st.radio(
            "Action",
            ["accept", "reject", "correct"],
            horizontal=True,
        )
        reason = st.text_area("Rationale", disabled=action == "accept")
        corrected = st.text_input(
            "Corrected value",
            disabled=action != "correct",
        )
        disabled = (
            not actor.strip()
            or (action in {"reject", "correct"} and not reason.strip())
            or (action == "correct" and not corrected.strip())
        )
        if st.button("Save field action", type="primary", disabled=disabled):
            _apply_action(
                review,
                action,
                field_key,
                actor.strip(),
                reason.strip(),
                corrected,
            )
    else:
        st.success("Every changed field has a terminal review status.")

    _render_snapshot_control(project_id, review, actor)

    with st.expander("Immutable revision history", expanded=False):
        st.dataframe(history_rows(history), width="stretch", hide_index=True)

    if st.button("Return to review selection"):
        _clear_selection()
        st.rerun()


def main() -> None:
    st.title("Specification Review")
    st.caption(
        "Governed Existing-versus-Proposed review with immutable approved-output handoff."
    )
    st.info(
        "Create or resume a persisted review. An approved specification snapshot "
        "is available only from the latest eligible revision and remains read-only."
    )

    projects = build_project_repository(DATABASE_PATH).list(archived=False)
    if not projects:
        st.warning("Create an active project before starting or resuming a review.")
        return

    project_options = {
        f"{row['project_code']} — {row['project_name']}": row for row in projects
    }
    selected_project_label = st.selectbox("Project", list(project_options))
    project_id = str(project_options[selected_project_label]["project_id"])
    if st.session_state.get(PROJECT_ID_KEY) not in {None, project_id}:
        _clear_selection()

    actor = st.text_input(
        "Actor reference",
        help="Required for review actions and approved snapshot creation.",
    )
    read_model = build_specification_review_read_model(DATABASE_PATH)
    summaries = read_model.list_reviews_for_project(project_id)
    mode_options = ["Create new review"] + (
        ["Resume persisted review"] if summaries else []
    )
    mode = st.radio("Mode", mode_options, horizontal=True)

    records = build_dataset_repository(DATABASE_PATH).list_for_project(project_id)
    valid_records = [
        row for row in records if row["validation_status"] == "valid"
    ]

    if mode == "Create new review":
        _clear_selection()
        _render_create(project_id, valid_records, actor)
        return

    summary_by_id = {summary.review_id: summary for summary in summaries}
    selected_review_id = st.selectbox(
        "Persisted review",
        list(summary_by_id),
        format_func=lambda value: review_summary_label(summary_by_id[value]),
    )
    st.session_state[REVIEW_ID_KEY] = selected_review_id
    st.session_state[PROJECT_ID_KEY] = project_id

    try:
        _render_review(project_id, selected_review_id, actor)
    except Exception as error:
        _clear_selection()
        _render_error(error)


main()
