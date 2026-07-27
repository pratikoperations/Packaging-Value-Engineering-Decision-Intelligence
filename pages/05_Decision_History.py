from __future__ import annotations

from pathlib import Path
from typing import Any

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
    return f"{record['scenario_name']} · {record['created_at']}"


def history_rows(records: list[dict]) -> list[dict]:
    return [
        {
            "Created": record["created_at"],
            "Status": str(record["status"]).replace("_", " ").title(),
            "Preferred Alternative": record["preferred_alternative_id"] or "None",
            "Scenario": record.get("scenario_name") or "Saved controlled scenario",
            "Engine": record["engine_version"],
        }
        for record in records
    ]


def recommendation_control_rows(recommendation: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "Decision control": "Autonomous approval",
            "Result": "Prohibited" if not recommendation.get("autonomous_approval") else "Allowed",
        },
        {
            "Decision control": "Engineering validation",
            "Result": "Required" if recommendation.get("engineering_validation_required") else "Not required",
        },
        {
            "Decision control": "Human approval",
            "Result": "Required" if recommendation.get("human_approval_required") else "Not required",
        },
        {
            "Decision control": "Preferred alternative",
            "Result": recommendation.get("preferred_alternative_id") or "None",
        },
    ]


def flatten_evidence(value: Any, prefix: str = "") -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            label = str(key).replace("_", " ").title()
            child_prefix = f"{prefix} — {label}" if prefix else label
            rows.extend(flatten_evidence(child, child_prefix))
    elif isinstance(value, list):
        if not value:
            rows.append({"Evidence item": prefix, "Recorded value": "None recorded"})
        else:
            for index, child in enumerate(value, start=1):
                item_prefix = f"{prefix} {index}" if len(value) > 1 else prefix
                rows.extend(flatten_evidence(child, item_prefix))
    else:
        if isinstance(value, bool):
            display = "Yes" if value else "No"
        elif value is None:
            display = "None"
        else:
            display = str(value).replace("_", " ")
        rows.append({"Evidence item": prefix, "Recorded value": display})
    return rows


def decision_reference_rows(record: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"Reference": "Decision snapshot", "Value": record["decision_snapshot_id"]},
        {"Reference": "Project", "Value": record["project_id"]},
        {"Reference": "Dataset version", "Value": record["dataset_id"]},
        {"Reference": "Threshold profile", "Value": record["threshold_profile_id"]},
        {"Reference": "Scenario", "Value": record["scenario_id"]},
        {"Reference": "Engine version", "Value": record["engine_version"]},
        {"Reference": "Source version", "Value": record["source_commit"]},
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
            st.metric("Recommendation Status", prepared.status.replace("_", " ").title())
            st.write(prepared.recommendation["summary"])

            with st.expander("Decision controls", expanded=True):
                st.dataframe(
                    recommendation_control_rows(prepared.recommendation),
                    width="stretch",
                    hide_index=True,
                )

            with st.expander("Technical, risk, threshold, and control evidence"):
                st.dataframe(
                    flatten_evidence(prepared.gate_results),
                    width="stretch",
                    hide_index=True,
                )

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
                f"{record['created_at']} · {str(record['status']).replace('_', ' ').title()}"
                for record in history
            ],
            key="decision-history-selection",
        )
        selected_index = [
            f"{record['created_at']} · {str(record['status']).replace('_', ' ').title()}"
            for record in history
        ].index(selected_history_label)
        selected_history = history[selected_index]

        left, right = st.columns(2)
        left.metric("Decision status", str(selected_history["status"]).replace("_", " ").title())
        right.metric("Preferred alternative", selected_history["preferred_alternative_id"] or "None")
        st.write(selected_history["recommendation"].get("summary", "No summary recorded."))

        with st.expander("Decision controls", expanded=True):
            st.dataframe(
                recommendation_control_rows(selected_history["recommendation"]),
                width="stretch",
                hide_index=True,
            )
        with st.expander("Technical, risk, threshold, and control evidence"):
            st.dataframe(
                flatten_evidence(selected_history["gate_results"]),
                width="stretch",
                hide_index=True,
            )
        with st.expander("Audit references"):
            st.dataframe(
                decision_reference_rows(selected_history),
                width="stretch",
                hide_index=True,
            )

    st.info(
        "History is read-only and project-scoped. This final PVE 1.0 build does not add supplier "
        "allocation, autonomous approval, authentication, or external database persistence."
    )


if __name__ == "__main__":
    main()
