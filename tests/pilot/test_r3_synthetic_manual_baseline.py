from __future__ import annotations

import json
import unittest
from pathlib import Path


class R3SyntheticManualBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.r3 = json.loads((root / "data" / "pve_real_user_pilot" / "r3_synthetic_manual_baseline.json").read_text())
        cls.source = json.loads((root / "data" / "pve_pilot" / "p3_synthetic_benchmark.json").read_text())

    def test_reuses_governed_manual_baseline_exactly(self):
        expected = self.source["manual_baseline"].copy()
        expected.pop("workflow_clarity_rating", None)
        expected.pop("generation_basis", None)
        self.assertEqual(self.r3["manual_baseline"], expected)

    def test_no_empirical_claim(self):
        self.assertFalse(self.r3["empirical_evidence_added"])
        self.assertFalse(self.r3["human_observation_added"])
        self.assertEqual(self.r3["claim_state"], "ESTIMATE")

    def test_accounting(self):
        self.assertEqual(self.r3["hours_completed_after_r3"], 14)
        self.assertEqual(self.r3["completion_pct_after_r3"], 46.7)


if __name__ == "__main__":
    unittest.main()
