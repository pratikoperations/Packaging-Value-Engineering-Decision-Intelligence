from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.browser_acceptance.contracts import PAGE_CONTRACTS, REQUIRED_JSON_KEYS, SIDEBAR_GROUPS, VIEWPORTS
from src.browser_acceptance.export_validation import validate_json_download, validate_markdown_download
from src.browser_acceptance.process_manager import allocate_port


class BrowserContractTests(unittest.TestCase):
    def test_exactly_thirteen_registered_page_contracts(self):
        self.assertEqual(13, len(PAGE_CONTRACTS))
        self.assertEqual(13, len({item[0] for item in PAGE_CONTRACTS}))

    def test_exactly_four_sidebar_groups(self):
        self.assertEqual(4, len(SIDEBAR_GROUPS))
        grouped = tuple(title for titles in SIDEBAR_GROUPS.values() for title in titles)
        self.assertEqual(10, len(grouped))
        self.assertEqual(10, len(set(grouped)))

    def test_direct_links_are_not_in_groups(self):
        grouped = {title for titles in SIDEBAR_GROUPS.values() for title in titles}
        self.assertTrue({"Home", "Showcase & Handoff", "Capabilities & Limits"}.isdisjoint(grouped))

    def test_viewports_are_governed(self):
        self.assertEqual({"width": 1440, "height": 1000}, VIEWPORTS["desktop"])
        self.assertEqual({"width": 412, "height": 915}, VIEWPORTS["narrow"])

    def test_ephemeral_port_is_allocated(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_json_validator_accepts_governed_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            payload = {key: {} for key in REQUIRED_JSON_KEYS}
            payload["metadata"] = {"synthetic_disclosure": "Synthetic demonstration data only."}
            payload["calculation_evidence"] = {"results": [{"calculation_id": "CALC-COST-001"}]}
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(payload, validate_json_download(path))

    def test_json_validator_rejects_missing_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_json_download(path)

    def test_markdown_validator_accepts_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(
                "# Synthetic Data Disclosure\nSynthetic demonstration only.\n"
                "# Packaging Value Engineering Decision Package\n"
                "## Independent Calculation Evidence\nEngineering validation remains mandatory.\n",
                encoding="utf-8",
            )
            self.assertIn("Calculation Evidence", validate_markdown_download(path))

    def test_markdown_validator_rejects_missing_limitations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text("# Synthetic Data Disclosure", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)


if __name__ == "__main__":
    unittest.main()
