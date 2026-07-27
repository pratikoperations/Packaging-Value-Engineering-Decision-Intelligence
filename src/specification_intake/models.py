from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.upload_routing.models import FileFormat


class DocumentRole(str, Enum):
    EXISTING = "existing"
    PROPOSED = "proposed"


class PairFormat(str, Enum):
    PDF_PDF = "pdf_pdf"
    DOCX_DOCX = "docx_docx"
    PDF_DOCX = "pdf_docx"
    DOCX_PDF = "docx_pdf"


@dataclass(frozen=True)
class UnifiedSourceBlock:
    block_id: str
    document_role: DocumentRole
    document_format: FileFormat
    raw_text: str
    normalized_text: str
    extraction_order: int
    parser_name: str
    parser_version: str
    source_location: dict[str, object]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class UnifiedSpecificationDocument:
    filename: str
    document_role: DocumentRole
    document_format: FileFormat
    sha256: str
    parser_name: str
    parser_version: str
    source_blocks: tuple[UnifiedSourceBlock, ...] = ()
    warnings: tuple[str, ...] = ()
