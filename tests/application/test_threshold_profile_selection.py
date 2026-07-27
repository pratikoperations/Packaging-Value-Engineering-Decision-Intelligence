from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THRESHOLD_PAGE = ROOT / "pages" / "03_Business_Thresholds.py"
SCENARIO_PAGE = ROOT / "pages" / "04_Controlled_Scenarios.py"


def load_selection_helper(path: Path):
    spec = importlib.util.spec_from_file_location(f"selection_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.selected_profile_index


class ThresholdProfileSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            {
                "threshold_profile_id": "default-1",
                "project_id": None,
            },
            {
                "threshold_profile_id": "demo-1",
                "project_id": "project-demo",
            },
            {
                "threshold_profile_id": "other-1",
                "project_id": "project-other",
            },
        ]

    def test_business_thresholds_selects_active_project_profile(self) -> None:
        helper = load_selection_helper(THRESHOLD_PAGE)
        self.assertEqual(helper(self.records, "demo-1", "project-demo"), 1)

    def test_controlled_scenarios_selects_active_project_profile(self) -> None:
        helper = load_selection_helper(SCENARIO_PAGE)
        self.assertEqual(helper(self.records, "demo-1", "project-demo"), 1)

    def test_controlled_default_can_be_selected(self) -> None:
        for path in (THRESHOLD_PAGE, SCENARIO_PAGE):
            helper = load_selection_helper(path)
            self.assertEqual(helper(self.records, "default-1", "project-demo"), 0)

    def test_stale_or_foreign_profile_falls_back_to_first_option(self) -> None:
        for path in (THRESHOLD_PAGE, SCENARIO_PAGE):
            helper = load_selection_helper(path)
            self.assertEqual(helper(self.records, "missing", "project-demo"), 0)
            self.assertEqual(helper(self.records, "other-1", "project-demo"), 0)


if __name__ == "__main__":
    unittest.main()
