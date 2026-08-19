from __future__ import annotations

import json
import os
import platform
import re
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page, sync_playwright

from .contracts import (
    ACCEPTANCE_REPORT_KEYS,
    ACTION_TIMEOUT_MILLISECONDS,
    APP_ROOT_SELECTOR,
    EXCEPTION_TEXT,
    HOME_HEADING,
    PAGE_CONTRACTS,
    PAGE_TIMEOUT_MILLISECONDS,
    VIEWPORTS,
)
from .diagnostics import RuntimeDiagnostics
from .export_validation import validate_json_download, validate_markdown_download
from .process_manager import StreamlitProcess

SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"
SCHEMA_VERSION = "1.5.0"
MATERIAL_CONSOLE_PATTERNS = (
    "uncaught",
    "traceback",
    "streamlitapiexception",
    "streamlitpagenotfounderror",
)
RESPONSIVE_ROUTE_PREFERENCES = (
    ("Showcase & Handoff", re.compile(r"Showcase", re.I)),
    ("Capabilities & Limits", re.compile(r"Capabilities", re.I)),
)
SIDEBAR_SELECTOR = '[data-testid="stSidebar"]'
SIDEBAR_OPENER_SELECTOR = '[data-testid="stExpandSidebarButton"]'
SIDEBAR_CONTROL_SCOPES = (
    ("stSidebarCollapsedControl", '[data-testid="stSidebarCollapsedControl"]'),
    ("stSidebarHeader", '[data-testid="stSidebarHeader"]'),
    ("stHeader", '[data-testid="stHeader"]'),
)
SIDEBAR_STATES = (
    "OPEN_AND_REACHABLE",
    "PRESENT_OFF_CANVAS",
    "COLLAPSED",
    "TRANSITIONING",
    "MISSING",
    "AMBIGUOUS",
)
SIDEBAR_TRANSITION_TIMEOUT_MILLISECONDS = PAGE_TIMEOUT_MILLISECONDS
SIDEBAR_TRANSITION_POLL_MILLISECONDS = 75
SIDEBAR_TRANSITION_STALL_SAMPLE_LIMIT = 4
_SIDEBAR_PROGRESS_RANK = {
    "COLLAPSED": 0,
    "PRESENT_OFF_CANVAS": 1,
    "TRANSITIONING": 2,
    "OPEN_AND_REACHABLE": 3,
}


def _visible(locator: Locator) -> list[Locator]:
    return [locator.nth(index) for index in range(locator.count()) if locator.nth(index).is_visible()]


def _first_visible(locator: Locator) -> Locator:
    candidates = _visible(locator)
    if not candidates:
        locator.first.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
        candidates = _visible(locator)
    if not candidates:
        raise AssertionError("Expected a visible matching element.")
    return candidates[0]


def _assert_no_visible_exception(page: Page) -> None:
    text = page.locator("body").inner_text()
    found = [marker for marker in EXCEPTION_TEXT if marker in text]
    if found:
        raise AssertionError(f"Visible Streamlit exception markers: {found}")


def _app_ready(page: Page, *, require_home: bool = False) -> None:
    page.locator(APP_ROOT_SELECTOR).wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    if require_home:
        page.get_by_role("heading", name=HOME_HEADING, exact=True).wait_for(
            state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
        )
    _assert_no_visible_exception(page)


def _open_sidebar(page: Page) -> None:
    """Desktop-only semantic opener retained outside the Stage 2 responsive gate."""
    if _visible(page.get_by_role("link", name="Home", exact=True)):
        return
    button = _first_visible(page.get_by_role("button", name=re.compile("sidebar", re.I)))
    button.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    _first_visible(page.get_by_role("link", name="Home", exact=True))


def _expand_group(page: Page, group: str, expected_link: str) -> None:
    _open_sidebar(page)
    expected = page.get_by_role("link", name=expected_link, exact=True)
    if _visible(expected):
        return
    controls = page.get_by_role("button", name=group, exact=True)
    visible_controls = _visible(controls)
    if visible_controls:
        control = visible_controls[0]
    else:
        text_matches = page.get_by_text(group, exact=True)
        visible_text_matches = _visible(text_matches)
        if not visible_text_matches:
            raise AssertionError(f"No visible sidebar group label found for {group!r}.")
        visible_ancestors: list[Locator] = []
        for text_match in visible_text_matches:
            ancestors = text_match.locator(
                "xpath=ancestor-or-self::*[self::button or self::summary or @role='button'][1]"
            )
            visible_ancestors.extend(_visible(ancestors))
        if not visible_ancestors:
            raise AssertionError(f"No visible semantic sidebar control found for {group!r}.")
        control = visible_ancestors[0]
    control.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
    control.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    _first_visible(expected)


def _resolved_link(page: Page, base_url: str, title: str, group: str | None) -> str:
    if group:
        _expand_group(page, group, title)
    else:
        _open_sidebar(page)
    link = _first_visible(page.get_by_role("link", name=title, exact=True))
    href = link.get_attribute("href")
    if not href:
        raise AssertionError(f"Route {title!r} has no href.")
    return urljoin(base_url + "/", href)


def _collect_routes(page: Page, base_url: str) -> dict[str, str]:
    routes = {"Home": base_url}
    for title, _heading, group in PAGE_CONTRACTS[1:]:
        routes[title] = _resolved_link(page, base_url, title, group)
    if len(routes) != 13 or len(set(routes.values())) != 13:
        raise AssertionError("Expected 13 unique resolved destinations.")
    if any(not value.strip() for value in routes.values()):
        raise AssertionError("Route inventory contains an empty destination.")
    return routes


def _visible_link_inventory(page: Page) -> list[dict[str, str]]:
    inventory: list[dict[str, str]] = []
    links = page.get_by_role("link")
    for index in range(links.count()):
        link = links.nth(index)
        if not link.is_visible():
            continue
        name = link.inner_text().strip()
        href = link.get_attribute("href") or ""
        if name:
            inventory.append({"name": name, "href": href})
    return inventory


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _ensure_assumptions_open(page: Page) -> tuple[Locator, Locator]:
    cost = page.get_by_label("Unit-cost adjustment (%)")
    material = page.get_by_label("Material-weight adjustment (%)")
    if _visible(cost) or _visible(material):
        return cost, material
    assumption_text = _first_visible(page.get_by_text(re.compile(r"\bassumptions$", re.I)))
    summary = assumption_text.locator("xpath=ancestor-or-self::summary[1]")
    if not _visible(summary):
        summary = assumption_text.locator(
            "xpath=ancestor-or-self::*[@role='button' or self::button][1]"
        )
    control = _first_visible(summary)
    control.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
    control.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    cost.first.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    return cost, material


