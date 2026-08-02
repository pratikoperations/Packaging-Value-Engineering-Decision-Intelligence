from __future__ import annotations

import json
import re
from pathlib import Path

from .contracts import REQUIRED_JSON_KEYS, REQUIRED_MARKDOWN_TEXT

_REALIZED_SAVINGS_LIMITATION_PATTERNS = (
    re.compile(r"\bno\s+realized\s+savings?\s+(?:are\s+)?claimed\b"),
    re.compile(
        r"\bnot\s+suitable\s+for\b[^.]{0,240}"
        r"\brealized\s+savings?\s+claims?\b"
    ),
    re.compile(
        r"\bnot\b[^.]{0,240}"
        r"\brealized\s+savings?\s+(?:claims?|validation)\b"
    ),
    re.compile(
        r"\brealized\s+savings?\s+(?:claims?\s+)?"
        r"(?:are\s+)?not\s+(?:claimed|validated)\b"
    ),
)


def _normalise_limitation_text(text: str) -> str:
    normalised = text.casefold()
    normalised = re.sub(r"[\u2010-\u2015\u2212-]", " ", normalised)
    return re.sub(r"\s+", " ", normalised).strip()


def _has_realized_savings_limitation(text: str) -> bool:
    normalised = _normalise_limitation_text(text)
    return any(pattern.search(normalised) for pattern in _REALIZED_SAVINGS_LIMITATION_PATTERNS)


def validate_json_download(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_JSON_KEYS if key not in payload]
    if missing:
        raise AssertionError(f"JSON export missing required keys: {missing}")
    metadata = payload.get("metadata", {})
    disclosure = str(metadata.get("synthetic_disclosure", ""))
    if "synthetic" not in disclosure.lower():
        raise AssertionError("JSON export lacks synthetic-data disclosure.")
    controls = payload.get("decision_controls", {})
    if controls.get("autonomous_technical_approval") is not False:
        raise AssertionError("JSON export must prohibit autonomous technical approval.")
    if controls.get("engineering_validation_required") is not True:
        raise AssertionError("JSON export must require engineering validation.")
    return payload


def validate_markdown_download(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_MARKDOWN_TEXT if item not in text]
    if missing:
        raise AssertionError(f"Markdown export missing required text: {missing}")
    if not _has_realized_savings_limitation(text):
        raise AssertionError("Markdown export lacks realized-savings limitation.")
    return text
