from __future__ import annotations

import json
from typing import Any

from src.recommendation import RecommendationResult
from src.risk_engine import RiskOutcome
from src.scenario_engine import ScenarioResult
from src.technical_qualification import QualificationOutcome


PACKAGE_VERSION = "0.6.0-decision-package"
PACKAGE_SCHEMA = "pve_internal_decision_package"
_REQUIRED_TOP_LEVEL = (
    "metadata",
    "executive_summary",
    "project",
    "scenario",
    "baseline",
    "alternatives",
    "decision_controls",
)


def _require_non_empty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-empty string.")
    return value.strip()


def _as_list(values: tuple[str, ...] | list[str]) -> list[str]:
    return list(values)


def assemble_decision_package(
    dataset: dict[str, Any],
    scenario: ScenarioResult,
    qualifications: dict[str, QualificationOutcome],
    risks: dict[str, RiskOutcome],
    recommendation: RecommendationResult,
    *,
    source_commit: str,
    generated_at: str,
) -> dict[str, Any]:
    """Assemble a deterministic, read-only internal decision package.

    The caller supplies source_commit and generated_at so the same explicit inputs
    always produce the same package. This is not the frozen integration contract.
    """
    source_commit = _require_non_empty_string(source_commit, "source_commit")
    generated_at = _require_non_empty_string(generated_at, "generated_at")

    project = dataset.get("packaging_project")
    alternatives = dataset.get("packaging_alternatives")
    baseline_specification = dataset.get("baseline_specification")
    export_metadata = dataset.get("export_metadata", {})
    if not isinstance(project, dict):
        raise ValueError("packaging_project must be an object.")
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError("packaging_alternatives must be a non-empty list.")
    if not isinstance(baseline_specification, dict):
        raise ValueError("baseline_specification must be an object.")

    project_id = _require_non_empty_string(project.get("project_id"), "packaging_project.project_id")
    project_name = _require_non_empty_string(project.get("project_name"), "packaging_project.project_name")
    category = _require_non_empty_string(project.get("category"), "packaging_project.category")
    currency = _require_non_empty_string(project.get("currency"), "packaging_project.currency")
    source_repository = _require_non_empty_string(
        export_metadata.get(
            "source_repository",
            "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
        ),
        "export_metadata.source_repository",
    )

    alternative_records: dict[str, dict[str, Any]] = {}
    baseline_id: str | None = None
    for record in alternatives:
        if not isinstance(record, dict):
            raise ValueError("Every packaging alternative must be an object.")
        alternative_id = _require_non_empty_string(record.get("alternative_id"), "alternative_id")
        if alternative_id in alternative_records:
            raise ValueError("Alternative identifiers must be unique.")
        alternative_records[alternative_id] = record
        if record.get("status") == "baseline":
            if baseline_id is not None:
                raise ValueError("Exactly one baseline alternative is required.")
            baseline_id = alternative_id

    if baseline_id is None:
        raise ValueError("Exactly one baseline alternative is required.")
    if baseline_specification.get("alternative_id") != baseline_id:
        raise ValueError("baseline_specification must reference the baseline alternative.")

    all_ids = set(alternative_records)
    for label, keys in (
        ("scenario", set(scenario.alternatives)),
        ("qualifications", set(qualifications)),
        ("risks", set(risks)),
    ):
        missing = all_ids - keys
        if missing:
            raise ValueError(f"{label} missing alternatives: {', '.join(sorted(missing))}.")

    proposed_ids = sorted(
        alternative_id
        for alternative_id, record in alternative_records.items()
        if record.get("status") == "proposed"
    )
    missing_recommendations = set(proposed_ids) - set(recommendation.alternatives)
    if missing_recommendations:
        raise ValueError(
            "recommendation missing alternatives: "
            + ", ".join(sorted(missing_recommendations))
            + "."
        )

    def build_alternative(alternative_id: str) -> dict[str, Any]:
        record = alternative_records[alternative_id]
        scenario_result = scenario.alternatives[alternative_id]
        qualification = qualifications[alternative_id]
        risk = risks[alternative_id]
        recommendation_result = recommendation.alternatives.get(alternative_id)
        return {
            "alternative_id": alternative_id,
            "name": record.get("name"),
            "design_status": record.get("status"),
            "specification": {
                "length_mm": record.get("length_mm"),
                "width_mm": record.get("width_mm"),
                "height_mm": record.get("height_mm"),
                "board_grade": record.get("board_grade"),
            },
            "scenario_assumptions": _as_list(scenario_result.assumptions),
            "cost_and_material": {
                "unit_cost": scenario_result.unit_cost,
                "annual_cost": scenario_result.annual_cost,
                "annual_savings_vs_baseline": scenario_result.annual_savings_vs_baseline,
                "case_weight_g": scenario_result.case_weight_g,
                "annual_material_kg": scenario_result.annual_material_kg,
                "material_change_percent_vs_baseline": scenario_result.material_change_percent_vs_baseline,
            },
            "technical_qualification": {
                "status": qualification.status,
                "reasons": _as_list(qualification.reasons),
                "missing_requirement_ids": _as_list(qualification.missing_requirement_ids),
                "evidence_ids": _as_list(qualification.evidence_ids),
                "validation_required": _as_list(qualification.validation_required),
            },
            "risk": {
                "overall_level": risk.overall_level,
                "data_complete": risk.data_complete,
                "reasons": _as_list(risk.reasons),
                "validation_required": _as_list(risk.validation_required),
                "indicators": [
                    {
                        "risk_type": indicator.risk_type,
                        "declared_level": indicator.declared_level,
                        "probability_percent": indicator.probability_percent,
                        "effective_level": indicator.effective_level,
                        "reasons": _as_list(indicator.reasons),
                    }
                    for indicator in risk.indicators
                ],
            },
            "recommendation": None
            if recommendation_result is None
            else {
                "status": recommendation_result.status,
                "rationale": _as_list(recommendation_result.rationale),
                "constraints": _as_list(recommendation_result.constraints),
                "validation_required": _as_list(recommendation_result.validation_required),
            },
        }

    baseline = build_alternative(baseline_id)
    proposed = [build_alternative(alternative_id) for alternative_id in proposed_ids]

    preferred = recommendation.preferred_alternative_id
    preferred_status = (
        recommendation.alternatives[preferred].status if preferred is not None else "no_preferred_alternative"
    )
    preferred_name = alternative_records[preferred].get("name") if preferred else None
    executive_summary = {
        "decision_status": preferred_status,
        "preferred_alternative_id": preferred,
        "preferred_alternative_name": preferred_name,
        "summary": (
            f"Preferred packaging alternative: {preferred} — {preferred_name}."
            if preferred
            else "No proposed packaging alternative currently passes the recommendation gate."
        ),
        "selection_basis": _as_list(recommendation.selection_basis),
        "technical_approval_required": True,
    }

    package = {
        "metadata": {
            "package_schema": PACKAGE_SCHEMA,
            "package_version": PACKAGE_VERSION,
            "contract_status": "internal_export_not_final_integration_contract",
            "source_repository": source_repository,
            "source_commit": source_commit,
            "generated_at": generated_at,
            "dataset_type": dataset.get("dataset_type"),
            "schema_version": dataset.get("schema_version"),
        },
        "executive_summary": executive_summary,
        "project": {
            "project_id": project_id,
            "project_name": project_name,
            "packaging_category": category,
            "annual_volume": scenario.annual_volume,
            "annual_volume_unit": project.get("annual_volume_unit"),
            "currency": currency,
        },
        "scenario": {
            "annual_volume": scenario.annual_volume,
            "alternative_ids": sorted(all_ids),
        },
        "baseline": baseline,
        "alternatives": proposed,
        "decision_controls": {
            "read_only": True,
            "autonomous_technical_approval": False,
            "supplier_allocation": False,
            "external_system_integration": False,
            "integration_contract_finalized": False,
            "engineering_validation_required": True,
        },
    }
    validate_decision_package(package)
    return package


