from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Mapping

from src.cost_engine import analyze_costs
from src.material_engine import analyze_materials


@dataclass(frozen=True)
class ScenarioInputs:
    annual_volume: float
    cost_adjustment_percent_by_alternative: Mapping[str, float]
    material_adjustment_percent_by_alternative: Mapping[str, float]


@dataclass(frozen=True)
class AlternativeScenario:
    alternative_id: str
    unit_cost: float
    annual_cost: float
    annual_savings_vs_baseline: float
    case_weight_g: float
    annual_material_kg: float
    material_change_percent_vs_baseline: float
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
    annual_volume: float
    alternatives: dict[str, AlternativeScenario]


def _validate_adjustment(value: float, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{path} must be numeric.")
    if value < -50 or value > 100:
        raise ValueError(f"{path} must be between -50 and 100 percent.")
    return float(value)


def evaluate_scenario(dataset: dict, inputs: ScenarioInputs) -> ScenarioResult:
    """Apply transparent scenario assumptions and recalculate cost and material outputs.

    Scenario adjustments are explicit by alternative. No forecasts, optimization, hidden
    defaults, or probability-weighted calculations are used.
    """
    if not isinstance(inputs.annual_volume, (int, float)) or isinstance(inputs.annual_volume, bool):
        raise ValueError("annual_volume must be numeric.")
    if inputs.annual_volume <= 0:
        raise ValueError("annual_volume must be greater than zero.")

    adjusted = deepcopy(dataset)
    alternatives = adjusted.get("packaging_alternatives")
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError("packaging_alternatives must be a non-empty list.")

    alternative_ids = {
        record.get("alternative_id")
        for record in alternatives
        if isinstance(record, dict) and isinstance(record.get("alternative_id"), str)
    }
    if len(alternative_ids) != len(alternatives):
        raise ValueError("Every alternative requires a unique alternative_id.")

    unknown_cost_ids = set(inputs.cost_adjustment_percent_by_alternative) - alternative_ids
    unknown_material_ids = set(inputs.material_adjustment_percent_by_alternative) - alternative_ids
    if unknown_cost_ids:
        raise ValueError(f"Unknown cost adjustment alternatives: {', '.join(sorted(unknown_cost_ids))}.")
    if unknown_material_ids:
        raise ValueError(
            f"Unknown material adjustment alternatives: {', '.join(sorted(unknown_material_ids))}."
        )

    cost_adjustments = {
        alternative_id: _validate_adjustment(
            inputs.cost_adjustment_percent_by_alternative.get(alternative_id, 0.0),
            f"cost adjustment for {alternative_id}",
        )
        for alternative_id in alternative_ids
    }
    material_adjustments = {
        alternative_id: _validate_adjustment(
            inputs.material_adjustment_percent_by_alternative.get(alternative_id, 0.0),
            f"material adjustment for {alternative_id}",
        )
        for alternative_id in alternative_ids
    }

    adjusted["packaging_project"]["annual_volume"] = float(inputs.annual_volume)

    for record in adjusted.get("cost_inputs", []):
        alternative_id = record.get("alternative_id")
        factor = 1.0 + cost_adjustments[alternative_id] / 100.0
        record["value"] = float(record["value"]) * factor

    for record in alternatives:
        alternative_id = record["alternative_id"]
        factor = 1.0 + material_adjustments[alternative_id] / 100.0
        record["case_weight_g"] = float(record["case_weight_g"]) * factor

    for record in adjusted.get("material_components", []):
        alternative_id = record.get("alternative_id")
        factor = 1.0 + material_adjustments[alternative_id] / 100.0
        record["weight_g"] = float(record["weight_g"]) * factor

    cost_results = analyze_costs(adjusted)
    material_results = analyze_materials(adjusted)

    results: dict[str, AlternativeScenario] = {}
    for alternative_id in sorted(alternative_ids):
        assumptions = (
            f"Annual volume set to {float(inputs.annual_volume):g} cases.",
            f"Unit-cost adjustment: {cost_adjustments[alternative_id]:g}%.",
            f"Material-weight adjustment: {material_adjustments[alternative_id]:g}%.",
        )
        cost = cost_results[alternative_id]
        material = material_results[alternative_id]
        results[alternative_id] = AlternativeScenario(
            alternative_id=alternative_id,
            unit_cost=cost.unit_cost,
            annual_cost=cost.annual_cost,
            annual_savings_vs_baseline=cost.annual_savings_vs_baseline,
            case_weight_g=material.case_weight_g,
            annual_material_kg=material.annual_material_kg,
            material_change_percent_vs_baseline=material.material_change_percent_vs_baseline,
            assumptions=assumptions,
        )

    return ScenarioResult(annual_volume=float(inputs.annual_volume), alternatives=results)
