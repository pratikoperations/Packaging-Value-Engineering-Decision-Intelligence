from __future__ import annotations

import json
import unittest
from decimal import Decimal
from pathlib import Path

from src.calculation_evidence import (
    ASSUMPTIONS,
    CALCULATION_CATALOGUE,
    RULE_LINEAGE,
    IndependentCalculationEvidenceService,
    calculate,
    reconcile,
)
from src.exports import attach_calculation_evidence, render_calculation_evidence_markdown
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import build_legacy_dataset, load_governed_package

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


class CatalogueAndFixtureTests(unittest.TestCase):
    def test_exact_numeric_formula_count(self) -> None:
        self.assertEqual(16, len(CALCULATION_CATALOGUE))

    def test_exact_rule_lineage_count(self) -> None:
        self.assertEqual(6, len(RULE_LINEAGE))

    def test_required_assumptions_exist(self) -> None:
        self.assertIn("ASM-SYN-ADH-001", ASSUMPTIONS)
        self.assertIn("ASM-SYN-FRT-001", ASSUMPTIONS)
        self.assertEqual("25", ASSUMPTIONS["ASM-SYN-ADH-001"]["value"])
        self.assertEqual("650", ASSUMPTIONS["ASM-SYN-FRT-001"]["value"])

    def test_formula_registry_matches_python_catalogue(self) -> None:
        registry = json.loads((ROOT / "data/calculation_evidence/formula_registry.json").read_text(encoding="utf-8"))
        self.assertEqual(set(CALCULATION_CATALOGUE), {item["calculation_id"] for item in registry["formulas"]})
        self.assertEqual("ROUND_HALF_EVEN", registry["rounding_mode"])
        self.assertEqual(["INR"], registry["currency_scope"])

    def test_independently_owned_numeric_fixtures(self) -> None:
        fixtures = json.loads((FIXTURES / "numeric_cases.json").read_text(encoding="utf-8"))
        for group in fixtures.values():
            for case in group:
                result = calculate(case["calculation_id"], case["inputs"], currency=case.get("currency"))
                self.assertEqual("calculated", result.status, case["case_id"])
                self.assertEqual(case["expected"], format(result.value, "f"), case["case_id"])


class DecimalPolicyTests(unittest.TestCase):
    def test_decimal_avoids_binary_float_sum_artifact(self) -> None:
        result = calculate("CALC-COST-001", {"cost_inputs": [0.1, 0.2]}, currency="INR")
        self.assertEqual(Decimal("0.300000"), result.value)

    def test_half_even_quantization(self) -> None:
        result = calculate("CALC-COST-002", {"unit_cost": "1.005", "annual_volume": "1"}, currency="INR")
        self.assertEqual(Decimal("1.00"), result.value)

    def test_unsupported_currency(self) -> None:
        result = calculate("CALC-COST-002", {"unit_cost": "1", "annual_volume": "1"}, currency="USD")
        self.assertEqual("unsupported", result.status)
        self.assertEqual("UNSUPPORTED_CURRENCY", result.issue_code)

    def test_zero_denominator_is_unsupported(self) -> None:
        result = calculate("CALC-COST-005", {"baseline_unit_cost": "0", "alternative_unit_cost": "1"}, currency="INR")
        self.assertEqual("unsupported", result.status)
        self.assertEqual("ZERO_DENOMINATOR", result.issue_code)

    def test_negative_cost_is_rejected(self) -> None:
        result = calculate("CALC-COST-001", {"cost_inputs": ["1", "-0.1"]}, currency="INR")
        self.assertEqual("insufficient_evidence", result.status)
        self.assertEqual("INVALID_SIGN", result.issue_code)

    def test_missing_input_is_insufficient(self) -> None:
        result = calculate("CALC-MAT-003", {"case_weight_g": "100"})
        self.assertEqual("insufficient_evidence", result.status)
        self.assertEqual("MISSING_INPUT", result.issue_code)

    def test_adjustment_below_range_is_rejected(self) -> None:
        result = calculate("CALC-SCN-001", {"adjustment_percent": "-51"})
        self.assertEqual("insufficient_evidence", result.status)
        self.assertEqual("OUT_OF_RANGE", result.issue_code)

    def test_adjustment_above_range_is_rejected(self) -> None:
        result = calculate("CALC-SCN-001", {"adjustment_percent": "101"})
        self.assertEqual("insufficient_evidence", result.status)

    def test_negative_savings_are_supported(self) -> None:
        result = calculate("CALC-COST-003", {"baseline_unit_cost": "10", "alternative_unit_cost": "12"}, currency="INR")
        self.assertEqual(Decimal("-2.000000"), result.value)

    def test_material_reduction_is_supported(self) -> None:
        result = calculate("CALC-MAT-004", {"alternative_weight_g": "900", "baseline_weight_g": "1000"})
        self.assertEqual(Decimal("-100.000000"), result.value)

    def test_adapter_board_assumption(self) -> None:
        result = calculate("CALC-ADP-001", {"case_weight_g": "980", "adhesive_ink_weight_g": "25"}, assumption_ids=("ASM-SYN-ADH-001",))
        self.assertEqual(Decimal("955.000000"), result.value)
        self.assertEqual(("ASM-SYN-ADH-001",), result.assumption_ids)

    def test_adapter_negative_board_weight_rejected(self) -> None:
        result = calculate("CALC-ADP-001", {"case_weight_g": "20", "adhesive_ink_weight_g": "25"})
        self.assertEqual("insufficient_evidence", result.status)


class ReconciliationAndMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.independent = calculate("CALC-COST-001", {"cost_inputs": ["100"]}, currency="INR")

    def test_exact_match(self) -> None:
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=self.independent, primary_result="100.000000")
        self.assertEqual("matched", result.state)

    def test_match_within_tolerance(self) -> None:
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=self.independent, primary_result="100.0000005")
        self.assertEqual("matched_within_tolerance", result.state)

    def test_mismatch(self) -> None:
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=self.independent, primary_result="100.01")
        self.assertEqual("mismatch", result.state)

    def test_missing_primary_is_insufficient(self) -> None:
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=self.independent, primary_result=None)
        self.assertEqual("insufficient_evidence", result.state)

    def test_unsupported_calculation_state(self) -> None:
        independent = calculate("CALC-UNKNOWN", {})
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="1")
        self.assertEqual("unsupported", result.state)

    def test_mutated_annual_cost_is_detected(self) -> None:
        independent = calculate("CALC-COST-002", {"unit_cost": "10", "annual_volume": "100"}, currency="INR")
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="10000")
        self.assertEqual("mismatch", result.state)

    def test_mutated_savings_sign_is_detected(self) -> None:
        independent = calculate("CALC-COST-004", {"unit_savings": "2", "annual_volume": "100"}, currency="INR")
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="-200")
        self.assertEqual("mismatch", result.state)

    def test_mutated_percentage_without_times_100_is_detected(self) -> None:
        independent = calculate("CALC-COST-005", {"baseline_unit_cost": "100", "alternative_unit_cost": "90"}, currency="INR")
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="-0.1")
        self.assertEqual("mismatch", result.state)

    def test_mutated_material_conversion_is_detected(self) -> None:
        independent = calculate("CALC-MAT-003", {"case_weight_g": "1000", "annual_volume": "100"})
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="1000")
        self.assertEqual("mismatch", result.state)

    def test_mutated_adjustment_factor_is_detected(self) -> None:
        independent = calculate("CALC-SCN-001", {"adjustment_percent": "10"})
        result = reconcile(scenario_id="SCN", alternative_id="ALT", independent=independent, primary_result="0.1")
        self.assertEqual("mismatch", result.state)


class IndependenceBoundaryTests(unittest.TestCase):
    def test_independent_modules_do_not_import_primary_engines(self) -> None:
        prohibited = (
            "src.cost_engine",
            "src.material_engine",
            "src.scenario_engine",
            "src.recommendation",
            "src.risk_engine",
            "src.technical_qualification",
        )
        for filename in ("catalogue.py", "formulas.py", "models.py", "reconciliation.py", "independent_service.py"):
            source = (ROOT / "src/calculation_evidence" / filename).read_text(encoding="utf-8")
            for import_name in prohibited:
                self.assertNotIn(import_name, source, f"{filename} imports {import_name}")

    def test_no_eval_or_exec(self) -> None:
        source = "\n".join(
            (ROOT / "src/calculation_evidence" / filename).read_text(encoding="utf-8")
            for filename in ("catalogue.py", "formulas.py", "models.py", "reconciliation.py", "independent_service.py")
        )
        self.assertNotIn("eval(", source)
        self.assertNotIn("exec(", source)

    def test_primary_engines_are_not_modified_by_gate_two(self) -> None:
        service_source = (ROOT / "src/calculation_evidence/independent_service.py").read_text(encoding="utf-8")
        self.assertIn("raw_unit_costs", service_source)
        self.assertNotIn("analyze_costs", service_source)
        self.assertNotIn("analyze_materials", service_source)
        self.assertNotIn("evaluate_scenario", service_source)


class IntegrationAndExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        package = load_governed_package(ROOT / "data/demo/governed_synthetic")
        cls.scenario_id = package["scenarios"][0]["scenario_id"]
        cls.dataset = build_legacy_dataset(package, cls.scenario_id)
        ids = [item["alternative_id"] for item in cls.dataset["packaging_alternatives"]]
        zero = {item: 0.0 for item in ids}
        cls.scenario = evaluate_scenario(
            cls.dataset,
            ScenarioInputs(
                annual_volume=float(cls.dataset["packaging_project"]["annual_volume"]),
                cost_adjustment_percent_by_alternative=zero,
                material_adjustment_percent_by_alternative=zero,
            ),
        )
        cls.evidence = IndependentCalculationEvidenceService().evaluate(
            dataset=cls.dataset,
            scenario_id=cls.scenario_id,
            scenario_result=cls.scenario,
            cost_adjustments=zero,
            material_adjustments=zero,
        )

    def test_service_outputs_all_16_formula_ids_per_alternative(self) -> None:
        alternatives = len(self.dataset["packaging_alternatives"])
        self.assertEqual(16 * alternatives, len(self.evidence["results"]))
        self.assertEqual(set(CALCULATION_CATALOGUE), {item["calculation_id"] for item in self.evidence["results"]})

    def test_exposed_primary_results_have_no_mismatch(self) -> None:
        self.assertEqual(0, self.evidence["summary"]["mismatch"])
        self.assertGreater(self.evidence["summary"]["matched"] + self.evidence["summary"]["matched_within_tolerance"], 0)

    def test_missing_primary_intermediates_are_explicit(self) -> None:
        self.assertGreater(self.evidence["summary"]["insufficient_evidence"], 0)

    def test_rule_lineage_is_separate(self) -> None:
        self.assertEqual(6, len(self.evidence["rule_lineage"]))
        self.assertNotIn("RULE-RISK-001", {item["calculation_id"] for item in self.evidence["results"]})

    def test_json_attachment_preserves_primary_package(self) -> None:
        package = {"metadata": {"source": "primary"}}
        attached = attach_calculation_evidence(package, self.evidence)
        self.assertEqual("primary", attached["metadata"]["source"])
        self.assertEqual("1.0.0", attached["calculation_evidence"]["registry_version"])
        self.assertIn("results", attached["calculation_evidence"])

    def test_markdown_contains_disclosure_and_states(self) -> None:
        markdown = render_calculation_evidence_markdown(self.evidence)
        self.assertIn("## Independent Calculation Evidence", markdown)
        self.assertIn("not supplier, engineering, regulatory, production or realized-savings validation", markdown)
        self.assertIn("Matched:", markdown)
        self.assertIn("Rule Lineage", markdown)

    def test_ui_route_contains_independent_reconciliation(self) -> None:
        page = (ROOT / "pages/28_calculation_evidence.py").read_text(encoding="utf-8")
        ui = (ROOT / "src/ui/calculation_evidence_ui.py").read_text(encoding="utf-8")
        self.assertIn("render_independent_reconciliation", page)
        self.assertIn("Independent Decimal Reconciliation", ui)
        self.assertIn("Reconciliation state", ui)

    def test_app_exports_calculation_evidence(self) -> None:
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("IndependentCalculationEvidenceService", source)
        self.assertIn("attach_calculation_evidence(package, calculation_evidence)", source)
        self.assertIn("render_calculation_evidence_markdown(calculation_evidence)", source)


if __name__ == "__main__":
    unittest.main()