def _select_scenario_and_adjust_inputs(page: Page) -> str:
    select = page.get_by_role(
        "combobox", name="Governed synthetic procurement scenario", exact=True
    )
    select.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    select.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    listbox = page.get_by_role("listbox")
    listbox.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    option = _first_visible(listbox.get_by_role("option"))
    scenario_id = option.inner_text().strip()
    if not scenario_id:
        raise AssertionError("Rendered governed scenario option has no accessible text.")
    option.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    listbox.wait_for(state="hidden", timeout=PAGE_TIMEOUT_MILLISECONDS)
    annual = page.get_by_label("Annual volume (cases)")
    annual.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    current = float(annual.input_value())
    annual.fill(str(current + 1000))
    annual.press("Enter")
    page.wait_for_timeout(1000)
    cost, material = _ensure_assumptions_open(page)
    cost_control = _first_visible(cost)
    cost_control.fill("1")
    cost_control.press("Enter")
    page.wait_for_timeout(800)
    if not _visible(material):
        cost, material = _ensure_assumptions_open(page)
    material_control = _first_visible(material)
    material_control.fill("1")
    material_control.press("Enter")
    page.wait_for_timeout(1000)
    _assert_no_visible_exception(page)
    return scenario_id


def _calculation_evidence_visible(page: Page) -> Locator:
    patterns = re.compile(r"^Calculation Evidence(?:\s|$)", re.I)
    candidates = (
        page.get_by_role("button", name=patterns),
        page.get_by_role("heading", name=patterns),
        page.get_by_text("Calculation Evidence", exact=True),
    )
    for locator in candidates:
        visible = _visible(locator)
        if visible:
            return visible[0]
    raise AssertionError("Calculation Evidence was not visibly rendered.")


def _download_exports(page: Page, download_dir: Path) -> tuple[Path, Path]:
    download_dir.mkdir(parents=True, exist_ok=True)
    with page.expect_download(timeout=PAGE_TIMEOUT_MILLISECONDS) as json_info:
        _first_visible(page.get_by_role("button", name="Download machine-readable JSON", exact=True)).click()
    json_path = download_dir / "pve_decision_package.json"
    json_info.value.save_as(json_path)
    validate_json_download(json_path)
    with page.expect_download(timeout=PAGE_TIMEOUT_MILLISECONDS) as markdown_info:
        _first_visible(page.get_by_role("button", name="Download human-readable report", exact=True)).click()
    markdown_path = download_dir / "pve_decision_report.md"
    markdown_info.value.save_as(markdown_path)
    validate_markdown_download(markdown_path)
    return json_path, markdown_path


def _physical_calculation_navigation(page: Page) -> None:
    _expand_group(page, "Evidence & Explanation", "Calculation Evidence")
    link = _first_visible(page.get_by_role("link", name="Calculation Evidence", exact=True))
    link.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
    link.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    page.get_by_role("heading", name=re.compile("Calculation Evidence", re.I)).first.wait_for(
        state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
    )
    _assert_no_visible_exception(page)


def _rect_intersects_viewport(rect: dict | None, viewport: dict) -> bool:
    return bool(
        rect
        and rect["width"] > 0
        and rect["height"] > 0
        and rect["right"] > 0
        and rect["bottom"] > 0
        and rect["left"] < viewport["width"]
        and rect["top"] < viewport["height"]
    )


def _centre_in_viewport(rect: dict | None, viewport: dict) -> bool:
    if not rect:
        return False
    centre_x = rect["left"] + rect["width"] / 2
    centre_y = rect["top"] + rect["height"] / 2
    return 0 <= centre_x <= viewport["width"] and 0 <= centre_y <= viewport["height"]


def _element_evidence(locator: Locator, index: int, scope: str, viewport: dict) -> dict:
    visible = locator.is_visible()
    enabled = locator.is_enabled()
    box = locator.bounding_box()
    dom = locator.evaluate(
        """element => {
            const rect = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            const ancestry = [];
            let parent = element.parentElement;
            let scrollOwner = null;
            while (parent) {
                const parentStyle = getComputedStyle(parent);
                const parentRect = parent.getBoundingClientRect();
                const entry = {
                    tag: parent.tagName,
                    id: parent.id || null,
                    className: typeof parent.className === 'string' ? parent.className : null,
                    role: parent.getAttribute('role'),
                    testid: parent.getAttribute('data-testid'),
                    rect: {left: parentRect.left, top: parentRect.top, right: parentRect.right,
                           bottom: parentRect.bottom, width: parentRect.width, height: parentRect.height},
                    scrollTop: parent.scrollTop, scrollHeight: parent.scrollHeight,
                    clientHeight: parent.clientHeight, scrollWidth: parent.scrollWidth,
                    clientWidth: parent.clientWidth, overflowX: parentStyle.overflowX,
                    overflowY: parentStyle.overflowY, position: parentStyle.position,
                    transform: parentStyle.transform
                };
                ancestry.push(entry);
                if (!scrollOwner && /(auto|scroll|overlay)/.test(parentStyle.overflowX + parentStyle.overflowY)
                    && (parent.scrollHeight > parent.clientHeight || parent.scrollWidth > parent.clientWidth)) {
                    scrollOwner = entry;
                }
                parent = parent.parentElement;
            }
            const role = element.getAttribute('role') ||
                (element.tagName === 'BUTTON' ? 'button' : null);
            const accessibleName = element.getAttribute('aria-label') ||
                element.getAttribute('title') || element.innerText.trim();
            return {
                tagName: element.tagName,
                role,
                accessibleName,
                textContent: element.textContent ? element.textContent.trim() : '',
                ariaLabel: element.getAttribute('aria-label'),
                title: element.getAttribute('title'),
                testid: element.getAttribute('data-testid'),
                id: element.id || null,
                className: typeof element.className === 'string' ? element.className : null,
                rect: {left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom,
                       width: rect.width, height: rect.height},
                computed: {display: style.display, visibility: style.visibility, opacity: style.opacity,
                           pointerEvents: style.pointerEvents, position: style.position,
                           transform: style.transform, overflowX: style.overflowX, overflowY: style.overflowY},
                ancestry, scrollOwner, scrollTop: element.scrollTop,
                scrollHeight: element.scrollHeight, clientHeight: element.clientHeight
            };
        }"""
    )
    rect = dom["rect"]
    centre = {"x": rect["left"] + rect["width"] / 2, "y": rect["top"] + rect["height"] / 2}
    return {
        "candidate_index": index,
        "discovery_scope": scope,
        "tag_name": dom["tagName"],
        "computed_role": dom["role"],
        "accessible_name": dom["accessibleName"],
        "text_content": dom["textContent"],
        "aria_label": dom["ariaLabel"],
        "title": dom["title"],
        "data_testid": dom["testid"],
        "id": dom["id"],
        "class_name": dom["className"],
        "visible": visible,
        "enabled": enabled,
        "bounding_box": box,
        "dom_rect": rect,
        "non_zero_size": rect["width"] > 0 and rect["height"] > 0,
        "viewport_intersection": visible and _rect_intersects_viewport(rect, viewport),
        "centre_point": centre,
        "centre_point_in_viewport": visible and _centre_in_viewport(rect, viewport),
        "computed_display": dom["computed"]["display"],
        "computed_visibility": dom["computed"]["visibility"],
        "computed_opacity": dom["computed"]["opacity"],
        "computed_pointer_events": dom["computed"]["pointerEvents"],
        "computed_position": dom["computed"]["position"],
        "computed_transform": dom["computed"]["transform"],
        "computed_overflow_x": dom["computed"]["overflowX"],
        "computed_overflow_y": dom["computed"]["overflowY"],
        "dom_ancestry": dom["ancestry"],
        "nearest_scroll_owner": dom["scrollOwner"],
        "scrollTop": dom["scrollTop"],
        "scrollHeight": dom["scrollHeight"],
        "clientHeight": dom["clientHeight"],
    }


