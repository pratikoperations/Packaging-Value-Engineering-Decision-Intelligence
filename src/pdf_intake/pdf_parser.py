"""Deterministic page-by-page parser for eligible searchable PDFs."""

from __future__ import annotations

import io
import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from .file_validation import PdfValidationError
from .models import ParsedPdf, PdfLayoutWarning, PdfSourceBlock, ValidatedPdf
from .source_blocks import make_pdf_source_block_id

PDF_PARSER_VERSION = "pve-pdf-parser-v1"
_TABLE_SEPARATORS = re.compile(r"(?:\t|\||\s{3,})")


def normalize_pdf_text(text: str) -> str:
    """Normalize whitespace for comparison while preserving raw evidence separately."""

    return " ".join(text.split())


def _layout_warnings(raw_text: str) -> tuple[PdfLayoutWarning, ...]:
    lines = [line for line in raw_text.splitlines() if line.strip()]
    warnings: list[PdfLayoutWarning] = []
    table_like_lines = sum(1 for line in lines if _TABLE_SEPARATORS.search(line))
    if table_like_lines >= 2:
        warnings.append(PdfLayoutWarning.TABLE_LIKE_CONTENT)
    wide_gap_lines = sum(1 for line in lines if re.search(r"\S\s{8,}\S", line))
    if wide_gap_lines >= 2:
        warnings.append(PdfLayoutWarning.MULTI_COLUMN_SUSPECTED)
    return tuple(warnings)


def _split_blocks(raw_text: str) -> list[str]:
    """Create ordered evidence blocks without altering retained source text."""

    blocks: list[str] = []
    current: list[str] = []
    for line in raw_text.splitlines():
        if line.strip():
            current.append(line.rstrip())
        elif current:
            blocks.append("\n".join(current))
            current = []
    if current:
        blocks.append("\n".join(current))
    if not blocks and raw_text.strip():
        blocks.append(raw_text.strip("\n"))
    return blocks


def parse_validated_pdf(
    document: ValidatedPdf,
    *,
    parser_version: str = PDF_PARSER_VERSION,
) -> ParsedPdf:
    """Extract ordered page-aware source blocks from an eligible PDF."""

    if not parser_version.strip():
        raise PdfValidationError("Parser version is required.")
    try:
        reader = PdfReader(io.BytesIO(document.content), strict=True)
    except (PdfReadError, OSError, ValueError) as exc:
        raise PdfValidationError("PDF became malformed or unreadable during parsing.") from exc

    blocks: list[PdfSourceBlock] = []
    document_warnings: set[PdfLayoutWarning] = set()
    extraction_order = 0
    for page_index, page in enumerate(reader.pages):
        page_number = page_index + 1
        try:
            raw_page_text = page.extract_text() or ""
        except Exception as exc:  # pypdf may expose diverse malformed-content errors
            raise PdfValidationError(
                f"PDF page {page_number} text could not be read safely."
            ) from exc
        page_warnings = _layout_warnings(raw_page_text)
        document_warnings.update(page_warnings)
        for block_index, raw_block in enumerate(_split_blocks(raw_page_text)):
            normalized = normalize_pdf_text(raw_block)
            if not normalized:
                continue
            blocks.append(
                PdfSourceBlock(
                    block_id=make_pdf_source_block_id(
                        document.sha256,
                        document.role,
                        page_number,
                        block_index,
                        parser_version,
                    ),
                    page_number=page_number,
                    block_index=block_index,
                    extraction_order=extraction_order,
                    raw_text=raw_block,
                    normalized_text=normalized,
                    parser_version=parser_version,
                    warnings=page_warnings,
                )
            )
            extraction_order += 1

    if not blocks:
        raise PdfValidationError("Eligible PDF produced no extractable source blocks.")
    return ParsedPdf(
        filename=document.filename,
        role=document.role,
        sha256=document.sha256,
        page_count=document.page_count,
        parser_version=parser_version,
        blocks=tuple(blocks),
        warnings=tuple(sorted(document_warnings, key=lambda item: item.value)),
    )
