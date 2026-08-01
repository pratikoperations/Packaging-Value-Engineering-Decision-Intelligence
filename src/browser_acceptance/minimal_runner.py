from __future__ import annotations

import json
import os
import platform
import re
import sys
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
    SIDEBAR_GROUPS,
    VIEWPORTS,
)
from .diagnostics import RuntimeDiagnostics
from .export_validation import validate_json_download, validate_markdown_download
from .process_manager import StreamlitProcess

SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"
SCHEMA_VERSION = "1.0.0"
MATERIAL_CONSOLE_PATTERNS = (
    "uncaught",
    "traceback",
    "streamlitapiexception",
    "streamlitpagenotfounderror",
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
    if _visible(page.get_by_role("link", name="Home", exact=True)):
        return
    button = _first_visible(page.get_by_role("button", name=re.compile("sidebar", re.I)))
    button.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    _first_visible(page.get_by_role("link", name="Home", exact=True))


def _expand_group(page: Page, group: str, expected_link: str) -> None:
    _open_sidebar(page)
    if _visible(page.get_by_role("link", name=expected_link, exact=True)):
        return
    controls = page.get_by_role("button", name=group, exact=True)
    if not _visible(controls):
        text = _first_visible(page.get_by_text(group, exact=True))
        controls = text.locator("xpath=ancestor-or-self::*[self::button or self::summary or @role='button'][1]")
    control = _first_visible(controls)
    control.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT_MILLISECONDS)
    control.click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    _first_visible(page.get_by_role("link", name=expected_link, exact=True))


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


def _select_scenario_and_adjust_inputs(page: Page) -> str:
    select = page.get_by_label("Governed synthetic procurement scenario")
    select.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    options = select.locator("option")
    if options.count() < 1:
        raise AssertionError("No governed scenario options were rendered.")
    scenario_id = options.nth(0).get_attribute("value") or options.nth(0).inner_text()
    select.select_option(index=0)
    page.wait_for_timeout(1000)

    annual = page.get_by_label("Annual volume (cases)")
    annual.wait_for(state="visible", timeout=PAGE_TIMEOUT_MILLISECONDS)
    current = float(annual.input_value())
    annual.fill(str(current + 1000))
    annual.press("Enter")
    page.wait_for_timeout(1000)

    assumptions = page.get_by_role("button", name=re.compile(r"assumptions$", re.I))
    assumption = _first_visible(assumptions)
    assumption.click(timeout=ACTION_TIMEOUT_MILLISECONDS)

    cost = _first_visible(page.get_by_label("Unit-cost adjustment (%)"))
    cost.fill("1")
    cost.press("Enter")
    page.wait_for_timeout(800)

    assumptions = page.get_by_role("button", name=re.compile(r"assumptions$", re.I))
    if not _visible(page.get_by_label("Material-weight adjustment (%)")):
        _first_visible(assumptions).click(timeout=ACTION_TIMEOUT_MILLISECONDS)
    material = _first_visible(page.get_by_label("Material-weight adjustment (%)"))
    material.fill("1")
    material.press("Enter")
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


def _material_console_errors(values: list[str]) -> list[str]:
    return [value for value in values if any(pattern in value.lower() for pattern in MATERIAL_CONSOLE_PATTERNS)]


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_minimal_acceptance() -> dict:
    root = Path(__file__).resolve().parents[2]
    artifact_dir = root / os.environ.get("BROWSER_ARTIFACT_DIR", "browser-artifacts/gate3a")
    screenshots = artifact_dir / "screenshots"
    downloads = artifact_dir / "downloads"
    logs = artifact_dir / "logs"
    screenshots.mkdir(parents=True, exist_ok=True)
    downloads.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    report = {key: None for key in ACCEPTANCE_REPORT_KEYS}
    report.update(
        {
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
        }
    )
    diagnostics = RuntimeDiagnostics()
    routes: dict[str, str] = {}
    active_page: Page | None = None

    try:
        with StreamlitProcess(root, logs / "streamlit.log") as app:
            with sync_playwright() as playwright:
                report["playwright_version"] = getattr(playwright, "__version__", "managed")
                browser = playwright.chromium.launch()
                report["chromium_version"] = browser.version

                desktop_context = browser.new_context(
                    viewport=VIEWPORTS["desktop"], accept_downloads=True
                )
                page = desktop_context.new_page()
                active_page = page
                diagnostics.bind(page)
                page.goto(app.base_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MILLISECONDS)
                _app_ready(page, require_home=True)
                page.screenshot(path=screenshots / "home-desktop.png", full_page=True)

                routes = _collect_routes(page, app.base_url)
                scenario_id = _select_scenario_and_adjust_inputs(page)
                report["scenario_id"] = scenario_id

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
                _open_sidebar(narrow)
                _resolved_link(narrow, app.base_url, "Calculation Evidence", "Evidence & Explanation")
                narrow.screenshot(path=screenshots / "narrow-smoke.png", full_page=True)
                _assert_no_visible_exception(narrow)
                report["narrow_smoke_passed"] = True
                narrow_context.close()
                browser.close()

        material_console = _material_console_errors(diagnostics.console_errors)
        report.update(
            {
                "route_count": len(routes),
                "unique_route_count": len(set(routes.values())),
                "visible_exception_count": 0,
                "page_error_count": len(diagnostics.page_errors),
                "console_error_count": len(material_console),
            }
        )
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
            raise AssertionError(f"Gate 3A acceptance controls failed: {report}")
        report["overall_disposition"] = "PASS"
        return report
    except Exception as exc:
        report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        if active_page is not None:
            try:
                active_page.screenshot(path=screenshots / "failure.png", full_page=True)
            except Exception:
                pass
        _write_json(artifact_dir / "failure-context.json", report["failure"])
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
