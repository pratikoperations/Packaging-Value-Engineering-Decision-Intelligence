from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from src.commercial import calculate_commercial_analysis
from src.validation_readiness.models import ReadinessAssessment


def _value_map(canonical_data: dict[str, Any], context: str) -> dict[str, Any]:
    return {
        str(row.get("field_key")): row.get("value")
        for row in canonical_data.get("intake_values", [])
        if row.get("context") == context and row.get("field_key")
    }


def _commercial(canonical_data: dict[str, Any], project: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    values = _value_map(canonical_data, "commercial")
    annual_volume = values.get("annual_volume") or project.get("annual_volume")
    current = values.get("current_unit_cost") or project.get("current_unit_cost")
    proposed = values.get("proposed_unit_cost") or project.get("proposed_unit_cost")
    missing = [name for name, value in (("annual_volume", annual_volume), ("current_unit_cost", current), ("proposed_unit_cost", proposed)) if value in (None, "")]
    if missing:
        return None, [f"Missing required commercial input: {name}" for name in missing]
    try:
        analysis = calculate_commercial_analysis(
            current_unit_cost=float(current),
            proposed_unit_cost=float(proposed),
            annual_volume=float(annual_volume),
            realization_percent=float(values.get("realization_percent") or project.get("expected_realization_percent") or 100),
            testing_cost=float(values.get("testing_cost") or project.get("testing_cost") or 0),
            tooling_cost=float(values.get("tooling_cost") or project.get("tooling_cost") or 0),
            implementation_cost=float(values.get("implementation_cost") or project.get("implementation_cost") or 0),
            qualification_cost=float(values.get("qualification_cost") or project.get("qualification_cost") or 0),
            assumptions=tuple(
                str(row.get("field_key"))
                for row in canonical_data.get("intake_values", [])
                if row.get("context") == "commercial" and row.get("source_classification") == "assumption"
            ),
        )
    except (TypeError, ValueError) as error:
        return None, [str(error)]
    return asdict(analysis), []


def build_executive_summary(*, project: dict[str, Any], canonical_data: dict[str, Any], assessment: ReadinessAssessment) -> dict[str, Any]:
    commercial, commercial_reasons = _commercial(canonical_data, project)
    unavailable = [
        {"output": item.name, "reasons": list(item.reasons)}
        for item in assessment.outputs if not item.available
    ]
    if commercial is None:
        unavailable.append({"output": "commercial_analysis", "reasons": commercial_reasons})
    return {
        "report_type": "PVE_1.1_INTAKE_READINESS_EXECUTIVE_SUMMARY",
        "project_summary": {
            "project_id": project.get("project_id"),
            "project_code": project.get("project_code"),
            "project_name": project.get("project_name"),
            "packaging_category": project.get("category"),
            "objective": project.get("objective"),
            "change_type": project.get("change_type"),
        },
        "readiness": assessment.as_dict(),
        "missing_mandatory_inputs": list(assessment.blockers),
        "blocking_issues": list(assessment.blockers),
        "document_status": canonical_data.get("document_register", []),
        "commercial_opportunity": commercial,
        "test_requirements": canonical_data.get("quality_tests", []),
        "available_outputs": [item.name for item in assessment.outputs if item.available],
        "unavailable_outputs": unavailable,
        "risks_and_assumptions": {
            "source_traceability": dict(assessment.source_traceability),
            "assumptions": commercial.get("assumptions", []) if commercial else [],
        },
        "recommended_next_actions": list(assessment.blockers) or ["Proceed to the next controlled validation stage."],
        "approval_limitation": assessment.approval_limitation,
        "source_traceability": dict(assessment.source_traceability),
    }


def render_summary_json(summary: dict[str, Any]) -> str:
    return json.dumps(summary, indent=2, sort_keys=True, default=str)


def render_summary_markdown(summary: dict[str, Any]) -> str:
    project = summary["project_summary"]
    readiness = summary["readiness"]
    lines = [
        "# PVE 1.1 Executive Intake and Readiness Summary",
        "",
        f"- Project: {project.get('project_code')} — {project.get('project_name')}",
        f"- Category: {project.get('packaging_category')}",
        f"- Objective: {project.get('objective')}",
        f"- Change type: {project.get('change_type')}",
        f"- Readiness: {readiness.get('score_percent')}%",
        f"- Stage: {readiness.get('stage')}",
        "",
        "## Blocking Issues",
    ]
    blockers = summary["blocking_issues"]
    lines.extend([f"- {item}" for item in blockers] or ["- None recorded"])
    lines.extend(["", "## Available Outputs"])
    lines.extend([f"- {item}" for item in summary["available_outputs"]] or ["- None"])
    lines.extend(["", "## Unavailable Outputs"])
    for item in summary["unavailable_outputs"]:
        reasons = "; ".join(item.get("reasons") or ["Requirements are not met."])
        lines.append(f"- {item['output']}: {reasons}")
    lines.extend(["", "## Commercial Opportunity"])
    commercial = summary.get("commercial_opportunity")
    if commercial:
        for key in ("saving_per_unit", "annual_gross_saving", "expected_realized_saving", "first_year_net_benefit", "payback_months", "percentage_cost_reduction"):
            lines.append(f"- {key.replace('_', ' ').title()}: {commercial.get(key)}")
        lines.append("- All commercial outputs are estimates based on entered inputs and assumptions.")
    else:
        lines.append("- Unavailable; see unavailable-output reasons.")
    lines.extend(["", "## Approval Limitation", summary["approval_limitation"], ""])
    return "\n".join(lines)
