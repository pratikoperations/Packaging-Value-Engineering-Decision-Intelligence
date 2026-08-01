from __future__ import annotations

import json
import os
import platform
import re
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

from .contracts import (
    ACTION_TIMEOUT_MILLISECONDS,
    PAGE_CONTRACTS,
    PAGE_TIMEOUT_MILLISECONDS,
    SIDEBAR_GROUPS,
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
PAGE_BY_TITLE = {title: (heading, group) for title, heading, group in PAGE_CONTRACTS}


def _assert_no_visible_exception(page: Page) -> None:
    body = page.locator("body").inner_text()
    found = [text for text in EXCEPTION_TEXT if text in body]
    if found:
        raise AssertionError(f"Visible Streamlit exception markers: {found}")


def _open_sidebar_if_needed(page: Page) -> None:
    if page.get_by_role("link", name="Home", exact=True).count():
        return
    sidebar_button = page.get_by_role("button", name=re.compile("sidebar", re.IGNORECASE))
    if sidebar_button.count() != 1:
        raise AssertionError("Expected one accessible sidebar toggle button.")
    sidebar_button.click()
    page.get_by_role("link", name="Home", exact=True).wait_for()


def _click_page(page: Page, title: str, group: str | None) -> None:
    _open_sidebar_if_needed(page)
    if group:
        group_control = page.get_by_text(group, exact=True)
        if group_control.count() != 1:
            raise AssertionError(f"Expected one sidebar group control for {group}.")
        group_control.click()
    link = page.get_by_role("link", name=title, exact=True)
    if link.count() != 1:
        raise AssertionError(f"Expected one registered page link for {title}.")
    link.click()
    heading, _ = PAGE_BY_TITLE[title]
    page.get_by_role("heading", name=re.compile(re.escape(heading), re.IGNORECASE)).first.wait_for()
    _assert_no_visible_exception(page)


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


def _home_journey(page: Page, artifacts: Path) -> dict[str, Any]:
    page.get_by_role(
        "heading", name="Packaging Value Engineering Decision Intelligence", exact=True
    ).wait_for()
    body = page.locator("body").inner_text()
    if body.lower().count("synthetic") < 2:
        raise AssertionError("Required synthetic disclosures are not visible.")

    _select_second_governed_scenario(page)
    annual_volume = page.get_by_role(
        "spinbutton", name="Annual volume (cases)", exact=True
    )
    annual_volume.fill("1010000")
    annual_volume.press("Enter")

    assumptions = page.get_by_text(
        re.compile(r"^[A-Za-z0-9_-]+ assumptions$", re.IGNORECASE), exact=True
    )
    assumptions.first.wait_for()
    if assumptions.count() < 1:
        raise AssertionError("No governed alternative-assumption expander is available.")
    assumptions.first.click()
    cost_adjustment = page.get_by_role(
        "spinbutton", name="Unit-cost adjustment (%)", exact=True
    ).first
    material_adjustment = page.get_by_role(
        "spinbutton", name="Material-weight adjustment (%)", exact=True
    ).first
    cost_adjustment.fill("1")
    cost_adjustment.press("Enter")
    material_adjustment.fill("-1")
    material_adjustment.press("Enter")

    page.get_by_role("heading", name="Scenario Comparison", exact=True).wait_for()
    page.get_by_role("heading", name="Preferred Alternative", exact=True).wait_for()
    page.get_by_role("heading", name="Explainable Recommendation Detail", exact=True).wait_for()
    _assert_no_visible_exception(page)
    return _download_and_validate(page, artifacts)


def _run_viewport(
    base_url: str,
    artifacts: Path,
    viewport_name: str,
    viewport: dict[str, int],
) -> dict[str, Any]:
    diagnostics = RuntimeDiagnostics()
    result: dict[str, Any] = {"viewport": viewport_name, "pages": [], "groups": {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport=viewport, accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(ACTION_TIMEOUT_MILLISECONDS)
        page.set_default_navigation_timeout(PAGE_TIMEOUT_MILLISECONDS)
        diagnostics.attach(page)
        page.goto(base_url, wait_until="domcontentloaded")
        page.get_by_role(
            "heading", name="Packaging Value Engineering Decision Intelligence", exact=True
        ).wait_for()

        result["downloads"] = _home_journey(page, artifacts / viewport_name)

        for title, _heading, group in PAGE_CONTRACTS:
            if title != "Home":
                _click_page(page, title, group)
            result["pages"].append(title)
            if title != "Home":
                _click_page(page, "Home", None)

        for group, expected in SIDEBAR_GROUPS.items():
            _open_sidebar_if_needed(page)
            group_control = page.get_by_text(group, exact=True)
            if group_control.count() != 1:
                raise AssertionError(f"Expected one sidebar group control for {group}.")
            group_control.click()
            visible = [
                title
                for title in expected
                if page.get_by_role("link", name=title, exact=True).count() == 1
            ]
            if tuple(visible) != tuple(expected):
                raise AssertionError(f"Sidebar group {group} mismatch: {visible}")
            result["groups"][group] = visible

        screenshot_dir = artifacts / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(screenshot_dir / f"{viewport_name}-home.png"), full_page=True
        )
        _assert_no_visible_exception(page)
        diagnostics.assert_clean()
        result["runtime_events"] = diagnostics.canonical()
        context.close()
        browser.close()
    return result


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
        lines.extend(
            [
                "",
                f"## {result['viewport']}",
                f"- Registered pages: {len(result.get('pages', []))}",
                f"- Sidebar groups: {len(result.get('groups', {}))}",
                f"- Runtime events: {len(result.get('runtime_events', []))}",
            ]
        )
    if "error" in summary:
        lines.extend(["", "## Error", "", summary["error"]])
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
        summary = {
            "status": "passed",
            "branch": os.environ.get("GITHUB_REF_NAME", "local"),
            "sha": os.environ.get("GITHUB_SHA", "local"),
            "python": sys.version,
            "platform": platform.platform(),
            "port": process.port,
            "duration_seconds": round(time.monotonic() - started, 3),
            "results": results,
        }
        return summary
    except Exception as exc:
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
        json_path = artifact_dir / "run-summary.json"
        markdown_path = artifact_dir / "run-summary.md"
        json_path.write_text(
            json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
        )
        _write_summary_markdown(summary, markdown_path)


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[2]
    output = Path(
        os.environ.get(
            "BROWSER_ARTIFACT_DIR", repository_root / "browser-artifacts"
        )
    )
    run_browser_acceptance(repository_root, output)