def validate_decision_package(package: dict[str, Any]) -> None:
    if not isinstance(package, dict):
        raise ValueError("Decision package must be an object.")
    missing = [key for key in _REQUIRED_TOP_LEVEL if key not in package]
    if missing:
        raise ValueError(f"Decision package missing top-level sections: {', '.join(missing)}.")

    metadata = package["metadata"]
    project = package["project"]
    controls = package["decision_controls"]
    alternatives = package["alternatives"]
    if not isinstance(metadata, dict) or not isinstance(project, dict) or not isinstance(controls, dict):
        raise ValueError("Metadata, project, and decision_controls must be objects.")
    if not isinstance(alternatives, list):
        raise ValueError("alternatives must be a list.")

    for field in ("package_schema", "package_version", "source_repository", "source_commit", "generated_at"):
        _require_non_empty_string(metadata.get(field), f"metadata.{field}")
    for field in ("project_id", "project_name", "packaging_category", "currency"):
        _require_non_empty_string(project.get(field), f"project.{field}")
    if not isinstance(project.get("annual_volume"), (int, float)) or project["annual_volume"] <= 0:
        raise ValueError("project.annual_volume must be greater than zero.")

    required_controls = {
        "read_only": True,
        "autonomous_technical_approval": False,
        "supplier_allocation": False,
        "external_system_integration": False,
        "integration_contract_finalized": False,
        "engineering_validation_required": True,
    }
    for key, expected in required_controls.items():
        if controls.get(key) is not expected:
            raise ValueError(f"decision_controls.{key} must be {expected}.")

    baseline = package["baseline"]
    if not isinstance(baseline, dict) or baseline.get("design_status") != "baseline":
        raise ValueError("baseline must be the baseline packaging alternative.")

    seen_ids = {baseline.get("alternative_id")}
    for index, alternative in enumerate(alternatives):
        if not isinstance(alternative, dict):
            raise ValueError(f"alternatives.{index} must be an object.")
        alternative_id = _require_non_empty_string(
            alternative.get("alternative_id"), f"alternatives.{index}.alternative_id"
        )
        if alternative_id in seen_ids:
            raise ValueError("Exported alternative identifiers must be unique.")
        seen_ids.add(alternative_id)
        for section in ("cost_and_material", "technical_qualification", "risk", "recommendation"):
            if not isinstance(alternative.get(section), dict):
                raise ValueError(f"alternatives.{index}.{section} must be an object.")


