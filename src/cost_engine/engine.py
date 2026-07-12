from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CostAnalysis:
    alternative_id: str
    currency: str
    unit_cost: float
    annual_cost: float
    unit_savings_vs_baseline: float
    annual_savings_vs_baseline: float
    cost_change_percent_vs_baseline: float


def _require_number(value: Any, path: str, *, allow_zero: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{path} must be numeric.")
    if value < 0 or (value == 0 and not allow_zero):
        rule = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{path} must be {rule}.")
    return float(value)


def analyze_costs(dataset: dict[str, Any]) -> dict[str, CostAnalysis]:
    """Aggregate declared unit-cost inputs and compare alternatives to baseline."""
    project = dataset.get("packaging_project")
    alternatives = dataset.get("packaging_alternatives")
    costs = dataset.get("cost_inputs")
    if not isinstance(project, dict):
        raise ValueError("packaging_project must be an object.")
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError("packaging_alternatives must be a non-empty list.")
    if not isinstance(costs, list):
        raise ValueError("cost_inputs must be a list.")

    annual_volume = _require_number(project.get("annual_volume"), "packaging_project.annual_volume")
    currency = project.get("currency")
    if not isinstance(currency, str) or not currency:
        raise ValueError("packaging_project.currency is required.")

    alternative_ids: set[str] = set()
    baseline_id: str | None = None
    for record in alternatives:
        alternative_id = record.get("alternative_id")
        if not alternative_id or alternative_id in alternative_ids:
            raise ValueError("Alternative identifiers must be present and unique.")
        alternative_ids.add(alternative_id)
        if record.get("status") == "baseline":
            if baseline_id is not None:
                raise ValueError("Exactly one baseline alternative is required.")
            baseline_id = alternative_id
    if baseline_id is None:
        raise ValueError("Exactly one baseline alternative is required.")

    totals = {alternative_id: 0.0 for alternative_id in alternative_ids}
    counts = {alternative_id: 0 for alternative_id in alternative_ids}
    expected_unit = f"{currency}_per_case"
    for index, record in enumerate(costs):
        alternative_id = record.get("alternative_id")
        if alternative_id not in alternative_ids:
            raise ValueError(f"cost_inputs.{index}.alternative_id is invalid.")
        if record.get("currency") != currency:
            raise ValueError(f"cost_inputs.{index}.currency must match project currency.")
        if record.get("unit") != expected_unit:
            raise ValueError(f"cost_inputs.{index}.unit must be {expected_unit}.")
        totals[alternative_id] += _require_number(
            record.get("value"), f"cost_inputs.{index}.value", allow_zero=True
        )
        counts[alternative_id] += 1

    missing = [alternative_id for alternative_id, count in counts.items() if count == 0]
    if missing:
        raise ValueError(f"Missing cost inputs for: {', '.join(sorted(missing))}.")

    baseline_cost = totals[baseline_id]
    if baseline_cost <= 0:
        raise ValueError("Baseline unit cost must be greater than zero.")

    results: dict[str, CostAnalysis] = {}
    for alternative_id in sorted(alternative_ids):
        unit_cost = totals[alternative_id]
        unit_savings = baseline_cost - unit_cost
        results[alternative_id] = CostAnalysis(
            alternative_id=alternative_id,
            currency=currency,
            unit_cost=round(unit_cost, 6),
            annual_cost=round(unit_cost * annual_volume, 6),
            unit_savings_vs_baseline=round(unit_savings, 6),
            annual_savings_vs_baseline=round(unit_savings * annual_volume, 6),
            cost_change_percent_vs_baseline=round((unit_cost - baseline_cost) / baseline_cost * 100.0, 6),
        )
    return results
