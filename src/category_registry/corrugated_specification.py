from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


BOX_STYLES = (
    "regular_slotted_container",
    "half_slotted_container",
    "full_overlap_slotted_container",
    "die_cut_case",
    "wrap_around_case",
    "tray_and_lid",
    "telescope_case",
    "other_documented_style",
)

CONVERTING_PROFILES = (
    "slotted_glued",
    "slotted_stitched",
    "die_cut_glued",
    "die_cut_stitched",
    "wrap_around_glued",
    "manual_assembly",
    "other_documented_process",
)

JOINT_TYPES = ("glued", "stitched", "taped", "lock_tab", "other_documented_joint")
CLOSURE_METHODS = ("tape", "hot_melt", "stitch", "self_locking", "other_documented_closure")
PRINT_PROCESSES = ("none", "flexographic", "digital", "litho_laminated", "screen", "other_documented_print")
VALIDATION_STATUSES = ("not_reviewed", "valid", "invalid", "missing", "expired")
SOURCE_CLASSIFICATIONS = (
    "uploaded_fact",
    "manually_entered_fact",
    "supplier_declared",
    "laboratory_tested",
    "predicted",
    "assumption",
)


@dataclass(frozen=True)
class SpecificationTolerance:
    field_key: str
    context: str
    nominal: float
    minimum: float
    maximum: float
    unit: str
    inspection_method: str
    criticality: str
    source_classification: str
    source_reference: str
    version: str
    validation_status: str


@dataclass(frozen=True)
class SpecificationDifference:
    field_key: str
    baseline_value: Any
    proposed_value: Any
    baseline_unit: str | None
    proposed_unit: str | None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_tolerance(record: Mapping[str, Any]) -> tuple[str, ...]:
    """Validate one sourced tolerance record without inventing a threshold."""
    issues: list[str] = []
    field_key = str(record.get("field_key") or "").strip()
    context = str(record.get("context") or "").strip()
    unit = str(record.get("unit") or "").strip()
    method = str(record.get("inspection_method") or "").strip()
    source = str(record.get("source_classification") or "").strip()
    source_reference = str(record.get("source_reference") or "").strip()
    version = str(record.get("version") or "").strip()
    status = str(record.get("validation_status") or "").strip()

    if not field_key:
        issues.append("Tolerance field_key is required")
    if context not in {"baseline", "proposed"}:
        issues.append("Tolerance context must be baseline or proposed")

    nominal = record.get("nominal")
    minimum = record.get("minimum")
    maximum = record.get("maximum")
    if not all(_is_number(value) for value in (nominal, minimum, maximum)):
        issues.append("Tolerance nominal, minimum and maximum must be numeric")
    else:
        if minimum > maximum:
            issues.append("Tolerance minimum cannot exceed maximum")
        if not minimum <= nominal <= maximum:
            issues.append("Tolerance nominal must be within minimum and maximum")

    if not unit:
        issues.append("Tolerance unit is required")
    if not method:
        issues.append("Tolerance inspection_method is required")
    if str(record.get("criticality") or "").strip() not in {"critical", "major", "minor"}:
        issues.append("Tolerance criticality must be critical, major or minor")
    if source not in SOURCE_CLASSIFICATIONS:
        issues.append("Tolerance source_classification is invalid")
    if not source_reference:
        issues.append("Tolerance source_reference is required")
    if not version:
        issues.append("Tolerance version is required")
    if status not in VALIDATION_STATUSES:
        issues.append("Tolerance validation_status is invalid")
    return tuple(issues)


def validate_tolerances(records: Iterable[Mapping[str, Any]]) -> tuple[str, ...]:
    issues: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for index, record in enumerate(records, start=1):
        key = (
            str(record.get("context") or ""),
            str(record.get("field_key") or ""),
            str(record.get("version") or ""),
        )
        if key in seen:
            issues.append(f"Duplicate tolerance record at row {index}: {key}")
        seen.add(key)
        issues.extend(f"Row {index}: {issue}" for issue in validate_tolerance(record))
    return tuple(issues)


def compare_specifications(
    baseline_rows: Iterable[Mapping[str, Any]],
    proposed_rows: Iterable[Mapping[str, Any]],
) -> tuple[SpecificationDifference, ...]:
    """Return transparent baseline/proposed differences; no engineering conclusion is made."""
    baseline = {str(row.get("field_key")): row for row in baseline_rows if row.get("field_key")}
    proposed = {str(row.get("field_key")): row for row in proposed_rows if row.get("field_key")}
    differences: list[SpecificationDifference] = []
    for field_key in sorted(set(baseline) | set(proposed)):
        base = baseline.get(field_key, {})
        prop = proposed.get(field_key, {})
        if base.get("value") != prop.get("value") or base.get("unit") != prop.get("unit"):
            differences.append(
                SpecificationDifference(
                    field_key=field_key,
                    baseline_value=base.get("value"),
                    proposed_value=prop.get("value"),
                    baseline_unit=base.get("unit"),
                    proposed_unit=prop.get("unit"),
                )
            )
    return tuple(differences)
