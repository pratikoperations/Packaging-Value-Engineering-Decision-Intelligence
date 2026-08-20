from __future__ import annotations

import json
from pathlib import Path
from typing import Any, MutableMapping

import streamlit as st

from src.application.runtime import (
    build_controlled_scenario_service,
    build_project_service,
    build_threshold_service,
)
from src.demo_portfolio import PortfolioSeedConflict, seed_portfolio_demo
from src.demo_portfolio.seeder import DEFAULT_SEED_PATH
from src.scenario_execution import ScenarioExecutionError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"
DATASET_SELECT_KEY = "controlled_scenario_dataset_label"
THRESHOLD_SELECT_KEY = "controlled_scenario_threshold_label"
EVALUATED_SCENARIO_KEY = "evaluated_controlled_scenario"
REFRESH_FEEDBACK_KEY = "controlled_scenario_refresh_feedback"

DEMO_ADJUSTMENT_DEFAULTS = {
    "ALT-BASE": (0.0, 0.0),
    "ALT-A": (-3.0, -5.0),
    "ALT-B": (2.0, -8.0),
    "ALT-C": (5.0, 3.0),
}


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


def selected_profile_index(records: list[dict], active_profile_id: object, project_id: str) -> int:
    """Select an active threshold only when it belongs to the current scope."""
    for index, record in enumerate(records):
        if (
            record["threshold_profile_id"] == active_profile_id
            and record["project_id"] in (None, project_id)
        ):
            return index
    return 0


def selected_dataset_index(records: list[dict], active_dataset_id: object, *, demo_project: bool) -> int:
    for index, record in enumerate(records):
        if record["dataset_id"] == active_dataset_id:
            return index
    if demo_project and records:
        return len(records) - 1
    return 0


def selected_record_label(
    options: dict[str, dict],
    state: MutableMapping[str, object],
    state_key: str,
    default_label: str,
) -> str:
    selected = state.get(state_key)
    if selected not in options:
        state[state_key] = default_label
        return default_label
    return str(selected)


def evaluated_selection_key(project_id: object, dataset_id: object, threshold_profile_id: object) -> tuple[str, str, str]:
    return (str(project_id), str(dataset_id), str(threshold_profile_id))


def clear_stale_evaluated_scenario(
    state: MutableMapping[str, object],
    selection_key: tuple[str, str, str],
) -> bool:
    evaluated = state.get(EVALUATED_SCENARIO_KEY)
    if evaluated is None:
        return False
    if evaluated_selection_key(
        evaluated.project_id,
        evaluated.dataset_id,
        evaluated.threshold_profile_id,
    ) == selection_key:
        return False
    state.pop(EVALUATED_SCENARIO_KEY, None)
    return True


def latest_dataset_matches_seed(records: list[dict], seed_payload: dict[str, Any]) -> bool:
    if not records:
        return False
    return json.loads(records[-1]["canonical_json"]) == seed_payload


@st.cache_data
def load_demo_seed_payload() -> dict[str, Any]:
    return json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))


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


def is_synthetic_demo(project: dict, dataset_record: dict) -> bool:
    project_code = str(project.get("project_code", "")).upper()
    filename = str(dataset_record.get("original_filename") or "").lower()
    return project_code.startswith("PVE-DEMO") or "synthetic" in filename or "demo" in filename


def default_adjustment(alternative_id: str, *, demo: bool) -> tuple[float, float]:
    if not demo:
        return 0.0, 0.0
    return DEMO_ADJUSTMENT_DEFAULTS.get(alternative_id, (0.0, 0.0))


def render_reason_items(title: str, items: object, empty_message: str) -> None:
    st.write(f"**{title}**")
    if not items:
        st.write(f"• {empty_message}")
        return
    if isinstance(items, (list, tuple)):
        for item in items:
            st.write(f"• {item}")
        return
    st.write(f"• {items}")


