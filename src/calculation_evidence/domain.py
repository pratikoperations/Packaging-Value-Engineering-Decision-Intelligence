from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.sourcemate.domain import SourceClassification


class CalculationEvidenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class CalculationInput:
    name: str
    value: Any
    unit: str
    classification: SourceClassification
    source_record: str
    rule_reference: str = ""

    def canonical(self) -> dict[str, Any]:
        return {
            "classification": self.classification.value,
            "name": self.name,
            "rule_reference": self.rule_reference,
            "source_record": self.source_record,
            "unit": self.unit,
            "value": self.value,
        }


@dataclass(frozen=True)
class CalculationStep:
    sequence: int
    label: str
    formula_reference: str
    formula_expression: str
    inputs: tuple[CalculationInput, ...]
    output_value: float
    output_unit: str
    precision: int = 2
    rounding_rule: str = "round-half-even"

    def canonical(self) -> dict[str, Any]:
        return {
            "formula_expression": self.formula_expression,
            "formula_reference": self.formula_reference,
            "inputs": [item.canonical() for item in self.inputs],
            "label": self.label,
            "output_unit": self.output_unit,
            "output_value": self.output_value,
            "precision": self.precision,
            "rounding_rule": self.rounding_rule,
            "sequence": self.sequence,
        }


@dataclass(frozen=True)
class CalculationEvidence:
    schema_version: str
    project_id: str
    target_id: str
    target_type: str
    revision_reference: str
    result_name: str
    result_value: float
    result_unit: str
    source_hash: str
    assumptions: tuple[CalculationInput, ...] = field(default_factory=tuple)
    steps: tuple[CalculationStep, ...] = field(default_factory=tuple)
    unit_conversions: tuple[str, ...] = field(default_factory=tuple)
    evidence_gaps: tuple[str, ...] = field(default_factory=tuple)
    validation_requirements: tuple[str, ...] = field(default_factory=tuple)
    claim_limitations: tuple[str, ...] = field(default_factory=tuple)
    archived: bool = False

    def canonical(self) -> dict[str, Any]:
        return {
            "archived": self.archived,
            "assumptions": [item.canonical() for item in self.assumptions],
            "claim_limitations": list(self.claim_limitations),
            "evidence_gaps": list(self.evidence_gaps),
            "project_id": self.project_id,
            "result_name": self.result_name,
            "result_unit": self.result_unit,
            "result_value": self.result_value,
            "revision_reference": self.revision_reference,
            "schema_version": self.schema_version,
            "source_hash": self.source_hash,
            "steps": [item.canonical() for item in self.steps],
            "target_id": self.target_id,
            "target_type": self.target_type,
            "unit_conversions": list(self.unit_conversions),
            "validation_requirements": list(self.validation_requirements),
        }
