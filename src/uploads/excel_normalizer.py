from __future__ import annotations

from typing import Any

from src.templates.excel_schema import SOURCE_CLASSIFICATIONS


def _clean(value: Any) -> Any:
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return None
    return value


def _field_map(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for row in rows:
        key = _clean(row.get("field_key"))
        if key:
            result[str(key)] = _clean(row.get("value"))
    return result


def _normalize_value_rows(rows: list[dict[str, Any]], context: str) -> list[dict[str, Any]]:
    normalized = []
    for row in rows:
        key = _clean(row.get("field_key"))
        if not key:
            continue
        normalized.append({
            "context": context,
            "field_key": str(key),
            "value": _clean(row.get("value")),
            "unit": _clean(row.get("unit")),
            "requirement": _clean(row.get("requirement")),
            "source_classification": _clean(row.get("source_classification")),
            "evidence_reference": _clean(row.get("evidence_reference")),
            "supplier_name": _clean(row.get("supplier_name")),
            "test_date": _clean(row.get("test_date")),
            "validation_status": _clean(row.get("validation_status")),
        })
    return normalized


def normalize_excel_workbook(raw: dict[str, list[dict[str, Any]]], project: dict[str, Any]) -> dict[str, Any]:
    project_values = _field_map(raw["PROJECT"])
    commercial_values = _field_map(raw["COMMERCIAL"])
    logistics_values = _field_map(raw["LOGISTICS"])

    uploaded_category = project_values.get("category") or project["category"]
    canonical = {
        "dataset_type": "user_upload",
        "schema_version": "1.1-excel-intake",
        "packaging_project": {
            "project_id": project["project_id"],
            "project_name": project_values.get("project_name") or project["project_name"],
            "category": uploaded_category,
            "objective": project_values.get("objective") or project.get("objective"),
            "change_type": project_values.get("change_type") or project.get("change_type"),
            "annual_volume": commercial_values.get("annual_volume") or project["annual_volume"],
            "annual_volume_unit": project_values.get("volume_unit") or project.get("volume_unit") or "units/year",
            "currency": project_values.get("currency") or project["currency"],
            "status": "active",
        },
        "intake_values": (
            _normalize_value_rows(raw["BASELINE"], "baseline")
            + _normalize_value_rows(raw["PROPOSED"], "proposed")
            + _normalize_value_rows(raw["COMMERCIAL"], "commercial")
            + _normalize_value_rows(raw["LOGISTICS"], "logistics")
        ),
        "quality_tests": [dict(row) for row in raw["QUALITY_TESTS"]],
        "document_register": [dict(row) for row in raw["DOCUMENT_REGISTER"]],
        "decision_recommendation": {
            "recommendation_id": "REC-UPLOAD-PLACEHOLDER",
            "status": "insufficient_data",
            "rationale": "Excel intake uploaded for validation readiness only. No autonomous approval is granted.",
        },
        "export_metadata": {
            "contract_version": "PVE-CONTRACT-v1.1-INTAKE",
            "source_repository": "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
            "source_commit": "USER-EXCEL-UPLOAD",
        },
    }
    for name in ("decision_evidence", "packaging_alternatives", "material_components", "cost_inputs", "logistics_inputs", "technical_requirements", "technical_qualification_results", "risk_records", "sustainability_indicators", "validation_requirements"):
        canonical[name] = []
    canonical["baseline_specification"] = {"baseline_id": "BASE-UPLOAD-001"}
    return canonical


def valid_source_classification(value: Any) -> bool:
    return value in SOURCE_CLASSIFICATIONS
