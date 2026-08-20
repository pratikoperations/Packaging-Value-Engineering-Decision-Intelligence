from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SidebarNavigationConfigTests(unittest.TestCase):
    def test_auto_generated_sidebar_navigation_is_disabled(self):
        config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("[client]", config)
        self.assertIn("showSidebarNavigation = false", config)

    def test_approved_task_navigation_is_rendered_explicitly(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.navigation(pages, position="hidden")', source)
        self.assertIn('st.page_link(home_page, label="Home")', source)
        self.assertIn("st.page_link(page, label=title)", source)
        self.assertIn('return 30, "Data Upload"', source)
        self.assertIn('return 70, "Capabilities & Limits"', source)

    def test_legacy_titles_are_not_registered(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertNotIn('"Upload Validate"', source)
        self.assertNotIn('"PVE 2.0 AI Word Intake"', source)
        self.assertNotIn('"PVE 2.1 Digital PDF Intake"', source)

    def test_mobile_sidebar_uses_native_streamlit_sizing(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertNotIn('_apply_responsive_sidebar_width', source)
        self.assertNotIn('[data-testid="stSidebar"][aria-expanded="true"]', source)
        self.assertNotIn("flex-basis:", source)
        self.assertNotIn("@media (max-width: 768px)", source)
        self.assertIn("with st.sidebar:", source)


if __name__ == "__main__":
    unittest.main()
