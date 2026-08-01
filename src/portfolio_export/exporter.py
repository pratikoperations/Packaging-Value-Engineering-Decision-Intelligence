from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Mapping

from src.exports import validate_decision_package

EXPORT_SCHEMA_VERSION = "1.0.0"
DATASET_TYPE = "synthetic_demo"
CONFIDENTIALITY_CLASS = "portfolio_synthetic"

TABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "project_summary.csv": (
        "project_id", "project_name", "packaging_category", "project_status",
        "base_currency", "baseline_annual_volume", "annual_volume_unit",
        "dataset_type", "dataset_schema_version", "synthetic_notice",
        "source_repository", "source_commit", "export_batch_id",
    ),
    "scenario_summary.csv": (
        "scenario_id", "project_id", "scenario_name", "scenario_type",
        "annual_volume", "annual_volume_unit", "is_baseline_scenario",
        "scenario_status", "generated_at_utc", "source_commit", "export_batch_id",
    ),
    "alternative_summary.csv": (
        "alternative_key", "project_id", "alternative_id", "alternative_name",
        "design_status", "board_grade", "length_mm", "width_mm", "height_mm",
        "declared_case_weight_g", "is_baseline", "baseline_id",
        "baseline_evidence_id", "export_batch_id",
    ),
    "scenario_results.csv": (
        "scenario_result_id", "scenario_id", "project_id", "alternative_key",
        "alternative_id", "unit_cost", "currency", "unit_cost_unit",
        "annual_cost", "annual_savings_vs_baseline", "case_weight_g",
        "annual_material_kg", "material_change_percent_vs_baseline",
        "cost_adjustment_percent", "material_adjustment_percent", "is_baseline",
        "export_batch_id",
    ),
    "technical_qualification.csv": (
        "scenario_qualification_id", "scenario_id", "project_id", "alternative_key",
        "alternative_id", "qualification_status", "reasons",
        "missing_requirement_ids", "evidence_ids", "validation_required",
        "export_batch_id",
    ),
    "risk_indicators.csv": (
        "scenario_risk_indicator_id", "scenario_id", "project_id", "alternative_key",
        "alternative_id", "risk_type", "declared_level", "probability_percent",
        "effective_level", "overall_risk_level", "data_complete", "reasons",
        "validation_required", "export_batch_id",
    ),
    "recommendations.csv": (
        "scenario_recommendation_id", "scenario_id", "project_id", "alternative_key",
        "alternative_id", "recommendation_status", "is_preferred_alternative",
        "annual_savings_vs_baseline", "material_change_percent_vs_baseline",
        "overall_risk", "qualification_status", "rationale", "constraints",
        "validation_required", "selection_basis", "technical_approval_required",
        "export_batch_id",
    ),
    "assumptions.csv": (
        "assumption_record_id", "scenario_id", "project_id", "alternative_key",
        "alternative_id", "assumption_sequence", "assumption_type",
        "assumption_text", "authoritative_service", "export_batch_id",
    ),
    "data_dictionary.csv": (
        "table_name", "column_name", "data_type", "required_flag",
        "business_definition", "authoritative_service", "schema_version",
    ),
}


def _require_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-empty string.")
    return value.strip()


def _join(values: Any) -> str:
    if values is None:
        return ""
    if isinstance(values, (list, tuple)):
        return " | ".join(str(item) for item in values)
    return str(values)


def _stable_id(*parts: Any) -> str:
    canonical = "||".join(str(part) for part in parts)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def _canonical_scenario_id(project_id: str, scenario_name: str, annual_volume: Any,
                           cost_adjustments: Mapping[str, float],
                           material_adjustments: Mapping[str, float]) -> str:
    payload = {
        "annual_volume": annual_volume,
        "cost_adjustments": dict(sorted(cost_adjustments.items())),
        "material_adjustments": dict(sorted(material_adjustments.items())),
        "project_id": project_id,
        "scenario_name": scenario_name,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{project_id}__{digest}"


def _csv_bytes(rows: list[dict[str, Any]], columns: tuple[str, ...]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in columns})
    return stream.getvalue().encode("utf-8")


def _alternative_records(package: dict[str, Any]) -> list[dict[str, Any]]:
    return [package["baseline"], *package["alternatives"]]


