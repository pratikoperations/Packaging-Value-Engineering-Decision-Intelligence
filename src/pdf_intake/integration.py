"""Adapters that reuse the existing governed extraction, review and comparison layers.

PDF-specific page and layout metadata is retained alongside the existing review
objects. No live provider, persistence, canonical mapping, OCR, or decision logic
is introduced here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

from src.ai_extraction import ExtractionProvider, ExtractionResult, extract_document
from src.document_intake import (
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
)
from src.review_comparison import (
    CandidateReview,
    ChangeSummary,
    FieldComparison,
    FieldReviewGroup,
    build_candidate_reviews,
    build_change_summary,
    compare_fields,
    group_reviews,
)

from .models import ParsedPdf, PdfLayoutWarning, PdfSourceBlock


@dataclass(frozen=True)
class PdfReviewEvidence:
    """PDF page metadata bound to an existing governed candidate review."""

    review: CandidateReview
    page_number: int
    pdf_block_index: int
    extraction_order: int
    parser_version: str
    layout_warnings: Tuple[PdfLayoutWarning, ...]
    raw_source_text: str


@dataclass(frozen=True)
class PdfReviewBundle:
    """Existing review groups plus page-aware evidence for PDF candidates."""

    reviews: Tuple[PdfReviewEvidence, ...]
    groups: Tuple[FieldReviewGroup, ...]


def pdf_to_parsed_document(document: ParsedPdf) -> ParsedDocument:
    """Convert PDF source blocks to the existing extraction request boundary.

    The normalized text is used for candidate grounding while exact raw PDF text
    remains available in ``ParsedPdf`` and ``PdfReviewEvidence``.
    """

    blocks = tuple(
        SourceBlock(
            block_id=block.block_id,
            block_type=SourceBlockType.PARAGRAPH,
            text=block.normalized_text,
            location=SourceLocation(
                paragraph_index=block.block_index,
                section_title=f"PDF page {block.page_number}",
            ),
        )
        for block in document.blocks
    )
    return ParsedDocument(
        filename=document.filename,
        role=document.role,
        sha256=document.sha256,
        blocks=blocks,
    )


def extract_pdf_document(
    document: ParsedPdf,
    provider: ExtractionProvider,
) -> ExtractionResult:
    """Run a PDF through the existing provider-neutral governed extraction layer."""

    return extract_document(pdf_to_parsed_document(document), provider)


def build_pdf_review_bundle(
    candidates,
    documents: Iterable[ParsedPdf],
) -> PdfReviewBundle:
    """Create existing review groups and retain PDF page/layout evidence."""

    pdf_documents = tuple(documents)
    adapted = tuple(pdf_to_parsed_document(document) for document in pdf_documents)
    base_reviews = build_candidate_reviews(candidates, adapted)

    block_index: dict[tuple[object, str], PdfSourceBlock] = {}
    for document in pdf_documents:
        for block in document.blocks:
            block_index[(document.role, block.block_id)] = block

    evidence: list[PdfReviewEvidence] = []
    for review in base_reviews:
        block = block_index.get(
            (review.candidate.document_role, review.candidate.source_block_id)
        )
        if block is None:
            raise ValueError("PDF source metadata is unavailable for candidate review.")
        evidence.append(
            PdfReviewEvidence(
                review=review,
                page_number=block.page_number,
                pdf_block_index=block.block_index,
                extraction_order=block.extraction_order,
                parser_version=block.parser_version,
                layout_warnings=block.layout_warnings,
                raw_source_text=block.raw_text,
            )
        )

    return PdfReviewBundle(
        reviews=tuple(evidence),
        groups=group_reviews(base_reviews),
    )


def compare_pdf_review_groups(
    groups: Iterable[FieldReviewGroup],
    governed_field_names: Iterable[str],
) -> tuple[Tuple[FieldComparison, ...], ChangeSummary]:
    """Reuse existing comparison statuses and deterministic change summary."""

    groups = tuple(groups)
    comparisons = compare_fields(governed_field_names, groups)
    return comparisons, build_change_summary(comparisons, groups)
