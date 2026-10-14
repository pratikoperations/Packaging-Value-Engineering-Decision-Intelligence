from __future__ import annotations

import json
import unittest
from pathlib import Path


class P4SyntheticValueSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_pilot" / "p4_synthetic_value_summary.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_claim_state_remains_estimate(self):
        self.assertEqual(self.data["evidence_classification"], "SYNTHETIC-ONLY")
        self.assertEqual(self.data["claim_state"], "ESTIMATE")
        self.assertEqual(self.data["finance_validation"], "NOT_PERFORMED")
        self.assertEqual(self.data["real_user_uat"], "NOT_PERFORMED")

    def test_all_modeled_kpis_are_labelled_modeled_pass(self):
        self.assertTrue(self.data["modeled_kpis"])
        for row in self.data["modeled_kpis"]:
            self.assertEqual(row["modeled_result"], "PASS")
            self.assertGreaterEqual(row["value"], row["target"])

    def test_human_only_measures_are_not_fabricated(self):
        for value in self.data["human_only_measures"].values():
            self.assertIn(value, {"NOT_MEASURED", "NOT_PERFORMED"})


if __name__ == "__main__":
    unittest.main()
