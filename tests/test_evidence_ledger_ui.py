from __future__ import annotations

import unittest
from pathlib import Path


class EvidenceLedgerUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("src/ui/evidence_ledger_ui.py").read_text(encoding="utf-8")

    def test_page_is_read_only_and_exports_json(self):
        self.assertIn("Download canonical ledger JSON", self.source)
        self.assertNotIn("number_input", self.source)
        self.assertNotIn("text_input", self.source)
        self.assertNotIn("text_area", self.source)

    def test_controlled_filters_and_governance_warning_exist(self):
        self.assertIn("Record family", self.source)
        self.assertIn("Source classification", self.source)
        self.assertIn("does not create audit events", self.source)

    def test_no_execution_or_approval_controls_exist(self):
        forbidden = ("Run analysis", "Approve decision", "Delete event", "Award supplier")
        for label in forbidden:
            self.assertNotIn(label, self.source)


if __name__ == "__main__":
    unittest.main()
