"""Deterministic validation and eligibility checks for digital PDFs."""

from __future__ import annotations

import hashlib
import io
from pathlib import PurePath
from typing import Iterable

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.document_intake import DocumentRole

from .models import PdfEligibility, ValidatedPdf

MAX_PDF_BYTES = 15 * 1024 * 1024
MAX_PAGES = 100
MIN_MEANINGFUL_CHARS_PER_PAGE = 20
MIN_TOTAL_CHARS = 100


class PdfValidationError(ValueError):
    """Raised when a PDF violates the controlled PVE 2.1 intake contract."""


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _meaningful_text(text: str) -> str:
    return " ".join(text.split())


def validate_pdf(
    filename: str,
    content: bytes,
    role: DocumentRole,
    *,
    mime_type: str | None = "application/pdf",
    max_bytes: int = MAX_PDF_BYTES,
    max_pages: int = MAX_PAGES,
) -> ValidatedPdf:
    if not isinstance(role, DocumentRole):
        raise PdfValidationError("Document role must be existing or proposed.")
    if not filename or PurePath(filename).suffix.lower() != ".pdf":
        raise PdfValidationError("Only .pdf files are supported.")
    if mime_type not in {None, "application/pdf", "application/x-pdf"}:
        raise PdfValidationError("Uploaded MIME type is not an approved PDF type.")
    if not isinstance(content, bytes) or not content:
        raise PdfValidationError("PDF content must be non-empty bytes.")
    if len(content) > max_bytes:
        raise PdfValidationError(f"PDF exceeds the {max_bytes}-byte size limit.")
    if not content.startswith(b"%PDF-"):
        raise PdfValidationError("File does not contain a valid PDF signature.")

    try:
        reader = PdfReader(io.BytesIO(content), strict=True)
    except (PdfReadError, OSError, ValueError) as exc:
        raise PdfValidationError("PDF is malformed or unreadable.") from exc

    if reader.is_encrypted:
        raise PdfValidationError("Encrypted PDFs are not supported.")
    page_count = len(reader.pages)
    if page_count < 1:
        raise PdfValidationError("PDF contains no pages.")
    if page_count > max_pages:
        raise PdfValidationError(f"PDF exceeds the {max_pages}-page limit.")

    total_chars = 0
    meaningful_pages = 0
    try:
        for page in reader.pages:
            text = _meaningful_text(page.extract_text() or "")
            total_chars += len(text)
            if len(text) >= MIN_MEANINGFUL_CHARS_PER_PAGE:
                meaningful_pages += 1
    except Exception as exc:  # pypdf can surface diverse malformed-content exceptions
        raise PdfValidationError("PDF text layer could not be read safely.") from exc

    if total_chars == 0:
        eligibility = PdfEligibility.SCANNED_OR_IMAGE_ONLY
    elif total_chars < MIN_TOTAL_CHARS or meaningful_pages == 0:
        eligibility = PdfEligibility.INSUFFICIENT_EXTRACTABLE_TEXT
    else:
        eligibility = PdfEligibility.SEARCHABLE

    if eligibility is not PdfEligibility.SEARCHABLE:
        raise PdfValidationError(eligibility.value)

    return ValidatedPdf(
        filename=PurePath(filename).name,
        role=role,
        content=content,
        sha256=_sha256(content),
        page_count=page_count,
        extracted_character_count=total_chars,
        pages_with_meaningful_text=meaningful_pages,
        eligibility=eligibility,
    )


def validate_pdf_pair(documents: Iterable[ValidatedPdf]) -> tuple[ValidatedPdf, ValidatedPdf]:
    items = tuple(documents)
    if len(items) != 2:
        raise PdfValidationError("Exactly two PDF files are required.")
    by_role = {item.role: item for item in items}
    if set(by_role) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
        raise PdfValidationError("Exactly one existing and one proposed PDF are required.")
    existing = by_role[DocumentRole.EXISTING]
    proposed = by_role[DocumentRole.PROPOSED]
    if existing.sha256 == proposed.sha256:
        raise PdfValidationError("Existing and proposed PDFs are duplicates.")
    return existing, proposed
