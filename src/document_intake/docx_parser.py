"""Deterministic, non-executing DOCX structure parser for PVE 2.0 Build Group B."""

from __future__ import annotations

import io
import zipfile
from xml.etree import ElementTree as ET

from .document_models import (
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
    UnsupportedContent,
)
from .file_validation import DocumentValidationError, ValidatedDocument
from .source_blocks import make_source_block_id

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
MAX_DOCUMENT_XML_BYTES = 5 * 1024 * 1024


def _tag(local_name: str) -> str:
    return f"{{{W_NS}}}{local_name}"


def _normalized_text(element: ET.Element) -> str:
    fragments: list[str] = []
    for node in element.iter():
        if node.tag == _tag("t") and node.text:
            fragments.append(node.text)
        elif node.tag in {_tag("tab"), _tag("br"), _tag("cr")}:
            fragments.append(" ")
    return " ".join("".join(fragments).split())


def _paragraph_style(paragraph: ET.Element) -> str | None:
    style = paragraph.find("./w:pPr/w:pStyle", NS)
    if style is None:
        return None
    return style.attrib.get(_tag("val"))


def _unsupported_content(part_names: tuple[str, ...], root: ET.Element) -> tuple[UnsupportedContent, ...]:
    items: list[UnsupportedContent] = []

    for name in part_names:
        lowered = name.lower()
        if lowered.startswith("word/media/"):
            items.append(UnsupportedContent("image_content", "Embedded image is not interpreted.", name))
        elif lowered.startswith("word/embeddings/"):
            items.append(UnsupportedContent("embedded_object", "Embedded object is not executed or interpreted.", name))
        elif "vbaproject" in lowered:
            items.append(UnsupportedContent("macro_content", "Macro content is not executed or interpreted.", name))

    if root.findall(".//w:altChunk", NS):
        items.append(UnsupportedContent("alternate_content", "Alternate imported content is unsupported."))
    if root.findall(".//w:object", NS):
        items.append(UnsupportedContent("word_object", "Word object content is unsupported."))

    unique: dict[tuple[str, str | None], UnsupportedContent] = {}
    for item in items:
        unique[(item.code, item.part_name)] = item
    return tuple(unique[key] for key in sorted(unique))


def parse_validated_docx(document: ValidatedDocument) -> ParsedDocument:
    """Parse ordered paragraphs, headings, tables, and cells from a validated DOCX."""

    try:
        with zipfile.ZipFile(io.BytesIO(document.content), "r") as archive:
            info = archive.getinfo("word/document.xml")
            if info.file_size > MAX_DOCUMENT_XML_BYTES:
                raise DocumentValidationError("word/document.xml exceeds the controlled parse limit.")
            xml_bytes = archive.read(info)
    except DocumentValidationError:
        raise
    except (KeyError, zipfile.BadZipFile, OSError) as exc:
        raise DocumentValidationError("DOCX package became unreadable during parsing.") from exc

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise DocumentValidationError("DOCX document XML is malformed.") from exc

    body = root.find("w:body", NS)
    if body is None:
        raise DocumentValidationError("DOCX document XML has no body.")

    blocks: list[SourceBlock] = []
    paragraph_index = 0
    table_index = 0
    current_section: str | None = None

    for child in body:
        if child.tag == _tag("p"):
            text = _normalized_text(child)
            style = _paragraph_style(child)
            is_heading = bool(style and style.lower().startswith("heading"))
            if is_heading and text:
                current_section = text
            if text:
                block_type = SourceBlockType.HEADING if is_heading else SourceBlockType.PARAGRAPH
                location = SourceLocation(
                    paragraph_index=paragraph_index,
                    section_title=current_section,
                )
                blocks.append(
                    SourceBlock(
                        block_id=make_source_block_id(
                            document.sha256, document.role, block_type, location
                        ),
                        block_type=block_type,
                        text=text,
                        location=location,
                    )
                )
            paragraph_index += 1

        elif child.tag == _tag("tbl"):
            for row_index, row in enumerate(child.findall("./w:tr", NS)):
                for cell_index, cell in enumerate(row.findall("./w:tc", NS)):
                    text = _normalized_text(cell)
                    if not text:
                        continue
                    location = SourceLocation(
                        table_index=table_index,
                        row_index=row_index,
                        cell_index=cell_index,
                        section_title=current_section,
                    )
                    blocks.append(
                        SourceBlock(
                            block_id=make_source_block_id(
                                document.sha256,
                                document.role,
                                SourceBlockType.TABLE_CELL,
                                location,
                            ),
                            block_type=SourceBlockType.TABLE_CELL,
                            text=text,
                            location=location,
                        )
                    )
            table_index += 1

    return ParsedDocument(
        filename=document.filename,
        role=document.role,
        sha256=document.sha256,
        blocks=tuple(blocks),
        unsupported_content=_unsupported_content(document.part_names, root),
    )
