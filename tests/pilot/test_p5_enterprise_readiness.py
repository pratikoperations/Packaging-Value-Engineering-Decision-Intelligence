from __future__ import annotations

import json
import unittest
from pathlib import Path


class P5EnterpriseReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_pilot" / "p5_enterprise_readiness.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_production_is_not_approved(self):
        self.assertEqual(self.data["overall_enterprise_readiness"], "NOT_APPROVED")
        self.assertEqual(self.data["production_deployment_authorization"], "NOT_GRANTED")

    def test_all_18_domains_are_assessed(self):
        self.assertEqual(len(self.data["domains"]), 18)
        self.assertEqual({row["id"] for row in self.data["domains"]}, {f"ER-{i:02d}" for i in range(1, 19)})

    def test_critical_controls_are_not_falsely_passed(self):
        critical = [row for row in self.data["domains"] if row["criticality"] == "CRITICAL"]
        self.assertTrue(critical)
        self.assertTrue(all(row["status"] in {"PENDING", "PARTIAL"} for row in critical))


if __name__ == "__main__":
    unittest.main()
