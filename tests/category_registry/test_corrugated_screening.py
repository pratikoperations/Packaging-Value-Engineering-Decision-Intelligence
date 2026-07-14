from __future__ import annotations

import unittest

from src.category_registry import screen_corrugated, validate_governed_factor
from src.uploads.normalizer import normalize_user_dataset


EXPECTED = {
    "project_id": "P-1",
    "context": "proposed",
    "specification_version": "SPEC-2",
    "supplier_name": "Supplier A",
    "manufacturing_site": "Site 1",
    "material_structure": "5-ply BC",
    "laboratory_name": "Lab A",
    "sample_or_batch_reference": "BATCH-1",
}


def evidence(method="BCT", value=1200, evidence_id="E-1", **overrides):
    record = {
        **EXPECTED,
        "evidence_id": evidence_id,
        "test_method": method,
        "result_value": value,
        "unit": "N" if method == "BCT" else "kN/m",
        "source_classification": "laboratory_tested",
        "validation_status": "valid",
        "test_date": "2026-07-01",
        "valid_until": "2099-12-31",
    }
    record.update(overrides)
    return record


class CorrugatedScreeningTestCase(unittest.TestCase):
    def test_governed_factor_requires_source_version_applicability_and_validation(self):
        factor = validate_governed_factor({
            "factor_key": "compression_safety_factor", "value": 1.2,
            "source_reference": "ENG-STD-1", "version": "2",
            "applicability": "export cases", "validation_status": "valid",
        })
        self.assertEqual(factor.value, 1.2)
        with self.assertRaises(ValueError):
            validate_governed_factor({"factor_key": "x", "value": 1.1})

    def test_supplied_bct_meets_explicit_requirement(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000},
            evidence=[evidence(value=1100)], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "criteria met")
        self.assertFalse(result.blockers)
        self.assertIn("No BCT", result.limitations[0])

    def test_bct_below_requirement_is_criteria_not_met(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1300, "annual_gross_saving": 999999},
            evidence=[evidence(value=1200)], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "criteria not met")
        self.assertIn("BCT below governed requirement", result.blockers)

    def test_missing_bct_evidence_requires_validation(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000},
            evidence=[], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "validation required")
        self.assertIn("validated BCT evidence missing", result.blockers)

    def test_safety_and_derating_factors_are_applied_only_when_governed(self):
        factors = [
            {"factor_key": "compression_safety_factor", "value": 1.1, "source_reference": "S1", "version": "1", "applicability": "route", "validation_status": "valid"},
            {"factor_key": "environmental_derating_factor", "value": 1.2, "source_reference": "S2", "version": "1", "applicability": "humid", "validation_status": "valid"},
        ]
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000, "humid_condition": True},
            evidence=[evidence(value=1250)], expected_evidence_context=EXPECTED, factors=factors,
        )
        self.assertEqual(result.outcome, "criteria not met")
        self.assertIn("1320 N", result.checks["bct"])

    def test_humidity_context_without_governed_factor_requires_validation(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000, "humidity_percent": 85},
            evidence=[evidence(value=1200)], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "validation required")
        self.assertIn("environmental derating factor required and missing", result.blockers)

    def test_stacking_and_pallet_limits_are_enforced(self):
        result = screen_corrugated(
            requirements={
                "compression_requirement_n": 1000, "stack_layers_required": 5,
                "proposed_stack_layers": 4, "pallet_load_kg": 900,
                "maximum_pallet_weight_kg": 800, "stacking_mode": "static",
            },
            evidence=[evidence()], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "criteria not met")
        self.assertIn("stack-layer requirement not met", result.blockers)
        self.assertIn("maximum pallet weight exceeded", result.blockers)

    def test_warehouse_overhang_and_stretch_wrap_are_blockers(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000}, evidence=[evidence()],
            expected_evidence_context=EXPECTED,
            warehouse={"storage_type": "floor", "pallet_overhang_mm": 10,
                       "stretch_wrap_compression": True, "stretch_wrap_validation_status": "missing"},
        )
        self.assertIn("pallet overhang present", result.blockers)
        self.assertIn("stretch-wrap compression validation missing", result.blockers)

    def test_machine_dimensions_and_sealing_compatibility_are_enforced(self):
        result = screen_corrugated(
            requirements={
                "compression_requirement_n": 1000, "external_length_mm": 600,
                "external_width_mm": 300, "external_height_mm": 250,
                "sealing_method": "hot_melt",
            },
            evidence=[evidence()], expected_evidence_context=EXPECTED,
            packing_line={"maximum_length_mm": 550, "supported_sealing_method": ["tape"]},
        )
        self.assertIn("case length above machine limit", result.blockers)
        self.assertIn("sealing method incompatible", result.blockers)

    def test_speed_squareness_warp_and_line_trial_block(self):
        result = screen_corrugated(
            requirements={
                "compression_requirement_n": 1000, "machine_speed_cases_per_min": 35,
                "squareness_within_tolerance": False, "warp_within_tolerance": False,
                "packing_line_trial_required": True,
            }, evidence=[evidence()], expected_evidence_context=EXPECTED,
            packing_line={"maximum_speed_cases_per_min": 30, "line_trial_status": "not_reviewed"},
        )
        self.assertIn("required machine speed exceeds line capability", result.blockers)
        self.assertIn("squareness within tolerance", result.blockers)
        self.assertIn("warp within tolerance", result.blockers)
        self.assertIn("mandatory packing-line trial incomplete", result.blockers)

    def test_conflicting_evidence_overrides_other_results(self):
        records = [evidence(value=1200, evidence_id="E-1"), evidence(value=1300, evidence_id="E-2")]
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000}, evidence=records,
            expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "evidence conflict")

    def test_wrong_project_evidence_is_not_used(self):
        result = screen_corrugated(
            requirements={"compression_requirement_n": 1000},
            evidence=[evidence(project_id="OTHER")], expected_evidence_context=EXPECTED,
        )
        self.assertEqual(result.outcome, "validation required")
        self.assertIn("wrong project", result.warnings)

    def test_no_requirement_returns_insufficient_data_not_approval(self):
        result = screen_corrugated(requirements={}, evidence=[], expected_evidence_context=EXPECTED)
        self.assertEqual(result.outcome, "insufficient technical data")
        self.assertNotIn(result.outcome, {"Approved", "Rejected", "Conditional"})

    def test_upload_normalization_preserves_build4_collections(self):
        raw = {
            "governed_factors": [{"factor_key": "x", "value": "1.2", "source_reference": "S"}],
            "warehouse_profiles": [{"pallet_overhang_mm": "5"}],
            "packing_line_profiles": [{"maximum_length_mm": "500"}],
        }
        project = {"project_id": "P-1", "project_name": "P", "category": "corrugated", "annual_volume": 1, "currency": "INR"}
        normalized = normalize_user_dataset(raw, project)
        self.assertEqual(normalized["governed_factors"][0]["value"], 1.2)
        self.assertEqual(normalized["warehouse_profiles"][0]["pallet_overhang_mm"], 5)
        self.assertEqual(normalized["packing_line_profiles"][0]["maximum_length_mm"], 500)


if __name__ == "__main__":
    unittest.main()
