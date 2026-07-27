"""Confirmed Word-intake snapshot and canonical-draft models.

Build Group E remains additive. It does not alter existing canonical validation,
readiness, threshold, scenario, recommendation, or decision logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Tuple


class IntakeMappingError(ValueError):
    """Raised when reviewed extraction data cannot be safely snapshotted or mapped."""


@dataclass(frozen=True)
class ConfirmedField:
    field_name: str
    document_role: str
    review_state: str
    raw_value: Any
    normalized_value: Any
    original_unit: str | None
    corrected_value: Any
    corrected_unit: str | None
    effective_value: Any
    effective_unit: str | None
    confidence: float
    confidence_band: str
    ambiguity_codes: Tuple[str, ...]
    source_block_id: str
    source_excerpt: str
    source_location: Mapping[str, Any]
    reviewer_note: str | None


@dataclass(frozen=True)
class ConfirmedIntakeSnapshot:
    snapshot_id: str
    project_id: str
    existing_filename: str
    existing_document_hash: str
    proposed_filename: str
    proposed_document_hash: str
    parser_version: str
    extraction_schema_version: str
    alias_registry_version: str
    provider_id: str
    confirmed_fields: Tuple[ConfirmedField, ...]
    canonical_dataset_draft: Mapping[str, Any]
    canonical_validation_issues: Tuple[Mapping[str, Any], ...]
    canonical_validation_valid: bool
    content_hash: str
