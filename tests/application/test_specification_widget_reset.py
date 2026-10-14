from __future__ import annotations

import ast
import unittest
from pathlib import Path


class SpecificationWidgetResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py").read_text(encoding="utf-8")

    def test_clear_callback_resets_file_widgets_and_review_context(self):
        tree = ast.parse(self.source)
        method = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "clear_specification_session_pair")
        code = ast.get_source_segment(self.source, method)
        self.assertIn("data_upload.existing_specification", code)
        self.assertIn("data_upload.proposed_specification", code)
        self.assertIn("SPEC_REVIEWS_KEY", code)
        self.assertIn("SESSION_SPEC_CACHE", code)
        self.assertIn("DRAFT_REVIEW_RESTORE_KEY", code)
        self.assertIn("triage_value_", code)
        self.assertIn("on_click=clear_specification_session_pair", self.source)

    def test_saved_draft_resume_clears_stale_upload_widgets(self):
        resume = self.source[self.source.index('if st.button("Resume selected draft"'):self.source.index('with st.expander("Restore a portable specification draft backup")')]
        self.assertIn('st.session_state.pop("data_upload.existing_specification", None)', resume)
        self.assertIn('st.session_state.pop("data_upload.proposed_specification", None)', resume)
        self.assertIn("st.session_state[SESSION_SPEC_CACHE]", resume)


if __name__ == "__main__":
    unittest.main()
