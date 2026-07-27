"""Models for controlled searchable digital PDF intake."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.document_intake import DocumentRole


class PdfEligibility(str, Enum):
    SEARCHABLE = "searchable"
    SCANNED_OR_IMAGE_ONLY = "scanned_or_image_only"
    INSUFFICIENT_EXTRACTABLE_TEXT = "insufficient_extractable_text"


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
