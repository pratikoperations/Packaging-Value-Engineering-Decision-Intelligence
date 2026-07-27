from __future__ import annotations

from dataclasses import dataclass

from src.specification_intake import (
    DocumentRole,
    SpecificationPair,
    UnifiedSpecificationDocument,
    adapt_specification,
    build_pair,
)
from src.upload_routing.models import DetectedUpload, FileFormat


@dataclass(frozen=True)
class SpecificationUploadInput:
    filename: str
    mime_type: str
    content: bytes
    detection: DetectedUpload
    role: DocumentRole


def parse_specification_pair(
    inputs: tuple[SpecificationUploadInput, SpecificationUploadInput],
) -> SpecificationPair:
    if len(inputs) != 2:
        raise ValueError("Exactly two specification documents are required.")
    documents: list[UnifiedSpecificationDocument] = []
    for item in inputs:
        if item.detection.file_format not in {FileFormat.DOCX, FileFormat.PDF}:
            raise ValueError("Only DOCX and searchable PDF specifications are supported.")
        documents.append(
            adapt_specification(
                item.filename,
                item.content,
                item.detection.file_format,
                item.role,
                mime_type=item.mime_type or None,
            )
        )
    return build_pair(tuple(documents))


def source_block_rows(pair: SpecificationPair) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for document in (pair.existing, pair.proposed):
        for block in document.source_blocks:
            location = block.source_location
            if location.get("type") == "pdf":
                location_label = f"Page {location.get('page_number')}, Block {location.get('block_index')}"
            else:
                parts = []
                if location.get("section_title"):
                    parts.append(f"Section {location['section_title']}")
                if location.get("paragraph_index") is not None:
                    parts.append(f"Paragraph {location['paragraph_index']}")
                if location.get("table_index") is not None:
                    parts.append(f"Table {location['table_index']}")
                if location.get("row_index") is not None:
                    parts.append(f"Row {location['row_index']}")
                if location.get("cell_index") is not None:
                    parts.append(f"Cell {location['cell_index']}")
                location_label = ", ".join(parts) or "DOCX source"
            rows.append(
                {
                    "Role": document.document_role.value.title(),
                    "Format": document.document_format.value.upper(),
                    "File": document.filename,
                    "Source location": location_label,
                    "Text": block.normalized_text,
                    "Parser": f"{block.parser_name} / {block.parser_version}",
                    "Warnings": ", ".join(block.warnings),
                }
            )
    return rows