def build_portfolio_export(
    dataset: dict[str, Any],
    decision_package: dict[str, Any],
    *,
    scenario_name: str,
    cost_adjustments: Mapping[str, float],
    material_adjustments: Mapping[str, float],
) -> dict[str, bytes]:
    """Serialize authoritative decision-package outputs into Power BI-ready files.

    No cost, material, qualification, risk, or recommendation formula is reproduced here.
    Values are copied from the validated decision package and governed source dataset.
    """
    validate_decision_package(decision_package)
    metadata = decision_package["metadata"]
    project = decision_package["project"]
    project_id = _require_text(project.get("project_id"), "project.project_id")
    source_commit = _require_text(metadata.get("source_commit"), "metadata.source_commit")
    generated_at = _require_text(metadata.get("generated_at"), "metadata.generated_at")
    dataset_type = _require_text(metadata.get("dataset_type"), "metadata.dataset_type")
    if dataset_type != DATASET_TYPE:
        raise ValueError("Portfolio export is restricted to synthetic_demo datasets.")
    source_repository = _require_text(metadata.get("source_repository"), "metadata.source_repository")
    schema_version = str(metadata.get("schema_version") or dataset.get("schema_version") or "unknown")
    synthetic_notice = str(
        metadata.get("synthetic_disclosure")
        or dataset.get("synthetic_notice")
        or "Synthetic demonstration data only."
    )
    scenario_id = _canonical_scenario_id(
        project_id,
        scenario_name,
        project["annual_volume"],
        cost_adjustments,
        material_adjustments,
    )
    export_batch_id = f"{scenario_id}__{source_commit[:12]}"
    source_alternatives = {
        item["alternative_id"]: item for item in dataset.get("packaging_alternatives", [])
    }
    baseline_specification = dataset.get("baseline_specification", {})
    preferred = decision_package["executive_summary"].get("preferred_alternative_id")
    selection_basis = _join(decision_package["executive_summary"].get("selection_basis", []))

    tables: dict[str, list[dict[str, Any]]] = {name: [] for name in TABLE_COLUMNS}
    tables["project_summary.csv"].append({
        "project_id": project_id,
        "project_name": project["project_name"],
        "packaging_category": project["packaging_category"],
        "project_status": dataset.get("packaging_project", {}).get("status", "active"),
        "base_currency": project["currency"],
        "baseline_annual_volume": dataset.get("packaging_project", {}).get("annual_volume"),
        "annual_volume_unit": project.get("annual_volume_unit"),
        "dataset_type": dataset_type,
        "dataset_schema_version": schema_version,
        "synthetic_notice": synthetic_notice,
        "source_repository": source_repository,
        "source_commit": source_commit,
        "export_batch_id": export_batch_id,
    })
    tables["scenario_summary.csv"].append({
        "scenario_id": scenario_id,
        "project_id": project_id,
        "scenario_name": scenario_name,
        "scenario_type": "governed_user_inputs",
        "annual_volume": project["annual_volume"],
        "annual_volume_unit": project.get("annual_volume_unit"),
        "is_baseline_scenario": all(float(value) == 0 for value in [*cost_adjustments.values(), *material_adjustments.values()]),
        "scenario_status": "evaluated",
        "generated_at_utc": generated_at,
        "source_commit": source_commit,
        "export_batch_id": export_batch_id,
    })

    for alternative in sorted(_alternative_records(decision_package), key=lambda item: item["alternative_id"]):
        alternative_id = alternative["alternative_id"]
        alternative_key = f"{project_id}__{alternative_id}"
        source = source_alternatives.get(alternative_id, {})
        is_baseline = alternative.get("design_status") == "baseline"
        tables["alternative_summary.csv"].append({
            "alternative_key": alternative_key,
            "project_id": project_id,
            "alternative_id": alternative_id,
            "alternative_name": alternative.get("name"),
            "design_status": alternative.get("design_status"),
            "board_grade": alternative.get("specification", {}).get("board_grade"),
            "length_mm": alternative.get("specification", {}).get("length_mm"),
            "width_mm": alternative.get("specification", {}).get("width_mm"),
            "height_mm": alternative.get("specification", {}).get("height_mm"),
            "declared_case_weight_g": source.get("case_weight_g"),
            "is_baseline": is_baseline,
            "baseline_id": baseline_specification.get("baseline_id") if is_baseline else "",
            "baseline_evidence_id": baseline_specification.get("evidence_id") if is_baseline else "",
            "export_batch_id": export_batch_id,
        })
        cost = alternative["cost_and_material"]
        tables["scenario_results.csv"].append({
            "scenario_result_id": _stable_id(scenario_id, alternative_id, "result"),
            "scenario_id": scenario_id,
            "project_id": project_id,
            "alternative_key": alternative_key,
            "alternative_id": alternative_id,
            "unit_cost": cost["unit_cost"],
            "currency": project["currency"],
            "unit_cost_unit": f"{project['currency']}_per_case",
            "annual_cost": cost["annual_cost"],
            "annual_savings_vs_baseline": cost["annual_savings_vs_baseline"],
            "case_weight_g": cost["case_weight_g"],
            "annual_material_kg": cost["annual_material_kg"],
            "material_change_percent_vs_baseline": cost["material_change_percent_vs_baseline"],
            "cost_adjustment_percent": float(cost_adjustments.get(alternative_id, 0.0)),
            "material_adjustment_percent": float(material_adjustments.get(alternative_id, 0.0)),
            "is_baseline": is_baseline,
            "export_batch_id": export_batch_id,
        })
        qualification = alternative["technical_qualification"]
        tables["technical_qualification.csv"].append({
            "scenario_qualification_id": _stable_id(scenario_id, alternative_id, "qualification"),
            "scenario_id": scenario_id,
            "project_id": project_id,
            "alternative_key": alternative_key,
            "alternative_id": alternative_id,
            "qualification_status": qualification["status"],
            "reasons": _join(qualification.get("reasons")),
            "missing_requirement_ids": _join(qualification.get("missing_requirement_ids")),
            "evidence_ids": _join(qualification.get("evidence_ids")),
            "validation_required": _join(qualification.get("validation_required")),
            "export_batch_id": export_batch_id,
        })
        risk = alternative["risk"]
        indicators = risk.get("indicators") or [{
            "risk_type": "not_recorded", "declared_level": "", "probability_percent": "",
            "effective_level": risk.get("overall_level"), "reasons": risk.get("reasons", []),
        }]
        for index, indicator in enumerate(indicators):
            tables["risk_indicators.csv"].append({
                "scenario_risk_indicator_id": _stable_id(scenario_id, alternative_id, "risk", index),
                "scenario_id": scenario_id,
                "project_id": project_id,
                "alternative_key": alternative_key,
                "alternative_id": alternative_id,
                "risk_type": indicator.get("risk_type"),
                "declared_level": indicator.get("declared_level"),
                "probability_percent": indicator.get("probability_percent"),
                "effective_level": indicator.get("effective_level"),
                "overall_risk_level": risk.get("overall_level"),
                "data_complete": risk.get("data_complete"),
                "reasons": _join(indicator.get("reasons") or risk.get("reasons")),
                "validation_required": _join(risk.get("validation_required")),
                "export_batch_id": export_batch_id,
            })
        recommendation = alternative.get("recommendation")
        if recommendation is not None:
            tables["recommendations.csv"].append({
                "scenario_recommendation_id": _stable_id(scenario_id, alternative_id, "recommendation"),
                "scenario_id": scenario_id,
                "project_id": project_id,
                "alternative_key": alternative_key,
                "alternative_id": alternative_id,
                "recommendation_status": recommendation["status"],
                "is_preferred_alternative": alternative_id == preferred,
                "annual_savings_vs_baseline": cost["annual_savings_vs_baseline"],
                "material_change_percent_vs_baseline": cost["material_change_percent_vs_baseline"],
                "overall_risk": risk["overall_level"],
                "qualification_status": qualification["status"],
                "rationale": _join(recommendation.get("rationale")),
                "constraints": _join(recommendation.get("constraints")),
                "validation_required": _join(recommendation.get("validation_required")),
                "selection_basis": selection_basis,
                "technical_approval_required": True,
                "export_batch_id": export_batch_id,
            })
        for sequence, assumption in enumerate(alternative.get("scenario_assumptions", []), start=1):
            tables["assumptions.csv"].append({
                "assumption_record_id": _stable_id(scenario_id, alternative_id, sequence, assumption),
                "scenario_id": scenario_id,
                "project_id": project_id,
                "alternative_key": alternative_key,
                "alternative_id": alternative_id,
                "assumption_sequence": sequence,
                "assumption_type": "scenario_assumption",
                "assumption_text": assumption,
                "authoritative_service": "scenario_engine",
                "export_batch_id": export_batch_id,
            })

    for table_name, columns in TABLE_COLUMNS.items():
        if table_name == "data_dictionary.csv":
            continue
        for column in columns:
            tables["data_dictionary.csv"].append({
                "table_name": table_name,
                "column_name": column,
                "data_type": "text_or_scalar",
                "required_flag": True,
                "business_definition": f"Governed export field {column}.",
                "authoritative_service": "portfolio_export_serialization",
                "schema_version": EXPORT_SCHEMA_VERSION,
            })

    files = {
        name: _csv_bytes(sorted(rows, key=lambda row: tuple(str(row.get(column, "")) for column in TABLE_COLUMNS[name])), TABLE_COLUMNS[name])
        for name, rows in tables.items()
    }
    manifest_files = []
    for name in sorted(files):
        content = files[name]
        row_count = max(0, content.decode("utf-8").count("\n") - 1)
        manifest_files.append({
            "file_name": name,
            "row_count": row_count,
            "column_count": len(TABLE_COLUMNS[name]),
            "sha256": hashlib.sha256(content).hexdigest(),
        })
    manifest = {
        "manifest_schema": "pve_portfolio_export_manifest",
        "manifest_version": EXPORT_SCHEMA_VERSION,
        "export_batch_id": export_batch_id,
        "generated_at_utc": generated_at,
        "source_repository": source_repository,
        "source_commit": source_commit,
        "dataset_type": dataset_type,
        "dataset_schema_version": schema_version,
        "export_schema_version": EXPORT_SCHEMA_VERSION,
        "confidentiality_class": CONFIDENTIALITY_CLASS,
        "files": manifest_files,
        "controls": {
            "read_only": True,
            "synthetic_data_only": True,
            "formulas_recalculated_by_exporter": False,
            "autonomous_technical_approval": False,
            "supplier_allocation": False,
            "production_release": False,
        },
    }
    files["export_manifest.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    return files


def write_portfolio_export(output_dir: Path, files: Mapping[str, bytes]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    for name in sorted(files):
        path = output_dir / name
        path.write_bytes(files[name])
        written[name] = path
    return written
