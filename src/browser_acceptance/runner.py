from __future__ import annotations

import json
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin, urlparse

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from .contracts import (
    ACTION_TIMEOUT_MILLISECONDS,
    APP_ROOT_SELECTOR,
    BROWSER_TEST_GROUPS,
    DIAGNOSTIC_FIELDS,
    MATRIX_REQUIRED_KEYS,
    PAGE_CONTRACTS,
    PAGE_TIMEOUT_MILLISECONDS,
    SIDEBAR_GROUPS,
    SIDEBAR_SELECTOR,
    VIEWPORT_RESPONSIBILITIES,
    VIEWPORTS,
)
from .diagnostics import RuntimeDiagnostics
from .export_validation import validate_json_download, validate_markdown_download
from .process_manager import StreamlitProcess

EXCEPTION_TEXT = (
    "StreamlitAPIException",
    "StreamlitPageNotFoundError",
    "Traceback (most recent call last)",
)
ASSUMPTION_LABEL = re.compile(r"^[A-Za-z0-9_-]+ assumptions$", re.IGNORECASE)
CALCULATION_EVIDENCE_LABEL = re.compile(r"^Calculation Evidence(?:\s|$)", re.IGNORECASE)
DIRECT_TITLES = ("Home", "Showcase & Handoff", "Capabilities & Limits")
HOME_HEADING = "Packaging Value Engineering Decision Intelligence"


def _visible_candidates(locator: Locator) -> list[Locator]:
    return [locator.nth(index) for index in range(locator.count()) if locator.nth(index).is_visible()]


def _first_visible(locator: Locator) -> Locator:
    visible = _visible_candidates(locator)
    if not visible:
        raise AssertionError("Expected at least one visible matching element.")
    return visible[0]


def _wait_for_first_visible(
    locator: Locator, *, timeout: int = PAGE_TIMEOUT_MILLISECONDS
) -> Locator:
    """Wait within a fixed bound for any matching locator to become visible."""
    deadline = time.monotonic() + timeout / 1000
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        count = locator.count()
        if count:
            for index in range(count):
                candidate = locator.nth(index)
                if candidate.is_visible():
                    return candidate
            remaining = max(1, int((deadline - time.monotonic()) * 1000))
            try:
                locator.first.wait_for(state="visible", timeout=remaining)
            except PlaywrightTimeoutError as exc:
                last_error = exc
            visible = _visible_candidates(locator)
            if visible:
                return visible[0]
        else:
            remaining = max(1, int((deadline - time.monotonic()) * 1000))
            try:
                locator.first.wait_for(state="attached", timeout=remaining)
            except PlaywrightTimeoutError as exc:
                last_error = exc
    raise AssertionError("Expected at least one visible matching element within timeout.") from last_error


def _wait_for_visible_calculation_evidence(page: Page) -> Locator:
    """Resolve the rendered Calculation Evidence component without selecting hidden duplicates."""
    candidates = (
        page.get_by_role("button", name=CALCULATION_EVIDENCE_LABEL),
        page.get_by_role("heading", name=CALCULATION_EVIDENCE_LABEL),
        page.get_by_text(CALCULATION_EVIDENCE_LABEL, exact=True),
    )
    deadline = time.monotonic() + PAGE_TIMEOUT_MILLISECONDS / 1000
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        for locator in candidates:
            visible = _visible_candidates(locator)
            if visible:
                return visible[0]
        remaining = max(1, int((deadline - time.monotonic()) * 1000))
        try:
            candidates[-1].first.wait_for(state="attached", timeout=min(250, remaining))
        except PlaywrightTimeoutError as exc:
            last_error = exc
    raise AssertionError("No visible Calculation Evidence component was rendered.") from last_error


def _app_ready(page: Page, *, require_home_heading: bool = False) -> None:
    root = page.locator(APP_ROOT_SELECTOR)
    root.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    if require_home_heading:
        page.get_by_role("heading", name=HOME_HEADING, exact=True).wait_for(
            state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS
        )
    else:
        page.wait_for_function(
            """
            selector => {
                const root = document.querySelector(selector);
                if (!root) return false;
                const text = (root.innerText || '').trim();
                const headings = Array.from(
                    root.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]')
                ).filter(element => {
                    const style = window.getComputedStyle(element);
                    const rect = element.getBoundingClientRect();
                    return style.visibility !== 'hidden' && style.display !== 'none'
                        && rect.width > 0 && rect.height > 0;
                });
                return headings.length > 0 || text.length >= 20;
            }
            """,
            arg=APP_ROOT_SELECTOR,
            timeout=PAGE_TIMEOUT_MILLISECONDS,
        )
    _assert_no_visible_exception(page)


