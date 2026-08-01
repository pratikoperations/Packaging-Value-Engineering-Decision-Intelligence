from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BENIGN_CONSOLE_PATTERNS = (
    "favicon",
    "ResizeObserver loop",
)


@dataclass
class RuntimeDiagnostics:
    console_errors: list[dict[str, Any]] = field(default_factory=list)
    page_errors: list[dict[str, Any]] = field(default_factory=list)
    failed_requests: list[dict[str, Any]] = field(default_factory=list)
    server_errors: list[dict[str, Any]] = field(default_factory=list)

    def attach(self, page: Any) -> None:
        page.on("pageerror", lambda error: self.page_errors.append({"message": str(error), "url": page.url}))
        page.on("console", lambda msg: self._on_console(msg, page.url))
        page.on("requestfailed", lambda request: self.failed_requests.append({
            "url": request.url,
            "method": request.method,
            "failure": str(request.failure),
        }))
        page.on("response", lambda response: self._on_response(response))

    def _on_console(self, message: Any, url: str) -> None:
        if message.type not in {"error", "assert"}:
            return
        text = message.text
        if any(pattern.lower() in text.lower() for pattern in BENIGN_CONSOLE_PATTERNS):
            return
        self.console_errors.append({"type": message.type, "text": text, "url": url})

    def _on_response(self, response: Any) -> None:
        if response.status >= 500:
            self.server_errors.append({"status": response.status, "url": response.url})

    def assert_clean(self) -> None:
        findings = {
            "page_errors": self.page_errors,
            "console_errors": self.console_errors,
            "failed_requests": self.failed_requests,
            "server_errors": self.server_errors,
        }
        active = {key: value for key, value in findings.items() if value}
        if active:
            raise AssertionError(f"Unexplained browser runtime events: {active}")

    def canonical(self) -> dict[str, Any]:
        return {
            "console_errors": self.console_errors,
            "page_errors": self.page_errors,
            "failed_requests": self.failed_requests,
            "server_errors": self.server_errors,
        }
