from __future__ import annotations

import unittest
from pathlib import Path

from src.ui.showcase_handoff_ui import (
    LIVE_DEMO_RECOVERY,
    PAGE_PATHS,
    PAGE_REGISTRY_SESSION_KEY,
)


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
EXPECTED_SIDEBAR_GROUPS = (
    ("Workspace", ("Project Dashboard", "Guided Workflow")),
    (
        "Inputs & Governance",
        ("Specification Review", "Data Upload", "Business Rules & Thresholds"),
    ),
    ("Analysis & Decision", ("Scenario Analysis", "Decision Records")),
    (
        "Evidence & Explanation",
        ("SourceMate", "Calculation Evidence", "Decision Evidence Ledger"),
    ),
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
            "Acceptance state: PASSED",
            "Per-page hosted acceptance",
            "Five-minute journey acceptance",
            "Responsive presentation checks",
            "Proof-versus-limit confirmation",
            "Accepted runtime exact-head workflow run",
            "Artifact SHA-256",
            "30687748523",
            "746",
        ):
            self.assertIn(required, content)

    def test_freeze_manifest_has_required_identity_and_evidence_fields(self) -> None:
        content = (ROOT / "docs" / "SHOWCASE_FREEZE_MANIFEST.md").read_text(encoding="utf-8")
        for required in (
            "PRE-MERGE ACCEPTED",
            "showcase-handoff-development",
            "Hosted acceptance evidence",
            "Frozen capabilities",
            "Known limitations",
            "Prohibited claims",
            "Deferred production requirements",
            "no Build 7 is proposed",
            "8814551912",
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

    def test_home_is_registered_as_callable_streamlit_page(self) -> None:
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('home_page = st.Page(render_home, title="Home", default=True)', source)
        self.assertIn('page_registry = {"Home": home_page}', source)

    def test_sidebar_and_journey_links_share_one_page_registry(self) -> None:
        app_source = (ROOT / "app.py").read_text(encoding="utf-8")
        ui_source = (ROOT / "src" / "ui" / "showcase_handoff_ui.py").read_text(encoding="utf-8")
        self.assertIn("st.session_state[PAGE_REGISTRY_SESSION_KEY] = page_registry", app_source)
        self.assertIn("page = page_registry[title]", app_source)
        self.assertIn("page_registry.get(step.page_reference)", ui_source)

    def test_home_string_path_is_not_passed_to_page_link(self) -> None:
        source = (ROOT / "src" / "ui" / "showcase_handoff_ui.py").read_text(encoding="utf-8")
        self.assertNotIn("st.page_link(path", source)
        self.assertIn("st.page_link(target_page", source)

    def test_registered_page_labels_match_governed_inventory(self) -> None:
        self.assertEqual(PAGE_REGISTRY_SESSION_KEY, "_pve_page_registry")
        self.assertEqual(tuple(PAGE_PATHS), EXPECTED_PAGES)

    def test_sidebar_group_headings_and_membership_are_exact(self) -> None:
        namespace: dict[str, object] = {}
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        start = source.index("SIDEBAR_GROUPS =")
        end = source.index("\n\n\n@st.cache_data", start)
        exec(source[start:end], {}, namespace)
        self.assertEqual(namespace["SIDEBAR_GROUPS"], EXPECTED_SIDEBAR_GROUPS)

    def test_grouped_sidebar_contains_every_registered_page_once(self) -> None:
        grouped_pages = [page for _, pages in EXPECTED_SIDEBAR_GROUPS for page in pages]
        direct_pages = ["Home", "Showcase & Handoff", "Capabilities & Limits"]
        self.assertEqual(len(grouped_pages) + len(direct_pages), 13)
        self.assertEqual(set(grouped_pages + direct_pages), set(EXPECTED_PAGES))
        self.assertEqual(len(grouped_pages + direct_pages), len(set(grouped_pages + direct_pages)))

    def test_required_pages_remain_directly_visible(self) -> None:
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.page_link(home_page, label="Home")', source)
        self.assertIn(
            'st.page_link(page_registry["Showcase & Handoff"], label="Showcase & Handoff")',
            source,
        )
        self.assertIn(
            'st.page_link(page_registry["Capabilities & Limits"], label="Capabilities & Limits")',
            source,
        )

    def test_sidebar_grouping_preserves_registered_page_objects(self) -> None:
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn("for group_title, page_titles in SIDEBAR_GROUPS:", source)
        self.assertIn("with st.expander(group_title, expanded=False):", source)
        self.assertIn("page = page_registry[title]", source)
        self.assertIn("st.page_link(page, label=title)", source)
        self.assertNotIn('st.page_link("app.py"', source)

    def test_build_does_not_modify_analytical_or_persistence_contracts(self) -> None:
        acceptance = (ROOT / "docs" / "SHOWCASE_FINAL_ACCEPTANCE.md").read_text(encoding="utf-8")
        freeze = (ROOT / "docs" / "SHOWCASE_FREEZE_MANIFEST.md").read_text(encoding="utf-8")
        self.assertIn("unit tests alone", acceptance)
        self.assertIn("no autonomous approval", freeze.lower())
        self.assertIn("no automated browser acceptance", freeze.lower())


if __name__ == "__main__":
    unittest.main()
