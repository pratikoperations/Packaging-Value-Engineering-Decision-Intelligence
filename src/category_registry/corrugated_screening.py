from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .corrugated_evidence import detect_conflicting_evidence, match_evidence

SCREENING_OUTCOMES = (
    "criteria met",
    "criteria not met",
    "validation required",
    "evidence conflict",
    "insufficient technical data",
)

@dataclass(frozen=True)
class GovernedFactor:
    key: str
    value: float
    source_reference: str
    version: str
    applicability: str
    validation_status: str

@dataclass(frozen=True)
class ScreeningAssessment:
    outcome: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    checks: Mapping[str, str]
    limitations: tuple[str, ...]


def _number(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def validate_governed_factor(record: Mapping[str, Any]) -> GovernedFactor:
    """Validate a supplied safety or derating factor without inventing defaults."""
    key = str(record.get("factor_key") or "").strip()
    value = _number(record.get("value"))
    source = str(record.get("source_reference") or "").strip()
    version = str(record.get("version") or "").strip()
    applicability = str(record.get("applicability") or "").strip()
    status = str(record.get("validation_status") or "").strip()
    if not key or value is None or value <= 0:
        raise ValueError("Factor key and positive numeric value are required.")
    if not source or not version or not applicability:
        raise ValueError("Factor source, version and applicability are required.")
    if status != "valid":
        raise ValueError("Only explicitly validated factors may be applied.")
    return GovernedFactor(key, value, source, version, applicability, status)


def _valid_evidence_values(
    evidence: Sequence[Mapping[str, Any]], expected: Mapping[str, Any], method: str
) -> tuple[list[float], list[str]]:
    values: list[float] = []
    issues: list[str] = []
    for record in evidence:
        if str(record.get("test_method") or "").strip().upper() != method.upper():
            continue
        match = match_evidence(record, {**expected, "test_method": method})
        if match.status != "matched":
            issues.extend(match.reasons)
            continue
        if record.get("validation_status") != "valid":
            issues.append(f"{method} evidence is not validated")
            continue
        value = _number(record.get("result_value"))
        if value is None:
            issues.append(f"{method} evidence has no numeric result")
            continue
        values.append(value)
    return values, issues


def screen_corrugated(
    *,
    requirements: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    expected_evidence_context: Mapping[str, Any],
    factors: Sequence[Mapping[str, Any]] = (),
    warehouse: Mapping[str, Any] | None = None,
    packing_line: Mapping[str, Any] | None = None,
) -> ScreeningAssessment:
    """Compare supplied evidence and operating limits; never predicts BCT or approves a design."""
    warehouse = warehouse or {}
    packing_line = packing_line or {}
    checks: dict[str, str] = {}
    blockers: list[str] = []
    warnings: list[str] = []
    limitations = [
        "No BCT, ECT-to-BCT or McKee prediction is performed.",
        "Engineering validation and explicit human approval remain mandatory.",
    ]

    conflicts = detect_conflicting_evidence(evidence)
    if conflicts:
        blockers.append("conflicting technical evidence")
        checks["evidence"] = "conflict"

    factor_map: dict[str, GovernedFactor] = {}
    for raw in factors:
        try:
            factor = validate_governed_factor(raw)
            factor_map[factor.key] = factor
        except ValueError as exc:
            blockers.append(f"invalid governed factor: {exc}")

    bct_required = _number(requirements.get("compression_requirement_n"))
    bct_values, bct_issues = _valid_evidence_values(evidence, expected_evidence_context, "BCT")
    warnings.extend(bct_issues)
    if bct_required is None:
        checks["bct"] = "requirement missing"
    elif not bct_values:
        checks["bct"] = "validation required"
        blockers.append("validated BCT evidence missing")
    else:
        required = bct_required
        safety = factor_map.get("compression_safety_factor")
        derating = factor_map.get("environmental_derating_factor")
        if safety:
            required *= safety.value
        if derating:
            required *= derating.value
        supplied = min(bct_values)
        checks["bct"] = f"supplied {supplied:g} N versus governed requirement {required:g} N"
        if supplied < required:
            blockers.append("BCT below governed requirement")

    ect_required = _number(requirements.get("ect_requirement_kn_m"))
    ect_values, ect_issues = _valid_evidence_values(evidence, expected_evidence_context, "ECT")
    warnings.extend(ect_issues)
    if ect_required is not None:
        if not ect_values:
            checks["ect"] = "validation required"
            blockers.append("validated ECT evidence missing")
        else:
            supplied = min(ect_values)
            checks["ect"] = f"supplied {supplied:g} kN/m versus requirement {ect_required:g} kN/m"
            if supplied < ect_required:
                blockers.append("ECT below governed requirement")
    else:
        checks["ect"] = "not required or requirement missing"

    required_layers = _number(requirements.get("stack_layers_required"))
    proposed_layers = _number(requirements.get("proposed_stack_layers"))
    if required_layers is not None and proposed_layers is not None:
        checks["stack_layers"] = f"proposed {proposed_layers:g} versus required {required_layers:g}"
        if proposed_layers < required_layers:
            blockers.append("stack-layer requirement not met")
    elif required_layers is not None:
        checks["stack_layers"] = "proposed stack layers missing"
        blockers.append("stacking data incomplete")

    pallet_load = _number(requirements.get("pallet_load_kg"))
    pallet_limit = _number(requirements.get("maximum_pallet_weight_kg"))
    if pallet_load is not None and pallet_limit is not None:
        checks["pallet_weight"] = f"load {pallet_load:g} kg versus limit {pallet_limit:g} kg"
        if pallet_load > pallet_limit:
            blockers.append("maximum pallet weight exceeded")

    duration = _number(requirements.get("storage_duration_days"))
    if duration is None:
        warnings.append("storage duration is missing")
    stacking_mode = str(requirements.get("stacking_mode") or "").strip().lower()
    if not stacking_mode:
        warnings.append("static or dynamic stacking mode is missing")
    elif stacking_mode not in {"static", "dynamic"}:
        blockers.append("invalid stacking mode")

    humidity = _number(requirements.get("humidity_percent"))
    humid_condition = bool(requirements.get("humid_condition"))
    refrigerated = bool(requirements.get("refrigerated_condition"))
    if (humid_condition or refrigerated or (humidity is not None and humidity >= 80)) and "environmental_derating_factor" not in factor_map:
        blockers.append("environmental derating factor required and missing")
        checks["environment"] = "validation required"
    else:
        checks["environment"] = "context recorded"

    storage_type = str(warehouse.get("storage_type") or "").strip().lower()
    if storage_type and storage_type not in {"floor", "rack"}:
        blockers.append("invalid warehouse storage type")
    overhang = _number(warehouse.get("pallet_overhang_mm"))
    if overhang is not None and overhang > 0:
        blockers.append("pallet overhang present")
    underhang = _number(warehouse.get("pallet_underhang_mm"))
    if underhang is not None and underhang > 0:
        warnings.append("pallet underhang may reduce footprint utilization")
    touches = _number(warehouse.get("handling_touches"))
    if touches is None:
        warnings.append("handling touches are missing")
    if warehouse.get("mixed_load_exposure") is True:
        warnings.append("mixed-load exposure requires transport validation")
    if warehouse.get("stretch_wrap_compression") is True and not warehouse.get("stretch_wrap_validation_status") == "valid":
        blockers.append("stretch-wrap compression validation missing")

    dimensions = {
        "length": _number(requirements.get("external_length_mm")),
        "width": _number(requirements.get("external_width_mm")),
        "height": _number(requirements.get("external_height_mm")),
    }
    for axis, value in dimensions.items():
        minimum = _number(packing_line.get(f"minimum_{axis}_mm"))
        maximum = _number(packing_line.get(f"maximum_{axis}_mm"))
        if value is not None and minimum is not None and value < minimum:
            blockers.append(f"case {axis} below machine limit")
        if value is not None and maximum is not None and value > maximum:
            blockers.append(f"case {axis} above machine limit")

    for key in ("case_erector_method", "sealing_method", "flap_geometry", "barcode_position"):
        required_value = str(requirements.get(key) or "").strip()
        supported = packing_line.get(f"supported_{key}")
        if required_value and supported:
            supported_values = {str(v).strip() for v in supported}
            if required_value not in supported_values:
                blockers.append(f"{key.replace('_', ' ')} incompatible")

    speed = _number(requirements.get("machine_speed_cases_per_min"))
    speed_limit = _number(packing_line.get("maximum_speed_cases_per_min"))
    if speed is not None and speed_limit is not None and speed > speed_limit:
        blockers.append("required machine speed exceeds line capability")
    for condition in ("squareness_within_tolerance", "warp_within_tolerance"):
        if requirements.get(condition) is False:
            blockers.append(condition.replace("_", " "))
    if requirements.get("packing_line_trial_required") is True and packing_line.get("line_trial_status") != "valid":
        blockers.append("mandatory packing-line trial incomplete")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    if conflicts:
        outcome = "evidence conflict"
    elif unique_blockers:
        validation_terms = ("missing", "incomplete", "validation required", "trial incomplete")
        if all(any(term in blocker for term in validation_terms) for blocker in unique_blockers):
            outcome = "validation required"
        else:
            outcome = "criteria not met"
    elif bct_required is None and ect_required is None:
        outcome = "insufficient technical data"
    else:
        outcome = "criteria met"
    return ScreeningAssessment(outcome, unique_blockers, unique_warnings, checks, tuple(limitations))
