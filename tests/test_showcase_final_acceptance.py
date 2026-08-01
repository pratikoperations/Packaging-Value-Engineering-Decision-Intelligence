from __future__ import annotations

import unittest
from pathlib import Path

from src.ui.showcase_handoff_ui import LIVE_DEMO_RECOVERY, PAGE_PATHS


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PAGES = (
    "Home",
    "Showcase & Handoff",
    "Project Dashboard",
    "Guided Workflow",
    "Specification Review",
    "Data Upload",
    "Business Rules & Thresholds",
    "Scenario Analysis",
    "Decision Records",
    "SourceMate",
    "Calculation Evidence",
    "Decision Evidence Ledger",
    "Capabilities & Limits",
)


class ShowcaseFinalAcceptanceTests(unittest.TestCase):
    def test_page_inventory_is_complete_and_ordered(self) -> None:
        self.assertEqual(tuple(PAGE_PATHS), EXPECTED_PAGES)

    def test_page_paths_reference_existing_files(self) -> None:
        for page, relative_path in PAGE_PATHS.items():
            with self.subTest(page=page):
                self.assertTrue((ROOT / relative_path).exists())

    def test_live_demo_recovery_is_read_only_and_governed(self) -> None:
        recovery = " ".join(LIVE_DEMO_RECOVERY).lower()
        for required in ("refresh", "return to home", "synthetic", "capabilities & limits"):
            self.assertIn(required, recovery)
        for prohibited in ("approve", "award supplier", "delete", "persist"):
            self.assertNotIn(prohibited, recovery)

    def test_final_acceptance_document_has_required_controls(self) -> None:
        content = (ROOT / "docs" / "SHOWCASE_FINAL_ACCEPTANCE.md").read_text(encoding="utf-8")
        for required in (
            "PENDING MANUAL HOSTED EVIDENCE",
            "Per-page hosted acceptance",
            "Five-minute journey acceptance",
            "Responsive presentation checks",
            "Proof-versus-limit confirmation",
            "Exact-head workflow run",
            "Artifact SHA-256",
        ):
            self.assertIn(required, content)

    def test_freeze_manifest_has_required_identity_and_evidence_fields(self) -> None:
        content = (ROOT / "docs" / "SHOWCASE_FREEZE_MANIFEST.md").read_text(encoding="utf-8")
        for required in (
            "CANDIDATE — NOT YET FINAL",
            "showcase-handoff-development",
            "Hosted acceptance evidence",
            "Frozen capabilities",
            "Known limitations",
            "Prohibited claims",
            "Deferred production requirements",
            "no Build 7 is proposed",
        ):
            self.assertIn(required, content)

    def test_synthetic_data_and_production_boundaries_are_preserved(self) -> None:
        acceptance = (ROOT / "docs" / "SHOWCASE_FINAL_ACCEPTANCE.md").read_text(encoding="utf-8").lower()
        freeze = (ROOT / "docs" / "SHOWCASE_FREEZE_MANIFEST.md").read_text(encoding="utf-8").lower()
        for content in (acceptance, freeze):
            self.assertIn("synthetic", content)
            self.assertIn("production readiness", content)
            self.assertIn("realized savings", content)

    def test_responsive_ui_contract_uses_full_width_controls(self) -> None:
        source = (ROOT / "src" / "ui" / "showcase_handoff_ui.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(source.count('width="stretch"'), 3)
        self.assertIn('st.expander("Live-demo recovery"', source)
        self.assertNotIn('st.columns(2)\n    with left:', source)

    def test_build_does_not_modify_analytical_or_persistence_contracts(self) -> None:
        acceptance = (ROOT / "docs" / "SHOWCASE_FINAL_ACCEPTANCE.md").read_text(encoding="utf-8")
        freeze = (ROOT / "docs" / "SHOWCASE_FREEZE_MANIFEST.md").read_text(encoding="utf-8")
        self.assertIn("unit tests alone", acceptance)
        self.assertIn("no autonomous approval", freeze.lower())
        self.assertIn("no automated browser acceptance", freeze.lower())


if __name__ == "__main__":
    unittest.main()
