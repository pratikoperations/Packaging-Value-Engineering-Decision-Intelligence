from __future__ import annotations

import json
import unittest
from pathlib import Path


class R5SyntheticCrossFunctionalReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r5_synthetic_cross_functional_review.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_all_review_authorities_are_simulated(self):
        self.assertTrue(self.data["simulated_reviews"])
        self.assertTrue(all(r["authority"] == "SIMULATED_ONLY" for r in self.data["simulated_reviews"]))

    def test_no_real_approval_is_claimed(self):
        self.assertFalse(self.data["real_approvals_performed"])
        self.assertFalse(self.data["finance_validation_performed"])
        self.assertFalse(self.data["engineering_approval_performed"])
        self.assertFalse(self.data["real_user_uat_performed"])
        self.assertEqual(self.data["claim_state"], "ESTIMATE")

    def test_no_open_critical_or_major_defects(self):
        self.assertEqual(self.data["defects"]["open_s1"], 0)
        self.assertEqual(self.data["defects"]["open_s2"], 0)

    def test_accounting(self):
        self.assertEqual(self.data["hours_completed_after_r5"], 25)
        self.assertEqual(self.data["completion_pct_after_r5"], 83.3)


if __name__ == "__main__":
    unittest.main()
