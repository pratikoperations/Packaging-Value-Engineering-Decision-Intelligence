from __future__ import annotations

import unittest
from unittest.mock import patch

from src.browser_acceptance import runner


class FakeCandidate:
    def __init__(self, *, visible: bool = True, href: str | None = None):
        self.visible = visible
        self.href = href
        self.wait_calls: list[dict[str, object]] = []

    def is_visible(self) -> bool:
        return self.visible

    def wait_for(self, **kwargs) -> None:
        self.wait_calls.append(kwargs)
        self.visible = True

    def get_attribute(self, name: str) -> str | None:
        return self.href if name == "href" else None


class FakeLocator:
    def __init__(self, candidates: list[FakeCandidate]):
        self.candidates = candidates

    @property
    def first(self) -> FakeCandidate:
        return self.candidates[0]

    def count(self) -> int:
        return len(self.candidates)

    def nth(self, index: int) -> FakeCandidate:
        return self.candidates[index]


class FakeBody:
    def inner_text(self) -> str:
        return ""


class FakeReadyPage:
    def __init__(self):
        self.root = FakeCandidate()
        self.heading = FakeCandidate()
        self.wait_for_function_calls: list[dict[str, object]] = []

    def locator(self, selector: str):
        if selector == runner.APP_ROOT_SELECTOR:
            return self.root
        if selector == "body":
            return FakeBody()
        raise AssertionError(f"Unexpected selector: {selector}")

    def get_by_role(self, role: str, **kwargs):
        if role == "heading":
            return self.heading
        raise AssertionError(f"Unexpected role: {role}")

    def wait_for_function(self, script: str, *, arg=None, timeout=None):
        self.wait_for_function_calls.append(
            {"script": script, "arg": arg, "timeout": timeout}
        )
        return True


class FakeRoutePage:
    def __init__(self, hrefs: dict[str, str]):
        self.hrefs = hrefs
        self.requested_titles: list[str] = []

    def get_by_role(self, role: str, *, name: str, exact: bool):
        if role != "link":
            raise AssertionError(f"Unexpected role: {role}")
        self.requested_titles.append(name)
        if name == "Home":
            raise AssertionError("Home must not be queried for an href")
        return FakeLocator([FakeCandidate(href=self.hrefs[name])])


class BrowserExecutableContractTests(unittest.TestCase):
    def test_app_ready_uses_keyword_only_playwright_argument(self):
        page = FakeReadyPage()

        runner._app_ready(page)

        self.assertEqual(len(page.wait_for_function_calls), 1)
        call = page.wait_for_function_calls[0]
        self.assertEqual(call["arg"], runner.APP_ROOT_SELECTOR)
        self.assertEqual(call["timeout"], runner.PAGE_TIMEOUT_MILLISECONDS)

    def test_home_ready_waits_for_exact_home_heading(self):
        page = FakeReadyPage()

        runner._app_ready(page, require_home_heading=True)

        self.assertEqual(page.wait_for_function_calls, [])
        self.assertEqual(
            page.heading.wait_calls,
            [{"state": "visible", "timeout": runner.PAGE_TIMEOUT_MILLISECONDS}],
        )

    def test_wait_for_first_visible_supports_hidden_then_visible(self):
        candidate = FakeCandidate(visible=False)
        locator = FakeLocator([candidate])

        selected = runner._wait_for_first_visible(locator, timeout=100)

        self.assertIs(selected, candidate)
        self.assertTrue(candidate.visible)
        self.assertEqual(candidate.wait_calls[0]["state"], "visible")

    def test_collect_route_inventory_uses_explicit_home_root(self):
        base_url = "http://127.0.0.1:8501/"
        non_home_titles = [
            title for title, _heading, _group in runner.PAGE_CONTRACTS if title != "Home"
        ]
        hrefs = {
            title: f"/{index}-{title.lower().replace(' ', '-')}"
            for index, title in enumerate(non_home_titles, start=1)
        }
        page = FakeRoutePage(hrefs)

        with patch.object(runner, "_goto_home"), patch.object(
            runner, "_expand_all_groups"
        ):
            routes = runner._collect_route_inventory(page, base_url)

        self.assertEqual(routes["Home"], "http://127.0.0.1:8501")
        self.assertNotIn("Home", page.requested_titles)
        self.assertEqual(len(routes), 13)
        self.assertEqual(len(set(routes.values())), 13)

    def test_route_inventory_rejects_duplicate_resolved_destination(self):
        routes = {
            title: f"http://127.0.0.1:8501/{index}"
            for index, (title, _heading, _group) in enumerate(
                runner.PAGE_CONTRACTS
            )
        }
        second_title = runner.PAGE_CONTRACTS[1][0]
        routes[second_title] = routes["Home"]

        with self.assertRaisesRegex(
            AssertionError, "13 unique resolved destinations"
        ):
            runner._validate_route_inventory(routes)


if __name__ == "__main__":
    unittest.main()
