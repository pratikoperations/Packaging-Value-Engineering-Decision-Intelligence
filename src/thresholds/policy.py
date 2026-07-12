from __future__ import annotations

from typing import Any

DEFAULT_CONTROLLED_PROFILE: dict[str, Any] = {
    "minimum_annual_savings": 0.0,
    "minimum_material_reduction_percent": 0.0,
    "maximum_business_risk": "high",
    "require_positive_savings_or_material_reduction": True,
}

MANDATORY_ENGINEERING_CONTROLS: dict[str, bool] = {
    "engineering_validation_required": True,
    "autonomous_approval_allowed": False,
    "critical_risk_blocked": True,
    "not_qualified_blocked": True,
    "insufficient_data_cannot_be_recommended": True,
}

_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def validate_threshold_profile(profile: dict[str, Any]) -> dict[str, Any]:
    required = set(DEFAULT_CONTROLLED_PROFILE)
    missing = sorted(required - set(profile))
    extra = sorted(set(profile) - required)
    if missing:
        raise ValueError(f"Missing threshold fields: {', '.join(missing)}")
    if extra:
        raise ValueError(f"Unsupported threshold fields: {', '.join(extra)}")

    normalized = dict(profile)
    for field in ("minimum_annual_savings", "minimum_material_reduction_percent"):
        value = normalized[field]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be numeric.")
        if value < 0:
            raise ValueError(f"{field} cannot be negative.")
        normalized[field] = float(value)

    risk = str(normalized["maximum_business_risk"]).strip().lower()
    if risk not in _RISK_ORDER:
        raise ValueError("maximum_business_risk must be low, medium, high, or critical.")
    normalized["maximum_business_risk"] = risk

    flag = normalized["require_positive_savings_or_material_reduction"]
    if not isinstance(flag, bool):
        raise ValueError("require_positive_savings_or_material_reduction must be boolean.")

    return normalized


def business_thresholds_pass(
    *,
    profile: dict[str, Any],
    annual_savings: float,
    material_change_percent: float,
    overall_risk: str,
) -> tuple[bool, tuple[str, ...]]:
    normalized = validate_threshold_profile(profile)
    reasons: list[str] = []

    if annual_savings < normalized["minimum_annual_savings"]:
        reasons.append("Annual savings are below the configured business threshold.")

    material_reduction = max(0.0, -float(material_change_percent))
    if material_reduction < normalized["minimum_material_reduction_percent"]:
        reasons.append("Material reduction is below the configured business threshold.")

    risk = str(overall_risk).lower()
    if risk not in _RISK_ORDER:
        reasons.append("Business risk level is not recognized.")
    elif _RISK_ORDER[risk] > _RISK_ORDER[normalized["maximum_business_risk"]]:
        reasons.append("Business risk exceeds the configured maximum.")

    if normalized["require_positive_savings_or_material_reduction"]:
        if annual_savings <= 0 and material_reduction <= 0:
            reasons.append("Neither positive savings nor material reduction is present.")

    return (not reasons, tuple(reasons))
