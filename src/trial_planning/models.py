from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

_ALLOWED_STATUSES = {"draft", "ready_for_authorization", "authorized", "blocked", "cancelled"}
_ALLOWED_AUTHORIZATION = {"not_requested", "pending", "authorized", "rejected"}
_ALLOWED_CRITERION_TYPES = {"numeric", "boolean", "categorical", "documentary"}


@dataclass(frozen=True)
class TrialPlanIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class TrialPlanValidation:
    issues: tuple[TrialPlanIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[TrialPlanIssue], code: str, field: str, message: str) -> None:
    issues.append(TrialPlanIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[TrialPlanIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _validate_criteria(criteria: Sequence[Mapping[str, Any]], issues: list[TrialPlanIssue]) -> None:
    identifiers: set[str] = set()
    for index, criterion in enumerate(criteria):
        field = f"acceptance_criteria[{index}]"
        identifier = str(criterion.get("criterion_id") or "").strip()
        if not identifier:
            _issue(issues, "missing_required", field, "criterion_id is required.")
        elif identifier in identifiers:
            _issue(issues, "duplicate_criterion", field, "criterion_id must be unique within the plan.")
        identifiers.add(identifier)
        if not str(criterion.get("description") or "").strip():
            _issue(issues, "missing_required", field, "description is required.")
        criterion_type = criterion.get("criterion_type")
        if criterion_type not in _ALLOWED_CRITERION_TYPES:
            _issue(issues, "invalid_enum", field, "Unsupported criterion_type.")
        if criterion_type == "numeric":
            if criterion.get("operator") not in {"<", "<=", "=", ">=", ">", "between"}:
                _issue(issues, "invalid_numeric_criterion", field, "Numeric criteria require a governed operator.")
            if criterion.get("target") is None:
                _issue(issues, "invalid_numeric_criterion", field, "Numeric criteria require a target.")
            if not str(criterion.get("unit") or "").strip():
                _issue(issues, "invalid_numeric_criterion", field, "Numeric criteria require a unit.")
        if not str(criterion.get("evidence_required") or "").strip():
            _issue(issues, "missing_required", field, "evidence_required is required.")


def validate_trial_plan(payload: Mapping[str, Any]) -> TrialPlanValidation:
    """Validate a trial plan without recording execution, results, or disposition."""
    issues: list[TrialPlanIssue] = []
    for field in (
        "project_id", "trial_code", "title", "objective", "protocol", "owner",
        "trial_site", "planned_start_date", "planned_end_date", "status",
        "authorization_status", "acceptance_criteria", "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("status") not in _ALLOWED_STATUSES:
        _issue(issues, "invalid_enum", "status", "Unsupported trial-plan status.")
    if payload.get("authorization_status") not in _ALLOWED_AUTHORIZATION:
        _issue(issues, "invalid_enum", "authorization_status", "Unsupported authorization status.")
    if payload.get("status") == "authorized" and payload.get("authorization_status") != "authorized":
        _issue(issues, "authorization_required", "authorization_status", "Authorized plans require explicit human authorization.")
    if payload.get("authorization_status") == "authorized" and not str(payload.get("authorized_by") or "").strip():
        _issue(issues, "missing_authorizer", "authorized_by", "Human authorizer identity is required.")

    try:
        start = date.fromisoformat(str(payload.get("planned_start_date")))
        end = date.fromisoformat(str(payload.get("planned_end_date")))
        if end < start:
            _issue(issues, "invalid_date_order", "planned_end_date", "Planned end date cannot precede start date.")
    except ValueError:
        _issue(issues, "invalid_date", "planned_start_date/planned_end_date", "Dates must use ISO YYYY-MM-DD format.")

    criteria = payload.get("acceptance_criteria")
    if isinstance(criteria, Sequence) and not isinstance(criteria, (str, bytes)):
        _validate_criteria(criteria, issues)
    else:
        _issue(issues, "invalid_type", "acceptance_criteria", "Acceptance criteria must be a sequence.")

    digest = str(payload.get("content_hash") or "")
    if digest and (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest.lower())):
        _issue(issues, "invalid_hash", "content_hash", "Content hash must be a 64-character SHA-256 hex digest.")

    prohibited = {"results", "measurements", "deviations", "disposition", "execution_status"}
    for field in prohibited.intersection(payload):
        if payload.get(field) not in (None, "", [], {}):
            _issue(issues, "execution_data_prohibited", field, "Build 3 cannot store trial execution or result data.")

    return TrialPlanValidation(tuple(issues))
