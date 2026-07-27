from __future__ import annotations

import unittest
from pathlib import Path


PAGE = Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py"
LIMITS_PAGE = Path(__file__).resolve().parents[2] / "pages" / "10_Capabilities_and_Limits.py"


class DataUploadPresentationTests(unittest.TestCase):
    def test_data_upload_uses_single_column_mobile_safe_control_flow(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertNotIn("st.columns(", source)
        self.assertIn('width="stretch"', source)
        self.assertIn("Detection and routing", source)
        self.assertIn("Exactly two specification documents are required", source)

    def test_data_upload_displays_validation_and_immutable_snapshot_boundaries(self):
        source = PAGE.read_text(encoding="utf-8")
        self.assertIn("Canonical validation found issues", source)
        self.assertIn("Create immutable specification snapshot", source)
        self.assertIn("DuplicateSpecificationSnapshotError", source)
        self.assertIn("Archived projects are read-only", source)

    def test_capabilities_page_states_supported_and_unsupported_boundaries(self):
        source = LIMITS_PAGE.read_text(encoding="utf-8")
        self.assertIn("What this application supports", source)
        self.assertIn("What this application does not support", source)
        self.assertIn("OCR", source)
        self.assertIn("does not prove", source)


if __name__ == "__main__":
    unittest.main()
