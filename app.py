from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from src.exports import (
    assemble_decision_package,
    render_decision_package_json,
    render_decision_package_markdown,
)
from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import SYNTHETIC_DISCLOSURE, build_legacy_dataset, load_governed_package
from src.technical_qualification import evaluate_technical_qualification
from src.ui.showcase_handoff_ui import PAGE_REGISTRY_SESSION_KEY


ROOT = Path(__file__).resolve().parent
GOVERNED_DEMO_PATH = ROOT / "data" / "demo" / "governed_synthetic"
SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"
LEGACY_SYNTHETIC_NOTICE = "This application uses synthetic demonstration data only."
SIDEBAR_GROUPS = (
    ("Workspace", ("Project Dashboard", "Guided Workflow")),
    (
        "Inputs & Governance",
        ("Specification Review", "Data Upload", "Business Rules & Thresholds"),
    ),
    ("Analysis & Decision", ("Scenario Analysis", "Decision Records")),
    (
        "Evidence & Explanation",
        ("SourceMate", "Calculation Evidence", "Decision Evidence Ledger"),
    ),
)


@st.cache_data
def load_governed_demo() -> dict:
    return load_governed_package(GOVERNED_DEMO_PATH)


def render_home() -> None:
    st.set_page_config(page_title="PVE Decision Intelligence", layout="wide")
    st.title("Packaging Value Engineering Decision Intelligence")
    st.caption("Deterministic scenario comparison, explainable recommendation, and read-only decision export")
    st.warning(f"{LEGACY_SYNTHETIC_NOTICE} {SYNTHETIC_DISCLOSURE}")

    governed_package = load_governed_demo()
    scenario_options = {
        item["scenario_id"]: item["title"] for item in governed_package["scenarios"]
    }
    selected_scenario_id = st.selectbox(
        "Governed synthetic procurement scenario",
        tuple(scenario_options),
        format_func=lambda value: scenario_options[value],
        help="All scenario records are deterministic fictional fixtures for testing and demonstration.",
    )
    dataset = build_legacy_dataset(governed_package, selected_scenario_id)
    alternatives = dataset["packaging_alternatives"]
    project = dataset["packaging_project"]

    st.sidebar.header("Scenario Inputs")
    annual_volume = st.sidebar.number_input(
        "Annual volume (cases)",
        min_value=1.0,
        value=float(project["annual_volume"]),
        step=10000.0,
    )

    cost_adjustments: dict[str, float] = {}
    material_adjustments: dict[str, float] = {}
    for alternative in alternatives:
        alternative_id = alternative["alternative_id"]
        with st.sidebar.expander(f"{alternative_id} assumptions"):
            cost_adjustments[alternative_id] = st.number_input(
                "Unit-cost adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key=f"cost-{selected_scenario_id}-{alternative_id}",
            )
            material_adjustments[alternative_id] = st.number_input(
                "Material-weight adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key=f"material-{selected_scenario_id}-{alternative_id}",
            )

    inputs = ScenarioInputs(
        annual_volume=annual_volume,
        cost_adjustment_percent_by_alternative=cost_adjustments,
        material_adjustment_percent_by_alternative=material_adjustments,
    )
    scenario = evaluate_scenario(dataset, inputs)
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)

    st.subheader("Scenario Comparison")
    st.warning(SYNTHETIC_DISCLOSURE)
    comparison_rows = []
    names = {item["alternative_id"]: item["name"] for item in alternatives}
    for alternative_id, result in scenario.alternatives.items():
        qualification = qualifications[alternative_id]
        risk = risks[alternative_id]
        rec = recommendation.alternatives.get(alternative_id)
        comparison_rows.append(
            {
                "Alternative": alternative_id,
                "Name": names[alternative_id],
                "Unit cost": result.unit_cost,
                "Annual savings": result.annual_savings_vs_baseline,
                "Material change %": result.material_change_percent_vs_baseline,
                "Qualification": qualification.status,
                "Risk": risk.overall_level,
                "Risk data complete": risk.data_complete,
                "Recommendation": rec.status if rec else "baseline",
            }
        )
    st.dataframe(comparison_rows, width="stretch", hide_index=True)

    st.subheader("Preferred Alternative")
    if recommendation.preferred_alternative_id:
        st.success(f"Preferred alternative: {recommendation.preferred_alternative_id}")
    else:
        st.warning("No proposed alternative currently meets the recommendation gate.")

    st.subheader("Explainable Recommendation Detail")
    for alternative_id, result in recommendation.alternatives.items():
        with st.expander(f"{alternative_id} — {result.status}"):
            st.write("**Rationale**")
            for item in result.rationale:
                st.write(f"- {item}")
            st.write("**Constraints**")
            for item in result.constraints or ("None",):
                st.write(f"- {item}")
            st.write("**Validation required**")
            for item in result.validation_required or ("None",):
                st.write(f"- {item}")

    st.subheader("Decision Package Export")
    st.warning(SYNTHETIC_DISCLOSURE)
    source_commit = st.text_input(
        "Source commit or version reference",
        value="GOVERNED-SYNTHETIC-DEMO",
        help="Provide the Git commit or version reference represented by this export.",
    )
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    package = assemble_decision_package(
        dataset,
        scenario,
        qualifications,
        risks,
        recommendation,
        source_commit=source_commit,
        generated_at=generated_at,
    )
    package["metadata"].update(
        {
            "dataset_id": dataset["dataset_id"],
            "dataset_version": dataset["dataset_version"],
            "synthetic_disclosure": SYNTHETIC_DISCLOSURE,
        }
    )
    json_export = render_decision_package_json(package)
    markdown_export = (
        "# Synthetic Data Disclosure\n\n"
        + SYNTHETIC_DISCLOSURE
        + "\n\n"
        + render_decision_package_markdown(package)
    )

    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download machine-readable JSON",
            data=json_export,
            file_name="pve_decision_package.json",
            mime="application/json",
            width="stretch",
        )
    with right:
        st.download_button(
            "Download human-readable report",
            data=markdown_export,
            file_name="pve_decision_report.md",
            mime="text/markdown",
            width="stretch",
        )

    st.caption(
        f"Read-only internal export from {SOURCE_REPOSITORY}. The final integration contract remains draft."
    )
    st.info(
        "This tool does not approve packaging designs autonomously. Recommendations and exports remain subject to engineering validation and documented evidence."
    )


