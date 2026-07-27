from __future__ import annotations

from dataclasses import dataclass

from src.upload_routing.models import FileFormat

from .models import DocumentRole, PairFormat, UnifiedSpecificationDocument


@dataclass(frozen=True)
class SpecificationPair:
    existing: UnifiedSpecificationDocument
    proposed: UnifiedSpecificationDocument
    pair_format: PairFormat


def classify_pair(existing_format: FileFormat, proposed_format: FileFormat) -> PairFormat:
    mapping = {
        (FileFormat.PDF, FileFormat.PDF): PairFormat.PDF_PDF,
        (FileFormat.DOCX, FileFormat.DOCX): PairFormat.DOCX_DOCX,
        (FileFormat.PDF, FileFormat.DOCX): PairFormat.PDF_DOCX,
        (FileFormat.DOCX, FileFormat.PDF): PairFormat.DOCX_PDF,
    }
    try:
        return mapping[(existing_format, proposed_format)]
    except KeyError as exc:
        raise ValueError("Specification pairs must contain DOCX or searchable PDF documents only.") from exc


def build_pair(documents: tuple[UnifiedSpecificationDocument, ...]) -> SpecificationPair:
    if len(documents) != 2:
        raise ValueError("Exactly one existing and one proposed specification are required.")
    by_role = {document.document_role: document for document in documents}
    if set(by_role) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
        raise ValueError("Exactly one existing and one proposed specification are required.")
    existing = by_role[DocumentRole.EXISTING]
    proposed = by_role[DocumentRole.PROPOSED]
    if existing.sha256 == proposed.sha256:
        raise ValueError("Duplicate specification content is not allowed.")
    return SpecificationPair(
        existing=existing,
        proposed=proposed,
        pair_format=classify_pair(existing.document_format, proposed.document_format),
    )
