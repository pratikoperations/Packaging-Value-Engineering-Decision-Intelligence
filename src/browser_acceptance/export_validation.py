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

    summary = payload.get("executive_summary")
    if not isinstance(summary, dict) or "decision_status" not in summary:
        raise AssertionError("JSON export lacks executive recommendation summary.")

    alternatives = payload.get("alternatives")
    if not isinstance(alternatives, list) or not alternatives:
        raise AssertionError("JSON export lacks proposed alternatives.")
    if any(not isinstance(item.get("recommendation"), dict) for item in alternatives):
        raise AssertionError("JSON export lacks per-alternative recommendation evidence.")

    controls = payload.get("decision_controls")
    if not isinstance(controls, dict):
        raise AssertionError("JSON export lacks decision controls.")
    if controls.get("engineering_validation_required") is not True:
        raise AssertionError("JSON export must require engineering validation.")
    if controls.get("autonomous_technical_approval") is not False:
        raise AssertionError("JSON export must prohibit autonomous technical approval.")

    return payload


def validate_markdown_download(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED_MARKDOWN_TEXT if item not in text]
    if missing:
        raise AssertionError(f"Markdown export missing required content: {missing}")
    lowered = text.lower()
    if "synthetic" not in lowered or "engineering validation" not in lowered:
        raise AssertionError("Markdown export lacks required limitations.")
    if "recommendation:" not in lowered:
        raise AssertionError("Markdown export lacks recommendation content.")
    if "realized savings" in lowered and "no realized savings" not in lowered:
        raise AssertionError("Markdown export contains an unsupported realized-savings claim.")
    return text
