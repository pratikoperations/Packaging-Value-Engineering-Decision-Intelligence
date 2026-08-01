from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .domain import (
    AUTHORIZED_CURRENCIES,
    AUTHORIZED_PROVENANCE,
    AUTHORIZED_UNITS,
    SYNTHETIC_DISCLOSURE,
    SyntheticDataError,
)
from .identifiers import validate_identifier

_REQUIRED_FILES = (
    "suppliers.json", "specifications.json", "quotations.json",
    "technical_results.json", "risk_events.json", "scenarios.json",
    "invalid_cases.json",
)
_REAL_DATA_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I),
    re.compile(r"\b(?:GSTIN|PAN|actual market price|supplier confirmed|laboratory certified)\b", re.I),
    re.compile(r"https?://|www\.", re.I),
)
_REAL_COMPANY_DENYLIST = {"pidilite", "marico", "atul limited", "amazon", "reliance", "tata"}


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SyntheticDataError("INVALID_JSON", f"Unable to load {path.name}: {exc}") from exc


def validate_package(root: Path, package: dict[str, Any]) -> None:
    manifest = package["manifest"]
    if manifest.get("dataset_type") != "synthetic_demo":
        raise SyntheticDataError("INVALID_DATASET_TYPE", "dataset_type must be synthetic_demo.")
    if manifest.get("synthetic_disclosure") != SYNTHETIC_DISCLOSURE:
        raise SyntheticDataError("MISSING_DISCLOSURE", "Mandatory synthetic disclosure is absent or altered.")
    if manifest.get("currency_basis", {}).get("currency") not in AUTHORIZED_CURRENCIES:
        raise SyntheticDataError("UNSUPPORTED_CURRENCY", "Gate 1 supports INR only.")
    for filename in _REQUIRED_FILES:
        if not (root / filename).is_file():
            raise SyntheticDataError("MISSING_FILE", f"Required file is missing: {filename}.")

    collections = {
        "suppliers": ("supplier", "supplier_id"),
        "specifications": ("specification", "specification_id"),
        "quotations": ("quotation", "quotation_id"),
        "technical_results": ("technical_result", "technical_result_id"),
        "risk_events": ("risk_event", "risk_event_id"),
        "scenarios": ("scenario", "scenario_id"),
        "invalid_cases": ("invalid_case", "invalid_case_id"),
    }
    ids: dict[str, set[str]] = {}
    for name, (kind, key) in collections.items():
        records = package[name]
        if not isinstance(records, list):
            raise SyntheticDataError("INVALID_COLLECTION", f"{name} must be a list.")
        seen: set[str] = set()
        for record in records:
            value = record.get(key)
            validate_identifier(kind, value)
            if value in seen:
                raise SyntheticDataError("DUPLICATE_ID", f"Duplicate {key}: {value}.")
            seen.add(value)
            _validate_record(record)
        ids[name] = seen

    expected = manifest.get("record_counts", {})
    for name, records in package.items():
        if name in collections and expected.get(name) != len(records):
            raise SyntheticDataError("COUNT_MISMATCH", f"Manifest count mismatch for {name}.")

    for quote in package["quotations"]:
        _require_ref(ids, "suppliers", quote.get("supplier_id"), "quotation supplier")
        _require_ref(ids, "specifications", quote.get("specification_id"), "quotation specification")
    for result in package["technical_results"]:
        _require_ref(ids, "specifications", result.get("specification_id"), "technical-result specification")
    for risk in package["risk_events"]:
        if risk.get("supplier_id"):
            _require_ref(ids, "suppliers", risk["supplier_id"], "risk supplier")
        if risk.get("specification_id"):
            _require_ref(ids, "specifications", risk["specification_id"], "risk specification")
    for scenario in package["scenarios"]:
        _require_ref(ids, "specifications", scenario.get("baseline_specification_id"), "scenario baseline")
        for value in scenario.get("proposed_specification_ids", []):
            _require_ref(ids, "specifications", value, "scenario proposal")
        for value in scenario.get("quotation_ids", []):
            _require_ref(ids, "quotations", value, "scenario quotation")

    serialized = json.dumps(package, sort_keys=True).lower()
    for company in _REAL_COMPANY_DENYLIST:
        if company in serialized:
            raise SyntheticDataError("REAL_NAME_DETECTED", f"Possible real company name detected: {company}.")
    for pattern in _REAL_DATA_PATTERNS:
        if pattern.search(serialized):
            raise SyntheticDataError("IDENTIFIABLE_DATA_DETECTED", "Possible identifiable or real-data content detected.")


def _validate_record(record: dict[str, Any]) -> None:
    unit = record.get("unit")
    if unit is not None and unit not in AUTHORIZED_UNITS:
        raise SyntheticDataError("UNSUPPORTED_UNIT", f"Unsupported unit: {unit}.")
    currency = record.get("currency")
    if currency is not None and currency not in AUTHORIZED_CURRENCIES:
        raise SyntheticDataError("UNSUPPORTED_CURRENCY", f"Unsupported currency: {currency}.")
    provenance = record.get("assumption_provenance")
    if provenance is not None and provenance not in AUTHORIZED_PROVENANCE:
        raise SyntheticDataError("INVALID_PROVENANCE", f"Unsupported assumption provenance: {provenance}.")
    for key, value in record.items():
        if key.endswith("cost") or key.endswith("price"):
            if isinstance(value, (int, float)) and value < 0:
                raise SyntheticDataError("NEGATIVE_COST", f"Negative cost is not permitted: {key}.")


def _require_ref(ids: dict[str, set[str]], family: str, value: str | None, label: str) -> None:
    if value not in ids[family]:
        raise SyntheticDataError("ORPHAN_REFERENCE", f"Unknown {label}: {value!r}.")
