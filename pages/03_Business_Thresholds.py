from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.runtime import build_project_service, build_threshold_service
from src.thresholds import MANDATORY_ENGINEERING_CONTROLS, ThresholdValidationError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


@st.cache_resource
def services():
    return build_project_service(DATABASE_PATH), build_threshold_service(DATABASE_PATH)


def profile_label(record: dict) -> str:
    scope = "Controlled default" if record["project_id"] is None else "Project-specific"
    return f"{record['profile_name']} · v{record['version_number']} · {scope}"


def main() -> None:
    st.set_page_config(page_title="PVE Business Thresholds", layout="wide")
    st.title("Configurable Business Thresholds")
    st.caption("Versioned commercial decision thresholds with mandatory engineering controls")

    project_service, threshold_service = services()
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

    if project["archived_at"] is not None:
        st.session_state.pop("active_project_id", None)
        st.error("Archived projects are read-only and cannot receive threshold versions.")
        st.stop()

    st.success(f"Active project: {project['project_code']} — {project['project_name']}")

    st.subheader("Mandatory Engineering Controls")
    st.warning("These controls are fixed, non-disableable, and are not business thresholds.")
    control_rows = [
        {"Control": key.replace("_", " ").title(), "Enforced": value}
        for key, value in MANDATORY_ENGINEERING_CONTROLS.items()
    ]
    st.dataframe(control_rows, width="stretch", hide_index=True)

    profiles = threshold_service.available_profiles(project["project_id"])
    options = {profile_label(profile): profile for profile in profiles}
    selected_label = st.selectbox("Available threshold profiles", options=list(options))
    selected = options[selected_label]
    st.session_state["active_threshold_profile_id"] = selected["threshold_profile_id"]

    st.subheader("Selected Profile")
    st.json(selected["profile"])
    if selected["project_id"] is None:
        st.info("The controlled default profile is read-only. Create a project-specific profile to customize business thresholds.")

    st.subheader("Create Project-Specific Threshold Version")
    with st.form("threshold-profile-form"):
        profile_name = st.text_input("Profile name", value="Project Business Thresholds")
        minimum_annual_savings = st.number_input(
            "Minimum annual savings",
            min_value=0.0,
            value=float(selected["profile"]["minimum_annual_savings"]),
            step=1000.0,
        )
        minimum_material_reduction = st.number_input(
            "Minimum material reduction (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(selected["profile"]["minimum_material_reduction_percent"]),
            step=0.5,
        )
        maximum_business_risk = st.selectbox(
            "Maximum acceptable business risk",
            options=["low", "medium", "high", "critical"],
            index=["low", "medium", "high", "critical"].index(selected["profile"]["maximum_business_risk"]),
        )
        require_positive = st.checkbox(
            "Require positive savings or material reduction",
            value=bool(selected["profile"]["require_positive_savings_or_material_reduction"]),
        )
        submitted = st.form_submit_button("Save immutable threshold version", width="stretch")

    if submitted:
        try:
            created = threshold_service.create_project_profile(
                project_id=project["project_id"],
                profile_name=profile_name,
                profile={
                    "minimum_annual_savings": minimum_annual_savings,
                    "minimum_material_reduction_percent": minimum_material_reduction,
                    "maximum_business_risk": maximum_business_risk,
                    "require_positive_savings_or_material_reduction": require_positive,
                },
            )
            st.session_state["active_threshold_profile_id"] = created["threshold_profile_id"]
            st.success(f"Threshold profile version {created['version_number']} saved and selected.")
            st.rerun()
        except ThresholdValidationError as error:
            st.error(str(error))

    st.info(
        "Thresholds influence business screening only. They cannot override failed technical qualification, "
        "critical-risk blocks, insufficient evidence, or mandatory engineering validation."
    )


if __name__ == "__main__":
    main()
