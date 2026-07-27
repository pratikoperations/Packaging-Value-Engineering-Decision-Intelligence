from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from src.ai_extraction import ConfidenceBand, ExtractionCandidate
from src.document_intake import (
    DocumentRole as LegacyRole,
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
)
from src.review_comparison import (
    CandidateReview,
    ReviewError,
    ReviewState,
    build_candidate_reviews,
    confirm,
    correct_and_confirm,
    intentionally_omit,
    reject,
)

from .models import DocumentRole, UnifiedSourceBlock, UnifiedSpecificationDocument
from .pairing import SpecificationPair

REGISTRY_PATH = Path(__file__).resolve().parents[2] / "config" / "pve_2_0_word_fields.json"
_NUMERIC = {
    "internal_length", "internal_width", "internal_height", "external_length",
    "external_width", "external_height", "ply_count", "liner_gsm", "medium_gsm",
    "total_board_gsm", "box_weight", "compression_requirement",
}
_VALUE = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*([A-Za-z]+)?\s*$")


@dataclass(frozen=True)
class CommonReviewView:
    review_id: str
    field_name: str
    document_role: DocumentRole
    document_format: str
    filename: str
    raw_value: str
    normalized_value: Any
    unit: str | None
    confidence: float
    confidence_band: str
    ambiguity_codes: tuple[str, ...]
    source_block_id: str
    source_excerpt: str
    source_location: dict[str, object]
    parser_name: str
    parser_version: str
    warnings: tuple[str, ...]
    review: CandidateReview

    @property
    def state(self) -> ReviewState:
        return self.review.state

    @property
    def reviewed(self) -> bool:
        return self.state is not ReviewState.PENDING


def load_field_registry() -> dict[str, tuple[str, ...]]:
    payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    fields = payload.get("fields", {})
    if len(fields) != 25:
        raise ValueError("The governed specification registry must contain exactly 25 fields.")
    return {name: tuple(alias.lower() for alias in aliases) for name, aliases in fields.items()}


def _legacy_role(role: DocumentRole) -> LegacyRole:
    return LegacyRole(role.value)


def _legacy_location(block: UnifiedSourceBlock) -> SourceLocation:
    location = block.source_location
    if location.get("type") == "pdf":
        return SourceLocation(
            paragraph_index=int(location.get("block_index", 0)),
            section_title=f"PDF page {location.get('page_number')}",
        )
    return SourceLocation(
        paragraph_index=location.get("paragraph_index"),
        table_index=location.get("table_index"),
        row_index=location.get("row_index"),
        cell_index=location.get("cell_index"),
        section_title=location.get("section_title"),
    )


def to_legacy_document(document: UnifiedSpecificationDocument) -> ParsedDocument:
    blocks = tuple(
        SourceBlock(
            block_id=block.block_id,
            block_type=SourceBlockType.PARAGRAPH,
            text=block.normalized_text,
            location=_legacy_location(block),
        )
        for block in document.source_blocks
    )
    return ParsedDocument(
        filename=document.filename,
        role=_legacy_role(document.document_role),
        sha256=document.sha256,
        blocks=blocks,
    )


def _parse_value(field_name: str, raw: str) -> tuple[Any, str | None]:
    if field_name not in _NUMERIC:
        return raw.strip(), None
    match = _VALUE.match(raw)
    if match is None:
        return raw.strip(), None
    number = float(match.group(1))
    return (int(number) if number.is_integer() else number), match.group(2)


def normalize_corrected_value(
    field_name: str,
    corrected_value: object,
    corrected_unit: str | None,
) -> tuple[Any, str | None]:
    if corrected_value is None or corrected_value == "":
        raise ReviewError("Corrected value must be supplied.")
    raw = str(corrected_value).strip()
    value, parsed_unit = _parse_value(field_name, raw)
    unit = corrected_unit.strip() if corrected_unit and corrected_unit.strip() else parsed_unit
    if field_name in _NUMERIC and not isinstance(value, (int, float)):
        raise ReviewError("Corrected numeric value must contain a valid number.")
    return value, unit


def _field_for_label(label: str, registry: dict[str, tuple[str, ...]]) -> str | None:
    normalized = " ".join(label.lower().strip().rstrip(":").split())
    return next((field for field, aliases in registry.items() if normalized in aliases), None)


