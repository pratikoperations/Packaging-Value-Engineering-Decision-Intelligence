import unittest

from src.category_registry import (
    AvailableOutput,
    UnavailableOutput,
    board_area_from_supplied_blank,
    compare_simple_pallet_patterns,
    logistics_comparison,
    material_comparison,
    physical_sustainability_indicators,
)
from src.uploads.normalizer import normalize_user_dataset


class CorrugatedAnalysisTestCase(unittest.TestCase):
    def test_board_area_uses_supplied_blank_only(self):
        result = board_area_from_supplied_blank({"blank_length_mm": 1000, "blank_width_mm": 600})
        self.assertIsInstance(result, AvailableOutput)
        self.assertEqual(result.value, 0.6)
        self.assertEqual(result.unit, "m2/case")

    def test_board_area_is_unavailable_without_blank_geometry(self):
        result = board_area_from_supplied_blank({"external_length_mm": 400, "external_width_mm": 300})
        self.assertIsInstance(result, UnavailableOutput)
        self.assertIn("blank_length_mm", result.missing_inputs)
        self.assertIn("not inferred", result.reason)

    def test_material_comparison_calculates_annual_consumption_and_change(self):
        result = material_comparison(
            annual_volume_cases=100000,
            baseline={"case_weight_g": 500, "blank_length_mm": 1000, "blank_width_mm": 600},
            proposed={"case_weight_g": 450, "blank_length_mm": 950, "blank_width_mm": 580},
        )
        self.assertEqual(result["baseline_annual_material"].value, 50000)
        self.assertEqual(result["proposed_annual_material"].value, 45000)
        self.assertEqual(result["annual_material_change"].value, -5000)

    def test_material_benefit_is_blocked_by_technical_risk(self):
        result = material_comparison(
            annual_volume_cases=1000,
            baseline={"case_weight_g": 500},
            proposed={"case_weight_g": 400},
            technical_blockers=("BCT below governed requirement",),
        )
        self.assertEqual(result["annual_material_change"].status, "blocked")
        self.assertIn("cannot be overridden", result["annual_material_change"].limitations[0])

    def test_simple_pallet_patterns_return_both_orientations(self):
        result = compare_simple_pallet_patterns({
            "case_external_length_mm": 400,
            "case_external_width_mm": 300,
            "case_external_height_mm": 250,
            "case_weight_kg": 10,
            "pallet_length_mm": 1200,
            "pallet_width_mm": 1000,
            "pallet_height_limit_mm": 1500,
            "pallet_weight_limit_kg": 1000,
            "empty_pallet_weight_kg": 25,
            "validated_stack_layers": 5,
            "annual_volume_cases": 10000,
        })
        self.assertEqual(len(result), 2)
        self.assertEqual({item.orientation for item in result}, {"length x width", "width x length"})
        self.assertTrue(all(item.cases_per_pallet > 0 for item in result))
        self.assertTrue(all("not global pallet optimisation" in item.limitations[0] for item in result))

    def test_pallet_pattern_respects_height_weight_and_stack_limits(self):
        result = compare_simple_pallet_patterns({
            "case_external_length_mm": 600,
            "case_external_width_mm": 500,
            "case_external_height_mm": 400,
            "case_weight_kg": 50,
            "pallet_length_mm": 1200,
            "pallet_width_mm": 1000,
            "pallet_height_limit_mm": 1300,
            "pallet_weight_limit_kg": 450,
            "empty_pallet_weight_kg": 50,
            "validated_stack_layers": 6,
            "annual_volume_cases": 1000,
        })
        best = max(result, key=lambda item: item.cases_per_pallet)
        self.assertLessEqual(best.layers_per_pallet, 3)
        self.assertLessEqual(best.pallet_height_mm, 1300)
        self.assertLessEqual(best.pallet_gross_weight_kg, 450)

    def test_missing_pallet_input_returns_unavailable(self):
        result = compare_simple_pallet_patterns({"case_external_length_mm": 400})
        self.assertIsInstance(result, UnavailableOutput)
        self.assertIn("pallet_length_mm", result.missing_inputs)

    def test_pallet_result_cannot_override_technical_blockers(self):
        result = compare_simple_pallet_patterns({
            "case_external_length_mm": 400,
            "case_external_width_mm": 300,
            "case_external_height_mm": 250,
            "case_weight_kg": 10,
            "pallet_length_mm": 1200,
            "pallet_width_mm": 1000,
            "pallet_height_limit_mm": 1500,
            "pallet_weight_limit_kg": 1000,
            "empty_pallet_weight_kg": 25,
            "validated_stack_layers": 5,
            "annual_volume_cases": 10000,
        }, technical_blockers=("packing-line incompatibility",))
        self.assertTrue(all(item.status == "blocked" for item in result))

    def test_logistics_comparison_uses_explicit_inputs(self):
        result = logistics_comparison(
            {"annual_pallet_movements": 1000, "annual_freight_cube_m3": 5000},
            {"annual_pallet_movements": 800, "annual_freight_cube_m3": 4500},
        )
        self.assertEqual(result["annual_pallet_movements_change"].value, -200)
        self.assertEqual(result["annual_freight_cube_m3_change"].value, -500)
        self.assertIsInstance(result["warehouse_positions_change"], UnavailableOutput)

    def test_physical_sustainability_indicators(self):
        result = physical_sustainability_indicators(
            annual_volume_cases=100000,
            baseline={"case_weight_g": 500},
            proposed={
                "case_weight_g": 450,
                "product_weight_per_case_kg": 12,
                "recycled_content_percent": 80,
                "virgin_fibre_percent": 20,
            },
            pallet_movements_baseline=1000,
            pallet_movements_proposed=800,
        )
        self.assertEqual(result["annual_paper_consumption"].value, 45000)
        self.assertEqual(result["annual_paper_reduction"].value, 5000)
        self.assertEqual(result["pallets_avoided"].value, 200)
        self.assertEqual(result["transport_movements_avoided"].value, 200)
        self.assertEqual(result["recycled_content_percent"].value, 80)
        self.assertEqual(result["virgin_fibre_percent"].value, 20)

    def test_invalid_fibre_percentages_are_unavailable(self):
        result = physical_sustainability_indicators(
            annual_volume_cases=100,
            baseline={"case_weight_g": 500},
            proposed={"case_weight_g": 450, "recycled_content_percent": 110, "virgin_fibre_percent": 10},
        )
        self.assertIsInstance(result["recycled_content_percent"], UnavailableOutput)

    def test_fibre_total_above_100_is_invalid(self):
        result = physical_sustainability_indicators(
            annual_volume_cases=100,
            baseline={"case_weight_g": 500},
            proposed={"case_weight_g": 450, "recycled_content_percent": 80, "virgin_fibre_percent": 30},
        )
        self.assertIsInstance(result["fibre_content_validation"], UnavailableOutput)
        self.assertIn("more than 100", result["fibre_content_validation"].reason)

    def test_carbon_output_remains_unavailable(self):
        result = physical_sustainability_indicators(
            annual_volume_cases=100,
            baseline={"case_weight_g": 500},
            proposed={"case_weight_g": 450},
            emission_factor_dataset={"source_reference": "EF-1", "version": "1", "validation_status": "valid"},
        )
        self.assertIsInstance(result["carbon_emissions"], UnavailableOutput)
        self.assertIn("outside PVE 1.2 Build 5", result["carbon_emissions"].reason)

    def test_build5_collections_and_numeric_values_are_normalized(self):
        project = {
            "project_id": "P-1", "project_name": "Corrugated", "category": "corrugated",
            "annual_volume": 1000, "currency": "INR",
        }
        raw = {
            "pallet_pattern_inputs": [{"pallet_length_mm": "1200", "annual_volume_cases": "10000"}],
            "physical_sustainability_profiles": [{"recycled_content_percent": "80"}],
        }
        normalized = normalize_user_dataset(raw, project)
        self.assertEqual(normalized["pallet_pattern_inputs"][0]["pallet_length_mm"], 1200)
        self.assertEqual(normalized["pallet_pattern_inputs"][0]["annual_volume_cases"], 10000)
        self.assertEqual(normalized["physical_sustainability_profiles"][0]["recycled_content_percent"], 80)


if __name__ == "__main__":
    unittest.main()
