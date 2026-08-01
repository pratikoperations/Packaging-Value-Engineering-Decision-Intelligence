from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.browser_acceptance.contracts import (
    ACCEPTANCE_REPORT_KEYS,
    APP_ROOT_SELECTOR,
    PAGE_CONTRACTS,
    SIDEBAR_GROUPS,
    VIEWPORTS,
)
from src.browser_acceptance.diagnostics import (
    material_console_errors,
    visible_exception_markers,
)
from src.browser_acceptance.export_validation import (
    validate_json_download,
    validate_markdown_download,
)
from src.browser_acceptance.process_manager import allocate_port


class MinimalBrowserContractTests(unittest.TestCase):
    def test_exactly_thirteen_registered_routes(self):
        self.assertEqual(13, len(PAGE_CONTRACTS))
        self.assertEqual(13, len({item[0] for item in PAGE_CONTRACTS}))

    def test_exactly_four_sidebar_groups(self):
        self.assertEqual(4, len(SIDEBAR_GROUPS))
        grouped = [title for titles in SIDEBAR_GROUPS.values() for title in titles]
        self.assertEqual(10, len(grouped))
        self.assertEqual(10, len(set(grouped)))

    def test_governed_viewports(self):
        self.assertEqual({"width": 1440, "height": 1000}, VIEWPORTS["desktop"])
        self.assertEqual({"width": 412, "height": 915}, VIEWPORTS["narrow"])

    def test_stable_streamlit_root_selector(self):
        self.assertEqual('[data-testid="stAppViewContainer"]', APP_ROOT_SELECTOR)

    def test_acceptance_report_schema_contains_required_fields(self):
        self.assertEqual(len(ACCEPTANCE_REPORT_KEYS), len(set(ACCEPTANCE_REPORT_KEYS)))
        self.assertIn("overall_disposition", ACCEPTANCE_REPORT_KEYS)
        self.assertIn("source_commit", ACCEPTANCE_REPORT_KEYS)
        self.assertIn("unique_route_count", ACCEPTANCE_REPORT_KEYS)

    def test_json_validator_accepts_governed_export(self):
        payload = {
            "metadata": {"synthetic_disclosure": "Synthetic demonstration data only."},
            "executive_summary": {},
            "project": {},
            "scenario": {},
            "baseline": {},
            "alternatives": [],
            "decision_controls": {
                "autonomous_technical_approval": False,
                "engineering_validation_required": True,
            },
            "calculation_evidence": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(payload, validate_json_download(path))

    def test_json_validator_rejects_missing_governance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_json_download(path)

    def test_markdown_validator_accepts_required_limitations(self):
        text = (
            "# Synthetic Data Disclosure\n"
            "# Packaging Value Engineering Decision Package\n"
            "## Independent Calculation Evidence\n"
            "Engineering validation remains mandatory.\n"
            "No realized savings are claimed.\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(text, validate_markdown_download(path))

    def test_markdown_validator_rejects_missing_limitations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text("# Synthetic Data Disclosure", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)

    def test_visible_exception_detection(self):
        self.assertEqual(
            ["Traceback (most recent call last)"],
            visible_exception_markers("Traceback (most recent call last)"),
        )

    def test_material_console_error_filter(self):
        values = ["harmless warning", "Uncaught TypeError", "Traceback in browser"]
        self.assertEqual(
            ["Uncaught TypeError", "Traceback in browser"],
            material_console_errors(values),
        )

    def test_ephemeral_port_allocation(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_single_governed_runner_entry_point_is_lazy(self):
        from src.browser_acceptance import run_minimal_acceptance

        self.assertTrue(callable(run_minimal_acceptance))


if __name__ == "__main__":
    unittest.main()
