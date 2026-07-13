from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class CategoryDefinition:
    key: str
    display_name: str
    objectives: Sequence[str]
    change_types: Sequence[str]
    warnings: Sequence[str] = ()
    metadata: Mapping[str, str] | None = None

    def supports_objective(self, objective: str) -> bool:
        return objective in self.objectives

    def supports_change_type(self, change_type: str) -> bool:
        return change_type in self.change_types
