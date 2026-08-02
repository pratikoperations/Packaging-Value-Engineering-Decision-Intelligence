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
from src.browser_acceptance.diagnostics import (
    material_console_errors,
    visible_exception_markers,
)
from src.browser_acceptance.export_validation import (
    validate_json_download,
    validate_markdown_download,
)
from src.browser_acceptance.process_manager import allocate_port


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

    def test_exactly_four_sidebar_groups(self):
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
        self.assertIn("overall_disposition", ACCEPTANCE_REPORT_KEYS)
        self.assertIn("source_commit", ACCEPTANCE_REPORT_KEYS)
        self.assertIn("unique_route_count", ACCEPTANCE_REPORT_KEYS)

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

    def _assert_markdown_accepted(self, limitation: str) -> None:
        text = _governed_markdown(limitation)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(text, encoding="utf-8")
            self.assertEqual(text, validate_markdown_download(path))

    def _assert_markdown_rejected(self, limitation: str) -> None:
        text = _governed_markdown(limitation)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)

    def test_markdown_validator_accepts_prior_exact_limitation(self):
        self._assert_markdown_accepted("No realized savings are claimed.")

    def test_markdown_validator_accepts_actual_artifact_claim_limitation(self):
        self._assert_markdown_accepted(
            "Not suitable for negotiation, supplier award, engineering approval, "
            "regulatory approval or realized-savings claims."
        )

    def test_markdown_validator_accepts_actual_artifact_validation_limitation(self):
        self._assert_markdown_accepted(
            "A match is not supplier, engineering, regulatory, production or "
            "realized-savings validation."
        )

    def test_markdown_validator_accepts_case_punctuation_and_hyphen_variants(self):
        self._assert_markdown_accepted("NO REALIZED—SAVINGS CLAIMS ARE VALIDATED!")

    def test_markdown_validator_accepts_line_wrapped_equivalent_limitation(self):
        self._assert_markdown_accepted(
            "This report is not suitable for realized-\nsavings claims."
        )

    def test_markdown_validator_rejects_generic_savings_wording(self):
        self._assert_markdown_rejected("Savings opportunities are shown.")

    def test_markdown_validator_rejects_missing_realized_savings_limitation(self):
        self._assert_markdown_rejected(
            "Engineering review is required before implementation."
        )

    def test_markdown_validator_rejects_positive_realized_savings_claim(self):
        self._assert_markdown_rejected("Realized savings are claimed and validated.")

    def test_markdown_validator_rejects_missing_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text("No realized savings are claimed.", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)

    def test_visible_exception_detection(self):
        self.assertEqual(
            ["Traceback (most recent call last)"],
            visible_exception_markers("Traceback (most recent call last)"),
        )

    def test_material_console_error_filter(self):
        values = ["harmless warning", "Uncaught TypeError", "Traceback in browser"]
        self.assertEqual(
            ["Uncaught TypeError", "Traceback in browser"],
            material_console_errors(values),
        )

    def test_ephemeral_port_allocation(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_single_governed_runner_entry_point_is_lazy(self):
        from src.browser_acceptance import run_minimal_acceptance

        self.assertTrue(callable(run_minimal_acceptance))

    def test_scenario_selector_targets_exact_combobox_role(self):
        runner_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "browser_acceptance"
            / "minimal_runner.py"
        )
        source = runner_path.read_text(encoding="utf-8")
        self.assertIn(
            'page.get_by_role(\n        "combobox",\n        name="Governed synthetic procurement scenario",\n        exact=True,\n    )',
            source,
        )
        self.assertNotIn(
            'page.get_by_label("Governed synthetic procurement scenario")',
            source,
        )
        self.assertNotIn(
            'get_by_role("button", name="Governed synthetic procurement scenario"',
            source,
        )

    def test_scenario_options_use_open_listbox_and_semantic_option_wait(self):
        runner_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "browser_acceptance"
            / "minimal_runner.py"
        )
        source = runner_path.read_text(encoding="utf-8")
        scenario_start = source.index("def _select_scenario_and_adjust_inputs")
        scenario_end = source.index("\ndef _calculation_evidence_visible", scenario_start)
        scenario_source = source[scenario_start:scenario_end]

        click_index = scenario_source.index("select.click(timeout=ACTION_TIMEOUT_MILLISECONDS)")
        listbox_index = scenario_source.index('listbox = page.get_by_role("listbox")')
        wait_index = scenario_source.index(
            'listbox.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)'
        )
        option_index = scenario_source.index('listbox.get_by_role("option")')
        self.assertLess(click_index, listbox_index)
        self.assertLess(listbox_index, wait_index)
        self.assertLess(wait_index, option_index)
        self.assertIn(
            'listbox.wait_for(state="hidden", timeout=PAGE_TIMEOUT_MILLISECONDS)',
            scenario_source,
        )
        self.assertNotIn('select.locator("option")', scenario_source)
        self.assertNotIn("select.select_option", scenario_source)
        self.assertNotIn("page.wait_for_timeout", scenario_source[:option_index])

    def test_assumptions_discovery_checks_controls_before_semantic_summary(self):
        runner_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "browser_acceptance"
            / "minimal_runner.py"
        )
        source = runner_path.read_text(encoding="utf-8")
        helper_start = source.index("def _ensure_assumptions_open")
        helper_end = source.index("\ndef _select_scenario_and_adjust_inputs", helper_start)
        helper_source = source[helper_start:helper_end]

        visible_check = helper_source.index("if _visible(cost) or _visible(material):")
        text_lookup = helper_source.index("page.get_by_text(re.compile")
        summary_lookup = helper_source.index('ancestor-or-self::summary[1]')
        fallback_lookup = helper_source.index("@role='button' or self::button")
        click_index = helper_source.index("control.click(timeout=ACTION_TIMEOUT_MILLISECONDS)")
        wait_index = helper_source.index(
            'cost.first.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)'
        )

        self.assertLess(visible_check, text_lookup)
        self.assertLess(text_lookup, summary_lookup)
        self.assertLess(summary_lookup, fallback_lookup)
        self.assertLess(fallback_lookup, click_index)
        self.assertLess(click_index, wait_index)
        self.assertNotIn('get_by_role("button", name=re.compile(r"assumptions$', helper_source)
        self.assertNotIn("data-testid", helper_source)
        self.assertNotIn("page.wait_for_timeout", helper_source)
        self.assertNotIn("retry", helper_source.lower())

    def test_narrow_sidebar_path_uses_semantic_open_and_group_resolution(self):
        runner_path = (
            Path(__file__).resolve().parents[2]
            / "src"
            / "browser_acceptance"
            / "minimal_runner.py"
        )
        source = runner_path.read_text(encoding="utf-8")
        sidebar_start = source.index("def _open_sidebar")
        sidebar_end = source.index("\ndef _expand_group", sidebar_start)
        sidebar_source = source[sidebar_start:sidebar_end]
        run_start = source.index("def run_minimal_acceptance")
        run_source = source[run_start:]

        self.assertIn('get_by_role("link", name="Home", exact=True)', sidebar_source)
        self.assertIn('get_by_role("button", name=re.compile("sidebar", re.I))', sidebar_source)
        self.assertIn("button.click(timeout=ACTION_TIMEOUT_MILLISECONDS)", sidebar_source)
        self.assertNotIn("data-testid", sidebar_source)
        self.assertNotIn("page.wait_for_timeout", sidebar_source)

        narrow_context_index = run_source.index(
            'narrow_context = browser.new_context(viewport=VIEWPORTS["narrow"])'
        )
        open_sidebar_index = run_source.index("_open_sidebar(narrow)", narrow_context_index)
        resolved_link_index = run_source.index(
            '_resolved_link(narrow, app.base_url, "Calculation Evidence", "Evidence & Explanation")',
            open_sidebar_index,
        )
        screenshot_index = run_source.index(
            'narrow.screenshot(path=screenshots / "narrow-smoke.png", full_page=True)',
            resolved_link_index,
        )
        self.assertLess(narrow_context_index, open_sidebar_index)
        self.assertLess(open_sidebar_index, resolved_link_index)
        self.assertLess(resolved_link_index, screenshot_index)


if __name__ == "__main__":
    unittest.main()