def _candidate_geometry(locator: Locator, index: int, viewport: dict) -> dict:
    evidence = _element_evidence(locator, index, "route", viewport)
    return {
        "index": index,
        "accessible_name": evidence["accessible_name"],
        "href": locator.get_attribute("href") or "",
        "is_visible": evidence["visible"],
        "is_enabled": evidence["enabled"],
        "non_zero_size": evidence["non_zero_size"],
        "bounding_box": evidence["bounding_box"],
        "rect": evidence["dom_rect"],
        "computed": {
            "display": evidence["computed_display"], "visibility": evidence["computed_visibility"],
            "opacity": evidence["computed_opacity"], "pointerEvents": evidence["computed_pointer_events"],
            "position": evidence["computed_position"], "transform": evidence["computed_transform"],
            "overflowX": evidence["computed_overflow_x"], "overflowY": evidence["computed_overflow_y"],
        },
        "ancestry": evidence["dom_ancestry"],
        "scroll_owner": evidence["nearest_scroll_owner"],
        "intersects_viewport": evidence["viewport_intersection"],
        "centre_in_viewport": evidence["centre_point_in_viewport"],
    }


def _sidebar_container_evidence(page: Page, viewport: dict) -> dict:
    sidebar = page.locator(SIDEBAR_SELECTOR)
    count = sidebar.count()
    if count == 0:
        return {"exists": False, "count": 0, "classification_reason": ["sidebar container missing"]}
    items = []
    for index in range(count):
        item = sidebar.nth(index)
        evidence = _element_evidence(item, index, "stSidebar", viewport)
        evidence["aria_expanded"] = item.get_attribute("aria-expanded")
        items.append(evidence)
    return {"exists": True, "count": count, "candidates": items}


def _classify_sidebar_state(sidebar: dict) -> tuple[str, list[str]]:
    if not sidebar.get("exists"):
        return "MISSING", ["stSidebar does not exist"]
    candidates = sidebar.get("candidates", [])
    if len(candidates) != 1:
        return "AMBIGUOUS", [f"expected one stSidebar container, found {len(candidates)}"]
    item = candidates[0]
    if item["computed_display"] == "none" or item["computed_visibility"] in {"hidden", "collapse"}:
        return "COLLAPSED", ["sidebar is not rendered by computed display/visibility"]
    if str(item["computed_opacity"]) in {"0", "0.0"}:
        return "COLLAPSED", ["sidebar computed opacity is zero"]
    if not item["non_zero_size"]:
        return "COLLAPSED", ["sidebar has zero rendered width or height"]
    if item["visible"] and item["viewport_intersection"]:
        return "OPEN_AND_REACHABLE", [
            "sidebar exists", "Playwright reports visible", "non-zero geometry",
            "computed state is rendered", "rectangle intersects viewport",
        ]
    rect = item["dom_rect"]
    if item["non_zero_size"] and not item["viewport_intersection"]:
        return "PRESENT_OFF_CANVAS", [f"sidebar rectangle is outside viewport: {rect}"]
    if item["visible"] != item["viewport_intersection"]:
        return "TRANSITIONING", ["sidebar visibility and viewport intersection are inconsistent"]
    return "AMBIGUOUS", ["sidebar state did not satisfy a deterministic classification rule"]


def _control_signature(evidence: dict) -> str:
    stable = {
        "discovery_scope": evidence["discovery_scope"],
        "tag_name": evidence["tag_name"],
        "computed_role": evidence["computed_role"],
        "accessible_name": evidence["accessible_name"],
        "title": evidence["title"],
        "aria_label": evidence["aria_label"],
        "data_testid": evidence["data_testid"],
        "id": evidence["id"],
        "dom_rect": evidence["dom_rect"],
        "visible": evidence["visible"],
        "enabled": evidence["enabled"],
        "viewport_intersection": evidence["viewport_intersection"],
    }
    return json.dumps(stable, sort_keys=True, separators=(",", ":"))


def _inventory_sidebar_controls(page: Page, viewport: dict) -> tuple[list[dict], dict[str, int | bool]]:
    records_by_signature: dict[str, dict] = {}
    collapsed_exists = page.locator('[data-testid="stSidebarCollapsedControl"]').count() > 0
    for scope, selector in SIDEBAR_CONTROL_SCOPES:
        root = page.locator(selector)
        for root_index in range(root.count()):
            scoped = root.nth(root_index).locator("button, [role='button'], [aria-label], [title]")
            for index in range(scoped.count()):
                candidate = scoped.nth(index)
                evidence = _element_evidence(candidate, 0, scope, viewport)
                signature = _control_signature(evidence)
                records_by_signature.setdefault(signature, evidence)
    records = [records_by_signature[key] for key in sorted(records_by_signature)]
    for index, record in enumerate(records):
        record["candidate_index"] = index
    summary = {
        "total_inventoried_controls": len(records),
        "total_viewport_intersecting_controls": sum(1 for item in records if item["viewport_intersection"]),
        "stSidebarCollapsedControl_exists": collapsed_exists,
    }
    return records, summary


