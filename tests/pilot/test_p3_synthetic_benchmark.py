from __future__ import annotations

import json
import unittest
from pathlib import Path


class P3SyntheticBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / "data" / "pve_pilot" / "p3_synthetic_benchmark.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_benchmark_is_explicitly_non_observed(self):
        self.assertEqual(self.data["evidence_classification"], "SYNTHETIC-ONLY")
        self.assertEqual(
            self.data["evidence_status"],
            "MODELED_BENCHMARK_NOT_OBSERVED_HUMAN_PERFORMANCE",
        )
        self.assertIsNone(self.data["manual_baseline"]["workflow_clarity_rating"])
        self.assertIsNone(self.data["pve_assisted"]["workflow_clarity_rating"])

    def test_modeled_productivity_math_matches_raw_values(self):
        m = self.data["manual_baseline"]
        p = self.data["pve_assisted"]
        expected = {
            "decision_preparation_effort_reduction_pct": (m["hands_on_minutes"] - p["hands_on_minutes"]) / m["hands_on_minutes"] * 100,
            "executive_summary_time_reduction_pct": (m["executive_summary_minutes"] - p["executive_summary_minutes"]) / m["executive_summary_minutes"] * 100,
            "manual_transfer_reduction_pct": (m["manual_transfer_count"] - p["manual_transfer_count"]) / m["manual_transfer_count"] * 100,
            "rework_reduction_pct": (m["calculation_rework_events"] - p["calculation_rework_events"]) / m["calculation_rework_events"] * 100,
        }
        for key, value in expected.items():
            self.assertAlmostEqual(self.data["derived_kpis"][key], value, places=2)

    def test_prohibited_claims_block_real_world_interpretation(self):
        prohibited = set(self.data["prohibited_claims"])
        self.assertIn("pilot-measured productivity improvement", prohibited)
        self.assertIn("realized savings", prohibited)
        self.assertIn("finance-validated benefit", prohibited)
        self.assertIn("real-user UAT acceptance", prohibited)
        self.assertIn("production readiness", prohibited)


if __name__ == "__main__":
    unittest.main()
