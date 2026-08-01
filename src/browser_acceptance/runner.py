from __future__ import annotations

import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

from .contracts import ACTION_TIMEOUT_MILLISECONDS, PAGE_CONTRACTS, PAGE_TIMEOUT_MILLISECONDS, SIDEBAR_GROUPS, VIEWPORTS
from .diagnostics import RuntimeDiagnostics
from .export_validation import validate_json_download, validate_markdown_download
from .process_manager import StreamlitProcess

EXCEPTION_TEXT = ("StreamlitAPIException", "StreamlitPageNotFoundError", "Traceback (most recent call last)")


def _assert_no_visible_exception(page: Page) -> None:
    body = page.locator("body").inner_text()
    found = [text for text in EXCEPTION_TEXT if text in body]
    if found:
        raise AssertionError(f"Visible Streamlit exception markers: {found}")


def _open_sidebar_if_needed(page: Page) -> None:
    if page.get_by_role("link", name="Home", exact=True).count():
        return
    buttons = page.get_by_role("button")
    for index in range(buttons.count()):
        label = buttons.nth(index).get_attribute("aria-label") or ""
        if "sidebar" in label.lower():
            buttons.nth(index).click()
            return


def _click_page(page: Page, title: str, group: str | None) -> None:
    _open_sidebar_if_needed(page)
    if group:
        expander = page.get_by_text(group, exact=True)
        if expander.count():
            expander.first.click()
    page.get_by_role("link", name=title, exact=True).first.click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(250)
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


def _home_journey(page: Page, artifacts: Path) -> dict[str, Any]:
    page.get_by_role("heading", name="Packaging Value Engineering Decision Intelligence", exact=True).wait_for()
    body = page.locator("body").inner_text()
    if body.lower().count("synthetic") < 2:
        raise AssertionError("Required synthetic disclosures are not visible.")
    page.get_by_label("Governed synthetic procurement scenario").select_option(index=1)
    annual_volume = page.get_by_label("Annual volume (cases)")
    annual_volume.fill("1010000")
    annual_volume.press("Enter")
    page.get_by_text("Scenario Comparison", exact=True).wait_for()
    page.get_by_text("Explainable Recommendation Detail", exact=True).wait_for()
    _assert_no_visible_exception(page)
    return _download_and_validate(page, artifacts)


def _run_viewport(base_url: str, artifacts: Path, viewport_name: str, viewport: dict[str, int]) -> dict[str, Any]:
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
        page.get_by_role("heading", name="Packaging Value Engineering Decision Intelligence", exact=True).wait_for()
        if viewport_name == "desktop":
            result["downloads"] = _home_journey(page, artifacts / viewport_name)
        for title, _heading, group in PAGE_CONTRACTS:
            if title != "Home":
                _click_page(page, title, group)
            result["pages"].append(title)
            if title != "Home":
                _click_page(page, "Home", None)
        for group, expected in SIDEBAR_GROUPS.items():
            _open_sidebar_if_needed(page)
            page.get_by_text(group, exact=True).first.click()
            visible = [title for title in expected if page.get_by_role("link", name=title, exact=True).count()]
            if tuple(visible) != tuple(expected):
                raise AssertionError(f"Sidebar group {group} mismatch: {visible}")
            result["groups"][group] = visible
        page.screenshot(path=str(artifacts / f"{viewport_name}-home.png"), full_page=True)
        _assert_no_visible_exception(page)
        diagnostics.assert_clean()
        result["runtime_events"] = diagnostics.canonical()
        context.close()
        browser.close()
    return result


def run_browser_acceptance(root: Path, artifact_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    process = StreamlitProcess(root=root, artifact_dir=artifact_dir / "streamlit")
    try:
        base_url = process.start()
        results = [_run_viewport(base_url, artifact_dir, name, viewport) for name, viewport in VIEWPORTS.items()]
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
        (artifact_dir / "run-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[2]
    output = Path(os.environ.get("BROWSER_ARTIFACT_DIR", repository_root / "browser-artifacts"))
    run_browser_acceptance(repository_root, output)
