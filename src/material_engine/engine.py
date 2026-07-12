from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaterialAnalysis:
    alternative_id: str
    case_weight_g: float
    component_weight_g: float
    component_variance_g: float
    annual_material_kg: float
    material_change_g_vs_baseline: float
    material_change_percent_vs_baseline: float


def _require_positive_number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{path} must be a positive number.")
    return float(value)


def analyze_materials(dataset: dict[str, Any]) -> dict[str, MaterialAnalysis]:
    """Calculate deterministic material metrics for every packaging alternative.

    The function does not optimize designs or approve technical suitability. It only
    calculates declared material totals and comparisons against the declared baseline.
    """
    project = dataset.get("packaging_project")
    alternatives = dataset.get("packaging_alternatives")
    components = dataset.get("material_components")

    if not isinstance(project, dict):
        raise ValueError("packaging_project must be an object.")
    if not isinstance(alternatives, list) or not alternatives:
        raise ValueError("packaging_alternatives must be a non-empty list.")
    if not isinstance(components, list):
        raise ValueError("material_components must be a list.")

    annual_volume = _require_positive_number(project.get("annual_volume"), "packaging_project.annual_volume")
    if project.get("annual_volume_unit") != "cases_per_year":
        raise ValueError("packaging_project.annual_volume_unit must be cases_per_year.")

    alternative_map: dict[str, dict[str, Any]] = {}
    baseline_id: str | None = None
    for record in alternatives:
        alternative_id = record.get("alternative_id")
        if not alternative_id or alternative_id in alternative_map:
            raise ValueError("Alternative identifiers must be present and unique.")
        alternative_map[alternative_id] = record
        if record.get("status") == "baseline":
            if baseline_id is not None:
                raise ValueError("Exactly one baseline alternative is required.")
            baseline_id = alternative_id

    if baseline_id is None:
        raise ValueError("Exactly one baseline alternative is required.")

    component_totals = {alternative_id: 0.0 for alternative_id in alternative_map}
    for index, component in enumerate(components):
        alternative_id = component.get("alternative_id")
        if alternative_id not in alternative_map:
            raise ValueError(f"material_components.{index}.alternative_id is invalid.")
        component_totals[alternative_id] += _require_positive_number(
            component.get("weight_g"), f"material_components.{index}.weight_g"
        )

    baseline_weight = _require_positive_number(
        alternative_map[baseline_id].get("case_weight_g"),
        f"packaging_alternatives[{baseline_id}].case_weight_g",
    )

    results: dict[str, MaterialAnalysis] = {}
    for alternative_id, record in alternative_map.items():
        case_weight = _require_positive_number(
            record.get("case_weight_g"),
            f"packaging_alternatives[{alternative_id}].case_weight_g",
        )
        component_weight = component_totals[alternative_id]
        if component_weight <= 0:
            raise ValueError(f"No positive material component weight exists for {alternative_id}.")

        change_g = case_weight - baseline_weight
        results[alternative_id] = MaterialAnalysis(
            alternative_id=alternative_id,
            case_weight_g=round(case_weight, 6),
            component_weight_g=round(component_weight, 6),
            component_variance_g=round(component_weight - case_weight, 6),
            annual_material_kg=round(case_weight * annual_volume / 1000.0, 6),
            material_change_g_vs_baseline=round(change_g, 6),
            material_change_percent_vs_baseline=round(change_g / baseline_weight * 100.0, 6),
        )

    return results
