from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.browser_acceptance.contracts import (
    APP_ROOT_SELECTOR,
    BROWSER_TEST_GROUPS,
    DIAGNOSTIC_FIELDS,
    MATRIX_REQUIRED_KEYS,
    PAGE_CONTRACTS,
    REQUIRED_JSON_KEYS,
    SIDEBAR_GROUPS,
    VIEWPORT_RESPONSIBILITIES,
    VIEWPORTS,
)
from src.browser_acceptance.export_validation import validate_json_download, validate_markdown_download
from src.browser_acceptance.process_manager import allocate_port
from src.browser_acceptance.runner import (
    _click_direct_link,
    _click_grouped_link,
    _collect_group_routes,
    _validate_route_inventory,
    _wait_for_visible_calculation_evidence,
)


class _Candidate:
    def __init__(self, visible: bool):
        self.visible = visible

    def is_visible(self) -> bool:
        return self.visible


class _Locator:
    def __init__(self, candidates: list[_Candidate]):
        self.candidates = candidates
        self.first = self

    def count(self) -> int:
        return len(self.candidates)

    def nth(self, index: int) -> _Candidate:
        return self.candidates[index]

    def wait_for(self, **_kwargs) -> None:
        return None


class _EvidencePage:
    def __init__(self):
        self.hidden_text = _Locator([_Candidate(False), _Candidate(False)])
        self.visible_heading = _Locator([_Candidate(False), _Candidate(True)])
        self.empty_button = _Locator([])

    def get_by_role(self, role: str, **_kwargs):
        return self.empty_button if role == "button" else self.visible_heading

    def get_by_text(self, *_args, **_kwargs):
        return self.hidden_text


