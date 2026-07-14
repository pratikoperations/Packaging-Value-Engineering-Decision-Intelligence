from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.category_registry import default_registry


FIXTURE = Path("data/demo/pve_1_1_release_cases.json")
EXPECTED_CATEGORIES = {
    "corrugated", "folding_carton", "rigid_plastic", "flexible_packaging",
    "labels", "closures", "glass", "metal",
}


class PVE11ReleaseQATestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.registry = default_registry()

    def test_release_fixture_is_explicitly_synthetic(self):
        self.assertEqual(self.data["dataset_type"], "synthetic_demo")
        self.assertIn("Synthetic", self.data["notice"])

    def test_exactly_one_sample_exists_for_each_supported_category(self):
        samples = self.data["category_samples"]
        self.assertEqual(len(samples), 8)
        self.assertEqual({item["category"] for item in samples}, EXPECTED_CATEGORIES)
        self.assertEqual(set(self.registry.keys()), EXPECTED_CATEGORIES)

    def test_sample_objective_and_change_type_are_registry_valid(self):
        for sample in self.data["category_samples"]:
            definition = self.registry.get(sample["category"])
            self.assertTrue(definition.supports_objective(sample["objective"]), sample)
            self.assertTrue(definition.supports_change_type(sample["change_type"]), sample)

    def test_three_required_detailed_demonstration_patterns_exist(self):
        cases = self.data["detailed_cases"]
        self.assertEqual(len(cases), 3)
        titles = {case["title"] for case in cases}
        self.assertIn("Commercially attractive and ready for testing", titles)
        self.assertIn("Attractive but blocked by missing technical data", titles)
        self.assertIn("Rejected because critical mandatory data is missing", titles)

    def test_blockers_override_commercial_attractiveness(self):
        blocked = next(case for case in self.data["detailed_cases"] if case["case_id"] == "DEMO-BLOCKED-002")
        self.assertEqual(blocked["commercial_status"], "attractive")
        self.assertTrue(blocked["blockers"])
        self.assertEqual(blocked["readiness_stage"], "Insufficient Data")

    def test_missing_commercial_inputs_make_analysis_unavailable(self):
        rejected = next(case for case in self.data["detailed_cases"] if case["case_id"] == "DEMO-REJECTED-003")
        unavailable = {item["output"]: item["reason"] for item in rejected["unavailable_outputs"]}
        self.assertIn("commercial_analysis", unavailable)
        self.assertIn("Annual volume", unavailable["commercial_analysis"])

    def test_no_demo_claims_autonomous_or_final_technical_approval(self):
        for case in self.data["detailed_cases"]:
            serialized = json.dumps(case).lower()
            self.assertNotIn('"autonomous_approval": true', serialized)
            for item in case["unavailable_outputs"]:
                if item["output"] == "final_technical_feasibility":
                    self.assertIn("Engineering validation", item["reason"])

    def test_every_unavailable_output_has_a_reason(self):
        for case in self.data["detailed_cases"]:
            for item in case["unavailable_outputs"]:
                self.assertTrue(item["output"])
                self.assertTrue(item["reason"])


if __name__ == "__main__":
    unittest.main()
