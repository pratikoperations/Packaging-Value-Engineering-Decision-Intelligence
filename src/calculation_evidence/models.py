from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal

ReconciliationState = Literal[
    "matched",
    "matched_within_tolerance",
    "mismatch",
    "insufficient_evidence",
    "unsupported",
]


@dataclass(frozen=True)
class CalculationDefinition:
    calculation_id: str
    version: str
    business_name: str
    expression: str
    required_inputs: tuple[str, ...]
    accepted_units: tuple[str, ...]
    output_unit: str
    quantum: Decimal
    rounding_mode: str
    tolerance_policy_id: str
    sign_policy: str
    currency: str | None
    primary_location: str
    evidence_location: str
    limitations: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TolerancePolicy:
    policy_id: str
    absolute: Decimal
    relative_percent: Decimal


@dataclass(frozen=True)
class IndependentCalculation:
    calculation_id: str
    formula_version: str
    value: Decimal | None
    unit: str
    raw_inputs: dict[str, str]
    assumption_ids: tuple[str, ...] = field(default_factory=tuple)
    status: Literal["calculated", "insufficient_evidence", "unsupported"] = "calculated"
    issue_code: str | None = None
    issue_message: str | None = None

    def canonical(self) -> dict[str, Any]:
        return {
            "calculation_id": self.calculation_id,
            "formula_version": self.formula_version,
            "value": None if self.value is None else format(self.value, "f"),
            "unit": self.unit,
            "raw_inputs": dict(sorted(self.raw_inputs.items())),
            "assumption_ids": list(self.assumption_ids),
            "status": self.status,
            "issue_code": self.issue_code,
            "issue_message": self.issue_message,
        }


@dataclass(frozen=True)
class ReconciliationResult:
    evidence_result_id: str
    scenario_id: str
    alternative_id: str
    calculation_id: str
    formula_version: str
    primary_result: Decimal | None
    independent_result: Decimal | None
    unit: str
    absolute_variance: Decimal | None
    relative_variance_percent: Decimal | None
    allowed_variance: Decimal | None
    tolerance_policy_id: str
    state: ReconciliationState
    raw_inputs: dict[str, str]
    assumption_ids: tuple[str, ...]
    limitations: tuple[str, ...]
    issue_code: str | None = None
    issue_message: str | None = None

    def canonical(self) -> dict[str, Any]:
        def text(value: Decimal | None) -> str | None:
            return None if value is None else format(value, "f")

        return {
            "evidence_result_id": self.evidence_result_id,
            "scenario_id": self.scenario_id,
            "alternative_id": self.alternative_id,
            "calculation_id": self.calculation_id,
            "formula_version": self.formula_version,
            "primary_result": text(self.primary_result),
            "independent_result": text(self.independent_result),
            "unit": self.unit,
            "absolute_variance": text(self.absolute_variance),
            "relative_variance_percent": text(self.relative_variance_percent),
            "allowed_variance": text(self.allowed_variance),
            "tolerance_policy_id": self.tolerance_policy_id,
            "state": self.state,
            "raw_inputs": dict(sorted(self.raw_inputs.items())),
            "assumption_ids": list(self.assumption_ids),
            "limitations": list(self.limitations),
            "issue_code": self.issue_code,
            "issue_message": self.issue_message,
        }
