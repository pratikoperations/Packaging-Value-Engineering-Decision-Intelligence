from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class FieldDefinition:
    key: str
    label: str
    requirement: str
    value_type: str
    units: Sequence[str] = ()
    minimum: float | None = None
    maximum: float | None = None
    critical: bool = False
    description: str = ""


@dataclass(frozen=True)
class DocumentDefinition:
    document_type: str
    requirement: str
    critical: bool = False


@dataclass(frozen=True)
class TestDefinition:
    name: str
    critical: bool = False
    applies_to: Sequence[str] = ()


@dataclass(frozen=True)
class CategoryDefinition:
    key: str
    display_name: str
    objectives: Sequence[str]
    change_types: Sequence[str]
    fields: Sequence[FieldDefinition] = ()
    documents: Sequence[DocumentDefinition] = ()
    tests: Sequence[TestDefinition] = ()
    readiness_blockers: Sequence[str] = ()
    available_analyses: Sequence[str] = ()
    unavailable_analyses: Sequence[str] = ()
    warnings: Sequence[str] = ()
    metadata: Mapping[str, str] | None = None

    def supports_objective(self, objective: str) -> bool:
        return objective in self.objectives

    def supports_change_type(self, change_type: str) -> bool:
        return change_type in self.change_types

    def fields_by_requirement(self, requirement: str) -> tuple[FieldDefinition, ...]:
        return tuple(field for field in self.fields if field.requirement == requirement)

    def documents_by_requirement(self, requirement: str) -> tuple[DocumentDefinition, ...]:
        return tuple(document for document in self.documents if document.requirement == requirement)
