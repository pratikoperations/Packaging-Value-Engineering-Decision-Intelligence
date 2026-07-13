from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from .change_types import CHANGE_TYPES
from .models import CategoryDefinition
from .objectives import PROJECT_OBJECTIVES
from .requirements import CATEGORY_REQUIREMENTS


_CATEGORY_NAMES = {
    "corrugated": "Corrugated Packaging",
    "folding_carton": "Folding Cartons / Paperboard",
    "rigid_plastic": "Rigid Plastic Packaging",
    "flexible_packaging": "Flexible Packaging",
    "labels": "Labels",
    "closures": "Closures",
    "glass": "Glass Packaging",
    "metal": "Metal Packaging",
}


class CategoryRegistry:
    def __init__(self, definitions: Iterable[CategoryDefinition] = ()) -> None:
        self._definitions: dict[str, CategoryDefinition] = {}
        for definition in definitions:
            self.register(definition)

    def register(self, definition: CategoryDefinition) -> None:
        if not definition.key or definition.key in self._definitions:
            raise ValueError(f"Duplicate or empty category key: {definition.key!r}")
        self._definitions[definition.key] = replace(definition)

    def get(self, key: str) -> CategoryDefinition:
        try:
            return self._definitions[key]
        except KeyError as exc:
            raise KeyError(f"Unknown packaging category: {key}") from exc

    def list(self) -> tuple[CategoryDefinition, ...]:
        return tuple(self._definitions[key] for key in sorted(self._definitions))

    def keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._definitions))


def default_registry() -> CategoryRegistry:
    definitions = []
    for key, display_name in _CATEGORY_NAMES.items():
        config = CATEGORY_REQUIREMENTS[key]
        definitions.append(
            CategoryDefinition(
                key=key,
                display_name=display_name,
                objectives=PROJECT_OBJECTIVES,
                change_types=CHANGE_TYPES[key],
                fields=config["fields"],
                documents=config["documents"],
                tests=config["tests"],
                readiness_blockers=config["blockers"],
                available_analyses=config["available_analyses"],
                unavailable_analyses=config["unavailable_analyses"],
                warnings=(
                    "Technical feasibility requires category-specific engineering validation.",
                    *config["warnings"],
                ),
            )
        )
    return CategoryRegistry(definitions)
