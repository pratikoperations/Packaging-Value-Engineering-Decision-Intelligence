from __future__ import annotations

import json
import unittest
from pathlib import Path


class R4SyntheticPVEAssistedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[2]
        cls.r4 = json.loads((root / "data" / "pve_real_user_pilot" / "r4_synthetic_pve_assisted.json").read_text())
        cls.source = json.loads((root / "data" / "pve_pilot" / "p3_synthetic_benchmark.json").read_text())

    def test_reuses_governed_pve_assisted_run_exactly(self):
        expected = self.source["pve_assisted"].copy()
        expected.pop("workflow_clarity_rating", None)
        expected.pop("generation_basis", None)
        self.assertEqual(self.r4["pve_assisted"], expected)

    def test_objective_functional_evidence_is_green(self):
        self.assertTrue(all(v == "PASS" for v in self.r4["objective_functional_evidence"].values()))

    def test_no_empirical_claim(self):
        self.assertFalse(self.r4["empirical_evidence_added"])
        self.assertFalse(self.r4["human_observation_added"])
        self.assertEqual(self.r4["claim_state"], "ESTIMATE")

    def test_accounting(self):
        self.assertEqual(self.r4["hours_completed_after_r4"], 20)
        self.assertEqual(self.r4["completion_pct_after_r4"], 66.7)


if __name__ == "__main__":
    unittest.main()
