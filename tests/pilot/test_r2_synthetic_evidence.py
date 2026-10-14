from __future__ import annotations

import json
import unittest
from pathlib import Path


class R2SyntheticEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p = Path(__file__).resolve().parents[2] / "data" / "pve_real_user_pilot" / "r2_synthetic_evidence.json"
        cls.data = json.loads(p.read_text(encoding="utf-8"))

    def test_environment_is_simulation_only(self):
        self.assertEqual(self.data["environment"], "CANONICAL_STREAMLIT_PORTFOLIO_SIMULATION_ONLY")
        self.assertFalse(self.data["confidential_data_allowed"])
        self.assertFalse(self.data["production_data_allowed"])
        self.assertFalse(self.data["live_integrations_allowed"])

    def test_all_evidence_is_synthetic_or_modeled(self):
        for item in self.data["evidence"]:
            self.assertTrue(item["classification"].startswith("SYNTHETIC"))

    def test_simulated_data_owner_has_no_real_authority(self):
        self.assertEqual(self.data["simulated_data_owner_authority"], "SYNTHETIC_ONLY")

    def test_accounting(self):
        self.assertEqual(self.data["hours_completed_after_r2"], 10)
        self.assertEqual(self.data["phase_hours"], 30)


if __name__ == "__main__":
    unittest.main()
