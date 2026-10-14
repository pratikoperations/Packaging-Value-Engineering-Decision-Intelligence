from __future__ import annotations

import json
import unittest
from pathlib import Path


class R0OrganizationalPilotGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r0_gate.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_r0_accounting(self):
        self.assertEqual(self.data["phase_planned_hours"], 30)
        self.assertEqual(self.data["completed_hours_after_r0"], 3)
        self.assertEqual(self.data["remaining_hours_after_r0"], 27)
        self.assertEqual(self.data["completion_pct_after_r0"], 10.0)

    def test_real_authorities_are_required(self):
        roles = set(self.data["required_named_roles"])
        self.assertIn("Organizational Pilot Sponsor", roles)
        self.assertIn("Packaging Engineer Reviewer", roles)
        self.assertIn("Finance / Value Reviewer", roles)
        self.assertIn("UAT Participant(s)", roles)
        self.assertIn("Do not fabricate organizational authority", self.data["explicit_stop_condition"])

    def test_no_production_authority_is_implied(self):
        self.assertEqual(self.data["production_deployment_authorization"], "NOT_GRANTED")
        self.assertEqual(self.data["enterprise_readiness"], "NOT_APPROVED")


if __name__ == "__main__":
    unittest.main()
