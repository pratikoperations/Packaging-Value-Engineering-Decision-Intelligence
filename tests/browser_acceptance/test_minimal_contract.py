from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.browser_acceptance.contracts import (
    ACCEPTANCE_REPORT_KEYS,
    APP_ROOT_SELECTOR,
    PAGE_CONTRACTS,
    SIDEBAR_GROUPS,
    VIEWPORTS,
)
from src.browser_acceptance.diagnostics import material_console_errors, visible_exception_markers
from src.browser_acceptance.export_validation import validate_json_download, validate_markdown_download
from src.browser_acceptance.process_manager import allocate_port


RUNNER_PATH = Path(__file__).resolve().parents[2] / "src" / "browser_acceptance" / "minimal_runner.py"
DOC_PATH = Path(__file__).resolve().parents[2] / "docs" / "enhancement_programme" / "GATE_3A_MINIMAL_BROWSER_ACCEPTANCE.md"


def _runner_source() -> str:
    return RUNNER_PATH.read_text(encoding="utf-8")


def _governed_markdown(limitation: str) -> str:
    return (
        "# Synthetic Data Disclosure\n"
        "# Packaging Value Engineering Decision Package\n"
        "## Independent Calculation Evidence\n"
        "Engineering validation remains mandatory.\n"
        f"{limitation}\n"
    )


