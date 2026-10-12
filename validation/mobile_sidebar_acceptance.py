from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = Path(os.environ.get("BROWSER_ARTIFACT_DIR", "browser-artifacts/mobile-sidebar"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
URL = "http://127.0.0.1:8501"
SIDEBAR = '[data-testid="stSidebar"]'
OPENER = '[data-testid="stExpandSidebarButton"]'
VIEWPORT = {"width": 412, "height": 915}
DESKTOP = {"width": 1440, "height": 1000}


def wait_server(proc: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 60
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"Streamlit exited before becoming ready with code {proc.returncode}")
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                if response.status < 500:
                    return
        except Exception as exc:
            last_error = exc
        time.sleep(0.25)
    raise RuntimeError(f"Streamlit did not become reachable: {last_error!r}")


def wait_ready(page: Page) -> None:
    page.goto(URL, wait_until="domcontentloaded", timeout=60_000)
    page.locator('[data-testid="stAppViewContainer"]').wait_for(state="visible", timeout=60_000)
    page.get_by_role("heading", name="Packaging Value Engineering Decision Intelligence", exact=True).wait_for(
        state="visible", timeout=60_000
    )


def box(page: Page) -> dict[str, float]:
    return page.locator(SIDEBAR).evaluate(
        """el => {
            const r = el.getBoundingClientRect();
            const s = getComputedStyle(el);
            return {
                left: r.left, right: r.right, top: r.top, bottom: r.bottom,
                width: r.width, height: r.height,
                computedWidth: s.width, minWidth: s.minWidth, maxWidth: s.maxWidth,
                flexBasis: s.flexBasis, transform: s.transform,
                clientWidth: el.clientWidth, scrollWidth: el.scrollWidth
            };
        }"""
    )


def visible_sidebar_button(page: Page):
    buttons = page.get_by_role("button", name=re.compile("sidebar", re.I))
    for i in range(buttons.count()):
        candidate = buttons.nth(i)
        if candidate.is_visible():
            return candidate
    return None


def open_once(page: Page) -> None:
    sidebar = page.locator(SIDEBAR)
    if sidebar.is_visible() and box(page)["width"] > 1 and box(page)["right"] > 1:
        return
    opener = page.locator(OPENER)
    opener.wait_for(state="visible", timeout=10_000)
    opener.click()
    deadline = time.monotonic() + 10
    stable = 0
    last_width = None
    while time.monotonic() < deadline:
        current = box(page)
        reachable = current["width"] > 1 and current["right"] > 1 and current["left"] < VIEWPORT["width"]
        if reachable and last_width is not None and abs(current["width"] - last_width) < 0.5:
            stable += 1
            if stable >= 2:
                return
        else:
            stable = 0
        last_width = current["width"]
        page.wait_for_timeout(100)
    raise AssertionError(f"Sidebar did not settle open: {box(page)}")


def close_sidebar(page: Page) -> None:
    button = visible_sidebar_button(page)
    if button is None:
        raise AssertionError("No visible semantic sidebar close/collapse button found.")
    button.click()
    page.locator(OPENER).wait_for(state="visible", timeout=10_000)


def assert_no_material_console(errors: list[str]) -> None:
    material = [e for e in errors if any(x in e.lower() for x in ("uncaught", "traceback", "streamlitapiexception"))]
    assert not material, material


def main() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless=true", "--server.address=127.0.0.1", "--server.port=8501"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    report: dict[str, object] = {"candidate_sha": os.environ.get("SOURCE_COMMIT"), "narrow_viewport": VIEWPORT}
    try:
        wait_server(proc)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=VIEWPORT)
            console_errors: list[str] = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            wait_ready(page)
            page.screenshot(path=str(ARTIFACT_DIR / "01-collapsed.png"), full_page=True)

            open_once(page)
            narrow = box(page)
            page.screenshot(path=str(ARTIFACT_DIR / "02-open.png"), full_page=True)
            report["narrow_sidebar"] = narrow

            assert 179 <= narrow["width"] <= 201, narrow
            assert narrow["width"] / VIEWPORT["width"] <= 0.50, narrow
            assert narrow["scrollWidth"] <= narrow["clientWidth"] + 2, narrow

            required_links = (
                "Home", "Project Dashboard", "Guided Workflow", "Specification Review",
                "Data Upload", "Business Rules & Thresholds", "Scenario Analysis",
                "Decision Records", "Capabilities & Limits",
            )
            for label in required_links:
                locator = page.get_by_role("link", name=label, exact=True)
                assert locator.count() == 1, f"Expected one {label!r} link, got {locator.count()}"
                locator.scroll_into_view_if_needed()
                assert locator.is_visible(), f"{label!r} is not visible"

            scenario_header = page.get_by_role("heading", name="Scenario Inputs", exact=True)
            scenario_header.scroll_into_view_if_needed()
            assert scenario_header.is_visible()
            annual = page.get_by_label("Annual volume (cases)", exact=True)
            annual.scroll_into_view_if_needed()
            assert annual.is_visible() and annual.is_enabled()
            annual.focus()

            close_sidebar(page)
            assert page.locator(OPENER).is_visible()
            open_once(page)
            reopened = box(page)
            report["reopened_sidebar"] = reopened
            assert abs(reopened["width"] - narrow["width"]) < 1.0, (narrow, reopened)

            capabilities = page.get_by_role("link", name="Capabilities & Limits", exact=True)
            capabilities.scroll_into_view_if_needed()
            capabilities.click()
            page.get_by_role("heading", name="Capabilities & Limits", exact=True).wait_for(state="visible", timeout=15_000)
            report["navigation_passed"] = True

            desktop = browser.new_page(viewport=DESKTOP)
            wait_ready(desktop)
            if not desktop.locator(SIDEBAR).is_visible():
                btn = visible_sidebar_button(desktop)
                if btn:
                    btn.click()
            desktop.locator(SIDEBAR).wait_for(state="visible", timeout=10_000)
            desktop_box = box(desktop)
            report["desktop_sidebar"] = desktop_box
            assert desktop_box["width"] > 200, desktop_box
            desktop.screenshot(path=str(ARTIFACT_DIR / "03-desktop.png"), full_page=True)

            report["console_errors"] = console_errors
            assert_no_material_console(console_errors)
            report["overall_disposition"] = "PASS"
            browser.close()
    except Exception as exc:
        report["overall_disposition"] = "FAIL"
        report["error"] = repr(exc)
        raise
    finally:
        (ARTIFACT_DIR / "acceptance-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        if proc.stdout:
            (ARTIFACT_DIR / "streamlit.log").write_text(proc.stdout.read(), encoding="utf-8")


if __name__ == "__main__":
    main()
