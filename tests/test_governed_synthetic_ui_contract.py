from __future__ import annotations

import unittest
from pathlib import Path

from src.synthetic_data import SYNTHETIC_DISCLOSURE


ROOT = Path(__file__).resolve().parents[1]


class GovernedSyntheticUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = (ROOT / "app.py").read_text(encoding="utf-8")
        cls.guide = (ROOT / "docs" / "INTERVIEW_DEMO_GUIDE.md").read_text(encoding="utf-8")

    def test_application_loads_governed_package_through_adapter(self) -> None:
        self.assertIn("load_governed_package", self.app)
        self.assertIn("build_legacy_dataset", self.app)
        self.assertNotIn("json.loads(DEMO_PATH", self.app)

    def test_application_exposes_three_scenario_registry(self) -> None:
        self.assertIn("Governed synthetic procurement scenario", self.app)
        self.assertIn("governed_package[\"scenarios\"]", self.app)

    def test_disclosure_precedes_results_and_exports(self) -> None:
        self.assertGreaterEqual(self.app.count("st.warning(SYNTHETIC_DISCLOSURE)"), 3)
        self.assertIn('"synthetic_disclosure": SYNTHETIC_DISCLOSURE', self.app)
        self.assertIn('"# Synthetic Data Disclosure\\n\\n"', self.app)

    def test_no_enterprise_integration_or_autonomous_approval_is_added(self) -> None:
        lowered = self.app.lower()
        self.assertNotIn("sap", lowered)
        self.assertNotIn("award supplier", lowered)
        self.assertIn("does not approve packaging designs autonomously", lowered)

    def test_mandatory_disclosure_is_stable(self) -> None:
        self.assertIn("Not sourced from actual suppliers", SYNTHETIC_DISCLOSURE)
        self.assertIn("realized-savings claims", SYNTHETIC_DISCLOSURE)


if __name__ == "__main__":
    unittest.main()
