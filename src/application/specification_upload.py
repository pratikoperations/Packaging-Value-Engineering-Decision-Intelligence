from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import MutableMapping

from src.specification_intake import (
    DocumentRole,
    SpecificationPair,
    UnifiedSpecificationDocument,
    adapt_specification,
    build_pair,
)
from src.upload_routing.models import DetectedUpload, FileFormat

SPEC_STATE_PREFIX = "data_upload.specification."
SPEC_BATCH_KEY = SPEC_STATE_PREFIX + "batch_fingerprint"
SPEC_CONFIRMATION_KEY = SPEC_STATE_PREFIX + "confirmed"
SPEC_REVIEWS_KEY = SPEC_STATE_PREFIX + "reviews"


@dataclass(frozen=True)
class SpecificationUploadInput:
    filename: str
    mime_type: str
    content: bytes
    detection: DetectedUpload
    role: DocumentRole


def specification_batch_fingerprint(inputs: tuple[SpecificationUploadInput, ...]) -> str:
    payload = "|".join(
        sorted(
            f"{item.detection.sha256}:{item.filename}:{item.role.value}:{item.detection.file_format.value}"
            for item in inputs
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def invalidate_specification_state_on_change(
    state: MutableMapping[str, object],
    inputs: tuple[SpecificationUploadInput, ...],
) -> bool:
    fingerprint = specification_batch_fingerprint(inputs)
    if state.get(SPEC_BATCH_KEY) == fingerprint:
        return False
    for key in tuple(state):
        if key.startswith(SPEC_STATE_PREFIX):
            state.pop(key, None)
    state[SPEC_BATCH_KEY] = fingerprint
    return True


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


@dataclass(frozen=True)
class SessionSpecificationFile:
    name: str
    type: str
    content: bytes

    def getvalue(self) -> bytes:
        return self.content


SESSION_SPEC_CACHE = "data_upload.specification_session_cache"


def restore_session_specifications(state: MutableMapping[str, object], existing, proposed):
    """Restore the uploaded pair only within the same active project and session."""
    project_id = state.get("active_project_id")
    cached = state.get(SESSION_SPEC_CACHE)
    if existing is not None and proposed is not None:
        files = (
            SessionSpecificationFile(existing.name, existing.type, existing.getvalue()),
            SessionSpecificationFile(proposed.name, proposed.type, proposed.getvalue()),
        )
        state[SESSION_SPEC_CACHE] = (project_id, files)
        return files, False
    if existing is None and proposed is None and cached and cached[0] == project_id:
        return cached[1], True
    return None, False


TRIAGE_PREFIX = "triage_"
TRIAGE_REVIEW_PREFIX = "provisional-triage:"


def serialize_provisional_triage(state: MutableMapping[str, object]) -> tuple[dict, ...]:
    """Persist only bounded non-authoritative triage notes, never confirmed values."""
    entries: list[dict] = []
    for key in sorted(state):
        if not key.startswith("triage_value_"):
            continue
        suffix = key[len("triage_value_"):]
        value = str(state.get(key) or "").strip()
        evidence = str(state.get("triage_evidence_" + suffix) or "").strip()
        manual = state.get("manual_source_" + suffix)
        if not value and not evidence and not manual:
            continue
        if len(suffix) > 128 or len(value) > 512 or len(evidence) > 1024:
            raise ValueError("Provisional triage entry is too long.")
        entries.append({
            "review_id": TRIAGE_REVIEW_PREFIX + suffix,
            "state": "provisional",
            "value": value,
            "evidence": evidence,
            **({"manual_source": manual} if manual else {}),
        })
    if len(entries) > 50:
        raise ValueError("Too many provisional triage entries.")
    return tuple(entries)


def restore_provisional_triage(state: MutableMapping[str, object], records) -> tuple[dict, ...]:
    """Restore UI notes independently of governed extracted candidate reviews."""
    extracted = []
    seen: set[str] = set()
    for record in records:
        identifier = record.get("review_id", "")
        if not identifier.startswith(TRIAGE_REVIEW_PREFIX):
            extracted.append(record)
            continue
        suffix = identifier[len(TRIAGE_REVIEW_PREFIX):]
        if (not suffix or len(suffix) > 128 or suffix in seen or
                record.get("state") != "provisional"):
            raise ValueError("Invalid saved provisional triage record.")
        value = str(record.get("value", ""))
        evidence = str(record.get("evidence", ""))
        if len(value) > 512 or len(evidence) > 1024:
            raise ValueError("Invalid saved provisional triage length.")
        seen.add(suffix)
        state["triage_value_" + suffix] = value
        state["triage_evidence_" + suffix] = evidence
        manual = record.get("manual_source")
        if manual is not None:
            if not isinstance(manual, dict) or not all(isinstance(manual.get(k), str) for k in ("block_id", "sha256", "value")):
                raise ValueError("Invalid saved manual source mapping.")
            state["manual_source_" + suffix] = manual
    return tuple(extracted)


def classify_triage_source_support(
    *, document: UnifiedSpecificationDocument, source_block_id: str,
    proposed_value: str,
) -> str:
    """Classify literal source-text support without asserting engineering validity.

    Only an exact selected block from the same uploaded document is eligible.
    Numeric comparison, inferred units and semantic equivalence are not attempted.
    """
    matching = [block for block in document.source_blocks if block.block_id == source_block_id and block.document_role == document.document_role and block.document_format == document.document_format]
    if len(matching) != 1:
        return "invalid_source_reference"
    value = " ".join(str(proposed_value).casefold().split())
    if not value:
        return "value_missing"
    source_text = " ".join(matching[0].normalized_text.casefold().split())
    if re.search(r"(?<![\\w.])" + re.escape(value) + r"(?![\\w.])", source_text):
        return "literal_value_present"
    return "source_block_requires_manual_verification"
