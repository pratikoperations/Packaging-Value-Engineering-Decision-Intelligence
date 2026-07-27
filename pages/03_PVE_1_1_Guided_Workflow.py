from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

import streamlit as st

from src.application.intake_workflow import commercial_from_context, load_active_context
from src.category_registry import default_registry
from src.reports import build_executive_summary, render_summary_json, render_summary_markdown

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


def _status(label: str, value: str, *, blocker: bool = False) -> None:
    if blocker:
        st.error(f"{label}: {value}")
    elif value:
        st.success(f"{label}: {value}")
    else:
        st.info(f"{label}: Not available")


def source_traceability_rows(value: Any, prefix: str = "") -> list[dict[str, str]]:
    """Flatten recorded source references for a business-readable table."""
    rows: list[dict[str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            label = str(key).replace("_", " ").title()
            child_prefix = f"{prefix} — {label}" if prefix else label
            rows.extend(source_traceability_rows(child, child_prefix))
    elif isinstance(value, list):
        for index, child in enumerate(value, start=1):
            item_prefix = f"{prefix} {index}" if len(value) > 1 else prefix
            rows.extend(source_traceability_rows(child, item_prefix))
    elif prefix:
        if isinstance(value, bool):
            display = "Yes" if value else "No"
        elif value is None or value == "":
            display = "Not recorded"
        else:
            display = str(value).replace("_", " ")
        rows.append({"Source reference": prefix, "Recorded value": display})
    return rows


def main() -> None:
    st.set_page_config(page_title="PVE 1.1 Guided Workflow", layout="wide")
    st.title("PVE 1.1 Guided Intake and Validation Readiness")
    st.caption("Deterministic all-category readiness, commercial opportunity, evidence guidance, and controlled reporting")
    st.warning("Readiness is not technical approval. Engineering validation and documented human approval remain mandatory.")

    project_id = st.session_state.get("active_project_id")
    if not project_id:
        st.info("Select an active project from the Project Dashboard, then upload and save a validated dataset.")
        st.stop()
    try:
        project, dataset, context = load_active_context(DATABASE_PATH, str(project_id))
    except (KeyError, ValueError) as error:
        st.error(str(error))
        st.stop()

    canonical = context["canonical"]
    assessment = context["assessment"]
    registry_key = "corrugated" if project["category"] == "corrugated_shipping_case" else project["category"]
    definition = default_registry().get(registry_key)

    st.success(f"Active project: {project['project_code']} — {project['project_name']}")
    overview = st.columns(4)
    overview[0].metric("Category", definition.display_name)
    overview[1].metric("Objective", project.get("objective") or "Not recorded")
    overview[2].metric("Change type", project.get("change_type") or "Not recorded")
    overview[3].metric("Dataset version", dataset["version_number"])

    guidance, readiness_tab, commercial_tab, testing_tab, report_tab = st.tabs([
        "Input Guidance", "Readiness", "Commercial & ROI", "Testing & Evidence", "Executive Report"
    ])

    with guidance:
        st.subheader("Category-specific requirements")
        rows = [{"Field": field.label, "Requirement": field.requirement, "Type": field.value_type, "Accepted units": ", ".join(field.units), "Critical": field.critical} for field in definition.fields]
        st.dataframe(rows, width="stretch", hide_index=True)
        st.subheader("Category warnings")
        for warning in definition.warnings:
            st.warning(warning)
        st.info("Use the Upload and Validation page to download the category/objective/change-type-specific Excel workbook.")

    with readiness_tab:
        left, right = st.columns(2)
        left.metric("Readiness percentage", f"{assessment.score_percent:.1f}%")
        right.metric("Current stage", assessment.stage)
        st.progress(min(max(assessment.score_percent / 100.0, 0.0), 1.0))
        st.subheader("Weighted components")
        st.dataframe([{"Component": item.label, "Weight": item.weight, "Completed": item.completed, "Required": item.total, "Weighted score": round(item.weighted_score, 1)} for item in assessment.component_scores], width="stretch", hide_index=True)
        st.subheader("Blocking issues")
        if assessment.blockers:
            for blocker in assessment.blockers:
                st.error(blocker)
        else:
            st.success("No readiness blocker is currently recorded.")
        st.subheader("Output availability")
        for output in assessment.outputs:
            if output.available:
                st.success(f"{output.name}: available")
            else:
                reasons = "; ".join(output.reasons) or "Requirements are not met."
                st.warning(f"{output.name}: unavailable — {reasons}")
        st.subheader("Source traceability")
        traceability_rows = source_traceability_rows(assessment.source_traceability)
        if traceability_rows:
            st.dataframe(traceability_rows, width="stretch", hide_index=True)
        else:
            st.info(
                "No additional source references are recorded for this synthetic demonstration dataset."
            )

    with commercial_tab:
        analysis, reasons = commercial_from_context(project, canonical)
        if analysis is None:
            st.warning("Commercial and ROI outputs are unavailable.")
            for reason in reasons:
                st.write(f"- {reason}")
        else:
            metrics = st.columns(4)
            metrics[0].metric("Saving per unit (estimate)", f"{analysis.saving_per_unit:,.2f}")
            metrics[1].metric("Annual gross saving (estimate)", f"{analysis.annual_gross_saving:,.2f}")
            metrics[2].metric("First-year net benefit (estimate)", f"{analysis.first_year_net_benefit:,.2f}")
            metrics[3].metric("Payback months (estimate)", "Unavailable" if analysis.payback_months is None else f"{analysis.payback_months:,.1f}")
            st.write(f"Expected realized saving: {analysis.expected_realized_saving:,.2f}")
            st.write(f"Percentage cost reduction: {analysis.percentage_cost_reduction:,.2f}%")
            for label in analysis.labels.values():
                st.caption(label)
            if analysis.assumptions:
                st.write("**Retained user assumptions**")
                for assumption in analysis.assumptions:
                    st.write(f"- {assumption}")

    with testing_tab:
        st.subheader("Configured testing checklist")
        st.dataframe([{"Test": item.name, "Critical": item.critical, "Applies to": ", ".join(item.applies_to)} for item in definition.tests], width="stretch", hide_index=True)
        st.subheader("Recorded quality evidence")
        recorded = canonical.get("quality_tests") or []
        if recorded:
            st.dataframe(recorded, width="stretch", hide_index=True)
        else:
            st.warning("No quality-test evidence is recorded.")
        st.subheader("Document register")
        documents = canonical.get("document_register") or []
        if documents:
            st.dataframe(documents, width="stretch", hide_index=True)
        else:
            st.warning("No document-register entries are recorded.")

    with report_tab:
        summary = build_executive_summary(project=project, canonical_data=canonical, assessment=assessment)
        json_report = render_summary_json(summary)
        markdown_report = render_summary_markdown(summary)
        st.download_button("Download machine-readable readiness JSON", json_report, "pve_1_1_readiness_summary.json", "application/json", width="stretch")
        st.download_button("Download human-readable executive report", markdown_report, "pve_1_1_executive_summary.md", "text/markdown", width="stretch")
        st.markdown(markdown_report)

    st.info(assessment.approval_limitation)


if __name__ == "__main__":
    main()
