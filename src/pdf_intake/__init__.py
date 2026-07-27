"""PVE 2.1 searchable digital PDF intake boundary."""

from .file_validation import PdfValidationError, validate_pdf, validate_pdf_pair
from .models import (
    ParsedPdf,
    PdfEligibility,
    PdfLayoutWarning,
    PdfSourceBlock,
    ValidatedPdf,
)
from .pdf_parser import PDF_PARSER_VERSION, normalize_pdf_text, parse_validated_pdf
from .source_blocks import make_pdf_source_block_id

__all__ = [
    "PDF_PARSER_VERSION",
    "ParsedPdf",
    "PdfEligibility",
    "PdfLayoutWarning",
    "PdfSourceBlock",
    "PdfValidationError",
    "ValidatedPdf",
    "make_pdf_source_block_id",
    "normalize_pdf_text",
    "parse_validated_pdf",
    "validate_pdf",
    "validate_pdf_pair",
]
