from __future__ import annotations

from typing import Any, Iterable

from src.data_models.validator import ValidationIssue, ValidationResult

_ALLOWED = {
    "project_status": {"draft", "active", "on_hold", "completed"},
    "alternative_status": {"baseline", "proposed", "screened_out"},
    "technical_status": {
        "not_assessed",
        "qualified",
        "conditionally_qualified",
        "not_qualified",
        "insufficient_data",
    },
    "risk_level": {"low", "medium", "high", "critical"},
    "risk_type": {"quality", "supply", "implementation", "logistics", "compliance", "sustainability"},
    "validation_status": {"not_started", "planned", "in_progress", "passed", "failed", "waived"},
    "board_grade": {"3PLY_B_FLUTE", "5PLY_BC_FLUTE", "3PLY_C_FLUTE", "5PLY_EB_FLUTE"},
    "currency": {"INR", "USD", "EUR", "GBP"},
}


def _issue(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code, path, message))


def _required(mapping: dict[str, Any], fields: Iterable[str], prefix: str, issues: list[ValidationIssue]) -> None:
    for field in fields:
        if field not in mapping or mapping[field] in (None, ""):
            _issue(issues, "missing_required", f"{prefix}.{field}", "Required field is missing or empty.")


def _positive(value: Any, path: str, issues: list[ValidationIssue], *, allow_zero: bool = False) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        _issue(issues, "invalid_number", path, "Value must be numeric.")
        return
    if value < 0 or (value == 0 and not allow_zero):
        _issue(issues, "out_of_range", path, "Value is outside the permitted range.")


