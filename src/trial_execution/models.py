from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

_ALLOWED_STATUSES = {"completed", "partial", "aborted"}
_ALLOWED_OUTCOMES = {"pass", "fail", "inconclusive", "aborted"}
_ALLOWED_RESULT_TYPES = {"numeric", "boolean", "categorical", "documentary"}
_ALLOWED_SEVERITIES = {"minor", "major", "critical"}
_ALLOWED_DISPOSITIONS = {"open", "accepted", "retest_required", "rejected"}
_PROHIBITED_BUILD5_FIELDS = {
    "defect_code", "defect_category", "complaint_category", "complaint_code",
    "supplier_qualification_status", "specification_approval_status",
}


@dataclass(frozen=True)
class ExecutionIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class ExecutionValidation:
    issues: tuple[ExecutionIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[ExecutionIssue], code: str, field: str, message: str) -> None:
    issues.append(ExecutionIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[ExecutionIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _validate_measurements(measurements: Sequence[Mapping[str, Any]], issues: list[ExecutionIssue]) -> None:
    identifiers: set[str] = set()
    for index, measurement in enumerate(measurements):
        field = f"measurements[{index}]"
        identifier = str(measurement.get("criterion_id") or "").strip()
        if not identifier:
            _issue(issues, "missing_required", field, "criterion_id is required.")
        elif identifier in identifiers:
            _issue(issues, "duplicate_measurement", field, "criterion_id must be unique within an execution.")
        identifiers.add(identifier)
        result_type = measurement.get("result_type")
        if result_type not in _ALLOWED_RESULT_TYPES:
            _issue(issues, "invalid_enum", field, "Unsupported result_type.")
        if result_type == "numeric":
            if not isinstance(measurement.get("value"), (int, float)):
                _issue(issues, "invalid_numeric_result", field, "Numeric measurements require a numeric value.")
            if not str(measurement.get("unit") or "").strip():
                _issue(issues, "invalid_numeric_result", field, "Numeric measurements require a unit.")
        elif result_type == "boolean" and not isinstance(measurement.get("value"), bool):
            _issue(issues, "invalid_boolean_result", field, "Boolean measurements require true or false.")
        elif result_type in {"categorical", "documentary"} and not str(measurement.get("value") or "").strip():
            _issue(issues, "missing_result", field, "A recorded result is required.")
        if not str(measurement.get("evidence_reference") or "").strip():
            _issue(issues, "missing_evidence", field, "evidence_reference is required.")


def _validate_deviations(deviations: Sequence[Mapping[str, Any]], issues: list[ExecutionIssue]) -> None:
    identifiers: set[str] = set()
    for index, deviation in enumerate(deviations):
        field = f"deviations[{index}]"
        identifier = str(deviation.get("deviation_id") or "").strip()
        if not identifier:
            _issue(issues, "missing_required", field, "deviation_id is required.")
        elif identifier in identifiers:
            _issue(issues, "duplicate_deviation", field, "deviation_id must be unique within an execution.")
        identifiers.add(identifier)
        for required in ("description", "impact_assessment", "owner"):
            if not str(deviation.get(required) or "").strip():
                _issue(issues, "missing_required", field, f"{required} is required.")
        if deviation.get("severity") not in _ALLOWED_SEVERITIES:
            _issue(issues, "invalid_enum", field, "Unsupported deviation severity.")
        if deviation.get("disposition_status") not in _ALLOWED_DISPOSITIONS:
            _issue(issues, "invalid_enum", field, "Unsupported deviation disposition_status.")
        for prohibited in _PROHIBITED_BUILD5_FIELDS.intersection(deviation):
            if deviation.get(prohibited) not in (None, "", [], {}):
                _issue(issues, "build5_data_prohibited", field, "Build 4 cannot store defect taxonomy or complaint classification.")


def validate_trial_execution(payload: Mapping[str, Any]) -> ExecutionValidation:
    """Validate an immutable execution snapshot without making approval decisions."""
    issues: list[ExecutionIssue] = []
    for field in (
        "project_id", "trial_plan_id", "execution_code", "started_at", "completed_at",
        "performed_by", "trial_site", "status", "outcome", "measurements",
        "reviewed_by", "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("status") not in _ALLOWED_STATUSES:
        _issue(issues, "invalid_enum", "status", "Unsupported execution status.")
    if payload.get("outcome") not in _ALLOWED_OUTCOMES:
        _issue(issues, "invalid_enum", "outcome", "Unsupported execution outcome.")
    if payload.get("status") == "aborted" and payload.get("outcome") != "aborted":
        _issue(issues, "invalid_outcome", "outcome", "Aborted execution requires aborted outcome.")
    if payload.get("status") != "aborted" and payload.get("outcome") == "aborted":
        _issue(issues, "invalid_outcome", "outcome", "Aborted outcome requires aborted execution status.")

    try:
        started = datetime.fromisoformat(str(payload.get("started_at")))
        completed = datetime.fromisoformat(str(payload.get("completed_at")))
        if completed < started:
            _issue(issues, "invalid_date_order", "completed_at", "Completion cannot precede start.")
    except ValueError:
        _issue(issues, "invalid_datetime", "started_at/completed_at", "Timestamps must use ISO-8601 format.")

    measurements = payload.get("measurements")
    if isinstance(measurements, Sequence) and not isinstance(measurements, (str, bytes)):
        _validate_measurements(measurements, issues)
    else:
        _issue(issues, "invalid_type", "measurements", "Measurements must be a sequence.")

    deviations = payload.get("deviations", ())
    if isinstance(deviations, Sequence) and not isinstance(deviations, (str, bytes)):
        _validate_deviations(deviations, issues)
    else:
        _issue(issues, "invalid_type", "deviations", "Deviations must be a sequence.")

    digest = str(payload.get("content_hash") or "")
    if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower())):
        _issue(issues, "invalid_hash", "content_hash", "Content hash must be a 64-character SHA-256 hex digest.")

    for field in _PROHIBITED_BUILD5_FIELDS.intersection(payload):
        if payload.get(field) not in (None, "", [], {}):
            _issue(issues, "build5_data_prohibited", field, "Build 4 cannot store Build 5 or later-build decisions.")

    return ExecutionValidation(tuple(issues))