def _sidebar_payload(page: Page, screenshot_filename: str | None = None) -> dict:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    sidebar = _sidebar_container_evidence(page, viewport)
    state, reasons = _classify_sidebar_state(sidebar)
    controls, summary = _inventory_sidebar_controls(page, viewport)
    return {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "current_url": page.url,
        "viewport": viewport,
        "window": page.evaluate(
            "() => ({innerWidth: window.innerWidth, innerHeight: window.innerHeight, devicePixelRatio: window.devicePixelRatio})"
        ),
        "tested_branch": os.environ.get("TESTED_BRANCH", "UNSPECIFIED"),
        "source_commit": os.environ.get("SOURCE_COMMIT", "UNSPECIFIED"),
        "screenshot_filename": screenshot_filename,
        "sidebar": sidebar,
        "sidebar_state": state,
        "classification_reasons": reasons,
        "controls": controls,
        "control_inventory_summary": summary,
    }


def _capture_sidebar_evidence(page: Page, artifact_dir: Path, screenshots: Path) -> dict:
    screenshot = screenshots / "narrow-pre-action.png"
    page.screenshot(path=screenshot, full_page=True)
    payload = _sidebar_payload(page, str(screenshot.relative_to(artifact_dir)))
    _write_json(artifact_dir / "narrow-sidebar-controls.json", payload)
    return payload


def _non_open_sidebar_error(evidence: dict, artifact_dir: Path) -> AssertionError:
    summary = evidence["control_inventory_summary"]
    return AssertionError(
        "Responsive sidebar is not OPEN_AND_REACHABLE; "
        f"state={evidence['sidebar_state']}; sidebar_exists={evidence['sidebar'].get('exists')}; "
        f"total_controls={summary['total_inventoried_controls']}; "
        f"viewport_intersecting_controls={summary['total_viewport_intersecting_controls']}; "
        f"stSidebarCollapsedControl_exists={summary['stSidebarCollapsedControl_exists']}; "
        f"evidence={artifact_dir / 'narrow-sidebar-controls.json'}"
    )


def _ensure_responsive_sidebar_open(page: Page, evidence: dict, artifact_dir: Path) -> dict:
    state = evidence["sidebar_state"]
    if state == "OPEN_AND_REACHABLE":
        evidence["sidebar_transition"] = None
        return evidence
    if state != "COLLAPSED":
        raise _non_open_sidebar_error(evidence, artifact_dir)

    viewport = page.viewport_size or VIEWPORTS["narrow"]
    opener_matches = page.locator(SIDEBAR_OPENER_SELECTOR)
    match_count = opener_matches.count()
    action = {
        "schema_version": SCHEMA_VERSION,
        "locator": SIDEBAR_OPENER_SELECTOR,
        "match_count": match_count,
        "pre_click_sidebar_state": state,
        "click_attempted": False,
        "click_completed": False,
        "observer_timeout_milliseconds": SIDEBAR_TRANSITION_TIMEOUT_MILLISECONDS,
        "polling_policy": {"mode": "deterministic_poll", "poll_interval_milliseconds": SIDEBAR_TRANSITION_POLL_MILLISECONDS},
        "stall_policy": {"max_non_progress_samples": SIDEBAR_TRANSITION_STALL_SAMPLE_LIMIT},
        "sample_count": 0,
        "samples": [],
        "first_progress_sample": None,
        "first_viewport_intersecting_sample": None,
        "first_open_and_reachable_sample": None,
        "second_stable_open_sample": None,
        "stable_open_streak": 0,
        "stall_detected": False,
        "timeout_reached": False,
        "regression_detected": False,
        "terminal_state": None,
        "terminal_reason": None,
        "total_elapsed_milliseconds": None,
    }
    if match_count != 1:
        _write_json(artifact_dir / "narrow-sidebar-post-open.json", action)
        raise AssertionError(f"Expected exactly one responsive sidebar opener; found {match_count}.")

    opener = opener_matches.nth(0)
    opener_evidence = _element_evidence(opener, 0, "stHeader", viewport)
    action["opener"] = opener_evidence
    failures = []
    if not opener_evidence["visible"]:
        failures.append("not visible")
    if not opener_evidence["enabled"]:
        failures.append("not enabled")
    if not opener_evidence["viewport_intersection"]:
        failures.append("does not intersect viewport")
    if failures:
        _write_json(artifact_dir / "narrow-sidebar-post-open.json", action)
        raise AssertionError("Responsive sidebar opener is " + ", ".join(failures) + ".")

    action["click_attempted"] = True
    started = monotonic()
    opener.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    action["click_completed"] = True
    action, latest_sidebar = _observe_sidebar_transition(page, action, started)
    action["post_click_sidebar_state"] = action["terminal_state"]
    action["post_open_sidebar"] = latest_sidebar
    _write_json(artifact_dir / "narrow-sidebar-post-open.json", action)
    if action["terminal_state"] != "OPEN_AND_REACHABLE" or action["stable_open_streak"] < 2:
        raise AssertionError(
            "Responsive sidebar did not achieve two consecutive OPEN_AND_REACHABLE samples after exact opener click; "
            f"terminal_state={action['terminal_state']}; reason={action['terminal_reason']}; "
            f"evidence={artifact_dir / 'narrow-sidebar-post-open.json'}"
        )
    post_open = _sidebar_payload(page)
    post_open["sidebar_transition"] = action
    sidebar_candidate = post_open["sidebar"]["candidates"][0]
    if not sidebar_candidate["viewport_intersection"] or not sidebar_candidate["non_zero_size"]:
        raise AssertionError("Post-open sidebar geometry is not viewport-reachable and non-zero.")
    return post_open


def _sidebar_geometry(page: Page) -> dict:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    sidebar = _sidebar_container_evidence(page, viewport)
    state, reasons = _classify_sidebar_state(sidebar)
    return {"state": state, "reasons": reasons, **sidebar}


