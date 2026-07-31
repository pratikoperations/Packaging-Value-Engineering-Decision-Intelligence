from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class ExplanationQuestion(str, Enum):
    STATUS_REASON = "STATUS_REASON"
    INPUTS_AFFECTING_RESULT = "INPUTS_AFFECTING_RESULT"
    APPLIED_ASSUMPTIONS = "APPLIED_ASSUMPTIONS"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    OVERRIDING_BLOCKERS = "OVERRIDING_BLOCKERS"
    REQUIRED_VALIDATION = "REQUIRED_VALIDATION"
    PROVEN_CLAIMS = "PROVEN_CLAIMS"
    UNPROVEN_CLAIMS = "UNPROVEN_CLAIMS"
    STATUS_IMPROVEMENT_REQUIREMENTS = "STATUS_IMPROVEMENT_REQUIREMENTS"


class SourceClassification(str, Enum):
    OBSERVED = "OBSERVED"
    DECLARED = "DECLARED"
    DERIVED = "DERIVED"
    ASSUMED = "ASSUMED"
    MISSING = "MISSING"
    VALIDATION_PENDING = "VALIDATION_PENDING"
    APPROVED_SNAPSHOT = "APPROVED_SNAPSHOT"
    AUTHORIZED_HANDOFF = "AUTHORIZED_HANDOFF"


@dataclass(frozen=True)
class SourceReference:
    field: str
    value: Any
    classification: SourceClassification
    source_record: str
    rule_reference: str = ""

    def canonical(self) -> dict[str, Any]:
        return {
            "classification": self.classification.value,
            "field": self.field,
            "rule_reference": self.rule_reference,
            "source_record": self.source_record,
            "value": self.value,
        }


@dataclass(frozen=True)
class ExplanationContext:
    project_id: str
    target_id: str
    target_type: str
    revision_reference: str
    status: str
    status_reason: str
    sources: tuple[SourceReference, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    evidence_gaps: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    required_validation: tuple[str, ...] = field(default_factory=tuple)
    required_human_action: tuple[str, ...] = field(default_factory=tuple)
    proven_claims: tuple[str, ...] = field(default_factory=tuple)
    claim_limitations: tuple[str, ...] = field(default_factory=tuple)
    status_improvement_requirements: tuple[str, ...] = field(default_factory=tuple)
    source_hash: str = ""
    archived: bool = False


@dataclass(frozen=True)
class ExplanationRequest:
    project_id: str
    target_id: str
    question: ExplanationQuestion
    revision_reference: str = ""


@dataclass(frozen=True)
class ExplanationResponse:
    schema_version: str
    question: ExplanationQuestion
    answer_summary: str
    project_reference: str
    target_reference: str
    target_type: str
    revision_reference: str
    status: str
    source_fields: tuple[SourceReference, ...]
    assumptions: tuple[str, ...]
    evidence_gaps: tuple[str, ...]
    blocking_controls: tuple[str, ...]
    required_validation: tuple[str, ...]
    required_human_action: tuple[str, ...]
    proven_claims: tuple[str, ...]
    claim_limitations: tuple[str, ...]
    source_hash: str
    archived: bool

    def canonical(self) -> dict[str, Any]:
        return {
            "answer_summary": self.answer_summary,
            "archived": self.archived,
            "assumptions": list(self.assumptions),
            "blocking_controls": list(self.blocking_controls),
            "claim_limitations": list(self.claim_limitations),
            "evidence_gaps": list(self.evidence_gaps),
            "project_reference": self.project_reference,
            "proven_claims": list(self.proven_claims),
            "question": self.question.value,
            "required_human_action": list(self.required_human_action),
            "required_validation": list(self.required_validation),
            "revision_reference": self.revision_reference,
            "schema_version": self.schema_version,
            "source_fields": [item.canonical() for item in self.source_fields],
            "source_hash": self.source_hash,
            "status": self.status,
            "target_reference": self.target_reference,
            "target_type": self.target_type,
        }


class ExplanationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


ERROR_MESSAGES: Mapping[str, str] = {
    "UNSUPPORTED_QUESTION": "SourceMate supports a fixed catalogue of governed explanation questions. This question is outside the current capability boundary. No answer has been generated.",
    "INSUFFICIENT_CONTEXT": "The selected record does not contain sufficient governed context for this explanation. No assumptions were added.",
    "RECORD_NOT_FOUND": "The requested record was not found within the selected project.",
    "PROJECT_SCOPE_VIOLATION": "The requested record does not belong to the selected project. Access has been rejected.",
    "INTEGRITY_FAILURE": "The selected governed record failed its existing integrity check and cannot be explained.",
}


def require_text(value: str, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ExplanationError("INSUFFICIENT_CONTEXT", f"{field_name} is required.")
    return normalized


def ordered(values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted({str(value).strip() for value in values if str(value).strip()}))
