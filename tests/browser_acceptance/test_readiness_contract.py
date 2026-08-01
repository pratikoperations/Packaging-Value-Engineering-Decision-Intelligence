from __future__ import annotations

import inspect
import unittest

from src.browser_acceptance import runner


class BrowserReadinessContractTests(unittest.TestCase):
    def test_app_readiness_uses_bounded_playwright_polling(self):
        source = inspect.getsource(runner._app_ready)
        self.assertIn("wait_for_function", source)
        self.assertGreaterEqual(source.count("PAGE_TIMEOUT_MILLISECONDS"), 2)
        self.assertIn("require_home_heading", source)
        self.assertIn("HOME_HEADING", source)
        self.assertNotIn("root.inner_text().strip()", source)
        self.assertNotIn("time.sleep", source)


if __name__ == "__main__":
    unittest.main()
