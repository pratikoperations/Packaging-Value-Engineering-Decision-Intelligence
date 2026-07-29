from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class SidebarNavigationConfigTests(unittest.TestCase):
    def test_auto_generated_sidebar_navigation_is_disabled(self):
        config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
        self.assertIn("[client]", config)
        self.assertIn("showSidebarNavigation = false", config)

    def test_task_navigation_remains_defined_in_app(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("st.navigation(pages, position=\"sidebar\")", source)
        self.assertIn('title="Data Upload"', source)
        self.assertIn('title="Capabilities & Limits"', source)


if __name__ == "__main__":
    unittest.main()
