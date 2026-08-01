from __future__ import annotations

import unittest
from pathlib import Path


class ShowcaseHandoffUIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.ui = (root / "src" / "ui" / "showcase_handoff_ui.py").read_text(encoding="utf-8")
        self.page = (root / "pages" / "05_showcase_handoff.py").read_text(encoding="utf-8")
        self.app = (root / "app.py").read_text(encoding="utf-8")
        self.guide = (root / "docs" / "INTERVIEW_DEMO_GUIDE.md").read_text(encoding="utf-8")

    def test_ui_contains_governed_controls_and_exports(self) -> None:
        for phrase in ("Audience", "Journey", "What this proves", "What this does not prove", "New-user handoff checklist", "Download governed journey"):
            self.assertIn(phrase, self.ui)

    def test_ui_has_no_unrestricted_or_mutating_controls(self) -> None:
        lowered = self.ui.lower()
        self.assertNotIn("text_area(", lowered)
        self.assertNotIn("number_input(", lowered)
        for phrase in ("approve decision", "execute scenario", "award supplier", "delete record"):
            self.assertNotIn(phrase, lowered)

    def test_page_fails_closed(self) -> None:
        self.assertIn("could not be loaded safely", self.page)
        self.assertIn("No business record was read or changed", self.page)

    def test_navigation_registers_hub(self) -> None:
        self.assertIn("showcase_handoff", self.app)
        self.assertIn("Showcase & Handoff", self.app)

    def test_interview_guide_contains_current_governed_routes(self) -> None:
        for phrase in ("Five-minute executive route", "Ten-minute detailed route", "SourceMate", "Calculation Evidence", "Decision Evidence Ledger", "What this proves", "What this does not prove"):
            self.assertIn(phrase, self.guide)


if __name__ == "__main__":
    unittest.main()
