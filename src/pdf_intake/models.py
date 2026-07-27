"""Models for controlled searchable digital PDF intake."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from src.document_intake import DocumentRole


class PdfEligibility(str, Enum):
    SEARCHABLE = "searchable"
    SCANNED_OR_IMAGE_ONLY = "scanned_or_image_only"
    INSUFFICIENT_EXTRACTABLE_TEXT = "insufficient_extractable_text"


class PdfLayoutWarning(str, Enum):
    MULTI_COLUMN_SUSPECTED = "multi_column_suspected"
    TABLE_LIKE_CONTENT = "table_like_content"


@dataclass(frozen=True)
class ValidatedPdf:
    filename: str
    role: DocumentRole
    content: bytes
    sha256: str
    page_count: int
    extracted_character_count: int
    pages_with_meaningful_text: int
    eligibility: PdfEligibility


@dataclass(frozen=True)
class PdfSourceBlock:
    block_id: str
    page_number: int
    block_index: int
    extraction_order: int
    raw_text: str
    normalized_text: str
    parser_version: str
    warnings: Tuple[PdfLayoutWarning, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ParsedPdf:
    filename: str
    role: DocumentRole
    sha256: str
    page_count: int
    parser_version: str
    blocks: Tuple[PdfSourceBlock, ...]
    warnings: Tuple[PdfLayoutWarning, ...] = field(default_factory=tuple)
