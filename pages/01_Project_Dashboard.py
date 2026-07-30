from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, MutableMapping

import streamlit as st

from src.application.runtime import build_project_service
from src.category_registry import default_registry
from src.demo_portfolio import PortfolioSeedConflict, seed_portfolio_demo

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"
SEED_FEEDBACK_KEY = "portfolio_seed_feedback"
NEW_PROJECT_UPLOAD_KEY = "new_project_upload_pending"
SEED_STAGES = (("project", "Project workspace"), ("dataset", "Validated dataset version"), ("threshold_profile", "Business threshold profile"), ("scenario", "Controlled scenario"), ("decision_snapshot", "Immutable decision snapshot"))

@st.cache_resource
def project_service():
    return build_project_service(DATABASE_PATH)

def select_active_workspace(session_state: MutableMapping[str, object], project_id: str, *, archived: bool) -> bool:
    if archived:
        return False
    session_state["active_project_id"] = project_id
    return True

def portfolio_seed_complete(result: Any) -> bool:
    required = ((result.project, "project_id"), (result.dataset, "dataset_id"), (result.threshold_profile, "threshold_profile_id"), (result.scenario, "scenario_id"), (result.decision_snapshot, "decision_snapshot_id"))
    return all(isinstance(record, dict) and bool(record.get(identifier)) for record, identifier in required)

def seed_stage_rows(created: tuple[str, ...]) -> list[dict[str, str]]:
    created_set = set(created)
    return [{"Workflow record": label, "Load result": "Created" if key in created_set else "Reused existing record"} for key, label in SEED_STAGES]

def project_table_rows(projects: list[dict]) -> list[dict]:
    return [{"Project Code": p["project_code"], "Project Name": p["project_name"], "Category": p["category"], "Objective": p.get("objective") or "Legacy / not recorded", "Change Type": p.get("change_type") or "Legacy / not recorded", "Status": p["status"], "Annual Volume": p["annual_volume"], "Currency": p["currency"], "Dataset Versions": p["dataset_versions"], "Scenarios": p["scenarios"], "Saved Decisions": p["decisions"], "Latest Decision": p["latest_decision_status"] or "Not evaluated"} for p in projects]

def render_portfolio_demo_loader() -> None:
    st.subheader("Portfolio Demonstration")
    st.write("Load one complete synthetic corrugated-packaging case containing a project, validated dataset, governed threshold profile, controlled scenario, and immutable decision snapshot.")
    st.warning("The demonstration uses synthetic data only. It is not supplier, laboratory, production, engineering-trial, or commercial evidence. Engineering validation and documented human approval remain mandatory; autonomous approval is prohibited.")
    feedback = st.session_state.pop(SEED_FEEDBACK_KEY, None)
    if isinstance(feedback, dict):
        st.success(feedback["message"])
        st.dataframe(feedback["rows"], width="stretch", hide_index=True)
    if st.button("Load demonstration project", type="primary", width="stretch"):
        try:
            result = seed_portfolio_demo(DATABASE_PATH)
            if not portfolio_seed_complete(result):
                raise RuntimeError("The demonstration record chain is incomplete and was not activated.")
            if not select_active_workspace(st.session_state, str(result.project["project_id"]), archived=result.project.get("archived_at") is not None):
                raise RuntimeError("The demonstration project is archived and cannot become active.")
            st.session_state["active_threshold_profile_id"] = str(result.threshold_profile["threshold_profile_id"])
            created_count = len(result.created)
            st.session_state[SEED_FEEDBACK_KEY] = {"message": f"Synthetic demonstration loaded and selected as the active workspace. {created_count} records were created; {len(SEED_STAGES) - created_count} existing records were reused.", "rows": seed_stage_rows(result.created)}
            st.rerun()
        except (PortfolioSeedConflict, RuntimeError, ValueError, KeyError, sqlite3.IntegrityError, OSError) as error:
            st.error(f"Demonstration project was not loaded: {error}")
    st.caption("Guided workflow after loading")
    st.markdown("1. **Project Dashboard** — review the active synthetic workspace and saved-record counts.\n2. **Upload and Validate** — inspect the immutable validated dataset version.\n3. **Business Thresholds** — review the governed project threshold profile.\n4. **Controlled Scenarios** — inspect deterministic evidence and mandatory controls.\n5. **Decision History** — review the immutable decision snapshot; it is not engineering approval.")

def render_current_workspace(service) -> None:
    project_id = st.session_state.get("active_project_id")
    if not project_id:
        st.info("No active workspace is selected.")
        return
    try:
        project = service.get_project(str(project_id))
    except KeyError:
        st.session_state.pop("active_project_id", None)
        st.warning("The previously selected workspace is no longer available.")
        return
    if project["archived_at"] is not None:
        st.session_state.pop("active_project_id", None)
        st.warning("The previously selected workspace is archived and was cleared.")
        return
    st.success(f"Current active workspace: {project['project_code']} — {project['project_name']}")

def render_new_project_upload_offer() -> None:
    if not st.session_state.get(NEW_PROJECT_UPLOAD_KEY):
        return
    st.success("Project created and selected. Add initial project data now, or continue without uploading.")
    st.page_link("pages/09_Data_Upload.py", label="Open governed Data Upload", icon="📤")
    if st.button("Continue without uploading", key="continue-without-initial-upload"):
        st.session_state.pop(NEW_PROJECT_UPLOAD_KEY, None)
        st.rerun()

