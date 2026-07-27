from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from src.persistence._utils import content_hash, new_id
from src.review_comparison import ReviewState

from .canonical_mapping import UnifiedCanonicalDraft
from .pairing import SpecificationPair
from .review_view import CommonReviewView, all_reviews_resolved

EXTRACTION_SCHEMA_VERSION = "pve-unified-specification-extraction-v1"
ALIAS_REGISTRY_VERSION = "1.0"
PROVIDER_ID = "deterministic-unified-specification"
_ACCEPTED = {ReviewState.CONFIRMED, ReviewState.CORRECTED_CONFIRMED}


@dataclass(frozen=True)
class SnapshotDocument:
    role: str
    format: str
    filename: str
    sha256: str
    parser_name: str
    parser_version: str


@dataclass(frozen=True)
class SnapshotField:
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
    source_format: str
    document_sha256: str
    parser_name: str
    parser_version: str
    source_block_id: str
    source_excerpt: str
    source_location: dict[str, object]
    confidence: float
    confidence_band: str
    ambiguity_codes: tuple[str, ...]
    reviewer_note: str | None


@dataclass(frozen=True)
class UnifiedSpecificationSnapshot:
    snapshot_id: str
    project_id: str
    pair_format: str
    existing_document: SnapshotDocument
    proposed_document: SnapshotDocument
    extraction_schema_version: str
    alias_registry_version: str
    provider_id: str
    confirmed_fields: tuple[SnapshotField, ...]
    canonical_dataset_draft: dict[str, Any]
    canonical_validation_issues: tuple[dict[str, Any], ...]
    canonical_validation_valid: bool
    content_hash: str


def _snapshot_document(document) -> SnapshotDocument:
    return SnapshotDocument(
        role=document.document_role.value,
        format=document.document_format.value,
        filename=document.filename,
        sha256=document.sha256,
        parser_name=document.parser_name,
        parser_version=document.parser_version,
    )


def _confirmed_fields(views: Iterable[CommonReviewView]) -> tuple[SnapshotField, ...]:
    fields: list[SnapshotField] = []
    for view in sorted(views, key=lambda item: (item.document_role.value, item.field_name)):
        review = view.review
        if review.state not in _ACCEPTED:
            continue
        fields.append(SnapshotField(
            field_name=view.field_name,
            document_role=view.document_role.value,
            review_state=review.state.value,
            raw_value=review.candidate.raw_value,
            normalized_value=review.candidate.normalized_value,
            original_unit=review.candidate.unit,
            corrected_value=review.corrected_value,
            corrected_unit=review.corrected_unit,
            effective_value=review.effective_value,
            effective_unit=review.effective_unit,
            source_format=view.document_format,
            document_sha256=next(
                value for value in (view.filename,) if value is not None
            ) and "",
            parser_name=view.parser_name,
            parser_version=view.parser_version,
            source_block_id=view.source_block_id,
            source_excerpt=view.source_excerpt,
            source_location=dict(view.source_location),
            confidence=view.confidence,
            confidence_band=view.confidence_band,
            ambiguity_codes=view.ambiguity_codes,
            reviewer_note=review.reviewer_note,
        ))
    return tuple(fields)


def build_unified_snapshot(
    *,
    project_id: str,
    pair: SpecificationPair,
    views: Iterable[CommonReviewView],
    canonical: UnifiedCanonicalDraft,
    snapshot_id: str | None = None,
) -> UnifiedSpecificationSnapshot:
    if not project_id.strip():
        raise ValueError("Project ID is required.")
    items = tuple(views)
    if not all_reviews_resolved(items):
        raise ValueError("All extraction candidates must be reviewed before snapshot creation.")

    hashes = {
        pair.existing.document_role.value: pair.existing.sha256,
        pair.proposed.document_role.value: pair.proposed.sha256,
    }
    fields = []
    for field in _confirmed_fields(items):
        fields.append(SnapshotField(**{**asdict(field), "document_sha256": hashes[field.document_role]}))
    confirmed_fields = tuple(fields)
    if not confirmed_fields:
        raise ValueError("At least one confirmed or corrected-confirmed field is required.")

    existing = _snapshot_document(pair.existing)
    proposed = _snapshot_document(pair.proposed)
    payload = {
        "project_id": project_id,
        "pair_format": pair.pair_format.value,
        "existing_document": asdict(existing),
        "proposed_document": asdict(proposed),
        "versions": {
            "extraction_schema": EXTRACTION_SCHEMA_VERSION,
            "alias_registry": ALIAS_REGISTRY_VERSION,
            "provider": PROVIDER_ID,
        },
        "confirmed_fields": [asdict(field) for field in confirmed_fields],
        "canonical_dataset_draft": canonical.canonical_data,
        "canonical_validation_issues": list(canonical.validation_issues),
        "canonical_validation_valid": canonical.is_valid,
    }
    return UnifiedSpecificationSnapshot(
        snapshot_id=snapshot_id or new_id("spec-intake"),
        project_id=project_id,
        pair_format=pair.pair_format.value,
        existing_document=existing,
        proposed_document=proposed,
        extraction_schema_version=EXTRACTION_SCHEMA_VERSION,
        alias_registry_version=ALIAS_REGISTRY_VERSION,
        provider_id=PROVIDER_ID,
        confirmed_fields=confirmed_fields,
        canonical_dataset_draft=canonical.canonical_data,
        canonical_validation_issues=canonical.validation_issues,
        canonical_validation_valid=canonical.is_valid,
        content_hash=content_hash(payload),
    )
