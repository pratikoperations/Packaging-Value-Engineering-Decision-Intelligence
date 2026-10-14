from __future__ import annotations

import json
import unittest
from pathlib import Path


class R7SyntheticOrgClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r7_final_decision.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_simulation_closes_at_full_planned_effort(self):
        self.assertEqual(self.data["phase_planned_hours"], 30)
        self.assertEqual(self.data["phase_completed_hours"], 30)
        self.assertEqual(self.data["phase_completion_pct"], 100.0)
        self.assertEqual(self.data["remaining_hours"], 0)
        self.assertEqual(self.data["synthetic_simulation_conclusion"], "COMPLETE")

    def test_organizational_decision_remains_deferred(self):
        self.assertEqual(self.data["final_recommendation"], "DECISION DEFERRED")
        self.assertFalse(self.data["real_user_validation"])
        self.assertFalse(self.data["organizational_acceptance"])
        self.assertFalse(self.data["independent_engineering_approval"])
        self.assertFalse(self.data["finance_validated_benefit"])

    def test_production_is_not_authorized(self):
        self.assertEqual(self.data["enterprise_readiness"], "NOT_APPROVED")
        self.assertEqual(self.data["production_deployment_authorization"], "NOT_GRANTED")
        self.assertEqual(self.data["claim_state"], "ESTIMATE")


if __name__ == "__main__":
    unittest.main()