def _percentage(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
        _issue(issues, "invalid_percentage", path, "Percentage must be between 0 and 100 inclusive.")


def _enum(value: Any, allowed: set[str], path: str, issues: list[ValidationIssue]) -> None:
    if value not in allowed:
        _issue(issues, "invalid_enum", path, f"Unsupported value: {value!r}.")


def _list(data: dict[str, Any], name: str, issues: list[ValidationIssue]) -> list[dict[str, Any]]:
    value = data.get(name, [])
    if not isinstance(value, list):
        _issue(issues, "invalid_type", name, f"{name} must be a list.")
        return []
    return [record for record in value if isinstance(record, dict)]


def _unique_ids(records: list[dict[str, Any]], field: str, collection: str, issues: list[ValidationIssue]) -> set[str]:
    seen: set[str] = set()
    for index, record in enumerate(records):
        value = record.get(field)
        path = f"{collection}.{index}.{field}"
        if not value:
            _issue(issues, "missing_required", path, "Identifier is required.")
        elif value in seen:
            _issue(issues, "duplicate_id", path, f"Duplicate identifier: {value}.")
        else:
            seen.add(str(value))
    return seen


def validate_user_dataset(
    data: dict[str, Any],
    *,
    expected_project_id: str,
    expected_category: str,
    expected_currency: str,
) -> ValidationResult:
    issues: list[ValidationIssue] = []

    if data.get("dataset_type") != "user_upload":
        _issue(issues, "invalid_dataset_type", "dataset_type", "User uploads must normalize to user_upload.")

    project = data.get("packaging_project")
    if not isinstance(project, dict):
        _issue(issues, "missing_required", "packaging_project", "Packaging project object is required.")
        project = {}
    _required(
        project,
        ["project_id", "project_name", "category", "annual_volume", "annual_volume_unit", "currency", "status"],
        "packaging_project",
        issues,
    )
    if project.get("project_id") != expected_project_id:
        _issue(issues, "project_mismatch", "packaging_project.project_id", "Upload must be bound to the active project.")
    if project.get("category") != expected_category:
        _issue(issues, "category_mismatch", "packaging_project.category", "Upload category must match the active project.")
    if project.get("currency") != expected_currency:
        _issue(issues, "currency_mismatch", "packaging_project.currency", "Upload currency must match the active project.")
    _positive(project.get("annual_volume"), "packaging_project.annual_volume", issues)
    if project.get("annual_volume_unit") != "cases_per_year":
        _issue(issues, "unsupported_unit", "packaging_project.annual_volume_unit", "Annual volume unit must be cases_per_year.")
    _enum(project.get("currency"), _ALLOWED["currency"], "packaging_project.currency", issues)
    _enum(project.get("status"), _ALLOWED["project_status"], "packaging_project.status", issues)

    evidence = _list(data, "decision_evidence", issues)
    evidence_ids = _unique_ids(evidence, "evidence_id", "decision_evidence", issues)
    for index, record in enumerate(evidence):
        _required(record, ["evidence_id", "evidence_type", "reference"], f"decision_evidence.{index}", issues)

    alternatives = _list(data, "packaging_alternatives", issues)
    alternative_ids = _unique_ids(alternatives, "alternative_id", "packaging_alternatives", issues)
    if len(alternatives) < 2:
        _issue(issues, "insufficient_alternatives", "packaging_alternatives", "At least one baseline and one proposed alternative are required.")
    baseline_count = 0
    for index, record in enumerate(alternatives):
        prefix = f"packaging_alternatives.{index}"
        _required(record, ["alternative_id", "name", "status", "length_mm", "width_mm", "height_mm", "case_weight_g", "board_grade"], prefix, issues)
        _enum(record.get("status"), _ALLOWED["alternative_status"], f"{prefix}.status", issues)
        if record.get("status") == "baseline":
            baseline_count += 1
        for field in ("length_mm", "width_mm", "height_mm", "case_weight_g"):
            _positive(record.get(field), f"{prefix}.{field}", issues)
        _enum(record.get("board_grade"), _ALLOWED["board_grade"], f"{prefix}.board_grade", issues)
    if baseline_count != 1:
        _issue(issues, "invalid_baseline_count", "packaging_alternatives", "Exactly one baseline alternative is required.")

    baseline = data.get("baseline_specification")
    if not isinstance(baseline, dict):
        _issue(issues, "missing_required", "baseline_specification", "Baseline specification is required.")
        baseline = {}
    _required(baseline, ["baseline_id", "alternative_id"], "baseline_specification", issues)
    if baseline.get("alternative_id") not in alternative_ids:
        _issue(issues, "invalid_reference", "baseline_specification.alternative_id", "Baseline must reference an existing alternative.")
    evidence_id = baseline.get("evidence_id")
    if evidence_id and evidence_id not in evidence_ids:
        _issue(issues, "missing_evidence", "baseline_specification.evidence_id", "Baseline evidence reference was not found.")

    collection_specs = {
        "material_components": ("component_id", ["alternative_id", "material_name", "weight_g", "recycled_content_percent"]),
        "cost_inputs": ("cost_id", ["alternative_id", "input_name", "value", "unit", "currency"]),
        "logistics_inputs": ("logistics_id", ["alternative_id", "cases_per_pallet", "freight_distance_km"]),
        "technical_requirements": ("requirement_id", ["name", "minimum_value", "unit"]),
        "technical_qualification_results": ("qualification_id", ["alternative_id", "requirement_id", "status"]),
        "risk_records": ("risk_id", ["alternative_id", "risk_type", "level", "probability_percent"]),
        "sustainability_indicators": ("indicator_id", ["alternative_id", "metric", "value", "unit"]),
        "validation_requirements": ("validation_id", ["alternative_id", "activity", "status"]),
    }
    collections: dict[str, list[dict[str, Any]]] = {}
    id_sets: dict[str, set[str]] = {}
    for name, (id_field, required) in collection_specs.items():
        records = _list(data, name, issues)
        collections[name] = records
        id_sets[name] = _unique_ids(records, id_field, name, issues)
        for index, record in enumerate(records):
            _required(record, [id_field, *required], f"{name}.{index}", issues)
            if "alternative_id" in record and record.get("alternative_id") not in alternative_ids:
                _issue(issues, "invalid_reference", f"{name}.{index}.alternative_id", "Alternative reference was not found.")

    for index, record in enumerate(collections["material_components"]):
        _positive(record.get("weight_g"), f"material_components.{index}.weight_g", issues)
        _percentage(record.get("recycled_content_percent"), f"material_components.{index}.recycled_content_percent", issues)

    for index, record in enumerate(collections["cost_inputs"]):
        _positive(record.get("value"), f"cost_inputs.{index}.value", issues, allow_zero=True)
        if record.get("currency") != expected_currency:
            _issue(issues, "currency_mismatch", f"cost_inputs.{index}.currency", "Cost currency must match the active project.")
        if record.get("unit") != f"{expected_currency}_per_case":
            _issue(issues, "unsupported_unit", f"cost_inputs.{index}.unit", "Cost unit must match project currency per case.")
        if record.get("evidence_id") and record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"cost_inputs.{index}.evidence_id", "Cost evidence reference was not found.")

    for index, record in enumerate(collections["logistics_inputs"]):
        _positive(record.get("cases_per_pallet"), f"logistics_inputs.{index}.cases_per_pallet", issues)
        _positive(record.get("freight_distance_km"), f"logistics_inputs.{index}.freight_distance_km", issues, allow_zero=True)
        if record.get("evidence_id") and record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"logistics_inputs.{index}.evidence_id", "Logistics evidence reference was not found.")

    requirement_ids = id_sets["technical_requirements"]
    for index, record in enumerate(collections["technical_requirements"]):
        _positive(record.get("minimum_value"), f"technical_requirements.{index}.minimum_value", issues, allow_zero=True)
        if record.get("unit") not in {"N", "kgf", "unitless"}:
            _issue(issues, "unsupported_unit", f"technical_requirements.{index}.unit", "Unsupported technical requirement unit.")

    for index, record in enumerate(collections["technical_qualification_results"]):
        _enum(record.get("status"), _ALLOWED["technical_status"], f"technical_qualification_results.{index}.status", issues)
        if record.get("requirement_id") not in requirement_ids:
            _issue(issues, "invalid_reference", f"technical_qualification_results.{index}.requirement_id", "Requirement reference was not found.")
        if record.get("status") not in {"not_assessed", "insufficient_data"} and record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"technical_qualification_results.{index}.evidence_id", "Assessed qualification requires valid evidence.")

    for index, record in enumerate(collections["risk_records"]):
        _enum(record.get("risk_type"), _ALLOWED["risk_type"], f"risk_records.{index}.risk_type", issues)
        _enum(record.get("level"), _ALLOWED["risk_level"], f"risk_records.{index}.level", issues)
        _percentage(record.get("probability_percent"), f"risk_records.{index}.probability_percent", issues)

    for index, record in enumerate(collections["sustainability_indicators"]):
        _positive(record.get("value"), f"sustainability_indicators.{index}.value", issues, allow_zero=True)
        if str(record.get("metric", "")).endswith("percent"):
            _percentage(record.get("value"), f"sustainability_indicators.{index}.value", issues)

    for index, record in enumerate(collections["validation_requirements"]):
        _enum(record.get("status"), _ALLOWED["validation_status"], f"validation_requirements.{index}.status", issues)

    recommendation = data.get("decision_recommendation")
    if not isinstance(recommendation, dict):
        _issue(issues, "missing_required", "decision_recommendation", "Decision recommendation placeholder is required.")
    else:
        _required(recommendation, ["recommendation_id", "status", "rationale"], "decision_recommendation", issues)
        if recommendation.get("status") != "insufficient_data":
            _issue(issues, "unsafe_upload_recommendation", "decision_recommendation.status", "Uploaded data must not pre-approve a recommendation.")

    export = data.get("export_metadata")
    if not isinstance(export, dict):
        _issue(issues, "missing_required", "export_metadata", "Export metadata is required.")
    else:
        _required(export, ["contract_version", "source_repository", "source_commit"], "export_metadata", issues)
        if export.get("contract_version") != "PVE-CONTRACT-v1.0-DRAFT":
            _issue(issues, "invalid_contract_version", "export_metadata.contract_version", "User uploads must retain the draft integration marker.")

    technical_results = collections["technical_qualification_results"]
    insufficient = (
        not technical_results
        or any(record.get("status") in {"not_assessed", "insufficient_data"} for record in technical_results)
        or not evidence
        or any(issue.code in {"missing_required", "missing_evidence", "invalid_reference"} for issue in issues)
    )
    return ValidationResult(tuple(issues), insufficient)
