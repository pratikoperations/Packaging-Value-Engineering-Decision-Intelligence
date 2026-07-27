"""Build immutable, content-addressed confirmed Word-intake snapshots."""

from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from src.document_intake import DocumentPair
from src.persistence._utils import content_hash, new_id
from src.review_comparison import FieldReviewGroup, ReviewState, unresolved_reason

from .models import ConfirmedField, ConfirmedIntakeSnapshot, IntakeMappingError

ACCEPTED_STATES = {ReviewState.CONFIRMED, ReviewState.CORRECTED_CONFIRMED}


def _location_payload(location) -> dict[str, object]:
    return {
        "paragraph_index": location.paragraph_index,
        "table_index": location.table_index,
        "row_index": location.row_index,
        "cell_index": location.cell_index,
        "section_title": location.section_title,
    }


def collect_confirmed_fields(groups: Iterable[FieldReviewGroup]) -> tuple[ConfirmedField, ...]:
    fields: list[ConfirmedField] = []
    for group in sorted(groups, key=lambda item: (item.document_role.value, item.field_name)):
        reason = unresolved_reason(group)
        if reason is not None:
            raise IntakeMappingError(
                f"Cannot create snapshot while {group.document_role.value}:{group.field_name} is unresolved: {reason}."
            )
        selected = group.selected_review
        if selected is None or selected.state not in ACCEPTED_STATES:
            continue
        candidate = selected.candidate
        fields.append(
            ConfirmedField(
                field_name=group.field_name,
                document_role=group.document_role.value,
                review_state=selected.state.value,
                raw_value=candidate.raw_value,
                normalized_value=candidate.normalized_value,
                original_unit=candidate.unit,
                corrected_value=selected.corrected_value,
                corrected_unit=selected.corrected_unit,
                effective_value=selected.effective_value,
                effective_unit=selected.effective_unit,
                confidence=candidate.confidence,
                confidence_band=candidate.confidence_band.value,
                ambiguity_codes=tuple(code.value for code in candidate.ambiguity_codes),
                source_block_id=selected.source.block_id,
                source_excerpt=selected.source.excerpt,
                source_location=_location_payload(selected.source.location),
                reviewer_note=selected.reviewer_note,
            )
        )
    return tuple(fields)


def build_confirmed_snapshot(
    *,
    project_id: str,
    documents: DocumentPair,
    groups: Iterable[FieldReviewGroup],
    canonical_dataset_draft: dict,
    canonical_validation_issues: tuple[dict, ...],
    canonical_validation_valid: bool,
    parser_version: str,
    extraction_schema_version: str,
    alias_registry_version: str,
    provider_id: str,
    snapshot_id: str | None = None,
) -> ConfirmedIntakeSnapshot:
    if not project_id.strip():
        raise IntakeMappingError("Project ID is required.")
    for label, value in {
        "parser_version": parser_version,
        "extraction_schema_version": extraction_schema_version,
        "alias_registry_version": alias_registry_version,
        "provider_id": provider_id,
    }.items():
        if not value.strip():
            raise IntakeMappingError(f"{label} is required.")

    confirmed_fields = collect_confirmed_fields(groups)
    if not confirmed_fields:
        raise IntakeMappingError("At least one confirmed or corrected-confirmed field is required.")

    payload = {
        "project_id": project_id,
        "documents": {
            "existing": {
                "filename": documents.existing.filename,
                "sha256": documents.existing.sha256,
            },
            "proposed": {
                "filename": documents.proposed.filename,
                "sha256": documents.proposed.sha256,
            },
        },
        "versions": {
            "parser": parser_version,
            "extraction_schema": extraction_schema_version,
            "alias_registry": alias_registry_version,
            "provider": provider_id,
        },
        "confirmed_fields": [asdict(field) for field in confirmed_fields],
        "canonical_dataset_draft": canonical_dataset_draft,
        "canonical_validation_issues": list(canonical_validation_issues),
        "canonical_validation_valid": canonical_validation_valid,
    }
    digest = content_hash(payload)
    return ConfirmedIntakeSnapshot(
        snapshot_id=snapshot_id or new_id("word-intake"),
        project_id=project_id,
        existing_filename=documents.existing.filename,
        existing_document_hash=documents.existing.sha256,
        proposed_filename=documents.proposed.filename,
        proposed_document_hash=documents.proposed.sha256,
        parser_version=parser_version,
        extraction_schema_version=extraction_schema_version,
        alias_registry_version=alias_registry_version,
        provider_id=provider_id,
        confirmed_fields=confirmed_fields,
        canonical_dataset_draft=canonical_dataset_draft,
        canonical_validation_issues=canonical_validation_issues,
        canonical_validation_valid=canonical_validation_valid,
        content_hash=digest,
    )
