from __future__ import annotations

import json
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
from src.technical_qualification import evaluate_technical_qualification


ROOT = Path(__file__).resolve().parent
DEMO_PATH = ROOT / "data" / "demo" / "corrugated_shipping_cases.json"
SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"


@st.cache_data
def load_demo() -> dict:
    return json.loads(DEMO_PATH.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="PVE Decision Intelligence", layout="wide")
    st.title("Packaging Value Engineering Decision Intelligence")
    st.caption("Deterministic scenario comparison, explainable recommendation, and read-only decision export")
    st.warning(
        "This application uses synthetic demonstration data only. "
        "It must not be treated as validated supplier, laboratory, production, "
        "engineering-trial, or commercial data."
    )

    dataset = load_demo()
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
                key=f"cost-{alternative_id}",
            )
            material_adjustments[alternative_id] = st.number_input(
                "Material-weight adjustment (%)",
                min_value=-50.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
                key=f"material-{alternative_id}",
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
    st.dataframe(comparison_rows, use_container_width=True, hide_index=True)

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
            if result.constraints:
                for item in result.constraints:
                    st.write(f"- {item}")
            else:
                st.write("- None")
            st.write("**Validation required**")
            if result.validation_required:
                for item in result.validation_required:
                    st.write(f"- {item}")
            else:
                st.write("- None")

    st.subheader("Decision Package Export")
    source_commit = st.text_input(
        "Source commit or version reference",
        value="LOCAL-DEMO",
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
    json_export = render_decision_package_json(package)
    markdown_export = render_decision_package_markdown(package)

    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download machine-readable JSON",
            data=json_export,
            file_name="pve_decision_package.json",
            mime="application/json",
            use_container_width=True,
        )
    with right:
        st.download_button(
            "Download human-readable report",
            data=markdown_export,
            file_name="pve_decision_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.caption(
        f"Read-only internal export from {SOURCE_REPOSITORY}. The final integration contract remains draft."
    )
    st.info(
        "This tool does not approve packaging designs autonomously. Recommendations and exports remain subject to engineering validation and documented evidence."
    )


if __name__ == "__main__":
    main()
