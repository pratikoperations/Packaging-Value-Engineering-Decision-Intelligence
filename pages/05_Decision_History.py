from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.application.runtime import (
    build_decision_snapshot_service,
    build_project_service,
)
from src.decision_snapshots import DecisionSnapshotError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


@st.cache_resource
def services():
    return (
        build_project_service(DATABASE_PATH),
        build_decision_snapshot_service(DATABASE_PATH),
    )


def scenario_label(record: dict) -> str:
    return f"{record['scenario_name']} · {record['created_at']} · {record['scenario_id']}"


def history_rows(records: list[dict]) -> list[dict]:
    return [
        {
            "Created": record["created_at"],
            "Status": record["status"],
            "Preferred Alternative": record["preferred_alternative_id"] or "None",
            "Scenario": record["scenario_id"],
            "Dataset": record["dataset_id"],
            "Threshold": record["threshold_profile_id"] or "None",
            "Engine": record["engine_version"],
        }
        for record in records
    ]


def main() -> None:
    st.set_page_config(page_title="PVE Decision History", layout="wide")
    st.title("Decision Snapshot and History")
    st.caption("Immutable, explainable decision-support evidence from saved scenarios")
    st.warning(
        "Decision snapshots do not approve packaging designs. Engineering validation and human "
        "approval remain mandatory; autonomous approval is prohibited."
    )

    project_service, decision_service = services()
    project_id = st.session_state.get("active_project_id")
    if not project_id:
        st.info("Select an active project from the Project Dashboard first.")
        st.stop()

    try:
        project = project_service.get_project(str(project_id))
    except KeyError:
        st.session_state.pop("active_project_id", None)
        st.error("The active project no longer exists.")
        st.stop()

    archived = project["archived_at"] is not None
    st.success(f"Project: {project['project_code']} — {project['project_name']}")
    if archived:
        st.info("Archived projects are read-only. Existing decision history remains viewable.")

    st.subheader("Create Decision Snapshot")
    scenarios = decision_service.available_scenarios(project["project_id"])
    if not scenarios:
        st.info("Save a controlled scenario before creating a decision snapshot.")
    else:
        options = {scenario_label(record): record for record in scenarios}
        selected_label = st.selectbox("Saved scenario", options=list(options))
        selected = options[selected_label]

        if st.button(
            "Prepare controlled decision snapshot",
            disabled=archived,
            width="stretch",
        ):
            try:
                prepared = decision_service.prepare(
                    project_id=project["project_id"],
                    scenario_id=selected["scenario_id"],
                )
                st.session_state["prepared_decision_snapshot"] = prepared
            except (DecisionSnapshotError, ValueError, KeyError) as error:
                st.error(str(error))

    prepared = st.session_state.get("prepared_decision_snapshot")
    if prepared is not None:
        if prepared.project_id != project["project_id"]:
            st.session_state.pop("prepared_decision_snapshot", None)
            st.warning("A decision snapshot from another project was cleared from the session.")
        else:
            st.subheader("Prepared Decision Evidence")
            st.metric("Recommendation Status", prepared.status)
            st.write(prepared.recommendation["summary"])
            st.json(
                {
                    "project_id": prepared.project_id,
                    "dataset_id": prepared.dataset_id,
                    "threshold_profile_id": prepared.threshold_profile_id,
                    "scenario_id": prepared.scenario_id,
                    "preferred_alternative_id": prepared.preferred_alternative_id,
                }
            )

            with st.expander("Recommendation boundary and controls", expanded=True):
                st.json(prepared.recommendation)

            with st.expander("Technical, risk, threshold, and control evidence"):
                st.json(prepared.gate_results)

            if st.button(
                "Save immutable decision snapshot",
                disabled=archived,
                width="stretch",
            ):
                try:
                    saved = decision_service.save(prepared)
                    st.success(f"Decision snapshot saved: {saved['decision_snapshot_id']}")
                    st.session_state.pop("prepared_decision_snapshot", None)
                    st.rerun()
                except (DecisionSnapshotError, ValueError, KeyError) as error:
                    st.error(str(error))

    st.subheader("Controlled Decision History")
    history = decision_service.history(project["project_id"])
    if not history:
        st.info("No decision snapshots have been saved for this project.")
    else:
        st.dataframe(history_rows(history), width="stretch", hide_index=True)
        selected_history_label = st.selectbox(
            "Inspect immutable decision evidence",
            options=[
                f"{record['created_at']} · {record['status']} · {record['decision_snapshot_id']}"
                for record in history
            ],
            key="decision-history-selection",
        )
        selected_index = [
            f"{record['created_at']} · {record['status']} · {record['decision_snapshot_id']}"
            for record in history
        ].index(selected_history_label)
        selected_history = history[selected_index]

        st.json(
            {
                "decision_snapshot_id": selected_history["decision_snapshot_id"],
                "project_id": selected_history["project_id"],
                "dataset_id": selected_history["dataset_id"],
                "threshold_profile_id": selected_history["threshold_profile_id"],
                "scenario_id": selected_history["scenario_id"],
                "status": selected_history["status"],
                "preferred_alternative_id": selected_history[
                    "preferred_alternative_id"
                ],
                "engine_version": selected_history["engine_version"],
                "source_commit": selected_history["source_commit"],
                "created_at": selected_history["created_at"],
            }
        )
        with st.expander("Recommendation evidence", expanded=True):
            st.json(selected_history["recommendation"])
        with st.expander("Technical, risk, threshold, and control evidence"):
            st.json(selected_history["gate_results"])

    st.info(
        "History is read-only and project-scoped. This final PVE 1.0 build does not add supplier "
        "allocation, autonomous approval, authentication, or external database persistence."
    )


if __name__ == "__main__":
    main()
