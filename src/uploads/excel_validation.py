from __future__ import annotations

from typing import Any

from src.category_registry import default_registry
from src.data_models.validator import ValidationIssue, ValidationResult
from src.templates.excel_schema import (
    DOCUMENT_HEADERS,
    PROJECT_HEADERS,
    QUALITY_HEADERS,
    SOURCE_CLASSIFICATIONS,
)


def _issue(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code, path, message))


def _field_map(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("field_key")): row for row in rows if row.get("field_key")}


def _check_headers(raw: dict[str, list[dict[str, Any]]], issues: list[ValidationIssue]) -> None:
    expected = {
        "PROJECT": PROJECT_HEADERS,
        "BASELINE": PROJECT_HEADERS,
        "PROPOSED": PROJECT_HEADERS,
        "COMMERCIAL": PROJECT_HEADERS,
        "LOGISTICS": PROJECT_HEADERS,
        "QUALITY_TESTS": QUALITY_HEADERS,
        "DOCUMENT_REGISTER": DOCUMENT_HEADERS,
    }
    for sheet, headers in expected.items():
        rows = raw.get(sheet, [])
        if not rows:
            _issue(issues, "empty_sheet", sheet, "Required worksheet contains no data rows.")
            continue
        present = set(rows[0])
        missing = [header for header in headers if header not in present]
        if missing:
            _issue(issues, "missing_columns", sheet, f"Missing required columns: {', '.join(missing)}")


def validate_excel_workbook(raw: dict[str, list[dict[str, Any]]], canonical: dict[str, Any], project: dict[str, Any]) -> ValidationResult:
    issues: list[ValidationIssue] = []
    _check_headers(raw, issues)

    project_values = _field_map(raw.get("PROJECT", []))
    category = canonical["packaging_project"].get("category")
    objective = canonical["packaging_project"].get("objective")
    change_type = canonical["packaging_project"].get("change_type")
    registry = default_registry()
    try:
        definition = registry.get(str(category))
    except KeyError:
        _issue(issues, "invalid_category", "PROJECT.category", "Workbook category is not supported.")
        definition = None

    if category != project["category"]:
        _issue(issues, "category_mismatch", "PROJECT.category", "Workbook category must match the active project.")
    if definition and not definition.supports_objective(str(objective)):
        _issue(issues, "invalid_objective", "PROJECT.objective", "Workbook objective is not supported.")
    if definition and not definition.supports_change_type(str(change_type)):
        _issue(issues, "invalid_change_type", "PROJECT.change_type", "Workbook change type is not supported for the category.")

    for key in ("project_code", "project_name", "category", "objective", "change_type", "product_sku", "business_unit_plant", "project_owner", "currency", "volume_unit"):
        row = project_values.get(key)
        if not row or row.get("value") in (None, ""):
            _issue(issues, "missing_required", f"PROJECT.{key}", "Mandatory project value is missing.")

    contexts = {record.get("context") for record in canonical.get("intake_values", []) if record.get("value") not in (None, "")}
    if "baseline" not in contexts:
        _issue(issues, "invalid_baseline_count", "BASELINE", "Exactly one populated baseline section is required.")
    if "proposed" not in contexts:
        _issue(issues, "missing_proposal", "PROPOSED", "At least one populated proposal is required.")

    allowed_sources = set(SOURCE_CLASSIFICATIONS)
    for index, record in enumerate(canonical.get("intake_values", [])):
        value = record.get("value")
        if value in (None, ""):
            if record.get("requirement") == "mandatory":
                _issue(issues, "missing_required", f"intake_values.{index}.value", "Mandatory value is missing.")
            continue
        source = record.get("source_classification")
        if source not in allowed_sources:
            _issue(issues, "invalid_source_classification", f"intake_values.{index}.source_classification", "Source classification is required and must be supported.")
        if definition:
            field = next((item for item in definition.fields if item.key == record.get("field_key")), None)
            if field:
                unit = record.get("unit")
                if field.units and unit not in field.units:
                    _issue(issues, "invalid_unit", f"intake_values.{index}.unit", f"Unit must be one of: {', '.join(field.units)}")
                if field.value_type in {"number", "integer"}:
                    try:
                        number = float(value)
                    except (TypeError, ValueError):
                        _issue(issues, "invalid_number", f"intake_values.{index}.value", "Value must be numeric.")
                    else:
                        if field.minimum is not None and number < field.minimum:
                            _issue(issues, "out_of_range", f"intake_values.{index}.value", "Value is below the allowed minimum.")
                        if field.maximum is not None and number > field.maximum:
                            _issue(issues, "out_of_range", f"intake_values.{index}.value", "Value exceeds the allowed maximum.")

    return ValidationResult(tuple(issues), True)