def _transition_sample(page: Page, sequence: int, started: float, stable_open_streak: int) -> tuple[dict, dict]:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    sidebar = _sidebar_container_evidence(page, viewport)
    state, reasons = _classify_sidebar_state(sidebar)
    candidate = sidebar["candidates"][0] if sidebar.get("count") == 1 else None
    rect = candidate["dom_rect"] if candidate else {}
    sample = {
        "sequence_number": sequence,
        "elapsed_milliseconds": round((monotonic() - started) * 1000, 3),
        "state": state,
        "classification_reasons": reasons,
        "sidebar_exists": sidebar.get("exists", False),
        "sidebar_count": sidebar.get("count", 0),
        "visible": candidate["visible"] if candidate else False,
        "width": rect.get("width"),
        "height": rect.get("height"),
        "left": rect.get("left"),
        "right": rect.get("right"),
        "top": rect.get("top"),
        "bottom": rect.get("bottom"),
        "transform": candidate.get("computed_transform") if candidate else None,
        "opacity": candidate.get("computed_opacity") if candidate else None,
        "viewport_intersection": candidate.get("viewport_intersection") if candidate else False,
        "centre_point_in_viewport": candidate.get("centre_point_in_viewport") if candidate else False,
        "forward_progress": {"progressed": False, "reasons": []},
        "stable_open_streak": stable_open_streak,
    }
    return sample, {"state": state, "reasons": reasons, **sidebar}


def _transition_progress(previous: dict | None, current: dict) -> tuple[bool, list[str]]:
    if previous is None:
        return True, ["initial sample"]
    reasons: list[str] = []
    previous_rank = _SIDEBAR_PROGRESS_RANK.get(previous["state"], -1)
    current_rank = _SIDEBAR_PROGRESS_RANK.get(current["state"], -1)
    if current_rank > previous_rank:
        reasons.append("state progressed toward OPEN_AND_REACHABLE")
    if previous.get("viewport_intersection") is False and current.get("viewport_intersection") is True:
        reasons.append("viewport intersection became true")
    previous_left = previous.get("left")
    current_left = current.get("left")
    if isinstance(previous_left, (int, float)) and isinstance(current_left, (int, float)):
        if abs(current_left) < abs(previous_left):
            reasons.append("left edge moved toward viewport")
    previous_right = previous.get("right")
    current_right = current.get("right")
    if isinstance(previous_right, (int, float)) and isinstance(current_right, (int, float)):
        if current_right > previous_right:
            reasons.append("right edge moved toward viewport")
    previous_width = previous.get("width")
    current_width = current.get("width")
    if isinstance(previous_width, (int, float)) and isinstance(current_width, (int, float)):
        if current_width > previous_width:
            reasons.append("width increased")
    if previous.get("transform") != current.get("transform"):
        reasons.append("transform changed")
    return bool(reasons), reasons


def _observe_sidebar_transition(page: Page, action: dict, started: float) -> tuple[dict, dict]:
    samples: list[dict] = []
    sequence = 0
    stable_open_streak = 0
    stall_streak = 0
    first_progress_sample = None
    first_viewport_sample = None
    first_open_sample = None
    second_stable_open_sample = None
    terminal_reason = "timeout"
    terminal_state = "TRANSITIONING"
    timeout_reached = False
    stalled = False
    regression_detected = False
    saw_open_state = False
    previous_sample: dict | None = None
    latest_sidebar = {"exists": False, "count": 0, "candidates": []}

    while True:
        sequence += 1
        sample, sidebar = _transition_sample(page, sequence, started, stable_open_streak)
        latest_sidebar = sidebar
        progressed, progress_reasons = _transition_progress(previous_sample, sample)
        sample["forward_progress"] = {"progressed": progressed, "reasons": progress_reasons}
        if progressed and first_progress_sample is None and sequence > 1:
            first_progress_sample = sample
        if sample["viewport_intersection"] and first_viewport_sample is None:
            first_viewport_sample = sample
        if sample["state"] == "OPEN_AND_REACHABLE":
            if not sample.get("width"):
                terminal_reason = "inconsistent evidence: OPEN_AND_REACHABLE without positive width"
                terminal_state = sample["state"]
                samples.append(sample)
                break
            if not sample.get("height"):
                terminal_reason = "inconsistent evidence: OPEN_AND_REACHABLE without positive height"
                terminal_state = sample["state"]
                samples.append(sample)
                break
            if not sample["viewport_intersection"]:
                terminal_reason = "inconsistent evidence: OPEN_AND_REACHABLE without viewport intersection"
                terminal_state = sample["state"]
                samples.append(sample)
                break
            stable_open_streak += 1
            sample["stable_open_streak"] = stable_open_streak
            if first_open_sample is None:
                first_open_sample = sample
            if stable_open_streak == 2 and second_stable_open_sample is None:
                second_stable_open_sample = sample
        else:
            if stable_open_streak > 0:
                stable_open_streak = 0
                sample["stable_open_streak"] = stable_open_streak
                if saw_open_state:
                    regression_detected = True
                    terminal_reason = "regression after open progression"
                    terminal_state = sample["state"]
                    samples.append(sample)
                    break
            if sample["state"] in {"COLLAPSED", "PRESENT_OFF_CANVAS", "TRANSITIONING"}:
                stall_streak = 0 if progressed else stall_streak + 1
            else:
                stall_streak = 0
        saw_open_state = saw_open_state or sample["state"] == "OPEN_AND_REACHABLE"
        samples.append(sample)
        previous_sample = sample

        if sample["state"] in {"MISSING", "AMBIGUOUS"}:
            terminal_reason = f"non-actionable state: {sample['state']}"
            terminal_state = sample["state"]
            break
        if stable_open_streak >= 2:
            terminal_reason = "two consecutive OPEN_AND_REACHABLE samples observed"
            terminal_state = sample["state"]
            break
        if stall_streak >= SIDEBAR_TRANSITION_STALL_SAMPLE_LIMIT:
            stalled = True
            terminal_reason = "bounded stall while sidebar remained non-open"
            terminal_state = sample["state"]
            break
        elapsed = round((monotonic() - started) * 1000, 3)
        if elapsed >= SIDEBAR_TRANSITION_TIMEOUT_MILLISECONDS:
            timeout_reached = True
            terminal_reason = "observer timeout before stable OPEN_AND_REACHABLE"
            terminal_state = sample["state"]
            break
        page.wait_for_timeout(SIDEBAR_TRANSITION_POLL_MILLISECONDS)

    action.update({
        "sample_count": len(samples),
        "samples": samples,
        "first_progress_sample": first_progress_sample,
        "first_viewport_intersecting_sample": first_viewport_sample,
        "first_open_and_reachable_sample": first_open_sample,
        "second_stable_open_sample": second_stable_open_sample,
        "stable_open_streak": stable_open_streak,
        "stall_detected": stalled,
        "timeout_reached": timeout_reached,
        "regression_detected": regression_detected,
        "terminal_state": terminal_state,
        "terminal_reason": terminal_reason,
        "total_elapsed_milliseconds": round((monotonic() - started) * 1000, 3),
    })
    return action, latest_sidebar


