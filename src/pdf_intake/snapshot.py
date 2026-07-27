"""Confirmed-only PDF snapshot and canonical-draft boundary."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Tuple

from src.intake_mapping import IntakeMappingError, build_canonical_dataset_draft, collect_confirmed_fields
from src.persistence._utils import content_hash, new_id
from src.review_comparison import FieldReviewGroup

from .models import ParsedPdf


@dataclass(frozen=True)
class ConfirmedPdfField:
    field_name: str
    document_role: str
    review_state: str
    raw_value: Any
    normalized_value: Any
    corrected_value: Any
    effective_value: Any
    effective_unit: str | None
    source_block_id: str
    source_excerpt: str
    raw_pdf_text: str
    page_number: int
    block_index: int
    extraction_order: int
    parser_version: str
    confidence: float
    ambiguity_codes: Tuple[str, ...]
    reviewer_note: str | None


@dataclass(frozen=True)
class ConfirmedPdfSnapshot:
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
    confirmed_fields: Tuple[ConfirmedPdfField, ...]
    canonical_dataset_draft: Mapping[str, Any]
    canonical_validation_issues: Tuple[Mapping[str, Any], ...]
    canonical_validation_valid: bool
    content_hash: str


def build_pdf_canonical_dataset_draft(*, project: dict[str, Any], groups: Iterable[FieldReviewGroup], source_repository: str, source_commit: str):
    draft, issues, valid = build_canonical_dataset_draft(
        project=project,
        groups=groups,
        source_repository=source_repository,
        source_commit=source_commit,
    )
    draft["synthetic_notice"] = "PVE 2.1 PDF-intake portfolio data is synthetic and requires engineering validation and human approval."
    draft["baseline_specification"]["baseline_id"] = "BASE-PDF-INTAKE"
    draft["baseline_specification"]["evidence_id"] = "EVID-PDF-EXISTING"
    draft["decision_evidence"] = [
        {"evidence_id": "EVID-PDF-EXISTING", "evidence_type": "uploaded_searchable_pdf_specification", "reference": "Existing searchable PDF; page-level traceability is retained in the PDF snapshot."},
        {"evidence_id": "EVID-PDF-PROPOSED", "evidence_type": "uploaded_searchable_pdf_specification", "reference": "Proposed searchable PDF; page-level traceability is retained in the PDF snapshot."},
    ]
    draft["decision_recommendation"]["recommendation_id"] = "REC-PDF-INTAKE-DRAFT"
    return draft, issues, valid


def build_confirmed_pdf_snapshot(
    *,
    project_id: str,
    documents: Iterable[ParsedPdf],
    groups: Iterable[FieldReviewGroup],
    canonical_dataset_draft: dict[str, Any],
    canonical_validation_issues: tuple[dict[str, Any], ...],
    canonical_validation_valid: bool,
    extraction_schema_version: str,
    alias_registry_version: str,
    provider_id: str,
    snapshot_id: str | None = None,
) -> ConfirmedPdfSnapshot:
    docs = {document.role.value: document for document in documents}
    if set(docs) != {"existing", "proposed"}:
        raise IntakeMappingError("Exactly one existing and one proposed parsed PDF are required.")
    if not project_id.strip():
        raise IntakeMappingError("Project ID is required.")
    confirmed = collect_confirmed_fields(groups)
    if not confirmed:
        raise IntakeMappingError("At least one confirmed or corrected-confirmed PDF field is required.")
    blocks = {(doc.role.value, block.block_id): block for doc in docs.values() for block in doc.blocks}
    fields: list[ConfirmedPdfField] = []
    for field in confirmed:
        block = blocks.get((field.document_role, field.source_block_id))
        if block is None:
            raise IntakeMappingError("Confirmed PDF field source metadata is unavailable.")
        fields.append(ConfirmedPdfField(
            field_name=field.field_name,
            document_role=field.document_role,
            review_state=field.review_state,
            raw_value=field.raw_value,
            normalized_value=field.normalized_value,
            corrected_value=field.corrected_value,
            effective_value=field.effective_value,
            effective_unit=field.effective_unit,
            source_block_id=field.source_block_id,
            source_excerpt=field.source_excerpt,
            raw_pdf_text=block.raw_text,
            page_number=block.page_number,
            block_index=block.block_index,
            extraction_order=block.extraction_order,
            parser_version=block.parser_version,
            confidence=field.confidence,
            ambiguity_codes=field.ambiguity_codes,
            reviewer_note=field.reviewer_note,
        ))
    parser_versions = {doc.parser_version for doc in docs.values()}
    if len(parser_versions) != 1:
        raise IntakeMappingError("Existing and proposed PDFs must use the same parser version.")
    parser_version = next(iter(parser_versions))
    payload = {
        "project_id": project_id,
        "documents": {role: {"filename": doc.filename, "sha256": doc.sha256} for role, doc in sorted(docs.items())},
        "versions": {"parser": parser_version, "extraction_schema": extraction_schema_version, "alias_registry": alias_registry_version, "provider": provider_id},
        "confirmed_fields": [asdict(field) for field in fields],
        "canonical_dataset_draft": canonical_dataset_draft,
        "canonical_validation_issues": list(canonical_validation_issues),
        "canonical_validation_valid": canonical_validation_valid,
    }
    digest = content_hash(payload)
    return ConfirmedPdfSnapshot(
        snapshot_id=snapshot_id or new_id("pdf-intake"),
        project_id=project_id,
        existing_filename=docs["existing"].filename,
        existing_document_hash=docs["existing"].sha256,
        proposed_filename=docs["proposed"].filename,
        proposed_document_hash=docs["proposed"].sha256,
        parser_version=parser_version,
        extraction_schema_version=extraction_schema_version,
        alias_registry_version=alias_registry_version,
        provider_id=provider_id,
        confirmed_fields=tuple(fields),
        canonical_dataset_draft=canonical_dataset_draft,
        canonical_validation_issues=canonical_validation_issues,
        canonical_validation_valid=canonical_validation_valid,
        content_hash=digest,
    )
