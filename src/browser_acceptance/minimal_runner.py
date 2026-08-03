from __future__ import annotations

import json
import os
import platform
import re
from datetime import datetime, timezone
from pathlib import Path
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
SCHEMA_VERSION = "1.3.0"
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
    """Desktop-only semantic opener retained outside the Stage 1 responsive gate."""
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


def _inventory_sidebar_controls(page: Page, viewport: dict) -> tuple[list[dict], dict[str, int | bool]]:
    records: list[dict] = []
    seen: set[str] = set()
    collapsed_exists = page.locator('[data-testid="stSidebarCollapsedControl"]').count() > 0
    for scope, selector in SIDEBAR_CONTROL_SCOPES:
        root = page.locator(selector)
        for root_index in range(root.count()):
            scoped = root.nth(root_index).locator("button, [role='button'], [aria-label], [title]")
            for index in range(scoped.count()):
                candidate = scoped.nth(index)
                key = candidate.evaluate(
                    """element => {
                        if (!element.dataset.gate3bEvidenceId) {
                            element.dataset.gate3bEvidenceId = 'gate3b-' + Math.random().toString(36).slice(2);
                        }
                        return element.dataset.gate3bEvidenceId;
                    }"""
                )
                if key in seen:
                    continue
                seen.add(key)
                records.append(_element_evidence(candidate, len(records), scope, viewport))
    summary = {
        "total_inventoried_controls": len(records),
        "total_viewport_intersecting_controls": sum(1 for item in records if item["viewport_intersection"]),
        "stSidebarCollapsedControl_exists": collapsed_exists,
    }
    return records, summary


def _capture_sidebar_evidence(page: Page, artifact_dir: Path, screenshots: Path) -> dict:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    screenshot = screenshots / "narrow-pre-action.png"
    page.screenshot(path=screenshot, full_page=True)
    sidebar = _sidebar_container_evidence(page, viewport)
    state, reasons = _classify_sidebar_state(sidebar)
    controls, summary = _inventory_sidebar_controls(page, viewport)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "current_url": page.url,
        "viewport": viewport,
        "window": page.evaluate(
            "() => ({innerWidth: window.innerWidth, innerHeight: window.innerHeight, devicePixelRatio: window.devicePixelRatio})"
        ),
        "tested_branch": os.environ.get("TESTED_BRANCH", "UNSPECIFIED"),
        "source_commit": os.environ.get("SOURCE_COMMIT", "UNSPECIFIED"),
        "screenshot_filename": str(screenshot.relative_to(artifact_dir)),
        "sidebar": sidebar,
        "sidebar_state": state,
        "classification_reasons": reasons,
        "controls": controls,
        "control_inventory_summary": summary,
    }
    _write_json(artifact_dir / "narrow-sidebar-controls.json", payload)
    return payload


def _require_open_responsive_sidebar(evidence: dict, artifact_dir: Path) -> None:
    state = evidence["sidebar_state"]
    if state == "OPEN_AND_REACHABLE":
        return
    summary = evidence["control_inventory_summary"]
    raise AssertionError(
        "Responsive sidebar is not OPEN_AND_REACHABLE; "
        f"state={state}; sidebar_exists={evidence['sidebar'].get('exists')}; "
        f"total_controls={summary['total_inventoried_controls']}; "
        f"viewport_intersecting_controls={summary['total_viewport_intersecting_controls']}; "
        f"stSidebarCollapsedControl_exists={summary['stSidebarCollapsedControl_exists']}; "
        f"evidence={artifact_dir / 'narrow-sidebar-controls.json'}"
    )


def _sidebar_geometry(page: Page) -> dict:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    sidebar = _sidebar_container_evidence(page, viewport)
    state, reasons = _classify_sidebar_state(sidebar)
    return {"state": state, "reasons": reasons, **sidebar}


