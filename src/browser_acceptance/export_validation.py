from __future__ import annotations

import json
from pathlib import Path

from .contracts import REQUIRED_JSON_KEYS, REQUIRED_MARKDOWN_TEXT


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
    if "No realized savings are claimed" not in text:
        raise AssertionError("Markdown export lacks realized-savings limitation.")
    return text
