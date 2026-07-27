"""Governed contracts for source-grounded AI-assisted Word extraction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Tuple

from src.document_intake import DocumentRole, SourceBlock


class ExtractionContractError(ValueError):
    """Raised when provider output violates the governed extraction contract."""


class AmbiguityCode(str, Enum):
    MULTIPLE_CANDIDATES = "multiple_candidates"
    INTERNAL_EXTERNAL_UNCLEAR = "internal_external_unclear"
    REQUIREMENT_RESULT_UNCLEAR = "requirement_result_unclear"
    UNIT_MISSING = "unit_missing"
    UNIT_CONFLICT = "unit_conflict"
    DOCUMENT_ROLE_UNCLEAR = "document_role_unclear"
    TABLE_HEADERS_UNCLEAR = "table_headers_unclear"
    EMBEDDED_IMAGE_ONLY = "embedded_image_only"
    SOURCE_NOT_FOUND = "source_not_found"
    PROMPT_INJECTION_SUSPECTED = "prompt_injection_suspected"


class ConfidenceBand(str, Enum):
    HIGH = "high"
    REVIEW = "review"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ExtractionCandidate:
    field_name: str
    document_role: DocumentRole
    raw_value: Any
    normalized_value: Any
    unit: str | None
    confidence: float
    confidence_band: ConfidenceBand
    source_block_id: str
    source_excerpt: str
    ambiguity_codes: Tuple[AmbiguityCode, ...] = ()


@dataclass(frozen=True)
class ExtractionResult:
    schema_version: str
    provider_id: str
    candidates: Tuple[ExtractionCandidate, ...]
    missing_fields: Tuple[str, ...]
    unsupported_content: Tuple[str, ...]


@dataclass(frozen=True)
class ExtractionRequest:
    schema_version: str
    allowed_fields: Tuple[str, ...]
    blocks: Tuple[SourceBlock, ...]
    document_role: DocumentRole


def require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ExtractionContractError(f"{label} must be an object.")
    return value
