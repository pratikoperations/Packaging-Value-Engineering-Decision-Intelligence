from __future__ import annotations

from src.document_intake import DocumentRole as LegacyDocumentRole
from src.document_intake.docx_parser import parse_validated_docx
from src.document_intake.file_validation import validate_docx
from src.pdf_intake.file_validation import validate_pdf
from src.pdf_intake.pdf_parser import PDF_PARSER_VERSION, parse_validated_pdf
from src.upload_routing.models import FileFormat

from .models import DocumentRole, UnifiedSourceBlock, UnifiedSpecificationDocument

DOCX_PARSER_NAME = "pve-docx-ooxml"
DOCX_PARSER_VERSION = "pve-docx-parser-v1"
PDF_PARSER_NAME = "pypdf"


def _legacy_role(role: DocumentRole) -> LegacyDocumentRole:
    return LegacyDocumentRole(role.value)


def adapt_docx(filename: str, content: bytes, role: DocumentRole) -> UnifiedSpecificationDocument:
    validated = validate_docx(filename, content, _legacy_role(role))
    parsed = parse_validated_docx(validated)
    blocks = tuple(
        UnifiedSourceBlock(
            block_id=block.block_id,
            document_role=role,
            document_format=FileFormat.DOCX,
            raw_text=block.text,
            normalized_text=" ".join(block.text.split()),
            extraction_order=index,
            parser_name=DOCX_PARSER_NAME,
            parser_version=DOCX_PARSER_VERSION,
            source_location={
                "type": "docx",
                "paragraph_index": block.location.paragraph_index,
                "table_index": block.location.table_index,
                "row_index": block.location.row_index,
                "cell_index": block.location.cell_index,
                "section_title": block.location.section_title,
            },
        )
        for index, block in enumerate(parsed.blocks)
    )
    warnings = tuple(sorted({item.code for item in parsed.unsupported_content}))
    return UnifiedSpecificationDocument(
        filename=parsed.filename,
        document_role=role,
        document_format=FileFormat.DOCX,
        sha256=parsed.sha256,
        parser_name=DOCX_PARSER_NAME,
        parser_version=DOCX_PARSER_VERSION,
        source_blocks=blocks,
        warnings=warnings,
    )


def adapt_pdf(
    filename: str,
    content: bytes,
    role: DocumentRole,
    *,
    mime_type: str | None = "application/pdf",
) -> UnifiedSpecificationDocument:
    validated = validate_pdf(filename, content, _legacy_role(role), mime_type=mime_type)
    parsed = parse_validated_pdf(validated)
    blocks = tuple(
        UnifiedSourceBlock(
            block_id=block.block_id,
            document_role=role,
            document_format=FileFormat.PDF,
            raw_text=block.raw_text,
            normalized_text=block.normalized_text,
            extraction_order=block.extraction_order,
            parser_name=PDF_PARSER_NAME,
            parser_version=block.parser_version,
            source_location={
                "type": "pdf",
                "page_number": block.page_number,
                "block_index": block.block_index,
            },
            warnings=tuple(item.value for item in block.warnings),
        )
        for block in parsed.blocks
    )
    return UnifiedSpecificationDocument(
        filename=parsed.filename,
        document_role=role,
        document_format=FileFormat.PDF,
        sha256=parsed.sha256,
        parser_name=PDF_PARSER_NAME,
        parser_version=parsed.parser_version or PDF_PARSER_VERSION,
        source_blocks=blocks,
        warnings=tuple(item.value for item in parsed.warnings),
    )


def adapt_specification(
    filename: str,
    content: bytes,
    file_format: FileFormat,
    role: DocumentRole,
    *,
    mime_type: str | None = None,
) -> UnifiedSpecificationDocument:
    if file_format is FileFormat.DOCX:
        return adapt_docx(filename, content, role)
    if file_format is FileFormat.PDF:
        return adapt_pdf(filename, content, role, mime_type=mime_type)
    raise ValueError("Only DOCX and searchable PDF specifications are supported.")
