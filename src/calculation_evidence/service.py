from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_EVEN
from typing import Any

from src.sourcemate.domain import SourceClassification

from .domain import (
    CalculationEvidence,
    CalculationEvidenceError,
    CalculationInput,
    CalculationStep,
)


class CalculationEvidenceService:
    SCHEMA_VERSION = "calculation-evidence-v1"
    SUPPORTED_RESULTS = {
        "annual_cost",
        "annual_savings_vs_baseline",
        "annual_material_kg",
        "material_change_percent_vs_baseline",
    }

    def build_for_scenario(
        self,
        *,
        project_id: str,
        scenario: dict[str, Any],
        alternative_id: str,
        result_name: str,
        archived: bool = False,
    ) -> CalculationEvidence:
        self._require_scope(project_id, scenario)
        if result_name not in self.SUPPORTED_RESULTS:
            raise CalculationEvidenceError("UNSUPPORTED_RESULT", "This result has no governed Build 3 calculation-evidence contract.")
        assumptions = self._mapping(scenario.get("assumptions_json"), "assumptions")
        results = self._mapping(scenario.get("results_json"), "results")
        alternatives = results.get("alternatives")
        if not isinstance(alternatives, dict) or alternative_id not in alternatives:
            raise CalculationEvidenceError("RECORD_NOT_FOUND", "The requested alternative was not found in the selected scenario.")
        outcome = alternatives[alternative_id]
        if not isinstance(outcome, dict) or result_name not in outcome:
            raise CalculationEvidenceError("MISSING_LINEAGE", "The stored result does not contain the requested governed output.")
        source_hash = str(scenario.get("content_hash") or "").strip()
        if not source_hash:
            raise CalculationEvidenceError("INTEGRITY_FAILURE", "The scenario has no immutable source hash.")

        annual_volume = self._number(assumptions.get("annual_volume"), "annual_volume")
        stored = self._number(outcome[result_name], result_name)
        assumption_inputs = (
            CalculationInput("annual_volume", annual_volume, "cases/year", SourceClassification.ASSUMED, str(scenario["scenario_id"]), "SCENARIO-ANNUAL-VOLUME"),
            CalculationInput("cost_adjustment_percent", self._adjustment(assumptions, "cost_adjustment_percent_by_alternative", alternative_id), "%", SourceClassification.ASSUMED, str(scenario["scenario_id"]), "SCENARIO-COST-ADJUSTMENT"),
            CalculationInput("material_adjustment_percent", self._adjustment(assumptions, "material_adjustment_percent_by_alternative", alternative_id), "%", SourceClassification.ASSUMED, str(scenario["scenario_id"]), "SCENARIO-MATERIAL-ADJUSTMENT"),
        )
        step = self._step(result_name, outcome, annual_volume, stored, str(scenario["scenario_id"]))
        self._reconcile(stored, step.output_value, step.precision)
        gaps = tuple(sorted(str(item) for item in outcome.get("technical_validation_required", ()) if str(item).strip()))
        gaps += tuple(sorted(str(item) for item in outcome.get("risk_validation_required", ()) if str(item).strip()))
        return CalculationEvidence(
            schema_version=self.SCHEMA_VERSION,
            project_id=project_id,
            target_id=str(scenario["scenario_id"]),
            target_type="scenario",
            revision_reference=str(scenario.get("created_at") or scenario["scenario_id"]),
            result_name=result_name,
            result_value=stored,
            result_unit=step.output_unit,
            source_hash=source_hash,
            assumptions=assumption_inputs,
            steps=(step,),
            unit_conversions=("grams / 1000 = kilograms",) if result_name == "annual_material_kg" else (),
            evidence_gaps=tuple(sorted(set(gaps))),
            validation_requirements=tuple(sorted(set(gaps))),
            claim_limitations=(
                "This workspace explains and reconciles a stored deterministic result; it does not run or replace the analytical engine.",
                "Engineering validation and explicit human approval remain mandatory.",
            ),
            archived=archived,
        )

    def canonical_json(self, evidence: CalculationEvidence) -> str:
        return json.dumps(evidence.canonical(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def _step(self, name: str, outcome: dict[str, Any], annual_volume: float, stored: float, source: str) -> CalculationStep:
        observed = lambda n, v, u, r: CalculationInput(n, v, u, SourceClassification.DERIVED, source, r)
        if name == "annual_cost":
            unit_cost = self._number(outcome.get("unit_cost"), "unit_cost")
            value = unit_cost * annual_volume
            inputs = (observed("unit_cost", unit_cost, "currency/case", "COST-UNIT-COST"), observed("annual_volume", annual_volume, "cases/year", "SCENARIO-ANNUAL-VOLUME"))
            return CalculationStep(1, "Annual cost", "COST-ANNUAL-COST", "unit_cost × annual_volume", inputs, value, "currency/year")
        if name == "annual_material_kg":
            case_weight = self._number(outcome.get("case_weight_g"), "case_weight_g")
            value = case_weight * annual_volume / 1000.0
            inputs = (observed("case_weight_g", case_weight, "g/case", "MATERIAL-CASE-WEIGHT"), observed("annual_volume", annual_volume, "cases/year", "SCENARIO-ANNUAL-VOLUME"))
            return CalculationStep(1, "Annual material", "MATERIAL-ANNUAL-KG", "case_weight_g × annual_volume ÷ 1000", inputs, value, "kg/year")
        if name == "annual_savings_vs_baseline":
            annual_cost = self._number(outcome.get("annual_cost"), "annual_cost")
            baseline_cost = annual_cost + stored
            inputs = (observed("baseline_annual_cost", baseline_cost, "currency/year", "COST-BASELINE-ANNUAL-COST"), observed("alternative_annual_cost", annual_cost, "currency/year", "COST-ANNUAL-COST"))
            return CalculationStep(1, "Annual savings versus baseline", "COST-ANNUAL-SAVINGS", "baseline_annual_cost − alternative_annual_cost", inputs, baseline_cost - annual_cost, "currency/year")
        material_change = stored
        current = self._number(outcome.get("annual_material_kg"), "annual_material_kg")
        if material_change == -100:
            raise CalculationEvidenceError("MISSING_LINEAGE", "A -100% material change cannot reconstruct a finite baseline.")
        baseline = current / (1.0 + material_change / 100.0)
        inputs = (observed("alternative_annual_material_kg", current, "kg/year", "MATERIAL-ANNUAL-KG"), observed("baseline_annual_material_kg", baseline, "kg/year", "MATERIAL-BASELINE-ANNUAL-KG"))
        value = ((current - baseline) / baseline) * 100.0
        return CalculationStep(1, "Material change versus baseline", "MATERIAL-CHANGE-PERCENT", "((alternative − baseline) ÷ baseline) × 100", inputs, value, "%")

    @staticmethod
    def _mapping(value: Any, label: str) -> dict[str, Any]:
        try:
            parsed = value if isinstance(value, dict) else json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise CalculationEvidenceError("MISSING_LINEAGE", f"The stored {label} payload is unavailable or invalid.") from exc
        if not isinstance(parsed, dict):
            raise CalculationEvidenceError("MISSING_LINEAGE", f"The stored {label} payload is not an object.")
        return parsed

    @staticmethod
    def _number(value: Any, label: str) -> float:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise CalculationEvidenceError("MISSING_INPUT", f"{label} is missing or non-numeric.")
        return float(value)

    @staticmethod
    def _adjustment(assumptions: dict[str, Any], key: str, alternative_id: str) -> float:
        values = assumptions.get(key, {})
        if not isinstance(values, dict) or alternative_id not in values:
            raise CalculationEvidenceError("MISSING_INPUT", f"{key} is missing for the selected alternative.")
        return CalculationEvidenceService._number(values[alternative_id], key)

    @staticmethod
    def _require_scope(project_id: str, scenario: dict[str, Any]) -> None:
        if not project_id or scenario.get("project_id") != project_id:
            raise CalculationEvidenceError("PROJECT_SCOPE_VIOLATION", "The selected scenario does not belong to the selected project.")

    @staticmethod
    def _reconcile(stored: float, reconstructed: float, precision: int) -> None:
        quantum = Decimal("1").scaleb(-precision)
        left = Decimal(str(stored)).quantize(quantum, rounding=ROUND_HALF_EVEN)
        right = Decimal(str(reconstructed)).quantize(quantum, rounding=ROUND_HALF_EVEN)
        if left != right:
            raise CalculationEvidenceError("RECONCILIATION_FAILURE", f"Stored result {left} does not reconcile with governed lineage {right}.")