def _select_viewport_candidate(page: Page, title: str, artifact_dir: Path) -> tuple[Locator, dict]:
    viewport = page.viewport_size or VIEWPORTS["narrow"]
    global_matches = page.get_by_role("link", name=title, exact=True)
    sidebar = page.locator(SIDEBAR_SELECTOR)
    scoped_matches = sidebar.get_by_role("link", name=title, exact=True)
    locator = scoped_matches if scoped_matches.count() else global_matches
    diagnostics = {
        "title": title,
        "viewport": viewport,
        "window_inner": page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})"),
        "global_candidate_count": global_matches.count(),
        "sidebar_candidate_count": scoped_matches.count(),
        "selection_scope": "sidebar" if scoped_matches.count() else "global",
        "sidebar": _sidebar_geometry(page),
        "candidates": [],
    }
    qualifying: list[tuple[Locator, dict]] = []
    for index in range(locator.count()):
        candidate = locator.nth(index)
        geometry = _candidate_geometry(candidate, index, viewport)
        diagnostics["candidates"].append(geometry)
        if geometry["intersects_viewport"]:
            qualifying.append((candidate, geometry))
    _write_json(artifact_dir / "narrow-candidate-geometry.json", diagnostics)
    if len(qualifying) != 1:
        raise AssertionError(
            f"Expected exactly one viewport-intersecting {title!r} link; "
            f"found {len(qualifying)} from {locator.count()} scoped candidates."
        )
    selected, pre_scroll = qualifying[0]
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
    evidence_write_status = {
        "narrow_pre_action": False,
        "narrow_sidebar_controls": False,
        "failure_screenshot": False,
        "failure_context": False,
    }
    try:
        sidebar_evidence = _capture_sidebar_evidence(page, artifact_dir, screenshots)
        evidence_write_status["narrow_pre_action"] = True
        evidence_write_status["narrow_sidebar_controls"] = True
        phase = "sidebar-state-classification"
        _require_open_responsive_sidebar(sidebar_evidence, artifact_dir)

        phase = "route-inventory"
        _write_json(artifact_dir / "narrow-link-inventory.json", _visible_link_inventory(page))
        selected_title: str | None = None
        selected_heading = None
        selected_link: Locator | None = None
        selection_evidence: dict | None = None
        selection_errors: list[str] = []
        phase = "route-candidate-selection"
        for title, heading in RESPONSIVE_ROUTE_PREFERENCES:
            if page.get_by_role("link", name=title, exact=True).count() == 0:
                continue
            try:
                selected_link, selection_evidence = _select_viewport_candidate(page, title, artifact_dir)
                selected_title = title
                selected_heading = heading
                break
            except AssertionError as exc:
                selection_errors.append(str(exc))
        if selected_link is None or selected_title is None or selected_heading is None:
            raise AssertionError(
                "No preferred controlled responsive route has exactly one viewport-intersecting candidate: "
                + "; ".join(selection_errors)
            )

        material_console = _material_console_errors(runtime_diagnostics.console_errors)
        if runtime_diagnostics.page_errors or material_console:
            raise AssertionError(
                f"Responsive pre-click runtime errors: page={runtime_diagnostics.page_errors}, console={material_console}"
            )

        phase = "route-scroll-and-click"
        selected_link.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
        viewport = page.viewport_size or VIEWPORTS["narrow"]
        post_scroll = _candidate_geometry(selected_link, selection_evidence["pre_scroll"]["index"], viewport)
        if not post_scroll["intersects_viewport"]:
            raise AssertionError("Selected responsive route no longer intersects the viewport after scrolling.")
        if not post_scroll["centre_in_viewport"]:
            raise AssertionError("Selected responsive route centre is outside the viewport after scrolling.")
        if not selected_link.is_visible():
            raise AssertionError("Selected responsive route is not visible before click.")
        evidence = selection_evidence["diagnostics"]
        evidence.update({
            "selected_title": selected_title,
            "selected_candidate_index": selection_evidence["pre_scroll"]["index"],
            "selected_href": selection_evidence["pre_scroll"]["href"],
            "pre_scroll_bounding_rectangle": selection_evidence["pre_scroll"]["rect"],
            "post_scroll_bounding_rectangle": post_scroll["rect"],
        })
        _write_json(artifact_dir / "narrow-candidate-geometry.json", evidence)
        selected_link.click(timeout=ACTION_TIMEOUT_MILLISECONDS)

        phase = "destination-heading"
        page.get_by_role("heading", name=selected_heading).first.wait_for(
            state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
        )
        evidence["destination_heading_result"] = "visible"
        _write_json(artifact_dir / "narrow-candidate-geometry.json", evidence)
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
        except Exception:
            pass
        context = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "failing_phase": phase,
            "current_url": page.url,
            "source_commit": os.environ.get("SOURCE_COMMIT", "UNSPECIFIED"),
            "tested_branch": os.environ.get("TESTED_BRANCH", "UNSPECIFIED"),
            "sidebar_classification": sidebar_evidence.get("sidebar_state"),
            "sidebar_details": sidebar_evidence.get("sidebar"),
            "control_inventory_summary": sidebar_evidence.get("control_inventory_summary"),
            "evidence_filenames": {
                "pre_action": "screenshots/narrow-pre-action.png",
                "failure": "screenshots/failure.png",
                "sidebar_controls": "narrow-sidebar-controls.json",
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
        geometry_path = artifact_dir / "narrow-candidate-geometry.json"
        if not geometry_path.exists():
            _write_json(geometry_path, {"error": "candidate geometry unavailable", **context})
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
