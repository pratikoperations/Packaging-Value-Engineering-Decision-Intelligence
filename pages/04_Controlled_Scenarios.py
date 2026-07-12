from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.application.runtime import (
    build_controlled_scenario_service,
    build_project_service,
    build_threshold_service,
)
from src.scenario_execution import ScenarioExecutionError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


@st.cache_resource
def services():
    return (
        build_project_service(DATABASE_PATH),
        build_threshold_service(DATABASE_PATH),
        build_controlled_scenario_service(DATABASE_PATH),
    )


def dataset_label(record: dict) -> str:
    filename = record.get("original_filename") or record["source_type"]
    return f"Dataset v{record['version_number']} · {filename}"


def threshold_label(record: dict) -> str:
    scope = "Controlled default" if record["project_id"] is None else "Project-specific"
    return f"{record['profile_name']} · v{record['version_number']} · {scope}"


def alternative_rows(result) -> list[dict]:
    rows: list[dict] = []
    for alternative_id, record in result.results["alternatives"].items():
        rows.append(
            {
                "Alternative": alternative_id,
                "Annual Savings": record["annual_savings_vs_baseline"],
                "Material Change %": record["material_change_percent_vs_baseline"],
                "Technical Status": record["technical_status"],
                "Risk": record["risk_level"],
                "Business Thresholds": "Pass" if record["business_thresholds_passed"] else "Fail",
                "Control Status": record["control_status"],
                "Engineering Validation": "Required",
            }
        )
    return rows


def main() -> None:
    st.set_page_config(page_title="PVE Controlled Scenarios", layout="wide")
    st.title("Controlled Scenario Execution")
    st.caption(
        "Deterministic scenario evaluation using immutable dataset and threshold-profile versions"
    )
    st.warning(
        "Scenario outputs are decision-support evidence only. Engineering validation and human "
        "approval remain mandatory; autonomous approval is prohibited."
    )

    project_service, threshold_service, scenario_service = services()
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
        st.error("Archived projects are read-only and cannot execute or save scenarios.")
        st.stop()

    st.success(f"Active project: {project['project_code']} — {project['project_name']}")

    datasets = scenario_service.available_datasets(project["project_id"])
    if not datasets:
        st.info("Upload and save a validated dataset version before running a scenario.")
        st.stop()

    threshold_service.ensure_default_profile()
    thresholds = scenario_service.available_thresholds(project["project_id"])
    if not thresholds:
        st.info("Create or load a threshold profile before running a scenario.")
        st.stop()

    dataset_options = {dataset_label(record): record for record in datasets}
    threshold_options = {threshold_label(record): record for record in thresholds}

    selected_dataset_label = st.selectbox(
        "Immutable dataset version",
        options=list(dataset_options),
    )
    selected_threshold_label = st.selectbox(
        "Immutable threshold profile version",
        options=list(threshold_options),
    )
    dataset_record = dataset_options[selected_dataset_label]
    threshold_record = threshold_options[selected_threshold_label]

    dataset = json.loads(dataset_record["canonical_json"])
    alternatives = dataset.get("packaging_alternatives", [])
    if not alternatives:
        st.error("The selected dataset does not contain packaging alternatives.")
        st.stop()

    with st.form("controlled-scenario-form"):
        scenario_name = st.text_input("Scenario name", value="Controlled Business Scenario")
        annual_volume = st.number_input(
            "Annual volume",
            min_value=1.0,
            value=float(dataset["packaging_project"]["annual_volume"]),
            step=1000.0,
        )

        st.subheader("Controlled Assumptions")
        st.caption("Adjustments are explicit, bounded, and applied by packaging alternative.")
        cost_adjustments: dict[str, float] = {}
        material_adjustments: dict[str, float] = {}
        for alternative in alternatives:
            alternative_id = alternative["alternative_id"]
            st.markdown(f"**{alternative_id} — {alternative['name']}**")
            left, right = st.columns(2)
            cost_adjustments[alternative_id] = left.number_input(
                "Unit-cost adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key=f"cost-adjustment-{alternative_id}",
            )
            material_adjustments[alternative_id] = right.number_input(
                "Material-weight adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=0.0,
                step=0.5,
                key=f"material-adjustment-{alternative_id}",
            )

        run_submitted = st.form_submit_button("Run deterministic scenario", width="stretch")

    if run_submitted:
        try:
            evaluated = scenario_service.evaluate(
                project_id=project["project_id"],
                dataset_id=dataset_record["dataset_id"],
                threshold_profile_id=threshold_record["threshold_profile_id"],
                scenario_name=scenario_name,
                annual_volume=annual_volume,
                cost_adjustments=cost_adjustments,
                material_adjustments=material_adjustments,
            )
            st.session_state["evaluated_controlled_scenario"] = evaluated
        except (ScenarioExecutionError, ValueError, KeyError) as error:
            st.error(str(error))

    evaluated = st.session_state.get("evaluated_controlled_scenario")
    if evaluated is not None:
        if evaluated.project_id != project["project_id"]:
            st.session_state.pop("evaluated_controlled_scenario", None)
            st.warning("A scenario from another project was cleared from the session.")
            st.stop()

        st.subheader("Explainable Scenario Results")
        st.dataframe(alternative_rows(evaluated), width="stretch", hide_index=True)

        for alternative_id, record in evaluated.results["alternatives"].items():
            with st.expander(f"{alternative_id} · {record['control_status']}"):
                st.write("Business-threshold reasons:")
                st.write(record["business_threshold_reasons"] or ["All configured business thresholds passed."])
                st.write("Mandatory-control reasons:")
                st.write(record["control_reasons"] or ["No mandatory blocking condition was triggered."])
                st.write("Technical validation required:")
                st.write(record["technical_validation_required"] or ["No additional activity recorded."])
                st.write("Risk validation required:")
                st.write(record["risk_validation_required"] or ["No additional activity recorded."])

        if st.button("Save immutable scenario record", width="stretch"):
            try:
                saved = scenario_service.save(evaluated)
                st.success(f"Scenario saved: {saved['scenario_id']}")
                st.session_state.pop("evaluated_controlled_scenario", None)
                st.rerun()
            except (ScenarioExecutionError, ValueError, KeyError) as error:
                st.error(str(error))

    st.info(
        "This build saves immutable scenario evidence only. It does not create a decision snapshot, "
        "approve a packaging design, or allocate suppliers."
    )


if __name__ == "__main__":
    main()