def main() -> None:
    st.set_page_config(page_title="PVE Controlled Scenarios", layout="wide")
    st.title("Controlled Scenario Execution")
    st.caption("Deterministic scenario evaluation using immutable dataset and threshold-profile versions")
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

    dataset_labels = list(dataset_options)
    demo_project = str(project.get("project_code", "")).upper().startswith("PVE-DEMO")
    dataset_index = selected_dataset_index(
        datasets,
        st.session_state.get("controlled_scenario_dataset_id"),
        demo_project=demo_project,
    )
    selected_dataset_label = selected_record_label(
        dataset_options,
        st.session_state,
        DATASET_SELECT_KEY,
        dataset_labels[dataset_index],
    )
    selected_dataset_label = st.selectbox(
        "Immutable dataset version",
        options=dataset_labels,
        index=dataset_labels.index(selected_dataset_label),
        key=DATASET_SELECT_KEY,
    )
    threshold_labels = list(threshold_options)
    threshold_index = selected_profile_index(
        thresholds,
        st.session_state.get("controlled_scenario_threshold_id")
        or st.session_state.get("active_threshold_profile_id"),
        project["project_id"],
    )
    selected_threshold_label = selected_record_label(
        threshold_options,
        st.session_state,
        THRESHOLD_SELECT_KEY,
        threshold_labels[threshold_index],
    )
    selected_threshold_label = st.selectbox(
        "Immutable threshold profile version",
        options=threshold_labels,
        index=threshold_labels.index(selected_threshold_label),
        key=THRESHOLD_SELECT_KEY,
    )
    dataset_record = dataset_options[selected_dataset_label]
    threshold_record = threshold_options[selected_threshold_label]
    st.session_state["controlled_scenario_dataset_id"] = dataset_record["dataset_id"]
    st.session_state["controlled_scenario_threshold_id"] = threshold_record["threshold_profile_id"]
    st.session_state["active_threshold_profile_id"] = threshold_record["threshold_profile_id"]

    feedback = st.session_state.pop(REFRESH_FEEDBACK_KEY, None)
    if isinstance(feedback, str):
        st.success(feedback)

    dataset = json.loads(dataset_record["canonical_json"])
    alternatives = dataset.get("packaging_alternatives", [])
    if not alternatives:
        st.error("The selected dataset does not contain packaging alternatives.")
        st.stop()

    latest_demo_dataset_stale = (
        demo_project
        and dataset_record["dataset_id"] == datasets[-1]["dataset_id"]
        and not latest_dataset_matches_seed(datasets, load_demo_seed_payload())
    )
    if latest_demo_dataset_stale:
        st.warning(
            "The newest immutable PVE demonstration dataset is not the complete showcase seed. "
            "Use the governed refresh action to reselect the complete synthetic demo record chain "
            "without overwriting history."
        )
        if st.button("Refresh complete demonstration dataset", width="stretch"):
            try:
                result = seed_portfolio_demo(DATABASE_PATH)
                st.session_state[DATASET_SELECT_KEY] = dataset_label(result.dataset)
                st.session_state[THRESHOLD_SELECT_KEY] = threshold_label(result.threshold_profile)
                st.session_state["controlled_scenario_dataset_id"] = result.dataset["dataset_id"]
                st.session_state["controlled_scenario_threshold_id"] = result.threshold_profile["threshold_profile_id"]
                st.session_state["active_threshold_profile_id"] = result.threshold_profile["threshold_profile_id"]
                st.session_state.pop(EVALUATED_SCENARIO_KEY, None)
                st.session_state[REFRESH_FEEDBACK_KEY] = (
                    "Complete synthetic demonstration refreshed through the governed seed path. "
                    "The complete immutable demo dataset is now selected."
                )
                st.rerun()
            except (PortfolioSeedConflict, ScenarioExecutionError, ValueError, KeyError, OSError) as error:
                st.error(f"The demonstration dataset was not refreshed: {error}")

    demo_defaults = is_synthetic_demo(project, dataset_record)
    if demo_defaults:
        st.info(
            "Synthetic demonstration assumptions are prefilled with editable example values. "
            "They are not supplier quotations, laboratory results or approved engineering inputs."
        )

    with st.form("controlled-scenario-form"):
        scenario_name = st.text_input("Scenario name", value="Controlled Business Scenario")
        annual_volume = st.number_input(
            "Annual volume",
            min_value=1.0,
            value=float(dataset["packaging_project"]["annual_volume"]),
            step=1000.0,
        )

        st.subheader("Controlled Assumptions")
        st.caption("Adjustments are explicit, bounded, editable and applied by packaging alternative.")
        cost_adjustments: dict[str, float] = {}
        material_adjustments: dict[str, float] = {}
        for alternative in alternatives:
            alternative_id = alternative["alternative_id"]
            default_cost, default_material = default_adjustment(alternative_id, demo=demo_defaults)
            st.markdown(f"**{alternative_id} — {alternative['name']}**")
            left, right = st.columns(2)
            cost_adjustments[alternative_id] = left.number_input(
                "Unit-cost adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=default_cost,
                step=0.5,
                key=f"cost-adjustment-{alternative_id}",
            )
            material_adjustments[alternative_id] = right.number_input(
                "Material-weight adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=default_material,
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
            st.session_state[EVALUATED_SCENARIO_KEY] = evaluated
        except (ScenarioExecutionError, ValueError, KeyError) as error:
            st.error(str(error))

    selection_key = evaluated_selection_key(
        project["project_id"],
        dataset_record["dataset_id"],
        threshold_record["threshold_profile_id"],
    )
    if clear_stale_evaluated_scenario(st.session_state, selection_key):
        st.info("The previously evaluated scenario was cleared because the active dataset or threshold selection changed.")

    evaluated = st.session_state.get(EVALUATED_SCENARIO_KEY)
    if evaluated is not None:
        st.subheader("Explainable Scenario Results")
        st.dataframe(alternative_rows(evaluated), width="stretch", hide_index=True)

        for alternative_id, record in evaluated.results["alternatives"].items():
            with st.expander(f"{alternative_id} · {record['control_status']}"):
                render_reason_items(
                    "Business-threshold assessment",
                    record["business_threshold_reasons"],
                    "All configured business thresholds passed.",
                )
                render_reason_items(
                    "Mandatory controls",
                    record["control_reasons"],
                    "No mandatory blocking condition was triggered.",
                )
                render_reason_items(
                    "Technical validation required",
                    record["technical_validation_required"],
                    "No additional technical-validation activity was recorded.",
                )
                render_reason_items(
                    "Risk validation required",
                    record["risk_validation_required"],
                    "No additional risk-validation activity was recorded.",
                )

        if st.button("Save immutable scenario record", width="stretch"):
            try:
                saved = scenario_service.save(evaluated)
                st.success(f"Scenario saved: {saved['scenario_id']}")
                st.session_state.pop(EVALUATED_SCENARIO_KEY, None)
                st.rerun()
            except (ScenarioExecutionError, ValueError, KeyError) as error:
                st.error(str(error))

    st.info(
        "This build saves immutable scenario evidence only. It does not create a decision snapshot, "
        "approve a packaging design, or allocate suppliers."
    )


if __name__ == "__main__":
    main()