class BrowserContractTests(unittest.TestCase):
    def test_exactly_thirteen_registered_page_contracts(self):
        self.assertEqual(13, len(PAGE_CONTRACTS))
        self.assertEqual(13, len({item[0] for item in PAGE_CONTRACTS}))

    def test_exactly_four_sidebar_groups(self):
        self.assertEqual(4, len(SIDEBAR_GROUPS))
        grouped = tuple(title for titles in SIDEBAR_GROUPS.values() for title in titles)
        self.assertEqual(10, len(grouped))
        self.assertEqual(10, len(set(grouped)))

    def test_direct_links_are_not_in_groups(self):
        grouped = {title for titles in SIDEBAR_GROUPS.values() for title in titles}
        self.assertTrue({"Home", "Showcase & Handoff", "Capabilities & Limits"}.isdisjoint(grouped))

    def test_viewports_are_governed(self):
        self.assertEqual({"width": 1440, "height": 1000}, VIEWPORTS["desktop"])
        self.assertEqual({"width": 412, "height": 915}, VIEWPORTS["narrow"])

    def test_browser_groups_are_isolated_and_complete(self):
        self.assertEqual(
            {
                "startup_and_home",
                "desktop_inputs_and_exports",
                "route_inventory",
                "sidebar_group_inventory",
                "narrow_responsive_smoke",
                "runtime_diagnostics",
            },
            set(BROWSER_TEST_GROUPS),
        )
        self.assertIn("desktop_inputs_and_exports", VIEWPORT_RESPONSIBILITIES["desktop"])
        self.assertNotIn("desktop_inputs_and_exports", VIEWPORT_RESPONSIBILITIES["narrow"])
        self.assertIn("narrow_responsive_smoke", VIEWPORT_RESPONSIBILITIES["narrow"])
        self.assertNotIn("narrow_responsive_smoke", VIEWPORT_RESPONSIBILITIES["desktop"])

    def test_streamlit_root_contract_has_no_semantic_main_dependency(self):
        self.assertEqual('[data-testid="stAppViewContainer"]', APP_ROOT_SELECTOR)
        runner_text = (Path(__file__).resolve().parents[2] / "src/browser_acceptance/runner.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('locator("main")', runner_text)
        self.assertNotIn("locator('main')", runner_text)

    def test_calculation_evidence_prefers_visible_semantic_candidate(self):
        candidate = _wait_for_visible_calculation_evidence(_EvidencePage())
        self.assertTrue(candidate.is_visible())

    @patch("src.browser_acceptance.runner._app_ready")
    @patch("src.browser_acceptance.runner._scroll_and_click")
    @patch("src.browser_acceptance.runner._wait_for_first_visible")
    @patch("src.browser_acceptance.runner._open_sidebar_if_needed")
    def test_direct_link_helper_has_explicit_call_path(
        self, open_sidebar, wait_visible, scroll_click, app_ready
    ):
        page = MagicMock()
        link = MagicMock()
        wait_visible.return_value = link
        _click_direct_link(page, "Showcase & Handoff")
        open_sidebar.assert_called_once_with(page)
        page.get_by_role.assert_called_once_with(
            "link", name="Showcase & Handoff", exact=True
        )
        scroll_click.assert_called_once_with(link)
        app_ready.assert_called_once_with(page)

    @patch("src.browser_acceptance.runner._app_ready")
    @patch("src.browser_acceptance.runner._scroll_and_click")
    @patch("src.browser_acceptance.runner._wait_for_first_visible")
    @patch("src.browser_acceptance.runner._ensure_group_expanded")
    @patch("src.browser_acceptance.runner._open_sidebar_if_needed")
    def test_grouped_link_helper_has_explicit_call_path(
        self, open_sidebar, ensure_group, wait_visible, scroll_click, app_ready
    ):
        page = MagicMock()
        link = MagicMock()
        wait_visible.return_value = link
        _click_grouped_link(page, "Workspace", "Project Dashboard")
        open_sidebar.assert_called_once_with(page)
        ensure_group.assert_called_once_with(
            page, "Workspace", "Project Dashboard", physical=True
        )
        page.get_by_role.assert_called_once_with(
            "link", name="Project Dashboard", exact=True
        )
        scroll_click.assert_called_once_with(link)
        app_ready.assert_called_once_with(page)

    @patch("src.browser_acceptance.runner._resolved_link")
    @patch("src.browser_acceptance.runner._ensure_group_expanded")
    def test_group_routes_are_collected_immediately_after_group_expansion(
        self, ensure_group, resolved_link
    ):
        page = MagicMock()
        resolved_link.side_effect = [
            "http://127.0.0.1:8501/dashboard",
            "http://127.0.0.1:8501/register",
        ]
        routes = _collect_group_routes(
            page,
            "http://127.0.0.1:8501",
            "Workspace",
            ("Project Dashboard", "Project Register"),
        )
        ensure_group.assert_called_once_with(page, "Workspace", "Project Dashboard")
        self.assertEqual(
            {
                "Project Dashboard": "http://127.0.0.1:8501/dashboard",
                "Project Register": "http://127.0.0.1:8501/register",
            },
            routes,
        )
        self.assertEqual(
            [
                unittest.mock.call(
                    page,
                    "http://127.0.0.1:8501",
                    "Project Dashboard",
                    group="Workspace",
                ),
                unittest.mock.call(
                    page,
                    "http://127.0.0.1:8501",
                    "Project Register",
                    group="Workspace",
                ),
            ],
            resolved_link.call_args_list,
        )

    def test_route_inventory_requires_thirteen_unique_hrefs(self):
        routes = {
            title: f"http://127.0.0.1:8501/route-{index}"
            for index, (title, _heading, _group) in enumerate(PAGE_CONTRACTS)
        }
        _validate_route_inventory(routes)
        duplicate = dict(routes)
        duplicate[PAGE_CONTRACTS[-1][0]] = duplicate[PAGE_CONTRACTS[0][0]]
        with self.assertRaises(AssertionError):
            _validate_route_inventory(duplicate)

    def test_diagnostic_and_matrix_schemas_are_complete(self):
        self.assertEqual(
            {
                "test_group",
                "current_url",
                "target_title",
                "target_href",
                "visible",
                "bounding_box",
                "viewport",
                "sidebar_scroll_top",
                "sidebar_scroll_height",
            },
            set(DIAGNOSTIC_FIELDS),
        )
        self.assertEqual(
            {"status", "viewport", "groups", "route_inventory", "runtime_events"},
            set(MATRIX_REQUIRED_KEYS),
        )

    def test_ephemeral_port_is_allocated(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_json_validator_accepts_governed_export(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            payload = {key: {} for key in REQUIRED_JSON_KEYS}
            payload["metadata"] = {"synthetic_disclosure": "Synthetic demonstration data only."}
            payload["executive_summary"] = {
                "decision_status": "recommended",
                "preferred_alternative_id": "ALT-001",
                "summary": "Preferred packaging alternative: ALT-001.",
            }
            payload["baseline"] = {"alternative_id": "ALT-BASE"}
            payload["alternatives"] = [
                {
                    "alternative_id": "ALT-001",
                    "recommendation": {
                        "status": "recommended",
                        "rationale": ["Lowest governed evaluated cost."],
                        "constraints": [],
                        "validation_required": ["Engineering validation."],
                    },
                }
            ]
            payload["decision_controls"] = {
                "engineering_validation_required": True,
                "autonomous_technical_approval": False,
            }
            payload["calculation_evidence"] = {"results": [{"calculation_id": "CALC-COST-001"}]}
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(payload, validate_json_download(path))

    def test_json_validator_rejects_missing_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.json"
            path.write_text("{}", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_json_download(path)

    def test_markdown_validator_accepts_required_sections(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text(
                "# Synthetic Data Disclosure\nSynthetic demonstration only.\n"
                "# Packaging Value Engineering Decision Package\n"
                "## Executive Summary\nPreferred packaging alternative: ALT-001.\n"
                "## Alternative Comparison\n- Recommendation: recommended\n"
                "## Independent Calculation Evidence\n"
                "Engineering validation remains mandatory. No realized savings are claimed.\n",
                encoding="utf-8",
            )
            self.assertIn("Calculation Evidence", validate_markdown_download(path))

    def test_markdown_validator_rejects_missing_limitations(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "export.md"
            path.write_text("# Synthetic Data Disclosure", encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_markdown_download(path)


if __name__ == "__main__":
    unittest.main()
