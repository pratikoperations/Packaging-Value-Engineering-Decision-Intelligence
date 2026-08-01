from __future__ import annotations

from collections import Counter
from typing import Any

from .catalogue import ASSUMPTIONS, CALCULATION_CATALOGUE, RULE_LINEAGE, validate_catalogue
from .formulas import calculate
from .models import ReconciliationResult
from .reconciliation import reconcile


class IndependentCalculationEvidenceService:
    REGISTRY_VERSION = "1.0.0"

    def evaluate(
        self,
        *,
        dataset: dict[str, Any],
        scenario_id: str,
        scenario_result: Any,
        cost_adjustments: dict[str, float] | None = None,
        material_adjustments: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        validate_catalogue()
        cost_adjustments = cost_adjustments or {}
        material_adjustments = material_adjustments or {}
        alternatives = dataset.get("packaging_alternatives", [])
        if not isinstance(alternatives, list) or not alternatives:
            raise ValueError("packaging_alternatives must be a non-empty list.")
        alternative_map = {item["alternative_id"]: item for item in alternatives}
        baseline_ids = [item["alternative_id"] for item in alternatives if item.get("status") == "baseline"]
        if len(baseline_ids) != 1:
            raise ValueError("Exactly one baseline alternative is required.")
        baseline_id = baseline_ids[0]
        annual_volume = dataset["packaging_project"]["annual_volume"]
        currency = dataset["packaging_project"].get("currency")
        costs_by_alt: dict[str, list[Any]] = {key: [] for key in alternative_map}
        for record in dataset.get("cost_inputs", []):
            costs_by_alt[record["alternative_id"]].append(record["value"])
        components_by_alt: dict[str, list[Any]] = {key: [] for key in alternative_map}
        for record in dataset.get("material_components", []):
            components_by_alt[record["alternative_id"]].append(record["weight_g"])

        independent_unit_costs = {
            alt_id: calculate("CALC-COST-001", {"cost_inputs": costs_by_alt[alt_id]}, currency=currency)
            for alt_id in alternative_map
        }
        baseline_unit = independent_unit_costs[baseline_id].value
        baseline_weight = alternative_map[baseline_id]["case_weight_g"]
        results: list[ReconciliationResult] = []

        for alt_id, record in sorted(alternative_map.items()):
            primary = scenario_result.alternatives.get(alt_id) if hasattr(scenario_result, "alternatives") else None
            cost_percent = cost_adjustments.get(alt_id, 0.0)
            material_percent = material_adjustments.get(alt_id, 0.0)
            cost_factor = calculate("CALC-SCN-001", {"adjustment_percent": cost_percent}, assumption_ids=(f"ASM-SCN-COST-{alt_id}",))
            material_factor = calculate("CALC-SCN-001", {"adjustment_percent": material_percent}, assumption_ids=(f"ASM-SCN-MAT-{alt_id}",))
            adjusted_cost = calculate("CALC-SCN-002", {"raw_cost": independent_unit_costs[alt_id].value, "adjustment_factor": cost_factor.value}, currency=currency, assumption_ids=(f"ASM-SCN-COST-{alt_id}",))
            unit_cost = adjusted_cost
            annual_cost = calculate("CALC-COST-002", {"unit_cost": unit_cost.value, "annual_volume": annual_volume}, currency=currency, assumption_ids=("ASM-SCN-VOL-001",))
            unit_savings = calculate("CALC-COST-003", {"baseline_unit_cost": baseline_unit, "alternative_unit_cost": unit_cost.value}, currency=currency)
            annual_savings = calculate("CALC-COST-004", {"unit_savings": unit_savings.value, "annual_volume": annual_volume}, currency=currency, assumption_ids=("ASM-SCN-VOL-001",))
            cost_variance = calculate("CALC-COST-005", {"baseline_unit_cost": baseline_unit, "alternative_unit_cost": unit_cost.value}, currency=currency)
            component_total = calculate("CALC-MAT-001", {"component_weights_g": components_by_alt[alt_id]})
            adjusted_case = calculate("CALC-SCN-003", {"raw_case_weight_g": record["case_weight_g"], "adjustment_factor": material_factor.value}, assumption_ids=(f"ASM-SCN-MAT-{alt_id}",))
            adjusted_components = [calculate("CALC-SCN-004", {"raw_component_weight_g": value, "adjustment_factor": material_factor.value}, assumption_ids=(f"ASM-SCN-MAT-{alt_id}",)).value for value in components_by_alt[alt_id]]
            adjusted_component_total = calculate("CALC-MAT-001", {"component_weights_g": adjusted_components})
            component_variance = calculate("CALC-MAT-002", {"component_total_g": adjusted_component_total.value, "case_weight_g": adjusted_case.value})
            annual_material = calculate("CALC-MAT-003", {"case_weight_g": adjusted_case.value, "annual_volume": annual_volume}, assumption_ids=("ASM-SCN-VOL-001",))
            material_change = calculate("CALC-MAT-004", {"alternative_weight_g": adjusted_case.value, "baseline_weight_g": baseline_weight})
            material_variance = calculate("CALC-MAT-005", {"alternative_weight_g": adjusted_case.value, "baseline_weight_g": baseline_weight})
            board = calculate("CALC-ADP-001", {"case_weight_g": record["case_weight_g"], "adhesive_ink_weight_g": 25}, assumption_ids=("ASM-SYN-ADH-001",))
            component_reconciliation = calculate("CALC-ADP-002", {"board_weight_g": board.value, "adhesive_ink_weight_g": 25}, assumption_ids=("ASM-SYN-ADH-001",))

            primary_map = {
                "CALC-COST-001": getattr(primary, "unit_cost", None),
                "CALC-COST-002": getattr(primary, "annual_cost", None),
                "CALC-COST-003": None if primary is None else (getattr(scenario_result.alternatives[baseline_id], "unit_cost", 0) - getattr(primary, "unit_cost", 0)),
                "CALC-COST-004": getattr(primary, "annual_savings_vs_baseline", None),
                "CALC-COST-005": None,
                "CALC-MAT-001": None,
                "CALC-MAT-002": None,
                "CALC-MAT-003": getattr(primary, "annual_material_kg", None),
                "CALC-MAT-004": None,
                "CALC-MAT-005": getattr(primary, "material_change_percent_vs_baseline", None),
                "CALC-SCN-001": None,
                "CALC-SCN-002": getattr(primary, "unit_cost", None),
                "CALC-SCN-003": getattr(primary, "case_weight_g", None),
                "CALC-SCN-004": None,
                "CALC-ADP-001": record["case_weight_g"] - 25,
                "CALC-ADP-002": record["case_weight_g"],
            }
            calculations = [
                independent_unit_costs[alt_id], annual_cost, unit_savings, annual_savings, cost_variance,
                component_total, component_variance, annual_material, material_change, material_variance,
                cost_factor, adjusted_cost, adjusted_case,
                calculate("CALC-SCN-004", {"raw_component_weight_g": components_by_alt[alt_id][0], "adjustment_factor": material_factor.value}, assumption_ids=(f"ASM-SCN-MAT-{alt_id}",)),
                board, component_reconciliation,
            ]
            for item in calculations:
                results.append(reconcile(scenario_id=scenario_id, alternative_id=alt_id, independent=item, primary_result=primary_map[item.calculation_id]))

        summary = Counter(item.state for item in results)
        return {
            "registry_version": self.REGISTRY_VERSION,
            "catalogue_count": len(CALCULATION_CATALOGUE),
            "rule_lineage": dict(RULE_LINEAGE),
            "assumptions": dict(ASSUMPTIONS),
            "summary": {state: summary.get(state, 0) for state in ("matched", "matched_within_tolerance", "mismatch", "insufficient_evidence", "unsupported")},
            "results": [item.canonical() for item in results],
            "disclosure": "Independent arithmetic reconciliation over synthetic demonstration data. A match is not supplier, engineering, regulatory, production or realized-savings validation.",
        }
