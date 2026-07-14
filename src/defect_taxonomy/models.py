from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping, Sequence

_ALLOWED_PACKAGING_LEVELS = {"primary", "secondary", "tertiary", "transport"}
_ALLOWED_MATERIAL_FAMILIES = {
    "corrugated", "paperboard", "flexible", "rigid_plastic", "glass", "metal", "wood", "other"
}
_ALLOWED_DEFECT_FAMILIES = {
    "dimensional", "structural", "material", "print", "artwork", "closure", "seal",
    "contamination", "moisture", "handling", "palletization", "labeling", "other",
}
_ALLOWED_SEVERITIES = {"minor", "major", "critical"}
_ALLOWED_STAGES = {"incoming", "conversion", "packing", "storage", "transport", "customer_use", "unknown"}
_ALLOWED_SOURCES = {"customer", "consumer", "plant", "warehouse", "logistics", "supplier", "internal_quality"}
_ALLOWED_REVIEW_STATUSES = {"pending", "reviewed", "rejected"}
_ALLOWED_CONTAINMENT = {"not_started", "in_progress", "completed", "not_required", "unknown"}
_PROHIBITED_BUILD6_FIELDS = {
    "specification_change_status", "implementation_change_status", "change_approval",
    "effective_date_approval", "supplier_qualification_status", "sourcing_award_status",
    "root_cause", "corrective_action_approval", "complaint_disposition",
}


@dataclass(frozen=True)
class TaxonomyIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class TaxonomyValidation:
    issues: tuple[TaxonomyIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[TaxonomyIssue], code: str, field: str, message: str) -> None:
    issues.append(TaxonomyIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[TaxonomyIssue]) -> None:
    if payload.get(field) in (None, "", [], {}):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def _validate_evidence(payload: Mapping[str, Any], issues: list[TaxonomyIssue]) -> None:
    refs = payload.get("evidence_references")
    status = payload.get("review_status")
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes)):
        _issue(issues, "invalid_type", "evidence_references", "Evidence references must be a sequence.")
    elif status == "reviewed" and not refs:
        _issue(issues, "missing_evidence", "evidence_references", "Reviewed classification requires evidence.")


def _reject_build6(payload: Mapping[str, Any], issues: list[TaxonomyIssue]) -> None:
    for field in _PROHIBITED_BUILD6_FIELDS.intersection(payload):
        if payload.get(field) not in (None, "", [], {}):
            _issue(issues, "build6_data_prohibited", field, "Build 5 cannot store Build 6 or later-build decisions.")


def validate_defect_classification(payload: Mapping[str, Any]) -> TaxonomyValidation:
    issues: list[TaxonomyIssue] = []
    for field in (
        "project_id", "taxonomy_version", "defect_code", "packaging_level", "material_family",
        "defect_family", "defect_mode", "description", "severity", "occurrence_stage",
        "review_status", "reviewed_by", "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("packaging_level") not in _ALLOWED_PACKAGING_LEVELS:
        _issue(issues, "invalid_enum", "packaging_level", "Unsupported packaging level.")
    if payload.get("material_family") not in _ALLOWED_MATERIAL_FAMILIES:
        _issue(issues, "invalid_enum", "material_family", "Unsupported material family.")
    if payload.get("defect_family") not in _ALLOWED_DEFECT_FAMILIES:
        _issue(issues, "invalid_enum", "defect_family", "Unsupported defect family.")
    if payload.get("severity") not in _ALLOWED_SEVERITIES:
        _issue(issues, "invalid_enum", "severity", "Unsupported severity.")
    if payload.get("occurrence_stage") not in _ALLOWED_STAGES:
        _issue(issues, "invalid_enum", "occurrence_stage", "Unsupported occurrence stage.")
    if payload.get("review_status") not in _ALLOWED_REVIEW_STATUSES:
        _issue(issues, "invalid_enum", "review_status", "Unsupported review status.")
    if payload.get("review_status") == "reviewed" and not str(payload.get("reviewed_by") or "").strip():
        _issue(issues, "human_review_required", "reviewed_by", "Reviewed classification requires a human reviewer.")

    _validate_evidence(payload, issues)
    _reject_build6(payload, issues)
    return TaxonomyValidation(tuple(issues))


def validate_complaint_record(payload: Mapping[str, Any]) -> TaxonomyValidation:
    issues: list[TaxonomyIssue] = []
    for field in (
        "project_id", "complaint_reference", "complaint_source", "received_date", "description",
        "containment_status", "review_status", "reviewed_by", "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("complaint_source") not in _ALLOWED_SOURCES:
        _issue(issues, "invalid_enum", "complaint_source", "Unsupported complaint source.")
    if payload.get("containment_status") not in _ALLOWED_CONTAINMENT:
        _issue(issues, "invalid_enum", "containment_status", "Unsupported containment status.")
    if payload.get("review_status") not in _ALLOWED_REVIEW_STATUSES:
        _issue(issues, "invalid_enum", "review_status", "Unsupported review status.")
    try:
        date.fromisoformat(str(payload.get("received_date")))
    except ValueError:
        _issue(issues, "invalid_date", "received_date", "Received date must use ISO-8601 format.")

    linked = payload.get("linked_defect_codes", ())
    if not isinstance(linked, Sequence) or isinstance(linked, (str, bytes)):
        _issue(issues, "invalid_type", "linked_defect_codes", "Linked defect codes must be a sequence.")
    if payload.get("review_status") == "reviewed" and not str(payload.get("reviewed_by") or "").strip():
        _issue(issues, "human_review_required", "reviewed_by", "Reviewed complaint requires a human reviewer.")

    quantity = payload.get("affected_quantity")
    if quantity is not None and (not isinstance(quantity, (int, float)) or quantity < 0):
        _issue(issues, "invalid_quantity", "affected_quantity", "Affected quantity must be zero or greater.")
    if quantity is not None and not str(payload.get("quantity_unit") or "").strip():
        _issue(issues, "missing_unit", "quantity_unit", "Affected quantity requires a unit.")

    _validate_evidence(payload, issues)
    _reject_build6(payload, issues)
    return TaxonomyValidation(tuple(issues))