def _assert_no_visible_exception(page: Page) -> None:
    body = page.locator("body").inner_text()
    found = [text for text in EXCEPTION_TEXT if text in body]
    if found:
        raise AssertionError(f"Visible Streamlit exception markers: {found}")


def _open_sidebar_if_needed(page: Page) -> None:
    home_links = page.get_by_role("link", name="Home", exact=True)
    if _visible_candidates(home_links):
        return
    buttons = page.get_by_role("button", name=re.compile("sidebar", re.IGNORECASE))
    button = _wait_for_first_visible(buttons)
    button.click()
    _wait_for_first_visible(home_links)


def _scroll_and_click(locator: Locator) -> None:
    locator.evaluate("element => element.scrollIntoView({block: 'center', inline: 'nearest'})")
    locator.click()


def _ensure_group_expanded(page: Page, group: str, expected_link: str, *, physical: bool = False) -> None:
    _open_sidebar_if_needed(page)
    links = page.get_by_role("link", name=expected_link, exact=True)
    if _visible_candidates(links):
        return
    control = _wait_for_first_visible(page.get_by_text(group, exact=True))
    if physical:
        _scroll_and_click(control)
    else:
        control.evaluate("element => element.click()")
    _wait_for_first_visible(links)


def _sidebar_metrics(page: Page) -> dict[str, int | None]:
    sidebar = page.locator(SIDEBAR_SELECTOR)
    if not sidebar.count():
        return {"sidebar_scroll_top": None, "sidebar_scroll_height": None}
    values = sidebar.first.evaluate(
        "element => ({scrollTop: element.scrollTop, scrollHeight: element.scrollHeight})"
    )
    return {
        "sidebar_scroll_top": int(values.get("scrollTop", 0)),
        "sidebar_scroll_height": int(values.get("scrollHeight", 0)),
    }


def _action_state(
    page: Page,
    test_group: str,
    target_title: str,
    locator: Locator | None = None,
    target_href: str | None = None,
) -> dict[str, Any]:
    visible = False
    bounding_box = None
    outer_html = None
    if locator is not None and locator.count():
        candidate = locator.first
        visible = candidate.is_visible()
        bounding_box = candidate.bounding_box()
        try:
            outer_html = candidate.evaluate("element => element.outerHTML")
        except Exception:
            outer_html = None
    state = {
        "test_group": test_group,
        "current_url": page.url,
        "target_title": target_title,
        "target_href": target_href,
        "visible": visible,
        "bounding_box": bounding_box,
        "viewport": page.viewport_size,
        "target_outer_html": outer_html,
        **_sidebar_metrics(page),
    }
    missing = [field for field in DIAGNOSTIC_FIELDS if field not in state]
    if missing:
        raise AssertionError(f"Action diagnostics missing fields: {missing}")
    return state


def _failure_snapshot(page: Page, artifacts: Path, group: str, error: Exception) -> dict[str, Any]:
    artifacts.mkdir(parents=True, exist_ok=True)
    screenshot = artifacts / f"failure-{group}.png"
    page.screenshot(path=str(screenshot), full_page=True)
    return {
        "error": f"{type(error).__name__}: {error}",
        "current_url": page.url,
        "visible_headings": [item.inner_text() for item in _visible_candidates(page.get_by_role("heading"))],
        "visible_links": [item.inner_text() for item in _visible_candidates(page.get_by_role("link"))],
        "viewport": page.viewport_size,
        "screenshot": str(screenshot),
        **_sidebar_metrics(page),
    }


def _goto_home(page: Page, base_url: str) -> None:
    page.goto(base_url, wait_until="domcontentloaded")
    _app_ready(page, require_home_heading=True)


def _select_second_governed_scenario(page: Page) -> None:
    scenario = page.locator(
        'input[role="combobox"][aria-label="Governed synthetic procurement scenario"]'
    )
    scenario.first.wait_for()
    if scenario.count() != 1:
        raise AssertionError("Expected one governed synthetic scenario input.")
    scenario.click()
    options = page.get_by_role("option")
    options.first.wait_for()
    if options.count() < 2:
        raise AssertionError("Expected at least two governed synthetic scenario options.")
    options.nth(1).click()
    _app_ready(page)


