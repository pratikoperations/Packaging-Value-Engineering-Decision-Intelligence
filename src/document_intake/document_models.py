"""Deterministic models for PVE 2.0 Word specification intake.

This module contains no AI, canonical mapping, persistence, or decision logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class DocumentRole(str, Enum):
    """Allowed roles for the controlled two-document intake."""

    EXISTING = "existing"
    PROPOSED = "proposed"


class SourceBlockType(str, Enum):
    """Supported deterministic DOCX source block types."""

    PARAGRAPH = "paragraph"
    HEADING = "heading"
    TABLE_CELL = "table_cell"


@dataclass(frozen=True)
class SourceLocation:
    """Stable structural location inside a DOCX document."""

    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    cell_index: int | None = None
    section_title: str | None = None


@dataclass(frozen=True)
class SourceBlock:
    """One ordered, source-traceable paragraph, heading, or table cell."""

    block_id: str
    block_type: SourceBlockType
    text: str
    location: SourceLocation


@dataclass(frozen=True)
class UnsupportedContent:
    """Content detected but intentionally not interpreted in Build Group B."""

    code: str
    description: str
    part_name: str | None = None


@dataclass(frozen=True)
class ParsedDocument:
    """Deterministic output of one validated DOCX parse."""

    filename: str
    role: DocumentRole
    sha256: str
    blocks: Tuple[SourceBlock, ...]
    unsupported_content: Tuple[UnsupportedContent, ...] = field(default_factory=tuple)

    @property
    def paragraphs(self) -> Tuple[SourceBlock, ...]:
        return tuple(
            block
            for block in self.blocks
            if block.block_type in {SourceBlockType.PARAGRAPH, SourceBlockType.HEADING}
        )

    @property
    def table_cells(self) -> Tuple[SourceBlock, ...]:
        return tuple(
            block for block in self.blocks if block.block_type is SourceBlockType.TABLE_CELL
        )


@dataclass(frozen=True)
class DocumentPair:
    """Exactly one existing and one proposed parsed specification."""

    existing: ParsedDocument
    proposed: ParsedDocument
