from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import REQUIRED_JSON_KEYS, REQUIRED_MARKDOWN_TEXT


def validate_json_download(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_JSON_KEYS if key not in payload]
    if missing:
        raise AssertionError(f"JSON export missing required keys: {missing}")
    disclosure = str(payload.get("metadata", {}).get("synthetic_disclosure", ""))
    if "synthetic" not in disclosure.lower():
        raise AssertionError("JSON export does not preserve synthetic disclosure.")
    evidence = payload.get("calculation_evidence")
    if not isinstance(evidence, dict) or not evidence.get("results"):
        raise AssertionError("JSON export lacks calculation-evidence results.")
    return payload


def validate_markdown_download(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_MARKDOWN_TEXT if item not in text]
    if missing:
        raise AssertionError(f"Markdown export missing required content: {missing}")
    lowered = text.lower()
    if "synthetic" not in lowered or "engineering validation" not in lowered:
        raise AssertionError("Markdown export lacks required limitations.")
    return text
