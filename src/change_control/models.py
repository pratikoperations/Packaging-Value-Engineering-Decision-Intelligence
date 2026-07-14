from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

_ALLOWED_CHANGE_TYPES = {"specification", "implementation", "combined"}
_ALLOWED_REVIEW_STATUSES = {"draft", "pending_review", "reviewed", "rejected", "withdrawn"}
_ALLOWED_APPROVAL_STATUSES = {"not_requested", "pending", "approved", "rejected"}
_ALLOWED_IMPLEMENTATION_STATUSES = {"planned", "authorized", "in_progress", "implemented", "aborted"}
_ALLOWED_VERIFICATION_STATUSES = {"not_started", "pending", "verified", "failed", "not_required"}
_PROHIBITED_BUILD7_FIELDS = {
    "supplier_qualification_status",
    "supplier_disqualification_status",
    "supplier_capability_score",
    "approved_supplier_list_status",
    "sourcing_award_status",
    "sourcing_allocation_percent",
    "supplier_rank",
    "autonomous_production_release",
}


@dataclass(frozen=True)
class ChangeControlIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class ChangeControlValidation:
    issues: tuple[ChangeControlIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[ChangeControlIssue], code: str, field: str, message: str) -> None:
    issues.append(ChangeControlIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[ChangeControlIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _sequence(payload: Mapping[str, Any], field: str, issues: list[ChangeControlIssue]) -> None:
    value = payload.get(field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _issue(issues, "invalid_type", field, f"{field} must be a sequence.")


def _iso_date(payload: Mapping[str, Any], field: str, issues: list[ChangeControlIssue]) -> None:
    value = payload.get(field)
    if value in (None, ""):
        return
    try:
        date.fromisoformat(str(value))
    except ValueError:
        _issue(issues, "invalid_date", field, "Date must use ISO-8601 format.")


def _reject_build7(payload: Mapping[str, Any], issues: list[ChangeControlIssue]) -> None:
    for field in _PROHIBITED_BUILD7_FIELDS.intersection(payload):
        if payload.get(field) not in (None, "", [], {}):
            _issue(
                issues,
                "build7_data_prohibited",
                field,
                "Build 6 cannot store Build 7 supplier-qualification or sourcing decisions.",
            )


def validate_specification_change(payload: Mapping[str, Any]) -> ChangeControlValidation:
    issues: list[ChangeControlIssue] = []
    for field in (
        "project_id",
        "change_code",
        "change_type",
        "title",
        "rationale",
        "current_specification_version",
        "proposed_specification_version",
        "review_status",
        "approval_status",
        "requested_by",
        "evidence_references",
        "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("change_type") not in _ALLOWED_CHANGE_TYPES:
        _issue(issues, "invalid_enum", "change_type", "Unsupported change type.")
    if payload.get("review_status") not in _ALLOWED_REVIEW_STATUSES:
        _issue(issues, "invalid_enum", "review_status", "Unsupported review status.")
    if payload.get("approval_status") not in _ALLOWED_APPROVAL_STATUSES:
        _issue(issues, "invalid_enum", "approval_status", "Unsupported approval status.")

    _sequence(payload, "evidence_references", issues)
    _sequence(payload, "linked_trial_execution_ids", issues)
    _sequence(payload, "linked_defect_classification_ids", issues)
    _sequence(payload, "linked_complaint_record_ids", issues)
    _iso_date(payload, "requested_effective_date", issues)

    if payload.get("approval_status") == "approved":
        for field in ("approved_by", "approval_reference", "approved_at"):
            _required(payload, field, issues)
        if not payload.get("evidence_references"):
            _issue(issues, "missing_evidence", "evidence_references", "Approved change requires evidence.")
        _iso_date(payload, "approved_at", issues)

    if payload.get("current_specification_version") == payload.get("proposed_specification_version"):
        _issue(
            issues,
            "version_not_changed",
            "proposed_specification_version",
            "Proposed specification version must differ from the current version.",
        )

    _reject_build7(payload, issues)
    return ChangeControlValidation(tuple(issues))


def validate_implementation_control(payload: Mapping[str, Any]) -> ChangeControlValidation:
    issues: list[ChangeControlIssue] = []
    for field in (
        "project_id",
        "change_request_id",
        "implementation_code",
        "implementation_site",
        "implementation_owner",
        "implementation_status",
        "verification_status",
        "evidence_references",
        "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("implementation_status") not in _ALLOWED_IMPLEMENTATION_STATUSES:
        _issue(issues, "invalid_enum", "implementation_status", "Unsupported implementation status.")
    if payload.get("verification_status") not in _ALLOWED_VERIFICATION_STATUSES:
        _issue(issues, "invalid_enum", "verification_status", "Unsupported verification status.")

    _sequence(payload, "evidence_references", issues)
    for field in ("planned_implementation_date", "actual_implementation_date", "verified_at"):
        _iso_date(payload, field, issues)

    if payload.get("implementation_status") in {"authorized", "in_progress", "implemented"}:
        for field in ("authorized_by", "authorization_reference"):
            _required(payload, field, issues)

    if payload.get("implementation_status") == "implemented":
        _required(payload, "actual_implementation_date", issues)
        if not payload.get("evidence_references"):
            _issue(issues, "missing_evidence", "evidence_references", "Implemented change requires evidence.")

    if payload.get("verification_status") == "verified":
        for field in ("verified_by", "verified_at"):
            _required(payload, field, issues)
        if not payload.get("evidence_references"):
            _issue(issues, "missing_evidence", "evidence_references", "Verified implementation requires evidence.")

    _reject_build7(payload, issues)
    return ChangeControlValidation(tuple(issues))