def _select_viewport_candidate(page: Page, title: str, artifact_dir: Path) -> tuple[Locator, dict]:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    sidebar = page.locator(SIDEBAR_SELECTOR)
    sidebar_count = sidebar.count()
    if sidebar_count != 1:
        raise AssertionError(f"Expected one open sidebar scope for responsive route selection; found {sidebar_count}.")
    scoped_sidebar = sidebar.nth(0)
    locator = scoped_sidebar.get_by_role("link", name=title, exact=True)
    candidate_count = locator.count()
    if candidate_count != 1:
        raise AssertionError(
            f"Expected exactly one semantic {title!r} link in the open sidebar before scroll; found {candidate_count}."
        )
    selected = locator.nth(0)
    pre_scroll = _candidate_geometry(selected, 0, viewport)
    diagnostics = {
        "schema_version": SCHEMA_VERSION,
        "title": title,
        "viewport": viewport,
        "semantic_scope": SIDEBAR_SELECTOR,
        "post_scroll_reacquired_match_count": None,
        "visible": None,
        "enabled": None,
        "intersects_viewport": None,
        "centre_in_viewport": None,
        "pointer_events_enabled": None,
        "click_attempted": False,
        "click_completed": False,
        "sidebar": _sidebar_geometry(page),
        "pre_scroll": pre_scroll,
        "post_scroll": None,
    }
    _write_json(artifact_dir / "narrow-candidate-geometry.json", diagnostics)
    return selected, {"diagnostics": diagnostics, "pre_scroll": pre_scroll}


