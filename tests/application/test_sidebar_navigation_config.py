from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SidebarNavigationConfigTests(unittest.TestCase):
    def test_sidebar_navigation_is_enabled(self):
        config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("[client]", config)
        self.assertIn("showSidebarNavigation = true", config)

    def test_approved_task_navigation_is_visible(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.navigation(pages, position="sidebar", expanded=True)', source)
        self.assertIn('initial_sidebar_state="expanded"', source)
        self.assertEqual(source.count("st.set_page_config("), 1)
        self.assertIn('return 30, "Data Upload"', source)
        self.assertIn('return 70, "Capabilities & Limits"', source)

    def test_legacy_titles_are_not_registered(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertNotIn('"Upload Validate"', source)
        self.assertNotIn('"PVE 2.0 AI Word Intake"', source)
        self.assertNotIn('"PVE 2.1 Digital PDF Intake"', source)

    def test_mobile_sidebar_width_uses_stable_streamlit_selector(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("_apply_mobile_sidebar_width", source)
        self.assertIn('[data-testid="stSidebar"] {', source)
        self.assertNotIn('[data-testid="stSidebar"][aria-expanded="true"]', source)
        self.assertIn("width: clamp(180px, 46vw, 200px) !important;", source)
        self.assertIn("flex-basis: clamp(180px, 46vw, 200px) !important;", source)
        self.assertIn("min-width: 180px !important;", source)
        self.assertIn("max-width: 200px !important;", source)
        self.assertIn('[data-testid="stSidebar"] > div:first-child', source)
        self.assertIn("overflow-x: hidden !important;", source)
        self.assertIn('[data-testid="stSidebar"] a {', source)
        self.assertIn("white-space: normal !important;", source)
        self.assertIn("overflow-wrap: break-word !important;", source)
        self.assertIn("@media (max-width: 768px)", source)
        self.assertIn("selected.run()", source)


if __name__ == "__main__":
    unittest.main()
