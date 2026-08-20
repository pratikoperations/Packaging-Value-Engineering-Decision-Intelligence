from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace

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


def load_scenario_module():
    spec = importlib.util.spec_from_file_location(f"selection_{SCENARIO_PAGE.stem}", SCENARIO_PAGE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCENARIO_PAGE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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

    def test_demo_dataset_defaults_to_latest_version(self) -> None:
        module = load_scenario_module()
        records = [
            {"dataset_id": "dataset-1"},
            {"dataset_id": "dataset-2"},
            {"dataset_id": "dataset-3"},
        ]
        self.assertEqual(module.selected_dataset_index(records, None, demo_project=True), 2)
        self.assertEqual(module.selected_dataset_index(records, None, demo_project=False), 0)
        self.assertEqual(module.selected_dataset_index(records, "dataset-2", demo_project=True), 1)

    def test_stale_evaluated_scenario_is_cleared_when_selection_changes(self) -> None:
        module = load_scenario_module()
        session_state = {
            module.EVALUATED_SCENARIO_KEY: SimpleNamespace(
                project_id="project-demo",
                dataset_id="dataset-1",
                threshold_profile_id="threshold-1",
            )
        }
        changed = module.clear_stale_evaluated_scenario(
            session_state,
            module.evaluated_selection_key("project-demo", "dataset-2", "threshold-1"),
        )
        self.assertTrue(changed)
        self.assertNotIn(module.EVALUATED_SCENARIO_KEY, session_state)

    def test_matching_selection_preserves_evaluated_scenario(self) -> None:
        module = load_scenario_module()
        evaluated = SimpleNamespace(
            project_id="project-demo",
            dataset_id="dataset-1",
            threshold_profile_id="threshold-1",
        )
        session_state = {module.EVALUATED_SCENARIO_KEY: evaluated}
        changed = module.clear_stale_evaluated_scenario(
            session_state,
            module.evaluated_selection_key("project-demo", "dataset-1", "threshold-1"),
        )
        self.assertFalse(changed)
        self.assertIs(session_state[module.EVALUATED_SCENARIO_KEY], evaluated)

    def test_pending_selection_is_consumed_when_valid(self) -> None:
        module = load_scenario_module()
        options = {"Dataset v1 · demo.json": {"dataset_id": "dataset-1"}}
        session_state = {module.PENDING_DATASET_SELECT_KEY: "Dataset v1 · demo.json"}
        selected = module.consume_pending_record_label(
            options,
            session_state,
            module.DATASET_SELECT_KEY,
            module.PENDING_DATASET_SELECT_KEY,
            "Dataset v1 · demo.json",
        )
        self.assertEqual(selected, "Dataset v1 · demo.json")
        self.assertEqual(session_state[module.DATASET_SELECT_KEY], "Dataset v1 · demo.json")
        self.assertNotIn(module.PENDING_DATASET_SELECT_KEY, session_state)

    def test_invalid_pending_selection_falls_closed_to_default(self) -> None:
        module = load_scenario_module()
        options = {"Dataset v2 · demo.json": {"dataset_id": "dataset-2"}}
        session_state = {module.PENDING_DATASET_SELECT_KEY: "Dataset v1 · stale.json"}
        selected = module.consume_pending_record_label(
            options,
            session_state,
            module.DATASET_SELECT_KEY,
            module.PENDING_DATASET_SELECT_KEY,
            "Dataset v2 · demo.json",
        )
        self.assertEqual(selected, "Dataset v2 · demo.json")
        self.assertEqual(session_state[module.DATASET_SELECT_KEY], "Dataset v2 · demo.json")
        self.assertNotIn(module.PENDING_DATASET_SELECT_KEY, session_state)

    def test_refresh_queues_pending_labels(self) -> None:
        module = load_scenario_module()
        session_state: dict[str, object] = {}
        module.queue_pending_refresh_selection(
            session_state,
            dataset={"version_number": 3, "source_type": "json", "original_filename": "refresh.json"},
            threshold_profile={"profile_name": "Controlled Default", "version_number": 4, "project_id": None},
        )
        self.assertEqual(session_state[module.PENDING_DATASET_SELECT_KEY], "Dataset v3 · refresh.json")
        self.assertEqual(
            session_state[module.PENDING_THRESHOLD_SELECT_KEY],
            "Controlled Default · v4 · Controlled default",
        )


if __name__ == "__main__":
    unittest.main()
