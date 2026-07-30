from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


def flatten_evidence_rows(value: Any, *, prefix: str = "") -> list[dict[str, str]]:
    """Flatten nested evidence into stable, human-readable path/value rows."""
    if is_dataclass(value):
        value = asdict(value)
    rows: list[dict[str, str]] = []
    if isinstance(value, dict):
        if not value:
            return [{"Evidence field": prefix or "Record", "Value": "No values recorded"}]
        for key in sorted(value, key=str):
            label = str(key).replace("_", " ").title()
            path = f"{prefix} › {label}" if prefix else label
            rows.extend(flatten_evidence_rows(value[key], prefix=path))
        return rows
    if isinstance(value, (list, tuple)):
        if not value:
            return [{"Evidence field": prefix or "Record", "Value": "None recorded"}]
        for index, item in enumerate(value, start=1):
            rows.extend(flatten_evidence_rows(item, prefix=f"{prefix} › Item {index}"))
        return rows
    return [{"Evidence field": prefix or "Value", "Value": "Not recorded" if value is None else str(value)}]
