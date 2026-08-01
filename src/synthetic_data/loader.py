from __future__ import annotations

from pathlib import Path
from typing import Any

from .validator import read_json, validate_package

_FILES = {
    "manifest": "manifest.json",
    "suppliers": "suppliers.json",
    "specifications": "specifications.json",
    "quotations": "quotations.json",
    "technical_results": "technical_results.json",
    "risk_events": "risk_events.json",
    "scenarios": "scenarios.json",
    "invalid_cases": "invalid_cases.json",
}


def load_governed_package(root: str | Path) -> dict[str, Any]:
    package_root = Path(root)
    package = {name: read_json(package_root / filename) for name, filename in _FILES.items()}
    validate_package(package_root, package)
    return package