class MinimalBrowserContractTests(unittest.TestCase):
    def test_exactly_thirteen_registered_routes(self):
        self.assertEqual(13, len(PAGE_CONTRACTS))
        self.assertEqual(13, len({item[0] for item in PAGE_CONTRACTS}))

    def test_exactly_four_desktop_sidebar_groups(self):
        self.assertEqual(4, len(SIDEBAR_GROUPS))
        grouped = [title for titles in SIDEBAR_GROUPS.values() for title in titles]
        self.assertEqual(10, len(grouped))
        self.assertEqual(10, len(set(grouped)))

    def test_governed_viewports(self):
        self.assertEqual({"width": 1440, "height": 1000}, VIEWPORTS["desktop"])
        self.assertEqual({"width": 412, "height": 915}, VIEWPORTS["narrow"])

    def test_stable_streamlit_root_selector(self):
        self.assertEqual('[data-testid="stAppViewContainer"]', APP_ROOT_SELECTOR)

    def test_acceptance_report_schema_contains_required_fields(self):
        self.assertEqual(len(ACCEPTANCE_REPORT_KEYS), len(set(ACCEPTANCE_REPORT_KEYS)))
        for key in (
            "source_commit",
            "unique_route_count",
            "physical_navigation_passed",
            "narrow_smoke_passed",
            "overall_disposition",
        ):
            self.assertIn(key, ACCEPTANCE_REPORT_KEYS)

    def test_json_validator_accepts_governed_export(self):
        payload = {
            "metadata": {"synthetic_disclosure": "Synthetic demonstration data only."},
            "executive_summary": {},
            "project": {},
            "scenario": {},
            "baseline": {},
            "alternatives": [],
            "decision_controls": {
                "autonomous_technical_approval": False,
                "engineering_validation_required": True,
            },
            "calculation_evidence": {},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(payload, validate_json_download(path))

    def test_json_validator_rejects_missing_governance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_json_download(path)

    def test_markdown_validator_accepts_realized_savings_limitation(self):
        text = _governed_markdown("No realized savings are claimed.")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(text, validate_markdown_download(path))

    def test_markdown_validator_rejects_positive_claim(self):
        text = _governed_markdown("Realized savings are claimed and validated.")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)

    def test_visible_exception_and_console_filters(self):
        self.assertEqual(
            ["Traceback (most recent call last)"],
            visible_exception_markers("Traceback (most recent call last)"),
        )
        self.assertEqual(
            ["Uncaught TypeError", "Traceback in browser"],
            material_console_errors(["harmless warning", "Uncaught TypeError", "Traceback in browser"]),
        )

    def test_ephemeral_port_allocation(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_single_governed_runner_entry_point_is_lazy(self):
        from src.browser_acceptance import run_minimal_acceptance

        self.assertTrue(callable(run_minimal_acceptance))

    def test_desktop_grouped_navigation_remains_mandatory(self):
        source = _runner_source()
        self.assertIn(
            '_expand_group(page, "Evidence & Explanation", "Calculation Evidence")',
            source,
        )
        self.assertIn("_physical_calculation_navigation(page)", source)
        self.assertIn('report["physical_navigation_passed"] = True', source)

    def test_group_fallback_remains_semantic_and_visible(self):
        source = _runner_source()
        start = source.index("def _expand_group")
        end = source.index("\ndef _resolved_link", start)
        group_source = source[start:end]
        self.assertIn('page.get_by_role("button", name=group, exact=True)', group_source)
        self.assertIn('page.get_by_text(group, exact=True)', group_source)
        self.assertIn("visible_text_matches = _visible(text_matches)", group_source)
        self.assertIn("ancestor-or-self::*[self::button or self::summary or @role='button'][1]", group_source)
        self.assertNotIn("data-testid", group_source)
        self.assertNotIn("bounding_box", group_source)
        self.assertNotIn("evaluate(", group_source)
        self.assertNotIn("session_state", group_source)
        self.assertNotIn("retry", group_source.lower())
        self.assertNotIn("page.wait_for_timeout", group_source)

    def test_responsive_physical_route_click_is_mandatory(self):
        source = _runner_source()
        start = source.index("def _responsive_physical_route")
        end = source.index("\ndef _material_console_errors", start)
        responsive_source = source[start:end]
        self.assertIn("_open_sidebar(page)", responsive_source)
        self.assertIn("selected_link.click(timeout=ACTION_TIMEOUT_MILLISECONDS)", responsive_source)
        self.assertIn("RESPONSIVE_ROUTE_PREFERENCES", responsive_source)
        self.assertIn('"Showcase & Handoff"', source)
        self.assertIn('"Capabilities & Limits"', source)
        self.assertNotIn("_expand_group(", responsive_source)

    def test_narrow_calculation_evidence_uses_governed_resolved_destination(self):
        source = _runner_source()
        start = source.index("def _responsive_physical_route")
        end = source.index("\ndef _material_console_errors", start)
        responsive_source = source[start:end]
        self.assertIn('routes.get("Calculation Evidence")', responsive_source)
        self.assertIn("page.goto(calculation_url", responsive_source)
        self.assertIn('name=re.compile("Calculation Evidence", re.I)', responsive_source)

    def test_narrow_success_and_link_evidence_are_mandatory(self):
        source = _runner_source()
        self.assertIn('artifact_dir / "narrow-link-inventory.json"', source)
        self.assertIn('screenshots / "narrow-smoke.png"', source)
        self.assertIn('screenshots / "failure.png"', source)
        self.assertIn('artifact_dir / "failure-visible-links.json"', source)

    def test_acceptance_cannot_pass_without_responsive_assertion(self):
        source = _runner_source()
        run_start = source.index("def run_minimal_acceptance")
        run_source = source[run_start:]
        call_index = run_source.index("_responsive_physical_route(")
        pass_index = run_source.index('report["narrow_smoke_passed"] = True')
        required_index = run_source.index('report["narrow_smoke_passed"],')
        disposition_index = run_source.index('report["overall_disposition"] = "PASS"')
        self.assertLess(call_index, pass_index)
        self.assertLess(pass_index, required_index)
        self.assertLess(required_index, disposition_index)

    def test_static_prohibition_controls(self):
        source = _runner_source()
        prohibited = (
            "bounding_box(",
            ".evaluate(",
            "session_state",
            "retry(",
            "document.querySelector",
        )
        for token in prohibited:
            self.assertNotIn(token, source)
        responsive_start = source.index("def _responsive_physical_route")
        responsive_end = source.index("\ndef _material_console_errors", responsive_start)
        responsive_source = source[responsive_start:responsive_end]
        self.assertNotIn("page.wait_for_timeout", responsive_source)

    def test_documentation_records_responsive_semantics_decision(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "The responsive contract validates user access and governed destination behavior at Android-sized width.",
            text,
        )
        self.assertIn(
            "It does not require the narrow layout to reproduce desktop sidebar grouping semantics.",
            text,
        )


if __name__ == "__main__":
    unittest.main()
