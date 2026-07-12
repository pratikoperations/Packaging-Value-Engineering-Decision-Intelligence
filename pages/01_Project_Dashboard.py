from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import MutableMapping

import streamlit as st

from src.application.runtime import build_project_service


ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


@st.cache_resource
def project_service():
    return build_project_service(DATABASE_PATH)


def select_active_workspace(
    session_state: MutableMapping[str, object],
    project_id: str,
    *,
    archived: bool,
) -> bool:
    """Select an active project explicitly; archived projects can never become active."""
    if archived:
        return False
    session_state["active_project_id"] = project_id
    return True


def project_table_rows(projects: list[dict]) -> list[dict]:
    return [
        {
            "Project Code": project["project_code"],
            "Project Name": project["project_name"],
            "Category": project["category"],
            "Status": project["status"],
            "Annual Volume": project["annual_volume"],
            "Currency": project["currency"],
            "Dataset Versions": project["dataset_versions"],
            "Scenarios": project["scenarios"],
            "Saved Decisions": project["decisions"],
            "Latest Decision": project["latest_decision_status"] or "Not evaluated",
            "Updated": project["updated_at"],
        }
        for project in projects
    ]


def render_current_workspace(service) -> None:
    active_project_id = st.session_state.get("active_project_id")
    if not active_project_id:
        st.info("No active workspace is selected.")
        return
    try:
        active_project = service.get_project(str(active_project_id))
    except KeyError:
        st.session_state.pop("active_project_id", None)
        st.warning("The previously selected workspace is no longer available.")
        return
    if active_project["archived_at"] is not None:
        st.session_state.pop("active_project_id", None)
        st.warning("The previously selected workspace is archived and was cleared.")
        return
    st.success(
        f"Current active workspace: {active_project['project_code']} — "
        f"{active_project['project_name']}"
    )


def render_project_actions(service, projects: list[dict], *, archived: bool) -> None:
    if not projects:
        label = "archived" if archived else "active"
        st.info(f"No {label} projects are available.")
        return

    options = {
        f"{project['project_code']} — {project['project_name']}": project
        for project in projects
    }
    selected_label = st.selectbox(
        "Select project",
        options=list(options),
        key=f"project-select-{'archived' if archived else 'active'}",
    )
    selected = options[selected_label]

    if archived:
        st.warning("Archived projects are read-only in this build and cannot become the active workspace.")
        return

    st.caption(
        "Choose an active project, then confirm it explicitly as the current workspace. "
        "Dataset upload and analysis workflows are delivered in later approved builds."
    )
    if st.button(
        "Select as active workspace",
        key=f"select-workspace-{selected['project_id']}",
        width="stretch",
    ):
        select_active_workspace(
            st.session_state,
            selected["project_id"],
            archived=False,
        )
        st.success(
            f"Active workspace selected: {selected['project_code']} — {selected['project_name']}"
        )
        st.rerun()

    action_left, action_right = st.columns(2)
    with action_left:
        with st.form("duplicate-project-form"):
            duplicate_code = st.text_input(
                "New project code",
                value=f"{selected['project_code']}-COPY",
            )
            duplicate_name = st.text_input(
                "New project name",
                value=f"{selected['project_name']} Copy",
            )
            duplicate_submitted = st.form_submit_button(
                "Duplicate project metadata",
                width="stretch",
            )
        if duplicate_submitted:
            try:
                service.duplicate_project(
                    selected["project_id"],
                    new_project_code=duplicate_code,
                    new_project_name=duplicate_name,
                )
                st.success("Project metadata duplicated. Historical datasets and decisions were not copied.")
                st.rerun()
            except (ValueError, sqlite3.IntegrityError) as error:
                st.error(str(error))

    with action_right:
        st.write("Archive project")
        st.caption("Archiving preserves all historical records and removes the project from the active list.")
        if st.button(
            "Archive selected project",
            key=f"archive-{selected['project_id']}",
            width="stretch",
        ):
            service.archive_project(selected["project_id"])
            if st.session_state.get("active_project_id") == selected["project_id"]:
                st.session_state.pop("active_project_id", None)
            st.success("Project archived without deleting history.")
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="PVE Project Dashboard", layout="wide")
    st.title("Packaging Value Engineering Project Dashboard")
    st.caption("Portfolio-level project management for the PVE 1.0 controlled build")
    st.warning(
        "This dashboard uses local SQLite demonstration persistence. Data may not remain durable "
        "after hosted application restarts or redeployments. It is not production storage."
    )

    service = project_service()
    summary = service.portfolio_summary()

    metric_columns = st.columns(5)
    metric_columns[0].metric("Total Projects", summary["total_projects"])
    metric_columns[1].metric("Active Projects", summary["active_projects"])
    metric_columns[2].metric("Archived Projects", summary["archived_projects"])
    metric_columns[3].metric("Dataset Versions", summary["dataset_versions"])
    metric_columns[4].metric("Saved Decisions", summary["decision_snapshots"])

    render_current_workspace(service)

    st.subheader("Create Project")
    with st.form("create-project-form", clear_on_submit=True):
        first, second, third = st.columns(3)
        project_code = first.text_input("Project code", placeholder="PVE-CASE-001")
        project_name = second.text_input("Project name", placeholder="Corrugated case optimization")
        category = third.selectbox(
            "Packaging category",
            options=["corrugated_shipping_case"],
            help="PVE 1.0 remains intentionally limited to the existing corrugated category.",
        )
        fourth, fifth = st.columns(2)
        currency = fourth.selectbox("Currency", options=["INR", "USD", "EUR", "GBP"])
        annual_volume = fifth.number_input(
            "Annual volume",
            min_value=1.0,
            value=100000.0,
            step=10000.0,
        )
        submitted = st.form_submit_button("Create project", width="stretch")

    if submitted:
        try:
            created = service.create_project(
                project_code=project_code,
                project_name=project_name,
                category=category,
                currency=currency,
                annual_volume=annual_volume,
            )
            select_active_workspace(
                st.session_state,
                created["project_id"],
                archived=False,
            )
            st.success(f"Project {created['project_code']} created and selected.")
            st.rerun()
        except (ValueError, sqlite3.IntegrityError) as error:
            st.error(str(error))

    active_tab, archived_tab = st.tabs(["Active Projects", "Archived Projects"])

    with active_tab:
        active_projects = service.dashboard_projects(archived=False)
        if active_projects:
            st.dataframe(project_table_rows(active_projects), width="stretch", hide_index=True)
        render_project_actions(service, active_projects, archived=False)

    with archived_tab:
        archived_projects = service.dashboard_projects(archived=True)
        if archived_projects:
            st.dataframe(project_table_rows(archived_projects), width="stretch", hide_index=True)
        render_project_actions(service, archived_projects, archived=True)

    st.info(
        "Dashboard metrics represent project records and saved evidence only. "
        "They do not represent realized savings, approved packaging changes, or supplier allocation."
    )


if __name__ == "__main__":
    main()