def render_decision_package_json(package: dict[str, Any]) -> str:
    validate_decision_package(package)
    return json.dumps(package, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_decision_package_markdown(package: dict[str, Any]) -> str:
    validate_decision_package(package)
    project = package["project"]
    summary = package["executive_summary"]
    lines = [
        "# Packaging Value Engineering Decision Package",
        "",
        f"**Project:** {project['project_name']} (`{project['project_id']}`)",
        f"**Category:** {project['packaging_category']}",
        f"**Annual volume:** {project['annual_volume']:,.0f} {project.get('annual_volume_unit') or ''}".rstrip(),
        f"**Currency:** {project['currency']}",
        f"**Decision status:** {summary['decision_status']}",
        f"**Preferred alternative:** {summary['preferred_alternative_id'] or 'None'}",
        "",
        "## Executive Summary",
        "",
        summary["summary"],
        "",
        "## Scenario Assumptions",
        "",
    ]
    for alternative in [package["baseline"], *package["alternatives"]]:
        lines.append(f"### {alternative['alternative_id']} — {alternative['name']}")
        for assumption in alternative["scenario_assumptions"]:
            lines.append(f"- {assumption}")
        lines.append("")

    lines.extend(["## Alternative Comparison", ""])
    for alternative in package["alternatives"]:
        cost = alternative["cost_and_material"]
        qualification = alternative["technical_qualification"]
        risk = alternative["risk"]
        recommendation = alternative["recommendation"]
        lines.extend(
            [
                f"### {alternative['alternative_id']} — {alternative['name']}",
                f"- Recommendation: {recommendation['status']}",
                f"- Unit cost: {cost['unit_cost']:.2f}",
                f"- Annual savings vs baseline: {cost['annual_savings_vs_baseline']:.2f}",
                f"- Material change vs baseline: {cost['material_change_percent_vs_baseline']:.2f}%",
                f"- Technical qualification: {qualification['status']}",
                f"- Overall risk: {risk['overall_level']} (data complete: {risk['data_complete']})",
                "- Rationale:",
            ]
        )
        lines.extend(f"  - {item}" for item in recommendation["rationale"])
        lines.append("- Constraints:")
        lines.extend(f"  - {item}" for item in recommendation["constraints"] or ["None"])
        lines.append("- Validation required:")
        lines.extend(f"  - {item}" for item in recommendation["validation_required"] or ["None"])
        lines.append("")

    lines.extend(
        [
            "## Decision Controls",
            "",
            "- Read-only export: Yes",
            "- Autonomous technical approval: No",
            "- Supplier allocation: No",
            "- External system integration: No",
            "- Final integration contract: No — draft remains unchanged",
            "- Engineering validation required: Yes",
            "",
            "## Package Metadata",
            "",
            f"- Package version: {package['metadata']['package_version']}",
            f"- Source repository: {package['metadata']['source_repository']}",
            f"- Source commit: {package['metadata']['source_commit']}",
            f"- Generated at: {package['metadata']['generated_at']}",
        ]
    )
    return "\n".join(lines) + "\n"
