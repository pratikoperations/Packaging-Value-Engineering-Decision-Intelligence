from __future__ import annotations

import json
import unittest
from pathlib import Path


class P6FinalDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_pilot" / "p6_final_decision.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_phase_closes_at_full_planned_effort(self):
        self.assertEqual(self.data["planned_hours"], 28)
        self.assertEqual(self.data["completed_hours"], 28)
        self.assertEqual(self.data["remaining_hours"], 0)
        self.assertEqual(self.data["synthetic_phase_completion_pct"], 100.0)

    def test_final_decision_is_deferred_not_go(self):
        self.assertEqual(self.data["final_recommendation"], "DECISION DEFERRED")
        self.assertEqual(self.data["enterprise_readiness"], "NOT_APPROVED")
        self.assertEqual(self.data["production_deployment_authorization"], "NOT_GRANTED")
        self.assertEqual(self.data["claim_state"], "ESTIMATE")

    def test_next_scope_requires_real_authority_and_users(self):
        required = set(self.data["next_scope_requires"])
        self.assertIn("named organizational sponsor", required)
        self.assertIn("named packaging engineering reviewer", required)
        self.assertIn("named Finance/value reviewer", required)
        self.assertIn("named UAT participants", required)


if __name__ == "__main__":
    unittest.main()
