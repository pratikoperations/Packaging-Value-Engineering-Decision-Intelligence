from datetime import date
import unittest

from src.category_registry import (
    assess_evidence_confidence,
    assess_supplier_capability,
    detect_conflicting_evidence,
    match_evidence,
    technical_requirement_profile,
)
from src.templates.excel_generator import generate_workbook
from src.uploads.normalizer import normalize_user_dataset


class CorrugatedEvidenceTestCase(unittest.TestCase):
    def setUp(self):
        self.expected = {
            "project_id": "P-1", "context": "proposed", "specification_version": "SPEC-2",
            "supplier_name": "Supplier A", "manufacturing_site": "Plant 1",
            "material_structure": "K150/SC120/K150", "test_method": "BCT",
            "laboratory_name": "Lab A", "sample_or_batch_reference": "B-1",
        }
        self.evidence = {
            "evidence_id": "E-1", **self.expected, "source_classification": "laboratory_tested",
            "test_date": "2026-01-01", "valid_until": "2027-01-01",
            "validation_status": "valid", "result_value": 4500, "unit": "N",
        }

    def test_requirement_profile_is_whitelisted_and_does_not_infer_thresholds(self):
        profile = technical_requirement_profile({"product_fragility": "high", "compression_requirement_n": 4000, "hidden": 9})
        self.assertEqual(profile["compression_requirement_n"], 4000)
        self.assertNotIn("hidden", profile)
        self.assertIsNone(profile["maximum_pallet_height_mm"])

    def test_evidence_matches_full_context(self):
        result = match_evidence(self.evidence, self.expected, as_of=date(2026, 7, 14))
        self.assertEqual(result.status, "matched")
        self.assertEqual(result.reasons, ())

    def test_wrong_project_spec_supplier_and_site_are_detected(self):
        changed = dict(self.evidence, project_id="P-2", specification_version="SPEC-1", supplier_name="Supplier B", manufacturing_site="Plant 2")
        reasons = set(match_evidence(changed, self.expected, as_of=date(2026, 7, 14)).reasons)
        self.assertTrue({"wrong project", "wrong specification", "wrong supplier", "wrong manufacturing site"} <= reasons)

    def test_expired_and_superseded_evidence_is_rejected(self):
        changed = dict(self.evidence, valid_until="2026-01-01", superseded_by="E-2")
        reasons = set(match_evidence(changed, self.expected, as_of=date(2026, 7, 14)).reasons)
        self.assertIn("expired evidence", reasons)
        self.assertIn("superseded evidence", reasons)

    def test_invalid_source_classification_is_detected(self):
        changed = dict(self.evidence, source_classification="verified")
        self.assertIn("invalid source classification", match_evidence(changed, self.expected).reasons)

    def test_conflicting_evidence_is_detected(self):
        other = dict(self.evidence, evidence_id="E-2", result_value=3900)
        conflicts = detect_conflicting_evidence((self.evidence, other))
        self.assertEqual(conflicts, (("E-1", "E-2"),))

    def test_supplier_capability_outcomes_are_not_rankings(self):
        required = {"supported_flutes": ("BC",), "maximum_ply": 5, "die_cutting_available": True}
        compatible = assess_supplier_capability(required, {"supported_flutes": ("BC", "B"), "maximum_ply": 7, "die_cutting_available": True})
        self.assertEqual(compatible.outcome, "compatible")
        incompatible = assess_supplier_capability(required, {"supported_flutes": ("B",), "maximum_ply": 3, "die_cutting_available": False})
        self.assertEqual(incompatible.outcome, "incompatible")
        self.assertIn("supported_flutes", incompatible.incompatibilities)
        missing = assess_supplier_capability(required, {})
        self.assertEqual(missing.outcome, "evidence missing")

    def test_confidence_describes_evidence_quality(self):
        second = dict(self.evidence, evidence_id="E-2", test_method="ECT", result_value=8.2, unit="kN/m")
        high = assess_evidence_confidence((self.evidence, second))
        self.assertEqual(high.classification, "High evidence confidence")
        assumed = dict(self.evidence, evidence_id="E-3", source_classification="assumption", validation_status="valid")
        moderate = assess_evidence_confidence((self.evidence, assumed))
        self.assertEqual(moderate.classification, "Moderate evidence confidence")
        self.assertIn("Predicted values or assumptions reduce evidence confidence.", moderate.reasons)
        self.assertNotIn("probability", " ".join(moderate.reasons).lower())
        self.assertEqual(assess_evidence_confidence(()).classification, "Not assessable")

    def test_normalizer_retains_source_traceability_and_numeric_values(self):
        project = {"project_id": "P-1", "project_name": "Box", "category": "corrugated", "annual_volume": 100, "currency": "INR"}
        raw = {
            "corrugated_evidence": [dict(self.evidence, result_value="4500")],
            "supplier_capabilities": [{"supplier_name": " Supplier A ", "maximum_ply": "7", "source_classification": "uploaded_fact"}],
            "technical_requirements": [{"compression_requirement_n": "4000", "source_classification": "manually_entered_fact"}],
        }
        normalized = normalize_user_dataset(raw, project)
        self.assertEqual(normalized["corrugated_evidence"][0]["result_value"], 4500)
        self.assertEqual(normalized["corrugated_evidence"][0]["source_classification"], "laboratory_tested")
        self.assertEqual(normalized["supplier_capabilities"][0]["maximum_ply"], 7)
        self.assertEqual(normalized["supplier_capabilities"][0]["supplier_name"], "Supplier A")
        self.assertEqual(normalized["technical_requirements"][0]["compression_requirement_n"], 4000)

    def test_existing_excel_generation_remains_compatible(self):
        workbook_bytes = generate_workbook("corrugated", "Cost reduction", "GSM reduction")
        self.assertGreater(len(workbook_bytes), 1000)


if __name__ == "__main__":
    unittest.main()