def _responsive_physical_route(
    page: Page,
    routes: dict[str, str],
    screenshots: Path,
    artifact_dir: Path,
    runtime_diagnostics: RuntimeDiagnostics,
) -> str:
    phase = "pre-action-evidence"
    sidebar_evidence: dict | None = None
    latest_sidebar_state_sample: dict | None = None
    transition_terminal_reason = None
    transition_sample_count = 0
    transition_stable_open_streak = 0
    route_selection_reached = False
    selected_title: str | None = None
    pre_scroll_reached = False
    post_scroll_reacquisition_reached = False
    route_click_attempted = False
    route_click_completed = False
    destination_verification_reached = False
    evidence_write_status = {
        "narrow_pre_action": False,
        "narrow_sidebar_controls": False,
        "narrow_sidebar_post_open": False,
        "narrow_link_inventory": False,
        "narrow_candidate_geometry": False,
        "failure_screenshot": False,
        "failure_context": False,
    }
    try:
        sidebar_evidence = _capture_sidebar_evidence(page, artifact_dir, screenshots)
        evidence_write_status["narrow_pre_action"] = True
        evidence_write_status["narrow_sidebar_controls"] = True
        phase = "sidebar-state-classification"
        sidebar_evidence = _ensure_responsive_sidebar_open(page, sidebar_evidence, artifact_dir)
        evidence_write_status["narrow_sidebar_post_open"] = (
            artifact_dir / "narrow-sidebar-post-open.json"
        ).exists()
        transition = sidebar_evidence.get("sidebar_transition") if isinstance(sidebar_evidence, dict) else None
        if transition:
            samples = transition.get("samples", [])
            latest_sidebar_state_sample = samples[-1] if samples else None
            transition_terminal_reason = transition.get("terminal_reason")
            transition_sample_count = transition.get("sample_count", 0)
            transition_stable_open_streak = transition.get("stable_open_streak", 0)
        else:
            latest_sidebar_state_sample = {
                "state": sidebar_evidence.get("sidebar_state"),
                "classification_reasons": sidebar_evidence.get("classification_reasons", []),
            }

        phase = "route-inventory"
        _write_json(artifact_dir / "narrow-link-inventory.json", _visible_link_inventory(page))
        evidence_write_status["narrow_link_inventory"] = True
        route_selection_reached = True
        selected_heading = None
        selected_link: Locator | None = None
        selection_evidence: dict | None = None
        preferred_title, preferred_heading = RESPONSIVE_ROUTE_PREFERENCES[0]
        fallback_title, fallback_heading = RESPONSIVE_ROUTE_PREFERENCES[1]
        sidebar_scope = page.locator(SIDEBAR_SELECTOR)
        scope_count = sidebar_scope.count()
        if scope_count != 1:
            raise AssertionError(f"Expected one open sidebar scope for route enumeration; found {scope_count}.")
        sidebar_scope = sidebar_scope.nth(0)

        preferred_matches = sidebar_scope.get_by_role("link", name=preferred_title, exact=True)
        preferred_count = preferred_matches.count()
        fallback_matches = sidebar_scope.get_by_role("link", name=fallback_title, exact=True)
        fallback_count = fallback_matches.count()
        candidate_evidence = {
            "schema_version": SCHEMA_VERSION,
            "preference_order": [preferred_title, fallback_title],
            "preferred_title": preferred_title,
            "preferred_match_count": preferred_count,
            "fallback_title": fallback_title,
            "fallback_match_count": fallback_count,
            "fallback_evaluated": preferred_count == 0,
            "fallback_reason": "preferred absent" if preferred_count == 0 else "preferred available",
            "selected_title": None,
            "semantic_scope": SIDEBAR_SELECTOR,
            "pre_scroll_geometry": None,
            "post_scroll_reacquired_match_count": None,
            "post_scroll_geometry": None,
            "visible": None,
            "enabled": None,
            "intersects_viewport": None,
            "centre_in_viewport": None,
            "pointer_events_enabled": None,
            "click_attempted": False,
            "click_completed": False,
            "destination_heading_result": None,
            "sidebar": _sidebar_geometry(page),
        }
        phase = "route-candidate-selection"
        if preferred_count > 1:
            _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
            evidence_write_status["narrow_candidate_geometry"] = True
            raise AssertionError(f"Preferred responsive route {preferred_title!r} is ambiguous; found {preferred_count} matches.")
        if preferred_count == 1:
            selected_title = preferred_title
            selected_heading = preferred_heading
            selected_link, selection_evidence = _select_viewport_candidate(page, preferred_title, artifact_dir)
            evidence_write_status["narrow_candidate_geometry"] = True
            candidate_evidence["fallback_evaluated"] = False
            candidate_evidence["fallback_reason"] = "preferred uniquely available"
        elif fallback_count > 1:
            _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
            evidence_write_status["narrow_candidate_geometry"] = True
            raise AssertionError(f"Fallback responsive route {fallback_title!r} is ambiguous; found {fallback_count} matches.")
        elif fallback_count == 1:
            selected_title = fallback_title
            selected_heading = fallback_heading
            selected_link, selection_evidence = _select_viewport_candidate(page, fallback_title, artifact_dir)
            evidence_write_status["narrow_candidate_geometry"] = True
        else:
            _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
            evidence_write_status["narrow_candidate_geometry"] = True
            raise AssertionError("Neither preferred nor fallback responsive route exists in the open sidebar.")
        candidate_evidence["selected_title"] = selected_title
        candidate_evidence["pre_scroll_geometry"] = selection_evidence["pre_scroll"]

        material_console = _material_console_errors(runtime_diagnostics.console_errors)
        if runtime_diagnostics.page_errors or material_console:
            raise AssertionError(
                f"Responsive pre-click runtime errors: page={runtime_diagnostics.page_errors}, console={material_console}"
            )

        phase = "route-scroll-and-click"
        pre_scroll_reached = True
        selected_link.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
        reacquired = page.locator(SIDEBAR_SELECTOR).nth(0).get_by_role("link", name=selected_title, exact=True)
        post_scroll_reacquisition_reached = True
        reacquired_count = reacquired.count()
        candidate_evidence["post_scroll_reacquired_match_count"] = reacquired_count
        if reacquired_count != 1:
            _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
            raise AssertionError(
                f"Post-scroll responsive route reacquisition must remain unique; found {reacquired_count} matches."
            )
        selected_link = reacquired.nth(0)
        viewport = page.viewport_size or VIEWPORTS["narrow"]
        post_scroll = _candidate_geometry(selected_link, 0, viewport)
        if not post_scroll["intersects_viewport"]:
            raise AssertionError("Selected responsive route no longer intersects the viewport after scrolling.")
        if not post_scroll["centre_in_viewport"]:
            raise AssertionError("Selected responsive route centre is outside the viewport after scrolling.")
        if not post_scroll["is_visible"]:
            raise AssertionError("Selected responsive route is not visible before click.")
        if not post_scroll["is_enabled"]:
            raise AssertionError("Selected responsive route is not enabled before click.")
        if not post_scroll["non_zero_size"]:
            raise AssertionError("Selected responsive route has non-positive geometry before click.")
        if post_scroll["computed"]["pointerEvents"] == "none":
            raise AssertionError("Selected responsive route pointer events are disabled before click.")
        candidate_evidence.update({
            "post_scroll_geometry": post_scroll,
            "visible": post_scroll["is_visible"],
            "enabled": post_scroll["is_enabled"],
            "intersects_viewport": post_scroll["intersects_viewport"],
            "centre_in_viewport": post_scroll["centre_in_viewport"],
            "pointer_events_enabled": post_scroll["computed"]["pointerEvents"] != "none",
        })
        _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
        route_click_attempted = True
        candidate_evidence["click_attempted"] = True
        selected_link.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
        route_click_completed = True
        candidate_evidence["click_completed"] = True
        _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)

        phase = "destination-heading"
        page.get_by_role("heading", name=selected_heading).first.wait_for(
            state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
        )
        destination_verification_reached = True
        candidate_evidence["destination_heading_result"] = "visible"
        _write_json(artifact_dir / "narrow-candidate-geometry.json", candidate_evidence)
        _app_ready(page)

        phase = "narrow-calculation-evidence"
        calculation_url = routes.get("Calculation Evidence")
        if not calculation_url:
            raise AssertionError("Resolved Calculation Evidence destination is unavailable.")
        page.goto(calculation_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MILLISECONDS)
        _app_ready(page)
        page.get_by_role("heading", name=re.compile("Calculation Evidence", re.I)).first.wait_for(
            state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
        )
        _assert_no_visible_exception(page)
        page.screenshot(path=screenshots / "narrow-smoke.png", full_page=True)
        return selected_title
    except Exception as exc:
        try:
            page.screenshot(path=screenshots / "failure.png", full_page=True)
            evidence_write_status["failure_screenshot"] = True
        except Exception:
            pass
        if sidebar_evidence is None:
            try:
                sidebar_evidence = _capture_sidebar_evidence(page, artifact_dir, screenshots)
                evidence_write_status["narrow_sidebar_controls"] = True
            except Exception:
                sidebar_evidence = {"sidebar_state": "AMBIGUOUS", "sidebar": {}, "control_inventory_summary": {}}
        try:
            _write_json(artifact_dir / "narrow-link-inventory.json", _visible_link_inventory(page))
            evidence_write_status["narrow_link_inventory"] = True
        except Exception:
            pass
        post_open_path = artifact_dir / "narrow-sidebar-post-open.json"
        if post_open_path.exists():
            evidence_write_status["narrow_sidebar_post_open"] = True
            if latest_sidebar_state_sample is None:
                try:
                    payload = json.loads(post_open_path.read_text(encoding="utf-8"))
                    transition = payload.get("samples", [])
                    if transition:
                        latest_sidebar_state_sample = transition[-1]
                    transition_terminal_reason = payload.get("terminal_reason", transition_terminal_reason)
                    transition_sample_count = payload.get("sample_count", transition_sample_count)
                    transition_stable_open_streak = payload.get("stable_open_streak", transition_stable_open_streak)
                except Exception:
                    pass
        geometry_path = artifact_dir / "narrow-candidate-geometry.json"
        if geometry_path.exists():
            evidence_write_status["narrow_candidate_geometry"] = True
        context = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "failing_phase": phase,
            "current_url": page.url,
            "source_commit": os.environ.get("SOURCE_COMMIT", "UNSPECIFIED"),
            "tested_branch": os.environ.get("TESTED_BRANCH", "UNSPECIFIED"),
            "latest_sidebar_state_sample": latest_sidebar_state_sample,
            "latest_sidebar_state": latest_sidebar_state_sample.get("state") if isinstance(latest_sidebar_state_sample, dict) else sidebar_evidence.get("sidebar_state"),
            "transition_terminal_reason": transition_terminal_reason,
            "transition_sample_count": transition_sample_count,
            "stable_open_streak": transition_stable_open_streak,
            "route_selection_reached": route_selection_reached,
            "selected_route": selected_title,
            "pre_scroll_reached": pre_scroll_reached,
            "post_scroll_reacquisition_reached": post_scroll_reacquisition_reached,
            "route_click_attempted": route_click_attempted,
            "route_click_completed": route_click_completed,
            "destination_verification_reached": destination_verification_reached,
            "sidebar_classification": sidebar_evidence.get("sidebar_state"),
            "sidebar_details": sidebar_evidence.get("sidebar"),
            "control_inventory_summary": sidebar_evidence.get("control_inventory_summary"),
            "evidence_filenames": {
                "pre_action": "screenshots/narrow-pre-action.png",
                "failure": "screenshots/failure.png",
                "sidebar_controls": "narrow-sidebar-controls.json",
                "sidebar_post_open": "narrow-sidebar-post-open.json",
                "narrow_link_inventory": "narrow-link-inventory.json",
                "narrow_candidate_geometry": "narrow-candidate-geometry.json",
                "failure_context": "failure-context.json",
            },
            "evidence_write_status": evidence_write_status,
        }
        try:
            evidence_write_status["failure_context"] = True
            context["evidence_write_status"] = evidence_write_status
            _write_json(artifact_dir / "failure-context.json", context)
        except Exception:
            evidence_write_status["failure_context"] = False
        if not geometry_path.exists():
            _write_json(geometry_path, {"error": "candidate geometry unavailable", **context})
            evidence_write_status["narrow_candidate_geometry"] = True
        raise


