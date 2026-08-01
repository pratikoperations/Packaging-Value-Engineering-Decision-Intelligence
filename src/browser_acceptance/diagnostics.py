from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RuntimeDiagnostics:
    page_errors: list[str] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    def bind(self, page) -> None:
        page.on("pageerror", lambda error: self.page_errors.append(str(error)))
        page.on(
            "console",
            lambda message: self.console_errors.append(message.text)
            if message.type == "error"
            else None,
        )

    def record(self, event: str, **details: Any) -> None:
        self.events.append({"event": event, **details})

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "page_errors": self.page_errors,
                    "console_errors": self.console_errors,
                    "events": self.events,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
