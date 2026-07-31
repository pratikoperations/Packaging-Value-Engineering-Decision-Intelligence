from __future__ import annotations

import json
import unittest

from src.calculation_evidence.domain import CalculationEvidenceError
from src.calculation_evidence.service import CalculationEvidenceService


class CalculationEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = CalculationEvidenceService()
        self.scenario = {
            "scenario_id": "scenario-1",
            "project_id": "project-1",
            "created_at": "2026-08-01T00:00:00Z",
            "content_hash": "abc123",
            "assumptions_json": json.dumps({
                "annual_volume": 1000,
                "cost_adjustment_percent_by_alternative": {"ALT-A": 0.0},
                "material_adjustment_percent_by_alternative": {"ALT-A": 0.0},
            }),
            "results_json": json.dumps({
                "alternatives": {
                    "ALT-A": {
                        "unit_cost": 48.8,
                        "annual_cost": 48800.0,
                        "annual_savings_vs_baseline": 3600.0,
                        "case_weight_g": 880.0,
                        "annual_material_kg": 880.0,
                        "material_change_percent_vs_baseline": -10.204081632653061,
                        "technical_validation_required": ["Compression test"],
                        "risk_validation_required": [],
                    }
                }
            }),
        }

    def build(self, result_name: str):
        return self.service.build_for_scenario(
            project_id="project-1",
            scenario=self.scenario,
            alternative_id="ALT-A",
            result_name=result_name,
        )

    def test_supported_results_are_fixed(self):
        self.assertEqual(4, len(self.service.SUPPORTED_RESULTS))

    def test_annual_cost_reconciles(self):
        evidence = self.build("annual_cost")
        self.assertEqual(48800.0, evidence.result_value)
        self.assertEqual("unit_cost × annual_volume", evidence.steps[0].formula_expression)

    def test_annual_material_reconciles_with_conversion(self):
        evidence = self.build("annual_material_kg")
        self.assertEqual(880.0, evidence.result_value)
        self.assertIn("grams / 1000 = kilograms", evidence.unit_conversions)

    def test_savings_reconciles(self):
        evidence = self.build("annual_savings_vs_baseline")
        self.assertEqual(3600.0, evidence.steps[0].output_value)

    def test_material_change_reconciles(self):
        evidence = self.build("material_change_percent_vs_baseline")
        self.assertAlmostEqual(-10.204081632653061, evidence.steps[0].output_value)

    def test_assumptions_are_classified(self):
        evidence = self.build("annual_cost")
        self.assertTrue(all(item.classification.value == "ASSUMED" for item in evidence.assumptions))

    def test_validation_requirements_are_preserved(self):
        evidence = self.build("annual_cost")
        self.assertEqual(("Compression test",), evidence.validation_requirements)

    def test_canonical_json_is_repeatable_and_has_no_timestamp(self):
        evidence = self.build("annual_cost")
        first = self.service.canonical_json(evidence)
        second = self.service.canonical_json(evidence)
        self.assertEqual(first, second)
        self.assertNotIn("timestamp", first)

    def test_project_scope_violation_fails_closed(self):
        with self.assertRaises(CalculationEvidenceError) as caught:
            self.service.build_for_scenario(
                project_id="other",
                scenario=self.scenario,
                alternative_id="ALT-A",
                result_name="annual_cost",
            )
        self.assertEqual("PROJECT_SCOPE_VIOLATION", caught.exception.code)

    def test_missing_hash_fails_closed(self):
        scenario = dict(self.scenario, content_hash="")
        with self.assertRaises(CalculationEvidenceError) as caught:
            self.service.build_for_scenario(
                project_id="project-1",
                scenario=scenario,
                alternative_id="ALT-A",
                result_name="annual_cost",
            )
        self.assertEqual("INTEGRITY_FAILURE", caught.exception.code)

    def test_missing_input_fails_closed(self):
        scenario = dict(self.scenario, assumptions_json="{}")
        with self.assertRaises(CalculationEvidenceError):
            self.service.build_for_scenario(
                project_id="project-1",
                scenario=scenario,
                alternative_id="ALT-A",
                result_name="annual_cost",
            )

    def test_reconciliation_failure_fails_closed(self):
        payload = json.loads(self.scenario["results_json"])
        payload["alternatives"]["ALT-A"]["annual_cost"] = 49000.0
        scenario = dict(self.scenario, results_json=json.dumps(payload))
        with self.assertRaises(CalculationEvidenceError) as caught:
            self.service.build_for_scenario(
                project_id="project-1",
                scenario=scenario,
                alternative_id="ALT-A",
                result_name="annual_cost",
            )
        self.assertEqual("RECONCILIATION_FAILURE", caught.exception.code)

    def test_service_has_no_mutation_or_execution_api(self):
        prohibited = {"create", "update", "delete", "approve", "execute", "rank", "award", "recalculate"}
        self.assertTrue(prohibited.isdisjoint(set(dir(self.service))))


if __name__ == "__main__":
    unittest.main()