def _task_page(path: Path) -> tuple[int, str] | None:
    stem = path.stem.lower()
    if "showcase_handoff" in stem:
        return 5, "Showcase & Handoff"
    if "project_dashboard" in stem:
        return 10, "Project Dashboard"
    if "guided_workflow" in stem:
        return 20, "Guided Workflow"
    if "specification_review" in stem:
        return 25, "Specification Review"
    if "data_upload" in stem:
        return 30, "Data Upload"
    if "business_thresholds" in stem:
        return 40, "Business Rules & Thresholds"
    if "controlled_scenarios" in stem:
        return 50, "Scenario Analysis"
    if "decision_history" in stem:
        return 60, "Decision Records"
    if "sourcemate" in stem:
        return 65, "SourceMate"
    if "calculation_evidence" in stem:
        return 67, "Calculation Evidence"
    if "decision_evidence_ledger" in stem:
        return 68, "Decision Evidence Ledger"
    if "capabilities_and_limits" in stem:
        return 70, "Capabilities & Limits"
    return None


def main() -> None:
    task_pages: list[tuple[int, str, st.Page]] = []
    for path in (ROOT / "pages").glob("*.py"):
        navigation = _task_page(path)
        if navigation is None:
            continue
        order, title = navigation
        task_pages.append((order, title, st.Page(str(path), title=title)))

    home_page = st.Page(render_home, title="Home", default=True)
    ordered_task_pages = sorted(task_pages, key=lambda item: item[0])
    page_registry = {"Home": home_page}
    page_registry.update({title: page for _, title, page in ordered_task_pages})
    st.session_state[PAGE_REGISTRY_SESSION_KEY] = page_registry

    pages = list(page_registry.values())
    selected = st.navigation(pages, position="hidden")
    with st.sidebar:
        st.page_link(home_page, label="Home")
        st.page_link(page_registry["Showcase & Handoff"], label="Showcase & Handoff")
        for group_title, page_titles in SIDEBAR_GROUPS:
            with st.expander(group_title, expanded=False):
                for title in page_titles:
                    page = page_registry[title]
                    st.page_link(page, label=title)
        st.page_link(page_registry["Capabilities & Limits"], label="Capabilities & Limits")
        st.divider()
    selected.run()


if __name__ == "__main__":
    main()
