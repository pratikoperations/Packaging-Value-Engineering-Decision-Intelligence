from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ValidationResult:
    issues: tuple[ValidationIssue, ...]
    insufficient_data_eligible: bool

    @property
    def is_valid(self) -> bool:
        return not self.issues


_ALLOWED = {
    "project_status": {"draft", "active", "on_hold", "completed"},
    "alternative_status": {"baseline", "proposed", "screened_out"},
    "technical_status": {"not_assessed", "qualified", "conditionally_qualified", "not_qualified", "insufficient_data"},
    "risk_level": {"low", "medium", "high", "critical"},
    "risk_type": {"quality", "supply", "implementation", "logistics", "compliance", "sustainability"},
    "recommendation_status": {"recommended", "conditionally_recommended", "not_recommended", "insufficient_data"},
    "validation_status": {"not_started", "planned", "in_progress", "passed", "failed", "waived"},
    "board_grade": {"3PLY_B_FLUTE", "5PLY_BC_FLUTE", "3PLY_C_FLUTE", "5PLY_EB_FLUTE"},
    "currency": {"INR", "USD", "EUR"},
}


def _issue(issues: list[ValidationIssue], code: str, path: str, message: str) -> None:
    issues.append(ValidationIssue(code, path, message))


def _required(mapping: dict[str, Any], fields: Iterable[str], prefix: str, issues: list[ValidationIssue]) -> None:
    for field in fields:
        if field not in mapping or mapping[field] in (None, ""):
            _issue(issues, "missing_required", f"{prefix}.{field}", "Required field is missing or empty.")


def _positive(value: Any, path: str, issues: list[ValidationIssue], allow_zero: bool = False) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        _issue(issues, "invalid_number", path, "Value must be numeric.")
        return
    if value < 0 or (value == 0 and not allow_zero):
        comparator = "greater than or equal to zero" if allow_zero else "greater than zero"
        _issue(issues, "out_of_range", path, f"Value must be {comparator}.")


