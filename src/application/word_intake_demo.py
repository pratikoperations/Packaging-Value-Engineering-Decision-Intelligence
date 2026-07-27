"""Controlled synthetic demonstration service for PVE 2.0 Word intake.

No live AI provider is connected. Extraction is deterministic and limited to
explicit synthetic labels in paragraph and table-cell source blocks.
"""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from html import escape
from typing import Iterable

from src.ai_extraction import ConfidenceBand, ExtractionCandidate
from src.document_intake import DocumentPair, DocumentRole, ParsedDocument, parse_document_pair
from src.persistence._utils import content_hash
from src.review_comparison import (
    CandidateReview,
    FieldReviewGroup,
    build_candidate_reviews,
    compare_fields,
    group_reviews,
)

PARSER_VERSION = "pve-docx-parser-v1"
EXTRACTION_SCHEMA_VERSION = "pve-word-extraction-v1"
ALIAS_REGISTRY_VERSION = "1.0"
PROVIDER_ID = "deterministic-synthetic-demo"

_LABELS = {
    "specification_number": ("specification number", "spec no"),
    "specification_revision": ("revision", "rev"),
    "item_code": ("item code", "material code"),
    "item_description": ("item description", "description"),
    "supplier_name": ("supplier",),
    "box_style": ("box style",),
    "internal_length": ("internal length",),
    "internal_width": ("internal width",),
    "internal_height": ("internal height",),
    "ply_count": ("ply count", "ply"),
    "flute_combination": ("flute combination", "flute"),
    "box_weight": ("box weight", "case weight"),
    "compression_requirement": ("compression requirement", "bct requirement"),
}

_NUMERIC_FIELDS = {
    "internal_length",
    "internal_width",
    "internal_height",
    "ply_count",
    "box_weight",
    "compression_requirement",
}

_UNIT_PATTERN = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$")


@dataclass(frozen=True)
class DemoEvaluation:
    precision: float = 1.0
    recall: float = 1.0
    source_grounding: float = 1.0
    document_role_accuracy: float = 1.0
    invented_values: int = 0
    unsourced_values: int = 0
    unconfirmed_values_mapped: int = 0


def _docx_bytes(title: str, rows: Iterable[tuple[str, str]]) -> bytes:
    table_rows = "".join(
        "<w:tr><w:tc><w:p><w:r><w:t>"
        + escape(label)
        + "</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>"
        + escape(value)
        + "</w:t></w:r></w:p></w:tc></w:tr>"
        for label, value in rows
    )
    document_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>
<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>{escape(title)}</w:t></w:r></w:p>
<w:tbl>{table_rows}</w:tbl></w:body></w:document>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def synthetic_demo_documents() -> tuple[bytes, bytes]:
    existing = _docx_bytes(
        "Existing synthetic corrugated specification",
        (
            ("Specification number", "CORR-1001"),
            ("Revision", "04"),
            ("Item code", "SYN-BOX-001"),
            ("Item description", "Synthetic shipping case"),
            ("Supplier", "Synthetic Supplier A"),
            ("Box style", "RSC"),
            ("Internal length", "400 mm"),
            ("Internal width", "300 mm"),
            ("Internal height", "250 mm"),
            ("Ply count", "5 ply"),
            ("Flute combination", "BC"),
            ("Box weight", "780 g"),
            ("Compression requirement", "620 kgf"),
        ),
    )
    proposed = _docx_bytes(
        "Proposed synthetic corrugated specification",
        (
            ("Specification number", "CORR-1001-P"),
            ("Revision", "01"),
            ("Item code", "SYN-BOX-001"),
            ("Item description", "Synthetic lightweight shipping case"),
            ("Supplier", "Synthetic Supplier B"),
            ("Box style", "RSC"),
            ("Internal length", "400 mm"),
            ("Internal width", "300 mm"),
            ("Internal height", "250 mm"),
            ("Ply count", "3 ply"),
            ("Flute combination", "B"),
            ("Box weight", "650 g"),
            ("Compression requirement", "580 kgf"),
        ),
    )
    return existing, proposed


def load_synthetic_pair() -> DocumentPair:
    existing, proposed = synthetic_demo_documents()
    return parse_document_pair("existing_synthetic.docx", existing, "proposed_synthetic.docx", proposed)


def _parse_value(field_name: str, text: str):
    if field_name not in _NUMERIC_FIELDS:
        return text.strip(), None
    match = _UNIT_PATTERN.match(text)
    if match is None:
        return text.strip(), None
    number = float(match.group(1))
    value = int(number) if number.is_integer() else number
    return value, match.group(2)


def _candidate_from_pair(document: ParsedDocument, index: int) -> ExtractionCandidate | None:
    if index + 1 >= len(document.blocks):
        return None
    label_block = document.blocks[index]
    value_block = document.blocks[index + 1]
    label = label_block.text.strip().lower()
    field_name = next(
        (field for field, aliases in _LABELS.items() if label in aliases),
        None,
    )
    if field_name is None:
        return None
    value, unit = _parse_value(field_name, value_block.text)
    return ExtractionCandidate(
        field_name=field_name,
        document_role=document.role,
        raw_value=value_block.text,
        normalized_value=value,
        unit=unit,
        confidence=99.0,
        confidence_band=ConfidenceBand.HIGH,
        source_block_id=value_block.block_id,
        source_excerpt=value_block.text,
        ambiguity_codes=(),
    )


def deterministic_demo_candidates(document: ParsedDocument) -> tuple[ExtractionCandidate, ...]:
    candidates = [
        candidate
        for index in range(len(document.blocks) - 1)
        if (candidate := _candidate_from_pair(document, index)) is not None
    ]
    unique: dict[str, ExtractionCandidate] = {}
    for candidate in candidates:
        unique.setdefault(candidate.field_name, candidate)
    return tuple(unique.values())


def build_demo_reviews(documents: DocumentPair) -> tuple[CandidateReview, ...]:
    candidates = deterministic_demo_candidates(documents.existing) + deterministic_demo_candidates(
        documents.proposed
    )
    return build_candidate_reviews(candidates, (documents.existing, documents.proposed))


def demo_groups(reviews: Iterable[CandidateReview]) -> tuple[FieldReviewGroup, ...]:
    return group_reviews(reviews)


def demo_comparisons(groups: Iterable[FieldReviewGroup]):
    return compare_fields(tuple(_LABELS), groups)


def in_memory_snapshot_hash(project_id: str, groups: Iterable[FieldReviewGroup]) -> str:
    accepted = []
    for group in groups:
        selected = group.selected_review
        if selected is not None and selected.is_accepted:
            accepted.append(
                {
                    "field": group.field_name,
                    "role": group.document_role.value,
                    "value": selected.effective_value,
                    "unit": selected.effective_unit,
                    "source": selected.source.block_id,
                    "state": selected.state.value,
                }
            )
    return content_hash({"project_id": project_id, "accepted": accepted})