def _download_and_validate(page: Page, artifacts: Path) -> dict[str, str]:
    downloads = artifacts / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    with page.expect_download(timeout=15_000) as info:
        page.get_by_role("button", name="Download machine-readable JSON", exact=True).click()
    json_path = downloads / "pve_decision_package.json"
    info.value.save_as(json_path)
    validate_json_download(json_path)
    with page.expect_download(timeout=15_000) as info:
        page.get_by_role("button", name="Download human-readable report", exact=True).click()
    markdown_path = downloads / "pve_decision_report.md"
    info.value.save_as(markdown_path)
    validate_markdown_download(markdown_path)
    return {"json": str(json_path), "markdown": str(markdown_path)}


def _resolved_link(page: Page, base_url: str, title: str, *, group: str | None) -> str:
    try:
        link = _wait_for_first_visible(page.get_by_role("link", name=title, exact=True))
        href = link.get_attribute("href")
        if not href:
            raise AssertionError("link has no href")
        return urljoin(base_url, href).rstrip("/")
    except Exception as exc:
        location = f"sidebar group {group!r}" if group else "direct routes"
        raise AssertionError(f"Failed collecting route {title!r} from {location}: {exc}") from exc


def _collect_group_routes(page: Page, base_url: str, group: str, titles: tuple[str, ...]) -> dict[str, str]:
    if not titles:
        return {}
    try:
        _ensure_group_expanded(page, group, titles[0])
    except Exception as exc:
        raise AssertionError(f"Failed opening sidebar group {group!r}: {exc}") from exc
    return {title: _resolved_link(page, base_url, title, group=group) for title in titles}


def _collect_route_inventory(page: Page, base_url: str) -> dict[str, str]:
    _goto_home(page, base_url)
    _open_sidebar_if_needed(page)
    routes: dict[str, str] = {"Home": base_url.rstrip("/")}
    for title in DIRECT_TITLES:
        if title != "Home":
            routes[title] = _resolved_link(page, base_url, title, group=None)
    for group, titles in SIDEBAR_GROUPS.items():
        routes.update(_collect_group_routes(page, base_url, group, titles))
    _validate_route_inventory(routes)
    return routes


def _validate_route_inventory(routes: dict[str, str]) -> None:
    expected = {title for title, _heading, _group in PAGE_CONTRACTS}
    if set(routes) != expected:
        raise AssertionError(f"Route inventory titles mismatch: {sorted(routes)}")
    if len(routes) != 13 or len(set(routes.values())) != 13:
        raise AssertionError("Expected 13 unique resolved destinations including Home.")
    for title, href in routes.items():
        parsed = urlparse(href)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise AssertionError(f"Route {title} has invalid href: {href}")


def _group_startup_and_home(page: Page, base_url: str, artifacts: Path, result: dict[str, Any]) -> None:
    _goto_home(page, base_url)
    body = page.locator(APP_ROOT_SELECTOR).inner_text()
    if body.lower().count("synthetic") < 2:
        raise AssertionError("Required synthetic disclosures are not visible.")
    _select_second_governed_scenario(page)
    result["scenario_selected"] = True


def _ensure_assumptions_expanded(page: Page) -> None:
    _open_sidebar_if_needed(page)
    cost_inputs = page.get_by_role("spinbutton", name="Unit-cost adjustment (%)", exact=True)
    if _visible_candidates(cost_inputs):
        return
    control = _wait_for_first_visible(page.get_by_text(ASSUMPTION_LABEL, exact=True))
    _scroll_and_click(control)
    _wait_for_first_visible(cost_inputs)


def _group_desktop_inputs_and_exports(
    page: Page, base_url: str, artifacts: Path, result: dict[str, Any]
) -> None:
    _goto_home(page, base_url)
    _select_second_governed_scenario(page)
    _open_sidebar_if_needed(page)
    annual = _wait_for_first_visible(
        page.get_by_role("spinbutton", name="Annual volume (cases)", exact=True)
    )
    annual.fill("1010000")
    annual.press("Enter")
    _ensure_assumptions_expanded(page)
    cost = _wait_for_first_visible(
        page.get_by_role("spinbutton", name="Unit-cost adjustment (%)", exact=True)
    )
    cost.fill("1")
    cost.press("Enter")
    _ensure_assumptions_expanded(page)
    material = _wait_for_first_visible(
        page.get_by_role("spinbutton", name="Material-weight adjustment (%)", exact=True)
    )
    material.fill("-1")
    material.press("Enter")
    page.get_by_role("heading", name="Scenario Comparison", exact=True).wait_for()
    page.get_by_role("heading", name="Preferred Alternative", exact=True).wait_for()
    page.get_by_role("heading", name="Explainable Recommendation Detail", exact=True).wait_for()
    evidence = _wait_for_visible_calculation_evidence(page)
    result["actions"].append(
        _action_state(page, "desktop_inputs_and_exports", "Calculation Evidence", evidence)
    )
    result["downloads"] = _download_and_validate(page, artifacts)
    result["sidebar_adjustments_exercised"] = True


