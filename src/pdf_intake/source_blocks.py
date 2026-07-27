"""Stable page-aware source identifiers for searchable digital PDFs."""

from __future__ import annotations

import hashlib

from src.document_intake import DocumentRole


def make_pdf_source_block_id(
    document_sha256: str,
    role: DocumentRole,
    page_number: int,
    block_index: int,
    parser_version: str,
) -> str:
    """Return a deterministic source ID bound to document, page and parser version."""

    if page_number < 1:
        raise ValueError("PDF page numbers are 1-based.")
    if block_index < 0:
        raise ValueError("PDF block index must be zero or greater.")
    if not parser_version.strip():
        raise ValueError("Parser version is required.")
    payload = "|".join(
        (
            document_sha256,
            role.value,
            str(page_number),
            str(block_index),
            parser_version,
        )
    )
    return "pdfsrc_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
