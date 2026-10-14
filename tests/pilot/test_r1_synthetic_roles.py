from __future__ import annotations

import json
import unittest
from pathlib import Path


class R1SyntheticRoleSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r1_synthetic_roles.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_mode_is_explicitly_synthetic(self):
        self.assertEqual(self.data["execution_mode"], "SYNTHETIC_ORGANIZATIONAL_PILOT_SIMULATION")
        self.assertEqual(self.data["evidence_type"], "SYNTHETIC-ONLY")
        self.assertTrue(all(r["authority"] == "SIMULATED_ONLY" for r in self.data["roles"]))

    def test_real_world_claims_are_blocked(self):
        blocked = set(self.data["prohibited_claims"])
        self.assertIn("real-user validation", blocked)
        self.assertIn("finance-validated benefit", blocked)
        self.assertIn("production readiness", blocked)
        self.assertIn("deployment authorization", blocked)

    def test_accounting_after_r1(self):
        self.assertEqual(self.data["hours_completed_after_r1"], 6)
        self.assertEqual(self.data["phase_hours"], 30)
        self.assertEqual(self.data["completion_pct_after_r1"], 20.0)


if __name__ == "__main__":
    unittest.main()
