from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

_ALLOWED_DOCUMENT_TYPES = {"drawing", "artwork", "dieline", "tooling", "cad"}
_ALLOWED_FILE_FORMATS = {"pdf", "dxf", "dwg", "svg", "png", "jpeg", "jpg", "ai", "eps"}
_ALLOWED_CLASSIFICATIONS = {"baseline", "proposed"}
_ALLOWED_SOURCE_CLASSES = {
    "uploaded_fact",
    "manually_entered_fact",
    "supplier_declared_value",
    "laboratory_tested_value",
    "observed_trial_result",
    "predicted_value",
    "assumption",
    "synthetic_demo",
}
_ALLOWED_VALIDATION_STATUSES = {"not_validated", "validation_required", "validated", "rejected"}
_ALLOWED_APPROVAL_STATUSES = {"not_approved", "approval_required", "approved", "rejected"}


@dataclass(frozen=True)
class DrawingEvidenceIssue:
    code: str
    field: str
    message: str


@dataclass(frozen=True)
class DrawingEvidenceValidation:
    issues: tuple[DrawingEvidenceIssue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues


def _issue(issues: list[DrawingEvidenceIssue], code: str, field: str, message: str) -> None:
    issues.append(DrawingEvidenceIssue(code=code, field=field, message=message))


def _required(payload: Mapping[str, Any], field: str, issues: list[DrawingEvidenceIssue]) -> None:
    if payload.get(field) in (None, ""):
        _issue(issues, "missing_required", field, "Required field is missing or empty.")


def validate_drawing_evidence(payload: Mapping[str, Any]) -> DrawingEvidenceValidation:
    """Validate governed metadata without interpreting CAD geometry or dimensions."""
    issues: list[DrawingEvidenceIssue] = []
    for field in (
        "project_id",
        "document_type",
        "document_number",
        "title",
        "revision",
        "classification",
        "file_format",
        "source_reference",
        "source_classification",
        "validation_status",
        "approval_status",
        "content_hash",
    ):
        _required(payload, field, issues)

    if payload.get("document_type") not in _ALLOWED_DOCUMENT_TYPES:
        _issue(issues, "invalid_enum", "document_type", "Unsupported drawing-evidence document type.")
    if str(payload.get("file_format", "")).lower() not in _ALLOWED_FILE_FORMATS:
        _issue(issues, "invalid_enum", "file_format", "Unsupported governed file format.")
    if payload.get("classification") not in _ALLOWED_CLASSIFICATIONS:
        _issue(issues, "invalid_enum", "classification", "Classification must be baseline or proposed.")
    if payload.get("source_classification") not in _ALLOWED_SOURCE_CLASSES:
        _issue(issues, "invalid_enum", "source_classification", "Unsupported source classification.")
    if payload.get("validation_status") not in _ALLOWED_VALIDATION_STATUSES:
        _issue(issues, "invalid_enum", "validation_status", "Unsupported validation status.")
    if payload.get("approval_status") not in _ALLOWED_APPROVAL_STATUSES:
        _issue(issues, "invalid_enum", "approval_status", "Unsupported approval status.")

    digest = str(payload.get("content_hash") or "")
    if digest and (len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower())):
        _issue(issues, "invalid_hash", "content_hash", "Content hash must be a 64-character SHA-256 hex digest.")

    issue_date = payload.get("issue_date")
    effective_date = payload.get("effective_date")
    try:
        parsed_issue = date.fromisoformat(str(issue_date)) if issue_date else None
        parsed_effective = date.fromisoformat(str(effective_date)) if effective_date else None
        if parsed_issue and parsed_effective and parsed_effective < parsed_issue:
            _issue(issues, "invalid_date_order", "effective_date", "Effective date cannot precede issue date.")
    except ValueError:
        _issue(issues, "invalid_date", "issue_date/effective_date", "Dates must use ISO YYYY-MM-DD format.")

    if payload.get("approval_status") == "approved" and payload.get("validation_status") != "validated":
        _issue(issues, "approval_without_validation", "approval_status", "Approval requires validated status.")

    if str(payload.get("file_format", "")).lower() in {"dxf", "dwg"} and payload.get("geometry_interpreted"):
        _issue(issues, "cad_interpretation_prohibited", "geometry_interpreted", "Build 2A stores DXF/DWG as governed references only.")

    return DrawingEvidenceValidation(tuple(issues))