def render_project_actions(service, projects: list[dict], *, archived: bool) -> None:
    if not projects:
        st.info(f"No {'archived' if archived else 'active'} projects are available.")
        return
    options = {f"{p['project_code']} — {p['project_name']}": p for p in projects}
    selected = options[st.selectbox("Select project", list(options), key=f"project-select-{archived}")]
    if archived:
        st.warning("Archived projects are read-only and cannot become the active workspace.")
        return
    if st.button("Select as active workspace", key=f"select-{selected['project_id']}", width="stretch"):
        select_active_workspace(st.session_state, selected["project_id"], archived=False)
        st.rerun()
    left, right = st.columns(2)
    with left:
        with st.form("duplicate-project-form"):
            code = st.text_input("New project code", value=f"{selected['project_code']}-COPY")
            name = st.text_input("New project name", value=f"{selected['project_name']} Copy")
            submitted = st.form_submit_button("Duplicate project metadata", width="stretch")
        if submitted:
            try:
                service.duplicate_project(selected["project_id"], new_project_code=code, new_project_name=name)
                st.success("Project metadata duplicated. Historical datasets and decisions were not copied.")
                st.rerun()
            except (ValueError, sqlite3.IntegrityError) as error:
                st.error(str(error))
    with right:
        st.caption("Archiving preserves all historical records.")
        if st.button("Archive selected project", key=f"archive-{selected['project_id']}", width="stretch"):
            service.archive_project(selected["project_id"])
            if st.session_state.get("active_project_id") == selected["project_id"]:
                st.session_state.pop("active_project_id", None)
            st.rerun()

def main() -> None:
    st.set_page_config(page_title="PVE Project Dashboard", layout="wide")
    st.title("Packaging Value Engineering Project Dashboard")
    st.caption("PVE controlled project intake and synthetic portfolio demonstration")
    st.warning("This dashboard uses local SQLite demonstration persistence. It is not production storage.")
    render_portfolio_demo_loader()
    service = project_service()
    registry = default_registry()
    summary = service.portfolio_summary()
    metrics = st.columns(5)
    for column, label, key in zip(metrics, ("Total Projects", "Active Projects", "Archived Projects", "Dataset Versions", "Saved Decisions"), ("total_projects", "active_projects", "archived_projects", "dataset_versions", "decision_snapshots")):
        column.metric(label, summary[key])
    render_current_workspace(service)
    render_new_project_upload_offer()
    st.subheader("Create Project")
    category_map = {item.display_name: item for item in registry.list()}
    with st.form("create-project-form", clear_on_submit=True):
        first, second, third = st.columns(3)
        project_code = first.text_input("Project code", placeholder="PVE-PACK-001")
        project_name = second.text_input("Project name", placeholder="Packaging value-engineering project")
        category_label = third.selectbox("Packaging category", list(category_map))
        definition = category_map[category_label]
        objective = st.selectbox("Project objective", list(definition.objectives))
        change_type = st.selectbox("Change type", list(definition.change_types))
        a, b, c = st.columns(3)
        product_sku = a.text_input("Product or SKU")
        business_unit_plant = b.text_input("Business unit or plant")
        project_owner = c.text_input("Project owner")
        d, e, f = st.columns(3)
        annual_volume = d.number_input("Annual volume", min_value=1.0, value=100000.0)
        volume_unit = e.text_input("Volume unit", value="units_per_year")
        currency = f.selectbox("Currency", ["INR", "USD", "EUR", "GBP"])
        g, h = st.columns(2)
        current_unit_cost = g.number_input("Current unit cost", min_value=0.0, value=0.0)
        proposed_unit_cost = h.number_input("Proposed unit cost, if available", min_value=0.0, value=0.0)
        current_supplier = st.text_input("Current supplier")
        proposed_supplier = st.text_input("Proposed supplier, if applicable")
        submitted = st.form_submit_button("Create project", width="stretch")
    if submitted:
        try:
            created = service.create_project(project_code=project_code, project_name=project_name, category=definition.key, objective=objective, change_type=change_type, product_sku=product_sku or None, business_unit_plant=business_unit_plant or None, project_owner=project_owner or None, annual_volume=annual_volume, volume_unit=volume_unit or None, currency=currency, current_unit_cost=current_unit_cost, proposed_unit_cost=proposed_unit_cost or None, current_supplier=current_supplier or None, proposed_supplier=proposed_supplier or None)
            select_active_workspace(st.session_state, created["project_id"], archived=False)
            st.session_state[NEW_PROJECT_UPLOAD_KEY] = True
            st.success(f"Project {created['project_code']} created and selected.")
            st.rerun()
        except (ValueError, KeyError, sqlite3.IntegrityError) as error:
            st.error(str(error))
    active_tab, archived_tab = st.tabs(["Active Projects", "Archived Projects"])
    with active_tab:
        active = service.dashboard_projects(archived=False)
        if active:
            st.dataframe(project_table_rows(active), width="stretch", hide_index=True)
        render_project_actions(service, active, archived=False)
    with archived_tab:
        archived = service.dashboard_projects(archived=True)
        if archived:
            st.dataframe(project_table_rows(archived), width="stretch", hide_index=True)
        render_project_actions(service, archived, archived=True)
    st.info("Dashboard metrics represent saved records only and do not represent realized savings, approved packaging changes, technical feasibility, or supplier allocation.")

if __name__ == "__main__":
    main()
