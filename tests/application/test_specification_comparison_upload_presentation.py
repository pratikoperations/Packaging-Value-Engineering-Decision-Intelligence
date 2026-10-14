from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SpecificationComparisonUploadPresentationTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "pages" / "09_Data_Upload.py").read_text(encoding="utf-8")

    def test_existing_and_proposed_upload_slots_are_explicit(self):
        self.assertIn('"Compare Existing vs Proposed specifications"', self.source)
        self.assertIn('"Existing specification — approved baseline"', self.source)
        self.assertIn('"Proposed specification — candidate change"', self.source)
        self.assertIn('"data_upload.existing_specification"', self.source)
        self.assertIn('"data_upload.proposed_specification"', self.source)

    def test_specification_roles_are_fixed_by_upload_slot(self):
        self.assertIn("(recovered_files[0], DocumentRole.EXISTING)", self.source)
        self.assertIn("(recovered_files[1], DocumentRole.PROPOSED)", self.source)
        self.assertNotIn('st.selectbox(f"Role for {upload.name}"', self.source)

    def test_project_feasibility_gate_is_visible_but_not_approval(self):
        self.assertIn('st.subheader("Project Feasibility Gate")', self.source)
        self.assertIn("READY FOR DOWNSTREAM FEASIBILITY ASSESSMENT", self.source)
        self.assertIn("FEASIBILITY ASSESSMENT BLOCKED", self.source)
        self.assertIn("It is not engineering approval", self.source)

    def test_structured_project_data_remains_available(self):
        self.assertIn('"Upload structured project data"', self.source)
        self.assertIn('type=["xlsx", "csv", "json"]', self.source)
        self.assertIn("validate_structured_batch", self.source)


if __name__ == "__main__":
    unittest.main()
