from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

_ALLOWED_STATUSES = {
    "pending",
    "conditionally_qualified",
    "qualified",
    "not_qualified",
    "expired",
}
_ALLOWED_ASSESSMENT_TYPES = {
    "initial",
    "renewal",
    "scope_extension",
    "corrective_reassessment",
    "periodic_review",
}
_PROHIBITED_BUILD8_FIELDS = {
    "release_certification_status",
    "release_signoff",
    "final_regression_attestation",
    "demonstration_case_approval",
    "deployment_readiness_status",
    "production_readiness_approval",
    "supplier_rank",
    "preferred_supplier_recommendation",
    "sourcing_award_status",
    "sourcing_allocation_percent",
    "commercial_terms_approval",
    "autonomous_qualification_decision",
}


@dataclass(frozen=True)
class SupplierQualificationIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class SupplierQualificationValidation:
    issues: tuple[SupplierQualificationIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[SupplierQualificationIssue], code: str, field: str, message: str) -> None:
    issues.append(SupplierQualificationIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[SupplierQualificationIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _sequence(payload: Mapping[str, Any], field: str, issues: list[SupplierQualificationIssue]) -> None:
    value = payload.get(field)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        _issue(issues, "invalid_type", field, f"{field} must be a sequence.")


def _iso_date(payload: Mapping[str, Any], field: str, issues: list[SupplierQualificationIssue]) -> None:
    value = payload.get(field)
    if value in (None, ""):
        return
    try:
        date.fromisoformat(str(value))
    except ValueError:
        _issue(issues, "invalid_date", field, "Date must use ISO-8601 format.")


def _reject_build8(payload: Mapping[str, Any], issues: list[SupplierQualificationIssue]) -> None:
    for field in _PROHIBITED_BUILD8_FIELDS.intersection(payload):
        if payload.get(field) not in (None, "", [], {}):
            _issue(
                issues,
                "build8_data_prohibited",
                field,
                "Build 7 cannot store Build 8 release decisions or sourcing/commercial decisions.",
            )


def validate_supplier_qualification(payload: Mapping[str, Any]) -> SupplierQualificationValidation:
    issues: list[SupplierQualificationIssue] = []
    for field in (
        "project_id",
        "qualification_code",
        "supplier_name",
        "supplier_site",
        "qualification_scope",
        "assessment_type",
        "assessment_date",
        "qualification_status",
        "assessed_by",
        "evidence_references",
        "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("qualification_status") not in _ALLOWED_STATUSES:
        _issue(issues, "invalid_enum", "qualification_status", "Unsupported qualification status.")
    if payload.get("assessment_type") not in _ALLOWED_ASSESSMENT_TYPES:
        _issue(issues, "invalid_enum", "assessment_type", "Unsupported assessment type.")

    for field in (
        "evidence_references",
        "linked_trial_execution_ids",
        "linked_defect_classification_ids",
        "linked_complaint_record_ids",
        "linked_specification_change_request_ids",
        "linked_implementation_control_ids",
        "conditions",
        "open_actions",
    ):
        _sequence(payload, field, issues)

    for field in ("assessment_date", "valid_from", "valid_until", "review_date", "approved_at"):
        _iso_date(payload, field, issues)

    status = payload.get("qualification_status")
    if status in {"qualified", "conditionally_qualified"}:
        for field in ("approved_by", "approval_reference", "approved_at", "decision_rationale"):
            _required(payload, field, issues)
        if not payload.get("evidence_references"):
            _issue(issues, "missing_evidence", "evidence_references", "Qualified assessment requires evidence.")

    if status == "conditionally_qualified" and not payload.get("conditions"):
        _issue(issues, "conditions_required", "conditions", "Conditional qualification requires conditions.")

    if payload.get("valid_from") and payload.get("valid_until"):
        try:
            if date.fromisoformat(str(payload["valid_until"])) < date.fromisoformat(str(payload["valid_from"])):
                _issue(issues, "invalid_date_order", "valid_until", "Validity end cannot precede validity start.")
        except ValueError:
            pass

    _reject_build8(payload, issues)
    return SupplierQualificationValidation(tuple(issues))