def _group_route_inventory(page: Page, base_url: str, artifacts: Path, result: dict[str, Any]) -> None:
    routes = _collect_route_inventory(page, base_url)
    checked: dict[str, dict[str, Any]] = {}
    for title, href in routes.items():
        result["actions"].append(_action_state(page, "route_inventory", title, target_href=href))
        page.goto(href, wait_until="domcontentloaded")
        _app_ready(page, require_home_heading=(title == "Home"))
        if page.url.rstrip("/") != href.rstrip("/"):
            raise AssertionError(f"Route {title} resolved to unexpected URL {page.url}; expected {href}")
        checked[title] = {
            "href": href,
            "visible_headings": [
                item.inner_text() for item in _visible_candidates(page.get_by_role("heading"))
            ],
        }
    result["route_inventory"] = checked


def _group_sidebar_group_inventory(
    page: Page, base_url: str, artifacts: Path, result: dict[str, Any]
) -> None:
    _goto_home(page, base_url)
    _open_sidebar_if_needed(page)
    groups: dict[str, list[str]] = {}
    for group, expected in SIDEBAR_GROUPS.items():
        try:
            _ensure_group_expanded(page, group, expected[0])
            visible: list[str] = []
            for title in expected:
                _wait_for_first_visible(page.get_by_role("link", name=title, exact=True))
                visible.append(title)
            groups[group] = visible
        except Exception as exc:
            raise AssertionError(f"Sidebar group inventory failed for {group!r}: {exc}") from exc
    result["sidebar_groups"] = groups


def _click_direct_link(page: Page, title: str) -> None:
    _open_sidebar_if_needed(page)
    link = _wait_for_first_visible(page.get_by_role("link", name=title, exact=True))
    _scroll_and_click(link)
    _app_ready(page)


def _click_grouped_link(page: Page, group: str, title: str) -> None:
    _open_sidebar_if_needed(page)
    _ensure_group_expanded(page, group, title, physical=True)
    link = _wait_for_first_visible(page.get_by_role("link", name=title, exact=True))
    _scroll_and_click(link)
    _app_ready(page)


def _group_narrow_responsive_smoke(
    page: Page, base_url: str, artifacts: Path, result: dict[str, Any]
) -> None:
    _goto_home(page, base_url)
    _select_second_governed_scenario(page)
    result["downloads"] = _download_and_validate(page, artifacts)
    _click_direct_link(page, "Showcase & Handoff")
    _goto_home(page, base_url)
    _click_grouped_link(page, "Workspace", "Project Dashboard")
    _goto_home(page, base_url)
    result["representative_clicks"] = ["Showcase & Handoff", "Project Dashboard", "Home"]
    result["sidebar_adjustments_exercised"] = False


def _group_runtime_diagnostics(
    page: Page, base_url: str, artifacts: Path, result: dict[str, Any]
) -> None:
    _goto_home(page, base_url)
    _select_second_governed_scenario(page)
    _assert_no_visible_exception(page)
    result["visible_exception_markers"] = []


GROUP_FUNCTIONS: dict[str, Callable[[Page, str, Path, dict[str, Any]], None]] = {
    "startup_and_home": _group_startup_and_home,
    "desktop_inputs_and_exports": _group_desktop_inputs_and_exports,
    "route_inventory": _group_route_inventory,
    "sidebar_group_inventory": _group_sidebar_group_inventory,
    "narrow_responsive_smoke": _group_narrow_responsive_smoke,
    "runtime_diagnostics": _group_runtime_diagnostics,
}