def deterministic_candidates(document: UnifiedSpecificationDocument) -> tuple[ExtractionCandidate, ...]:
    registry = load_field_registry()
    candidates: list[ExtractionCandidate] = []
    blocks = document.source_blocks
    for index, block in enumerate(blocks):
        text = block.normalized_text.strip()
        if ":" in text:
            label, raw = text.split(":", 1)
            field = _field_for_label(label, registry)
            if field and raw.strip():
                value, unit = _parse_value(field, raw)
                candidates.append(ExtractionCandidate(
                    field_name=field,
                    document_role=_legacy_role(document.document_role),
                    raw_value=raw.strip(), normalized_value=value, unit=unit,
                    confidence=99.0, confidence_band=ConfidenceBand.HIGH,
                    source_block_id=block.block_id, source_excerpt=text,
                    ambiguity_codes=(),
                ))
        field = _field_for_label(text, registry)
        if field and index + 1 < len(blocks):
            value_block = blocks[index + 1]
            raw = value_block.normalized_text.strip()
            if raw:
                value, unit = _parse_value(field, raw)
                candidates.append(ExtractionCandidate(
                    field_name=field,
                    document_role=_legacy_role(document.document_role),
                    raw_value=raw, normalized_value=value, unit=unit,
                    confidence=99.0, confidence_band=ConfidenceBand.HIGH,
                    source_block_id=value_block.block_id, source_excerpt=raw,
                    ambiguity_codes=(),
                ))
    unique: dict[str, ExtractionCandidate] = {}
    for candidate in candidates:
        unique.setdefault(candidate.field_name, candidate)
    return tuple(unique.values())


def build_common_review_views(pair: SpecificationPair) -> tuple[CommonReviewView, ...]:
    documents = (pair.existing, pair.proposed)
    candidates = tuple(candidate for document in documents for candidate in deterministic_candidates(document))
    reviews = build_candidate_reviews(candidates, tuple(to_legacy_document(document) for document in documents))
    block_index = {
        (document.document_role.value, block.block_id): (document, block)
        for document in documents for block in document.source_blocks
    }
    views: list[CommonReviewView] = []
    for review in reviews:
        document, block = block_index[(review.candidate.document_role.value, review.source.block_id)]
        views.append(CommonReviewView(
            review_id=f"{review.candidate.document_role.value}:{review.candidate.field_name}:{review.source.block_id}",
            field_name=review.candidate.field_name,
            document_role=document.document_role,
            document_format=document.document_format.value,
            filename=document.filename,
            raw_value=review.candidate.raw_value,
            normalized_value=review.candidate.normalized_value,
            unit=review.candidate.unit,
            confidence=review.candidate.confidence,
            confidence_band=review.candidate.confidence_band.value,
            ambiguity_codes=tuple(code.value for code in review.candidate.ambiguity_codes),
            source_block_id=block.block_id,
            source_excerpt=review.source.excerpt,
            source_location=dict(block.source_location),
            parser_name=block.parser_name,
            parser_version=block.parser_version,
            warnings=block.warnings,
            review=review,
        ))
    return tuple(views)


def apply_review_action(
    view: CommonReviewView,
    action: ReviewState,
    *,
    corrected_value: object | None = None,
    corrected_unit: str | None = None,
    reviewer_note: str | None = None,
) -> CommonReviewView:
    if action is ReviewState.PENDING:
        updated = replace(view.review, state=ReviewState.PENDING, corrected_value=None, corrected_unit=None, reviewer_note=None)
    elif action is ReviewState.CONFIRMED:
        updated = confirm(view.review, reviewer_note=reviewer_note)
    elif action is ReviewState.CORRECTED_CONFIRMED:
        normalized_value, normalized_unit = normalize_corrected_value(
            view.field_name, corrected_value, corrected_unit
        )
        updated = correct_and_confirm(
            view.review, normalized_value, normalized_unit,
            reviewer_note=reviewer_note or "",
        )
    elif action is ReviewState.INTENTIONALLY_OMITTED:
        updated = intentionally_omit(view.review, reviewer_note=reviewer_note or "")
    elif action is ReviewState.REJECTED:
        updated = reject(view.review, reviewer_note=reviewer_note or "")
    else:
        raise ReviewError("Unsupported review action.")
    return replace(view, review=updated)


def all_reviews_resolved(views: Iterable[CommonReviewView]) -> bool:
    items = tuple(views)
    return bool(items) and all(item.reviewed for item in items)
