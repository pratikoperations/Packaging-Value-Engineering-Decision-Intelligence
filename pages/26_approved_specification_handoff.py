from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.application.approved_specification_consumption_service import (
    ApprovedSpecificationConsumptionError,
)
from src.application.runtime import (
    build_approved_specification_consumption_read_model,
    build_approved_specification_consumption_service,
    build_approved_specification_read_model,
    build_project_repository,
)
from src.domain.approved_specification_consumption import AuthorizedConsumptionPurpose
from src.ui.approved_specification_consumption_ui import (
    ConsumptionHandoffActionRequest,
    authorization_identity_rows,
    business_error_message,
    clear_handoff_token,
    envelope_identity_rows,
    execute_handoff_once,
    handoff_audit_rows,
    purpose_label,
    snapshot_identity_rows,
)

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))


def _render_error(error: Exception) -> None:
    if isinstance(error, ApprovedSpecificationConsumptionError):
        st.error(business_error_message(error.code, error.message))
    elif isinstance(error, KeyError):
        st.error("The selected project, snapshot, envelope, or authorization is unavailable.")
    else:
        st.error("The governed handoff could not be completed safely. No partial action was saved.")


def _render_snapshot(snapshot) -> None:
    st.subheader("Approved Specification Snapshot")
    st.caption("Read-only source. No direct dataset or review-state input is accepted on this page.")
    st.dataframe(snapshot_identity_rows(snapshot), width="stretch", hide_index=True)
    with st.expander("Snapshot audit details", expanded=False):
        st.text(f"Snapshot content hash: {snapshot.content_hash}")
        st.text(f"Approval rationale: {snapshot.approval_reason}")


def _render_handoff(handoff) -> None:
    st.subheader("Governed Consumption Handoff")
    st.success("Approved input package and immutable authorization record are available.")
    st.dataframe(envelope_identity_rows(handoff.envelope), width="stretch", hide_index=True)
    st.dataframe(
        authorization_identity_rows(handoff.authorization),
        width="stretch",
        hide_index=True,
    )
    with st.expander("Handoff audit details", expanded=False):
        st.dataframe(handoff_audit_rows(handoff), width="stretch", hide_index=True)
    st.info(
        "This record proves preparation and authorization of an approved input package. "
        "It does not prove that a cost, scenario, risk, recommendation, sourcing, or award engine executed."
    )


def _create_handoff(project_id: str, snapshot_id: str, purpose, actor: str, reason: str):
    request = ConsumptionHandoffActionRequest(
        project_id=project_id,
        snapshot_id=snapshot_id,
        purpose=purpose,
        actor_reference=actor,
        business_reason=reason,
    )
    service = build_approved_specification_consumption_service(DATABASE_PATH)
    return execute_handoff_once(
        st.session_state,
        request,
        lambda: service.create_handoff(
            project_id=project_id,
            snapshot_id=snapshot_id,
            purpose=purpose,
            actor_reference=actor,
            business_reason=reason,
        ),
    )


def main() -> None:
    st.title("Approved Specification Handoff")
    st.caption("Governed preparation of immutable approved inputs for future downstream analysis.")
    st.info(
        "This page creates no analytical result and makes no supplier-award, production, "
        "engineering, commercial, sourcing, or recommendation decision."
    )

    projects = build_project_repository(DATABASE_PATH).list(archived=False)
    if not projects:
        st.warning("Create an active project and approved specification snapshot first.")
        return

    project_options = {
        f"{row['project_code']} — {row['project_name']}": row for row in projects
    }
    selected_project = st.selectbox("Project", list(project_options))
    project_id = str(project_options[selected_project]["project_id"])

    snapshot_read_model = build_approved_specification_read_model(DATABASE_PATH)
    snapshots = snapshot_read_model.list_snapshots_for_project(project_id)
    if not snapshots:
        st.warning("This project has no approved specification snapshot available for handoff.")
        return

    snapshot_by_id = {item.snapshot_id: item for item in snapshots}
    snapshot_id = st.selectbox("Approved snapshot", list(snapshot_by_id))
    snapshot = snapshot_by_id[snapshot_id]
    _render_snapshot(snapshot)

    purposes = list(AuthorizedConsumptionPurpose)
    purpose = st.selectbox("Governed purpose", purposes, format_func=purpose_label)
    actor = st.text_input("Actor reference", help="Required human or accountable role reference.")
    reason = st.text_area("Business reason", help="Required. Explain the intended governed use.")
    confirmed = st.checkbox(
        "I understand this prepares an approved input package and authorization record only; "
        "it does not execute or approve any downstream analysis or decision."
    )

    disabled = not actor.strip() or not reason.strip() or not confirmed
    if st.button("Create governed handoff", type="primary", disabled=disabled):
        try:
            executed, handoff = _create_handoff(
                project_id,
                snapshot_id,
                purpose,
                actor.strip(),
                reason.strip(),
            )
            if executed and handoff is not None:
                st.session_state["latest_consumption_authorization_id"] = (
                    handoff.authorization.authorization_id
                )
                st.success("Governed handoff created.")
                st.rerun()
        except Exception as error:
            _render_error(error)

    authorization_id = st.session_state.get("latest_consumption_authorization_id")
    if authorization_id:
        try:
            read_model = build_approved_specification_consumption_read_model(DATABASE_PATH)
            authorization = read_model.get_authorization(
                str(authorization_id), project_id=project_id
            )
            envelope = read_model.get_authorized_envelope(
                str(authorization_id), project_id=project_id
            )
            from src.domain.approved_specification_consumption import GovernedConsumptionHandoff

            _render_handoff(GovernedConsumptionHandoff(envelope, authorization))
            if st.button("Clear latest handoff selection"):
                st.session_state.pop("latest_consumption_authorization_id", None)
                clear_handoff_token(st.session_state)
                st.rerun()
        except Exception as error:
            st.session_state.pop("latest_consumption_authorization_id", None)
            clear_handoff_token(st.session_state)
            _render_error(error)


main()
