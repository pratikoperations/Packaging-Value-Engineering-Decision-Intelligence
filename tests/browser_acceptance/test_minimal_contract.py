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


def _responsive_source() -> str:
    source = _runner_source()
    start = source.index("def _responsive_physical_route")
    end = source.index("\ndef _material_console_errors", start)
    return source[start:end]


def _sidebar_stage_source() -> str:
    source = _runner_source()
    start = source.index("def _sidebar_container_evidence")
    end = source.index("\ndef _select_viewport_candidate", start)
    return source[start:end]


def _opener_source() -> str:
    source = _runner_source()
    start = source.index("def _ensure_responsive_sidebar_open")
    end = source.index("\ndef _sidebar_geometry", start)
    return source[start:end]


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
        for key in ("source_commit", "unique_route_count", "physical_navigation_passed", "narrow_smoke_passed", "overall_disposition"):
            self.assertIn(key, ACCEPTANCE_REPORT_KEYS)

    def test_json_validator_accepts_governed_export(self):
        payload = {
            "metadata": {"synthetic_disclosure": "Synthetic demonstration data only."},
            "executive_summary": {}, "project": {}, "scenario": {}, "baseline": {},
            "alternatives": [],
            "decision_controls": {"autonomous_technical_approval": False, "engineering_validation_required": True},
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
        self.assertEqual(["Traceback (most recent call last)"], visible_exception_markers("Traceback (most recent call last)"))
        self.assertEqual(["Uncaught TypeError", "Traceback in browser"], material_console_errors(["harmless warning", "Uncaught TypeError", "Traceback in browser"]))

    def test_ephemeral_port_allocation(self):
        port = allocate_port()
        self.assertGreater(port, 0)
        self.assertLess(port, 65536)

    def test_single_governed_runner_entry_point_is_lazy(self):
        from src.browser_acceptance import run_minimal_acceptance
        self.assertTrue(callable(run_minimal_acceptance))

    def test_desktop_grouped_navigation_remains_mandatory(self):
        source = _runner_source()
        self.assertIn('_expand_group(page, "Evidence & Explanation", "Calculation Evidence")', source)
        self.assertIn("_physical_calculation_navigation(page)", source)
        self.assertIn('report["physical_navigation_passed"] = True', source)

    def test_group_fallback_remains_semantic_and_visible(self):
        source = _runner_source()
        start = source.index("def _expand_group")
        end = source.index("\ndef _resolved_link", start)
        group_source = source[start:end]
        self.assertIn('page.get_by_role("button", name=group, exact=True)', group_source)
        self.assertIn('page.get_by_text(group, exact=True)', group_source)
        self.assertNotIn("session_state", group_source)
        self.assertNotIn("retry", group_source.lower())
        self.assertNotIn("page.wait_for_timeout", group_source)

    def test_responsive_stage_does_not_call_desktop_opener(self):
        responsive = _responsive_source()
        self.assertNotIn("_open_sidebar(page)", responsive)
        self.assertIn("_capture_sidebar_evidence", responsive)
        self.assertIn("_ensure_responsive_sidebar_open", responsive)

    def test_home_link_is_not_responsive_state_contract(self):
        stage = _sidebar_stage_source()
        self.assertNotIn('name="Home"', stage)
        self.assertIn("SIDEBAR_SELECTOR", stage)
        self.assertIn("_classify_sidebar_state", stage)

    def test_all_six_sidebar_states_are_declared(self):
        source = _runner_source()
        for state in ("OPEN_AND_REACHABLE", "PRESENT_OFF_CANVAS", "COLLAPSED", "TRANSITIONING", "MISSING", "AMBIGUOUS"):
            self.assertIn(f'"{state}"', source)

    def test_open_state_requires_geometry_and_viewport_intersection(self):
        stage = _sidebar_stage_source()
        for token in ('item["non_zero_size"]', 'item["viewport_intersection"]', 'item["visible"]', 'item["computed_display"]', 'item["computed_visibility"]', 'item["computed_opacity"]'):
            self.assertIn(token, stage)

    def test_random_dom_identifier_is_removed(self):
        source = _runner_source()
        self.assertNotIn("Math.random", source)
        self.assertNotIn("data-gate3b-evidence-id", source)
        self.assertNotIn("gate3bEvidenceId", source)

    def test_control_inventory_is_non_mutating_and_deterministic(self):
        source = _runner_source()
        inventory = source[source.index("def _control_signature"):source.index("\ndef _sidebar_payload")]
        self.assertIn("json.dumps(stable, sort_keys=True", inventory)
        self.assertIn("records_by_signature.setdefault", inventory)
        self.assertIn("for key in sorted(records_by_signature)", inventory)
        self.assertNotIn("dataset", inventory)
        self.assertNotIn("setAttribute", inventory)
        self.assertNotIn("removeAttribute", inventory)
        self.assertNotIn("candidate.evaluate", inventory)

    def test_control_inventory_uses_nth_enumeration(self):
        source = _runner_source()
        inventory = source[source.index("def _inventory_sidebar_controls"):source.index("\ndef _sidebar_payload")]
        self.assertIn("for root_index in range(root.count())", inventory)
        self.assertIn("for index in range(scoped.count())", inventory)
        self.assertIn("root.nth(root_index)", inventory)
        self.assertIn("scoped.nth(index)", inventory)

    def test_control_inventory_captures_required_metadata(self):
        source = _runner_source()
        for token in ('"computed_role"', '"accessible_name"', '"aria_label"', '"title"', '"data_testid"', '"bounding_box"', '"dom_rect"', '"viewport_intersection"', '"centre_point_in_viewport"', '"computed_pointer_events"', '"dom_ancestry"', '"nearest_scroll_owner"', '"scrollTop"', '"scrollHeight"', '"clientHeight"'):
            self.assertIn(token, source)

    def test_exact_streamlit_opener_locator_is_governed(self):
        source = _runner_source()
        self.assertIn("SIDEBAR_OPENER_SELECTOR = '[data-testid=\"stExpandSidebarButton\"]'", source)
        opener = _opener_source()
        self.assertIn("page.locator(SIDEBAR_OPENER_SELECTOR)", opener)
        self.assertNotIn("get_by_role", opener)
        self.assertNotIn("keyboard_double_arrow_right", opener)

    def test_opener_is_used_only_for_collapsed_state(self):
        opener = _opener_source()
        self.assertIn('if state == "OPEN_AND_REACHABLE":', opener)
        self.assertIn('if state != "COLLAPSED":', opener)
        self.assertLess(opener.index('if state != "COLLAPSED":'), opener.index("page.locator(SIDEBAR_OPENER_SELECTOR)"))

    def test_non_actionable_states_fail_before_locator(self):
        opener = _opener_source()
        self.assertIn("raise _non_open_sidebar_error", opener)
        for state in ("PRESENT_OFF_CANVAS", "TRANSITIONING", "MISSING", "AMBIGUOUS"):
            self.assertIn(f'"{state}"', _runner_source())

    def test_opener_requires_unique_visible_enabled_intersecting_control(self):
        opener = _opener_source()
        self.assertIn("if match_count != 1", opener)
        self.assertIn('opener_evidence["visible"]', opener)
        self.assertIn('opener_evidence["enabled"]', opener)
        self.assertIn('opener_evidence["viewport_intersection"]', opener)

    def test_exact_opener_uses_one_normal_click(self):
        opener = _opener_source()
        self.assertEqual(1, opener.count("opener.click(timeout=ACTION_TIMEOUT_MILLISECONDS)"))
        self.assertNotIn("force=True", opener)
        self.assertNotIn("dispatch_event", opener)
        self.assertNotIn("page.mouse", opener)
        self.assertNotIn("evaluate", opener)

    def test_post_open_evidence_and_state_are_required(self):
        opener = _opener_source()
        self.assertIn('artifact_dir / "narrow-sidebar-post-open.json"', opener)
        self.assertIn('page.locator(SIDEBAR_SELECTOR).wait_for(state="visible"', opener)
        self.assertIn('post_open["sidebar_state"] != "OPEN_AND_REACHABLE"', opener)
        self.assertIn('sidebar_candidate["viewport_intersection"]', opener)
        self.assertIn('sidebar_candidate["non_zero_size"]', opener)

    def test_responsive_sidebar_path_has_no_first_fallback(self):
        responsive = _responsive_source()
        before_route = responsive.split('phase = "route-candidate-selection"', 1)[0]
        self.assertNotIn(".first.wait_for", before_route)
        self.assertNotIn(".first.click", before_route)
        self.assertNotIn("_first_visible", before_route)

    def test_pre_action_evidence_precedes_state_gate(self):
        responsive = _responsive_source()
        self.assertLess(responsive.index("_capture_sidebar_evidence"), responsive.index("_ensure_responsive_sidebar_open"))
        self.assertIn('screenshots / "narrow-pre-action.png"', _runner_source())
        self.assertIn('artifact_dir / "narrow-sidebar-controls.json"', _runner_source())

    def test_route_candidate_selection_runs_after_sidebar_gate(self):
        responsive = _responsive_source()
        self.assertLess(responsive.index("_ensure_responsive_sidebar_open"), responsive.index('phase = "route-candidate-selection"'))

    def test_route_candidate_selection_remains_viewport_based(self):
        source = _runner_source()
        selector = source[source.index("def _select_viewport_candidate"):source.index("\ndef _responsive_physical_route")]
        self.assertIn("for index in range(locator.count())", selector)
        self.assertIn("global_candidate_count", selector)
        self.assertIn("sidebar_candidate_count", selector)
        self.assertIn("if len(qualifying) != 1", selector)
        self.assertIn("Expected exactly one viewport-intersecting", selector)

    def test_route_preference_is_preserved(self):
        source = _runner_source()
        self.assertLess(source.index('("Showcase & Handoff"'), source.index('("Capabilities & Limits"'))

    def test_post_scroll_geometry_is_revalidated(self):
        responsive = _responsive_source()
        self.assertIn("scroll_into_view_if_needed", responsive)
        self.assertIn("post_scroll = _candidate_geometry", responsive)
        self.assertIn('post_scroll["intersects_viewport"]', responsive)
        self.assertIn('post_scroll["centre_in_viewport"]', responsive)
        self.assertIn("selected_link.click(timeout=ACTION_TIMEOUT_MILLISECONDS)", responsive)

    def test_narrow_calculation_evidence_uses_governed_destination(self):
        responsive = _responsive_source()
        self.assertIn('routes.get("Calculation Evidence")', responsive)
        self.assertIn("page.goto(calculation_url", responsive)
        self.assertIn('name=re.compile("Calculation Evidence", re.I)', responsive)

    def test_failure_evidence_is_inside_responsive_boundary(self):
        responsive = _responsive_source()
        for token in ('screenshots / "failure.png"', 'artifact_dir / "failure-context.json"', '"failing_phase"', '"evidence_write_status"', '"control_inventory_summary"', '"sidebar_post_open"'):
            self.assertIn(token, responsive)
        self.assertIn("raise", responsive)

    def test_acceptance_cannot_pass_without_responsive_assertion(self):
        source = _runner_source()
        run_source = source[source.index("def run_minimal_acceptance"):]
        self.assertLess(run_source.index("_responsive_physical_route("), run_source.index('report["narrow_smoke_passed"] = True'))
        self.assertLess(run_source.index('report["narrow_smoke_passed"] = True'), run_source.index('report["narrow_smoke_passed"],'))
        self.assertLess(run_source.index('report["narrow_smoke_passed"],'), run_source.index('report["overall_disposition"] = "PASS"'))

    def test_static_prohibition_controls(self):
        source = _runner_source()
        prohibited = ("force=True", "dispatch_event(", "document.querySelector", "session_state", "page.mouse.click", "locator.click()", "retry(", "time.sleep(", "nth-child")
        for token in prohibited:
            self.assertNotIn(token, source)
        responsive = _responsive_source()
        self.assertNotIn("page.wait_for_timeout", responsive)
        self.assertNotIn("page.evaluate", responsive)

    def test_documentation_records_stage_two_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        for phrase in (
            "Stage 1 physically established that the narrow sidebar is `COLLAPSED`",
            "`[data-testid=\"stExpandSidebarButton\"]`",
            "one exact evidence-backed physical opener click",
            "removes random evidence identifiers and all evidence-only DOM mutation",
            "new exact-head standard CI run is required",
            "new exact-head physical Chromium run is required",
            "browser acceptance remains unpassed",
            "no production browser certification is claimed",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
