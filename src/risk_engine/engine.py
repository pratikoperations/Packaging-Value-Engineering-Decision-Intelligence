from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_REQUIRED_RISK_TYPES = ("quality", "supply", "implementation")
_LEVEL_ORDER = {"not_recorded": -1, "low": 0, "medium": 1, "high": 2, "critical": 3}
_ALLOWED_LEVELS = {"low", "medium", "high", "critical"}


@dataclass(frozen=True)
class RiskIndicator:
    risk_type: str
    declared_level: str
    probability_percent: float | None
    effective_level: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class RiskOutcome:
    alternative_id: str
    overall_level: str
    data_complete: bool
    indicators: tuple[RiskIndicator, ...]
    reasons: tuple[str, ...]
    validation_required: tuple[str, ...]


def _require_list(value: Any, path: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list.")
    if not all(isinstance(item, dict) for item in value):
        raise ValueError(f"Every item in {path} must be an object.")
    return value


def _probability_level(probability: float) -> str:
    if probability >= 70:
        return "critical"
    if probability >= 50:
        return "high"
    if probability >= 25:
        return "medium"
    return "low"


def _max_level(*levels: str) -> str:
    return max(levels, key=lambda level: _LEVEL_ORDER[level])


def evaluate_risks(dataset: dict[str, Any]) -> dict[str, RiskOutcome]:
    """Evaluate deterministic quality, supply, and implementation risk indicators.

    The engine preserves declared risk data, escalates effective severity when the
    probability band is higher, and explicitly reports missing risk categories.
    """
    alternatives = _require_list(dataset.get("packaging_alternatives"), "packaging_alternatives")
    records = _require_list(dataset.get("risk_records", []), "risk_records")

    alternative_ids: set[str] = set()
    for record in alternatives:
        alternative_id = record.get("alternative_id")
        if not isinstance(alternative_id, str) or not alternative_id:
            raise ValueError("Every packaging alternative requires a non-empty alternative_id.")
        if alternative_id in alternative_ids:
            raise ValueError("Alternative identifiers must be unique.")
        alternative_ids.add(alternative_id)

    by_alternative: dict[str, dict[str, list[dict[str, Any]]]] = {
        alternative_id: {risk_type: [] for risk_type in _REQUIRED_RISK_TYPES}
        for alternative_id in alternative_ids
    }

    for index, record in enumerate(records):
        alternative_id = record.get("alternative_id")
        risk_type = record.get("risk_type")
        level = record.get("level")
        probability = record.get("probability_percent")
        if alternative_id not in alternative_ids:
            raise ValueError(f"risk_records.{index}.alternative_id is invalid.")
        if risk_type not in _REQUIRED_RISK_TYPES:
            continue
        if level not in _ALLOWED_LEVELS:
            raise ValueError(f"risk_records.{index}.level is invalid.")
        if not isinstance(probability, (int, float)) or isinstance(probability, bool):
            raise ValueError(f"risk_records.{index}.probability_percent must be numeric.")
        if probability < 0 or probability > 100:
            raise ValueError(f"risk_records.{index}.probability_percent must be between 0 and 100.")
        by_alternative[alternative_id][risk_type].append(record)

    outcomes: dict[str, RiskOutcome] = {}
    for alternative_id in sorted(alternative_ids):
        indicators: list[RiskIndicator] = []
        reasons: list[str] = []
        required_validation: list[str] = []
        effective_levels: list[str] = []
        data_complete = True

        for risk_type in _REQUIRED_RISK_TYPES:
            category_records = by_alternative[alternative_id][risk_type]
            if not category_records:
                data_complete = False
                reasons.append(f"No {risk_type} risk record is available.")
                required_validation.append(f"Complete {risk_type} risk assessment")
                indicators.append(
                    RiskIndicator(
                        risk_type=risk_type,
                        declared_level="not_recorded",
                        probability_percent=None,
                        effective_level="not_recorded",
                        reasons=(f"Missing {risk_type} risk record.",),
                    )
                )
                continue

            record_indicators: list[tuple[str, float, str, tuple[str, ...]]] = []
            for record in category_records:
                declared_level = record["level"]
                probability = float(record["probability_percent"])
                probability_level = _probability_level(probability)
                effective_level = _max_level(declared_level, probability_level)
                indicator_reasons: list[str] = [
                    f"Declared {declared_level}; probability {probability:g}% maps to {probability_level}."
                ]
                if effective_level != declared_level:
                    indicator_reasons.append(
                        f"Effective level escalated to {effective_level} by probability band."
                    )
                record_indicators.append(
                    (declared_level, probability, effective_level, tuple(indicator_reasons))
                )

            selected = max(record_indicators, key=lambda item: _LEVEL_ORDER[item[2]])
            declared_level, probability, effective_level, indicator_reasons = selected
            effective_levels.append(effective_level)
            indicators.append(
                RiskIndicator(
                    risk_type=risk_type,
                    declared_level=declared_level,
                    probability_percent=probability,
                    effective_level=effective_level,
                    reasons=indicator_reasons,
                )
            )
            if effective_level in {"high", "critical"}:
                reasons.append(f"{risk_type.capitalize()} risk is {effective_level}.")
                required_validation.append(f"Mitigate and validate {risk_type} risk")

        overall_level = _max_level(*effective_levels) if effective_levels else "not_recorded"
        outcomes[alternative_id] = RiskOutcome(
            alternative_id=alternative_id,
            overall_level=overall_level,
            data_complete=data_complete,
            indicators=tuple(indicators),
            reasons=tuple(dict.fromkeys(reasons)),
            validation_required=tuple(dict.fromkeys(required_validation)),
        )

    return outcomes