def _run_group(
    browser: Any,
    base_url: str,
    artifacts: Path,
    viewport_name: str,
    viewport: dict[str, int],
    group: str,
) -> dict[str, Any]:
    if group not in VIEWPORT_RESPONSIBILITIES[viewport_name]:
        return {"status": "skipped", "reason": f"Not assigned to {viewport_name}"}
    group_artifacts = artifacts / viewport_name / group
    group_artifacts.mkdir(parents=True, exist_ok=True)
    diagnostics = RuntimeDiagnostics()
    context = browser.new_context(viewport=viewport, accept_downloads=True)
    page = context.new_page()
    page.set_default_timeout(ACTION_TIMEOUT_MILLISECONDS)
    page.set_default_navigation_timeout(PAGE_TIMEOUT_MILLISECONDS)
    diagnostics.attach(page)
    result: dict[str, Any] = {"status": "running", "actions": []}
    try:
        GROUP_FUNCTIONS[group](page, base_url, group_artifacts, result)
        diagnostics.assert_clean()
        result["status"] = "passed"
    except Exception as exc:
        result["status"] = "failed"
        result["failure"] = _failure_snapshot(page, group_artifacts, group, exc)
    finally:
        result["runtime_events"] = diagnostics.canonical()
        context.close()
    return result


def _run_viewport(
    base_url: str,
    artifacts: Path,
    viewport_name: str,
    viewport: dict[str, int],
) -> dict[str, Any]:
    matrix: dict[str, Any] = {
        "status": "running",
        "viewport": viewport_name,
        "groups": {},
        "route_inventory": {},
        "runtime_events": {},
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for group in BROWSER_TEST_GROUPS:
            outcome = _run_group(browser, base_url, artifacts, viewport_name, viewport, group)
            matrix["groups"][group] = outcome
            if group == "route_inventory" and outcome.get("status") == "passed":
                matrix["route_inventory"] = outcome.get("route_inventory", {})
            matrix["runtime_events"][group] = outcome.get("runtime_events", {})
        browser.close()
    matrix["status"] = (
        "passed"
        if all(item.get("status") in {"passed", "skipped"} for item in matrix["groups"].values())
        else "failed"
    )
    missing = [key for key in MATRIX_REQUIRED_KEYS if key not in matrix]
    if missing:
        raise AssertionError(f"Browser matrix missing keys: {missing}")
    return matrix


def _selected_viewports() -> dict[str, dict[str, int]]:
    requested = os.environ.get("BROWSER_VIEWPORT", "all").strip().lower()
    if requested == "all":
        return dict(VIEWPORTS)
    if requested not in VIEWPORTS:
        raise ValueError(
            f"Unsupported BROWSER_VIEWPORT {requested!r}; expected one of all, "
            + ", ".join(VIEWPORTS)
        )
    return {requested: VIEWPORTS[requested]}


def _write_summary_markdown(summary: dict[str, Any], path: Path) -> None:
    lines = [
        "# Browser Acceptance Run Summary",
        "",
        f"- Status: {summary['status']}",
        f"- Branch: {summary.get('branch', 'unknown')}",
        f"- SHA: {summary.get('sha', 'unknown')}",
        f"- Duration seconds: {summary.get('duration_seconds', 'unknown')}",
    ]
    for result in summary.get("results", []):
        lines.extend(["", f"## {result['viewport']}", f"- Status: {result['status']}"])
        for group, outcome in result.get("groups", {}).items():
            lines.append(f"- {group}: {outcome.get('status', 'unknown')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_browser_acceptance(root: Path, artifact_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    process = StreamlitProcess(root=root, artifact_dir=artifact_dir / "streamlit")
    summary: dict[str, Any] = {}
    try:
        base_url = process.start()
        results = [
            _run_viewport(base_url, artifact_dir, name, viewport)
            for name, viewport in _selected_viewports().items()
        ]
        status = "passed" if all(item["status"] == "passed" for item in results) else "failed"
        summary = {
            "status": status,
            "branch": os.environ.get("GITHUB_REF_NAME", "local"),
            "sha": os.environ.get("GITHUB_SHA", "local"),
            "python": sys.version,
            "platform": platform.platform(),
            "port": process.port,
            "duration_seconds": round(time.monotonic() - started, 3),
            "results": results,
        }
        if status != "passed":
            raise AssertionError("One or more browser matrix groups failed; inspect run-summary.json.")
        return summary
    except Exception as exc:
        if not summary:
            summary = {
                "status": "failed",
                "branch": os.environ.get("GITHUB_REF_NAME", "local"),
                "sha": os.environ.get("GITHUB_SHA", "local"),
                "error": f"{type(exc).__name__}: {exc}",
                "duration_seconds": round(time.monotonic() - started, 3),
            }
        raise
    finally:
        process.stop()
        (artifact_dir / "run-summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        _write_summary_markdown(summary, artifact_dir / "run-summary.md")


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[2]
    output = Path(
        os.environ.get("BROWSER_ARTIFACT_DIR", repository_root / "browser-artifacts")
    )
    run_browser_acceptance(repository_root, output)