def _percentage(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
        _issue(issues, "invalid_percentage", path, "Percentage must be between 0 and 100 inclusive.")


def _enum(value: Any, allowed: set[str], path: str, issues: list[ValidationIssue]) -> None:
    if value not in allowed:
        _issue(issues, "invalid_enum", path, f"Unsupported value: {value!r}.")


def _unique_ids(records: list[dict[str, Any]], id_field: str, collection: str, issues: list[ValidationIssue]) -> set[str]:
    seen: set[str] = set()
    for index, record in enumerate(records):
        value = record.get(id_field)
        path = f"{collection}.{index}.{id_field}"
        if not value:
            _issue(issues, "missing_required", path, "Identifier is required.")
        elif value in seen:
            _issue(issues, "duplicate_id", path, f"Duplicate identifier: {value}.")
        else:
            seen.add(value)
    return seen


def validate_dataset(data: dict[str, Any]) -> ValidationResult:
    issues: list[ValidationIssue] = []

    if data.get("dataset_type") != "synthetic_demo":
        _issue(issues, "not_synthetic", "dataset_type", "Committed demo data must be labelled synthetic_demo.")
    if not data.get("synthetic_notice"):
        _issue(issues, "missing_required", "synthetic_notice", "Synthetic-data notice is required.")

    project = data.get("packaging_project")
    if not isinstance(project, dict):
        _issue(issues, "missing_required", "packaging_project", "Packaging project object is required.")
        project = {}
    _required(project, ["project_id", "project_name", "category", "annual_volume", "annual_volume_unit", "currency", "status"], "packaging_project", issues)
    _positive(project.get("annual_volume"), "packaging_project.annual_volume", issues)
    if project.get("annual_volume_unit") != "cases_per_year":
        _issue(issues, "unsupported_unit", "packaging_project.annual_volume_unit", "Annual volume unit must be cases_per_year.")
    _enum(project.get("currency"), _ALLOWED["currency"], "packaging_project.currency", issues)
    _enum(project.get("status"), _ALLOWED["project_status"], "packaging_project.status", issues)

    evidence = data.get("decision_evidence", [])
    if not isinstance(evidence, list):
        _issue(issues, "invalid_type", "decision_evidence", "Decision evidence must be a list.")
        evidence = []
    evidence_ids = _unique_ids(evidence, "evidence_id", "decision_evidence", issues)
    for i, record in enumerate(evidence):
        _required(record, ["evidence_id", "evidence_type", "reference"], f"decision_evidence.{i}", issues)

    alternatives = data.get("packaging_alternatives", [])
    if not isinstance(alternatives, list):
        _issue(issues, "invalid_type", "packaging_alternatives", "Packaging alternatives must be a list.")
        alternatives = []
    alternative_ids = _unique_ids(alternatives, "alternative_id", "packaging_alternatives", issues)
    if len(alternatives) < 4:
        _issue(issues, "insufficient_alternatives", "packaging_alternatives", "Demo requires one baseline and at least three alternatives.")
    baseline_count = 0
    for i, record in enumerate(alternatives):
        prefix = f"packaging_alternatives.{i}"
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
    _required(baseline, ["baseline_id", "alternative_id", "evidence_id"], "baseline_specification", issues)
    if baseline.get("alternative_id") not in alternative_ids:
        _issue(issues, "invalid_reference", "baseline_specification.alternative_id", "Baseline must reference an existing alternative.")
    if baseline.get("evidence_id") not in evidence_ids:
        _issue(issues, "missing_evidence", "baseline_specification.evidence_id", "Baseline evidence reference was not found.")

    collections = {
        "material_components": ("component_id", ["alternative_id", "material_name", "weight_g", "recycled_content_percent"]),
        "cost_inputs": ("cost_id", ["alternative_id", "input_name", "value", "unit", "currency", "evidence_id"]),
        "logistics_inputs": ("logistics_id", ["alternative_id", "cases_per_pallet", "freight_distance_km", "evidence_id"]),
        "technical_requirements": ("requirement_id", ["name", "minimum_value", "unit"]),
        "technical_qualification_results": ("qualification_id", ["alternative_id", "requirement_id", "status"]),
        "risk_records": ("risk_id", ["alternative_id", "risk_type", "level", "probability_percent"]),
        "sustainability_indicators": ("indicator_id", ["alternative_id", "metric", "value", "unit"]),
        "validation_requirements": ("validation_id", ["alternative_id", "activity", "status"]),
    }
    id_sets: dict[str, set[str]] = {}
    for name, (id_field, required) in collections.items():
        records = data.get(name, [])
        if not isinstance(records, list):
            _issue(issues, "invalid_type", name, f"{name} must be a list.")
            records = []
        id_sets[name] = _unique_ids(records, id_field, name, issues)
        for i, record in enumerate(records):
            _required(record, [id_field, *required], f"{name}.{i}", issues)
            if "alternative_id" in record and record.get("alternative_id") not in alternative_ids:
                _issue(issues, "invalid_reference", f"{name}.{i}.alternative_id", "Alternative reference was not found.")

    for i, record in enumerate(data.get("material_components", [])):
        _positive(record.get("weight_g"), f"material_components.{i}.weight_g", issues)
        _percentage(record.get("recycled_content_percent"), f"material_components.{i}.recycled_content_percent", issues)

    project_currency = project.get("currency")
    for i, record in enumerate(data.get("cost_inputs", [])):
        _positive(record.get("value"), f"cost_inputs.{i}.value", issues, allow_zero=True)
        if record.get("currency") != project_currency:
            _issue(issues, "currency_mismatch", f"cost_inputs.{i}.currency", "Cost currency must match project currency.")
        if record.get("unit") != f"{project_currency}_per_case":
            _issue(issues, "unsupported_unit", f"cost_inputs.{i}.unit", "Cost unit must match project currency per case.")
        if record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"cost_inputs.{i}.evidence_id", "Cost evidence reference was not found.")

    for i, record in enumerate(data.get("logistics_inputs", [])):
        _positive(record.get("cases_per_pallet"), f"logistics_inputs.{i}.cases_per_pallet", issues)
        _positive(record.get("freight_distance_km"), f"logistics_inputs.{i}.freight_distance_km", issues, allow_zero=True)
        if record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"logistics_inputs.{i}.evidence_id", "Logistics evidence reference was not found.")

    requirement_ids = id_sets.get("technical_requirements", set())
    for i, record in enumerate(data.get("technical_requirements", [])):
        _positive(record.get("minimum_value"), f"technical_requirements.{i}.minimum_value", issues, allow_zero=True)
        if record.get("unit") not in {"N", "kgf", "unitless"}:
            _issue(issues, "unsupported_unit", f"technical_requirements.{i}.unit", "Unsupported technical-requirement unit.")

    for i, record in enumerate(data.get("technical_qualification_results", [])):
        _enum(record.get("status"), _ALLOWED["technical_status"], f"technical_qualification_results.{i}.status", issues)
        if record.get("requirement_id") not in requirement_ids:
            _issue(issues, "invalid_reference", f"technical_qualification_results.{i}.requirement_id", "Requirement reference was not found.")
        if record.get("status") not in {"not_assessed", "insufficient_data"} and record.get("evidence_id") not in evidence_ids:
            _issue(issues, "missing_evidence", f"technical_qualification_results.{i}.evidence_id", "Assessed qualification requires valid evidence.")

    for i, record in enumerate(data.get("risk_records", [])):
        _enum(record.get("risk_type"), _ALLOWED["risk_type"], f"risk_records.{i}.risk_type", issues)
        _enum(record.get("level"), _ALLOWED["risk_level"], f"risk_records.{i}.level", issues)
        _percentage(record.get("probability_percent"), f"risk_records.{i}.probability_percent", issues)

    for i, record in enumerate(data.get("sustainability_indicators", [])):
        _positive(record.get("value"), f"sustainability_indicators.{i}.value", issues, allow_zero=True)
        metric = record.get("metric", "")
        if metric.endswith("percent"):
            _percentage(record.get("value"), f"sustainability_indicators.{i}.value", issues)

    for i, record in enumerate(data.get("validation_requirements", [])):
        _enum(record.get("status"), _ALLOWED["validation_status"], f"validation_requirements.{i}.status", issues)

    recommendation = data.get("decision_recommendation")
    if not isinstance(recommendation, dict):
        _issue(issues, "missing_required", "decision_recommendation", "Decision recommendation placeholder is required.")
        recommendation = {}
    _required(recommendation, ["recommendation_id", "status", "rationale"], "decision_recommendation", issues)
    _enum(recommendation.get("status"), _ALLOWED["recommendation_status"], "decision_recommendation.status", issues)

    export = data.get("export_metadata")
    if not isinstance(export, dict):
        _issue(issues, "missing_required", "export_metadata", "Export metadata is required.")
        export = {}
    _required(export, ["contract_version", "source_repository", "source_commit"], "export_metadata", issues)
    if export.get("contract_version") != "PVE-CONTRACT-v1.0-DRAFT":
        _issue(issues, "invalid_contract_version", "export_metadata.contract_version", "PVE-0.2 must use the draft v1.0 contract marker.")

    technical_results = data.get("technical_qualification_results")
    insufficient = (
        not technical_results
        or any(r.get("status") in {"not_assessed", "insufficient_data"} for r in technical_results if isinstance(r, dict))
        or any(issue.code in {"missing_required", "missing_evidence", "invalid_reference"} for issue in issues)
    )
    return ValidationResult(tuple(issues), insufficient)