def _material_console_errors(values: list[str]) -> list[str]:
    return [value for value in values if any(pattern in value.lower() for pattern in MATERIAL_CONSOLE_PATTERNS)]


def run_minimal_acceptance() -> dict:
    root = Path(__file__).resolve().parents[2]
    artifact_dir = root / os.environ.get("BROWSER_ARTIFACT_DIR", "browser-artifacts/gate3b")
    screenshots = artifact_dir / "screenshots"
    downloads = artifact_dir / "downloads"
    logs = artifact_dir / "logs"
    screenshots.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    report = {key: None for key in ACCEPTANCE_REPORT_KEYS}
    report.update({
        "schema_version": SCHEMA_VERSION,
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": os.environ.get("SOURCE_COMMIT", "UNSPECIFIED"),
        "tested_branch": os.environ.get("TESTED_BRANCH", "UNSPECIFIED"),
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "python_version": platform.python_version(),
        "desktop_viewport": VIEWPORTS["desktop"],
        "narrow_viewport": VIEWPORTS["narrow"],
        "json_export_valid": False,
        "markdown_export_valid": False,
        "calculation_evidence_visible": False,
        "physical_navigation_passed": False,
        "narrow_smoke_passed": False,
        "tracked_files_unchanged": True,
        "overall_disposition": "FAIL",
    })
    diagnostics = RuntimeDiagnostics()
    routes: dict[str, str] = {}
    active_page: Page | None = None
    try:
        with StreamlitProcess(root, logs / "streamlit.log") as app:
            with sync_playwright() as playwright:
                report["playwright_version"] = getattr(playwright, "__version__", "managed")
                browser = playwright.chromium.launch()
                report["chromium_version"] = browser.version
                desktop_context = browser.new_context(viewport=VIEWPORTS["desktop"], accept_downloads=True)
                page = desktop_context.new_page()
                active_page = page
                diagnostics.bind(page)
                page.goto(app.base_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MILLISECONDS)
                _app_ready(page, require_home=True)
                page.screenshot(path=screenshots / "home-desktop.png", full_page=True)
                routes = _collect_routes(page, app.base_url)
                report["scenario_id"] = _select_scenario_and_adjust_inputs(page)
                _calculation_evidence_visible(page)
                report["calculation_evidence_visible"] = True
                page.screenshot(path=screenshots / "calculation-evidence-desktop.png", full_page=True)
                _download_exports(page, downloads)
                report["json_export_valid"] = True
                report["markdown_export_valid"] = True
                _physical_calculation_navigation(page)
                report["physical_navigation_passed"] = True
                desktop_context.close()

                narrow_context = browser.new_context(viewport=VIEWPORTS["narrow"])
                narrow = narrow_context.new_page()
                active_page = narrow
                diagnostics.bind(narrow)
                narrow.goto(app.base_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MILLISECONDS)
                _app_ready(narrow, require_home=True)
                report["responsive_route"] = _responsive_physical_route(
                    narrow, routes, screenshots, artifact_dir, diagnostics
                )
                report["narrow_smoke_passed"] = True
                narrow_context.close()
                browser.close()

        material_console = _material_console_errors(diagnostics.console_errors)
        report.update({
            "route_count": len(routes),
            "unique_route_count": len(set(routes.values())),
            "visible_exception_count": 0,
            "page_error_count": len(diagnostics.page_errors),
            "console_error_count": len(material_console),
        })
        required_passes = (
            report["route_count"] == 13,
            report["unique_route_count"] == 13,
            report["json_export_valid"],
            report["markdown_export_valid"],
            report["calculation_evidence_visible"],
            report["physical_navigation_passed"],
            report["narrow_smoke_passed"],
            report["page_error_count"] == 0,
            report["console_error_count"] == 0,
        )
        if not all(required_passes):
            raise AssertionError(f"Gate 3B acceptance controls failed: {report}")
        report["overall_disposition"] = "PASS"
        return report
    except Exception as exc:
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        if active_page is not None:
            try:
                active_page.screenshot(path=screenshots / "failure.png", full_page=True)
                _write_json(artifact_dir / "narrow-link-inventory.json", _visible_link_inventory(active_page))
            except Exception:
                pass
        failure_context = artifact_dir / "failure-context.json"
        if not failure_context.exists():
            _write_json(failure_context, report["failure"])
        raise
    finally:
        report["route_count"] = report.get("route_count") or len(routes)
        report["unique_route_count"] = report.get("unique_route_count") or len(set(routes.values()))
        report["page_error_count"] = report.get("page_error_count") if report.get("page_error_count") is not None else len(diagnostics.page_errors)
        report["console_error_count"] = report.get("console_error_count") if report.get("console_error_count") is not None else len(_material_console_errors(diagnostics.console_errors))
        report["visible_exception_count"] = report.get("visible_exception_count") if report.get("visible_exception_count") is not None else 0
        _write_json(artifact_dir / "route-inventory.json", routes)
        diagnostics.write(artifact_dir / "runtime-events.json")
        _write_json(artifact_dir / "acceptance-report.json", report)


def main() -> None:
    report = run_minimal_acceptance()
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
