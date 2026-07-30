from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UPLOAD = ROOT / "pages" / "09_Data_Upload.py"
SCENARIOS = ROOT / "pages" / "04_Controlled_Scenarios.py"
DASHBOARD = ROOT / "pages" / "01_Project_Dashboard.py"
PAGES = ROOT / "pages"


class FinalWorkflowPresentationCorrectionTests(unittest.TestCase):
    def test_existing_specification_is_explicitly_confirmed_read_only_baseline(self):
        source = UPLOAD.read_text(encoding="utf-8")
        self.assertIn("approved baseline and may be used as read-only reference evidence", source)
        self.assertIn("def confirm_existing_baseline", source)
        self.assertIn("DocumentRole.EXISTING", source)
        self.assertIn("✅ APPROVED BASELINE", source)
        self.assertIn("Review actions apply only to the Proposed specification", source)

    def test_only_proposed_candidates_are_actionable_and_counted(self):
        source = UPLOAD.read_text(encoding="utf-8")
        self.assertIn("if view.document_role is DocumentRole.PROPOSED", source)
        self.assertIn("Proposed candidates resolved", source)
        self.assertIn("Proposed candidates require action", source)
        self.assertIn("Pending Proposed candidates remain", source)

    def test_snapshot_and_canonical_builders_are_preserved(self):
        source = UPLOAD.read_text(encoding="utf-8")
        self.assertIn("build_unified_canonical_draft", source)
        self.assertIn("build_unified_snapshot", source)
        self.assertIn("snapshot_repository.create(snapshot)", source)

    def test_scenario_reasons_are_rendered_as_business_readable_items(self):
        source = SCENARIOS.read_text(encoding="utf-8")
        self.assertIn("def render_reason_items", source)
        self.assertIn('st.write(f"• {item}")', source)
        self.assertNotIn('st.write(record["business_threshold_reasons"]', source)
        self.assertNotIn('st.write(record["control_reasons"]', source)

    def test_synthetic_demo_has_editable_non_zero_defaults(self):
        source = SCENARIOS.read_text(encoding="utf-8")
        self.assertIn('"ALT-BASE": (0.0, 0.0)', source)
        self.assertIn('"ALT-A": (-3.0, -5.0)', source)
        self.assertIn('"ALT-B": (2.0, -8.0)', source)
        self.assertIn('"ALT-C": (5.0, 3.0)', source)
        self.assertIn("if not demo", source)
        self.assertIn("They are not supplier quotations", source)

    def test_project_creation_offers_existing_governed_upload_page(self):
        source = DASHBOARD.read_text(encoding="utf-8")
        self.assertIn("NEW_PROJECT_UPLOAD_KEY", source)
        self.assertIn('st.page_link("pages/09_Data_Upload.py"', source)
        self.assertIn("Continue without uploading", source)
        self.assertIn('st.session_state[NEW_PROJECT_UPLOAD_KEY] = True', source)
        self.assertNotIn("st.file_uploader", source)

    def test_public_pages_do_not_use_streamlit_json_renderer(self):
        offenders = []
        for page in PAGES.glob("*.py"):
            if "st.json(" in page.read_text(encoding="utf-8"):
                offenders.append(page.name)
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
