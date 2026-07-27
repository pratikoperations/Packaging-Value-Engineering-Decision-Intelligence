"""PVE 2.1 searchable digital PDF intake boundary."""

from .file_validation import PdfValidationError, validate_pdf, validate_pdf_pair
from .integration import (
    PdfReviewBundle,
    PdfReviewEvidence,
    build_pdf_review_bundle,
    compare_pdf_review_groups,
    extract_pdf_document,
    pdf_to_parsed_document,
)
from .models import (
    ParsedPdf,
    PdfEligibility,
    PdfLayoutWarning,
    PdfSourceBlock,
    ValidatedPdf,
)
from .pdf_parser import PDF_PARSER_VERSION, normalize_pdf_text, parse_validated_pdf
from .snapshot import (
    ConfirmedPdfField,
    ConfirmedPdfSnapshot,
    build_confirmed_pdf_snapshot,
    build_pdf_canonical_dataset_draft,
)
from .source_blocks import make_pdf_source_block_id

__all__ = [
    "ConfirmedPdfField",
    "ConfirmedPdfSnapshot",
    "PDF_PARSER_VERSION",
    "ParsedPdf",
    "PdfEligibility",
    "PdfLayoutWarning",
    "PdfReviewBundle",
    "PdfReviewEvidence",
    "PdfSourceBlock",
    "PdfValidationError",
    "ValidatedPdf",
    "build_confirmed_pdf_snapshot",
    "build_pdf_canonical_dataset_draft",
    "build_pdf_review_bundle",
    "compare_pdf_review_groups",
    "extract_pdf_document",
    "make_pdf_source_block_id",
    "normalize_pdf_text",
    "parse_validated_pdf",
    "pdf_to_parsed_document",
    "validate_pdf",
    "validate_pdf_pair",
]
