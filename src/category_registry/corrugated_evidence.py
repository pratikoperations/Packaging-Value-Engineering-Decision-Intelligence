from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

SOURCE_CLASSIFICATIONS = (
    "uploaded_fact", "manually_entered_fact", "supplier_declared",
    "laboratory_tested", "predicted", "assumption",
)
EVIDENCE_CONFIDENCE = ("High evidence confidence", "Moderate evidence confidence", "Low evidence confidence", "Not assessable")
CAPABILITY_OUTCOMES = ("compatible", "incompatible", "evidence missing")

TECHNICAL_REQUIREMENT_FIELDS = (
    "product_description", "product_fragility", "gross_packed_weight_kg",
    "compression_requirement_n", "stack_layers_required", "storage_duration_days",
    "storage_temperature_min_c", "storage_temperature_max_c", "humidity_percent",
    "distribution_mode", "route_duration_days", "handling_method", "handling_touches",
    "maximum_pallet_height_mm", "maximum_pallet_weight_kg",
    "laboratory_trial_required", "transport_trial_required", "packing_line_trial_required",
)

SUPPLIER_CAPABILITY_FIELDS = (
    "supported_flutes", "maximum_ply", "corrugator_width_mm",
    "minimum_sheet_length_mm", "maximum_sheet_length_mm",
    "minimum_sheet_width_mm", "maximum_sheet_width_mm", "maximum_print_colours",
    "die_cutting_available", "stitching_available", "gluing_available",
    "coating_available", "laboratory_access", "trial_capability",
    "backup_site_available", "subcontracted_processes",
)

@dataclass(frozen=True)
class EvidenceMatch:
    evidence_id: str
    status: str
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class CapabilityAssessment:
    outcome: str
    missing_fields: tuple[str, ...]
    incompatibilities: tuple[str, ...]

@dataclass(frozen=True)
class EvidenceConfidenceAssessment:
    classification: str
    reasons: tuple[str, ...]
    counts: Mapping[str, int]


def technical_requirement_profile(values: Mapping[str, Any]) -> dict[str, Any]:
    """Return only governed corrugated requirement fields; no thresholds are inferred."""
    return {key: values.get(key) for key in TECHNICAL_REQUIREMENT_FIELDS}


