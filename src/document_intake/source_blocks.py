"""Stable source block identifiers for deterministic DOCX parsing."""

from __future__ import annotations

import hashlib

from .document_models import DocumentRole, SourceBlockType, SourceLocation


def make_source_block_id(
    document_sha256: str,
    role: DocumentRole,
    block_type: SourceBlockType,
    location: SourceLocation,
) -> str:
    """Create a stable ID from document identity and structural location.

    Text is deliberately excluded so the identifier represents source location,
    while a changed document receives a different document hash and therefore a
    different block identifier.
    """

    coordinates = (
        location.paragraph_index,
        location.table_index,
        location.row_index,
        location.cell_index,
        location.section_title or "",
    )
    payload = "|".join(
        [document_sha256, role.value, block_type.value, *(str(value) for value in coordinates)]
    )
    return "src_" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]
