from __future__ import annotations

import json
import unittest
from pathlib import Path


class R6SyntheticValueReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r6_synthetic_value_readiness.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_value_claim_remains_estimate(self):
        self.assertEqual(self.data["claim_state"], "ESTIMATE")
        self.assertFalse(self.data["finance_validated"])
        self.assertFalse(self.data["realized_value"])
        self.assertFalse(self.data["real_user_validation"])
        self.assertFalse(self.data["organizational_acceptance"])

    def test_enterprise_readiness_remains_unapproved(self):
        self.assertEqual(self.data["enterprise_readiness"], "NOT_APPROVED")
        self.assertEqual(self.data["production_deployment_authorization"], "NOT_GRANTED")
        self.assertTrue(all(v in {"PENDING", "PARTIAL"} for v in self.data["enterprise_controls"].values()))

    def test_accounting(self):
        self.assertEqual(self.data["hours_completed_after_r6"], 28)
        self.assertEqual(self.data["completion_pct_after_r6"], 93.3)


if __name__ == "__main__":
    unittest.main()
