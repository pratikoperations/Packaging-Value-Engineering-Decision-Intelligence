from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS_PAGE = ROOT / "pages" / "03_Business_Thresholds.py"
HISTORY_PAGE = ROOT / "pages" / "05_Decision_History.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HumanReadableEvidenceTests(unittest.TestCase):
    def test_public_pages_do_not_render_raw_json(self) -> None:
        for path in (THRESHOLDS_PAGE, HISTORY_PAGE):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("st.json(", source)

    def test_threshold_profile_is_presented_as_business_rows(self) -> None:
        module = load_module(THRESHOLDS_PAGE, "pve_thresholds_human_readable")
        record = {
            "profile": {
                "minimum_annual_savings": 2_500_000,
                "minimum_material_reduction_percent": 5,
                "maximum_business_risk": "high",
                "require_positive_savings_or_material_reduction": True,
            }
        }
        rows = module.profile_summary_rows(record)
        by_name = {row["Business threshold"]: row["Configured value"] for row in rows}
        self.assertEqual(by_name["Minimum annual savings"], "INR 2,500,000")
        self.assertEqual(by_name["Minimum material reduction"], "5.0%")
        self.assertEqual(by_name["Maximum acceptable business risk"], "High")
        self.assertEqual(by_name["Positive savings or material reduction required"], "Yes")

    def test_decision_controls_use_plain_language(self) -> None:
        module = load_module(HISTORY_PAGE, "pve_history_human_readable")
        rows = module.recommendation_control_rows(
            {
                "autonomous_approval": False,
                "engineering_validation_required": True,
                "human_approval_required": True,
                "preferred_alternative_id": None,
            }
        )
        by_name = {row["Decision control"]: row["Result"] for row in rows}
        self.assertEqual(by_name["Autonomous approval"], "Prohibited")
        self.assertEqual(by_name["Engineering validation"], "Required")
        self.assertEqual(by_name["Human approval"], "Required")
        self.assertEqual(by_name["Preferred alternative"], "None")

    def test_nested_evidence_is_flattened_for_table_display(self) -> None:
        module = load_module(HISTORY_PAGE, "pve_history_flattened_evidence")
        rows = module.flatten_evidence(
            {
                "business_thresholds_passed": False,
                "reasons": ["insufficient_data", "engineering_validation_required"],
            }
        )
        values = {row["Evidence item"]: row["Recorded value"] for row in rows}
        self.assertEqual(values["Business Thresholds Passed"], "No")
        self.assertIn("insufficient data", values.values())
        self.assertIn("engineering validation required", values.values())


if __name__ == "__main__":
    unittest.main()