def _clean(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _parse_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def match_evidence(
    evidence: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    as_of: date | None = None,
) -> EvidenceMatch:
    """Deterministically match evidence to explicit project/specification context."""
    reasons: list[str] = []
    comparisons = (
        ("project_id", "wrong project"),
        ("context", "wrong context"),
        ("specification_version", "wrong specification"),
        ("supplier_name", "wrong supplier"),
        ("manufacturing_site", "wrong manufacturing site"),
        ("material_structure", "wrong material structure"),
        ("test_method", "wrong test method"),
        ("laboratory_name", "wrong laboratory"),
        ("sample_or_batch_reference", "wrong sample or batch"),
    )
    for key, reason in comparisons:
        wanted = _clean(expected.get(key))
        actual = _clean(evidence.get(key))
        if wanted and actual != wanted:
            reasons.append(reason)

    source = _clean(evidence.get("source_classification"))
    if source not in SOURCE_CLASSIFICATIONS:
        reasons.append("invalid source classification")
    if evidence.get("superseded_by"):
        reasons.append("superseded evidence")

    today = as_of or date.today()
    valid_until = _parse_date(evidence.get("valid_until"))
    if evidence.get("valid_until") and valid_until is None:
        reasons.append("invalid validity date")
    elif valid_until and valid_until < today:
        reasons.append("expired evidence")

    test_date = _parse_date(evidence.get("test_date"))
    if evidence.get("test_date") and test_date is None:
        reasons.append("invalid test date")

    evidence_id = _clean(evidence.get("evidence_id")) or "UNIDENTIFIED"
    return EvidenceMatch(evidence_id, "matched" if not reasons else "not matched", tuple(reasons))


def detect_conflicting_evidence(records: Iterable[Mapping[str, Any]]) -> tuple[tuple[str, ...], ...]:
    """Return evidence-id groups sharing identity but reporting different results."""
    grouped: dict[tuple[str, ...], dict[str, list[str]]] = {}
    identity_fields = (
        "project_id", "context", "specification_version", "supplier_name",
        "manufacturing_site", "material_structure", "test_method",
        "sample_or_batch_reference",
    )
    for row in records:
        identity = tuple(_clean(row.get(key)) for key in identity_fields)
        result = f"{_clean(row.get('result_value'))}|{_clean(row.get('unit'))}"
        grouped.setdefault(identity, {}).setdefault(result, []).append(_clean(row.get("evidence_id")) or "UNIDENTIFIED")
    conflicts = []
    for by_result in grouped.values():
        if len(by_result) > 1:
            conflicts.append(tuple(sorted(item for ids in by_result.values() for item in ids)))
    return tuple(sorted(conflicts))


def assess_supplier_capability(required: Mapping[str, Any], capability: Mapping[str, Any]) -> CapabilityAssessment:
    """Assess compatibility only; never rank or allocate suppliers."""
    missing: list[str] = []
    incompatible: list[str] = []
    for field in SUPPLIER_CAPABILITY_FIELDS:
        if field in required and required.get(field) not in (None, "") and capability.get(field) in (None, ""):
            missing.append(field)

    numeric_minimums = (
        "maximum_ply", "corrugator_width_mm", "maximum_sheet_length_mm",
        "maximum_sheet_width_mm", "maximum_print_colours",
    )
    for field in numeric_minimums:
        if required.get(field) not in (None, "") and capability.get(field) not in (None, ""):
            if float(capability[field]) < float(required[field]):
                incompatible.append(field)

    numeric_maximums = ("minimum_sheet_length_mm", "minimum_sheet_width_mm")
    for field in numeric_maximums:
        if required.get(field) not in (None, "") and capability.get(field) not in (None, ""):
            if float(capability[field]) > float(required[field]):
                incompatible.append(field)

    for field in ("die_cutting_available", "stitching_available", "gluing_available", "coating_available", "laboratory_access", "trial_capability", "backup_site_available"):
        if required.get(field) is True and capability.get(field) is not True:
            if capability.get(field) in (None, ""):
                if field not in missing:
                    missing.append(field)
            else:
                incompatible.append(field)

    required_flutes = {str(v).strip() for v in required.get("supported_flutes", ()) if str(v).strip()}
    actual_flutes = {str(v).strip() for v in capability.get("supported_flutes", ()) if str(v).strip()}
    if required_flutes and not actual_flutes:
        missing.append("supported_flutes")
    elif required_flutes - actual_flutes:
        incompatible.append("supported_flutes")

    if incompatible:
        outcome = "incompatible"
    elif missing:
        outcome = "evidence missing"
    else:
        outcome = "compatible"
    return CapabilityAssessment(outcome, tuple(sorted(set(missing))), tuple(sorted(set(incompatible))))


def assess_evidence_confidence(records: Sequence[Mapping[str, Any]]) -> EvidenceConfidenceAssessment:
    """Classify evidence quality, not probability of technical success."""
    counts = {key: 0 for key in SOURCE_CLASSIFICATIONS}
    if not records:
        return EvidenceConfidenceAssessment("Not assessable", ("No evidence records are available.",), counts)

    issues: list[str] = []
    valid_records = 0
    for row in records:
        source = _clean(row.get("source_classification"))
        if source in counts:
            counts[source] += 1
        else:
            issues.append("One or more records have an invalid source classification.")
        if row.get("validation_status") == "valid" and not row.get("superseded_by"):
            valid_records += 1
        if row.get("validation_status") in {"expired", "invalid", "missing"}:
            issues.append("One or more records are expired, invalid, or missing.")
        if row.get("superseded_by"):
            issues.append("One or more records are superseded.")

    tested = counts["laboratory_tested"]
    assumptions = counts["assumption"] + counts["predicted"]
    if tested >= 2 and valid_records == len(records) and assumptions == 0 and not issues:
        classification = "High evidence confidence"
    elif valid_records >= max(1, len(records) // 2) and tested >= 1:
        classification = "Moderate evidence confidence"
    else:
        classification = "Low evidence confidence"
    if assumptions:
        issues.append("Predicted values or assumptions reduce evidence confidence.")
    if not tested:
        issues.append("No laboratory-tested evidence is present.")
    return EvidenceConfidenceAssessment(classification, tuple(dict.fromkeys(issues)), counts)
