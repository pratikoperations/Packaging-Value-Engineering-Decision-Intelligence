from __future__ import annotations

from decimal import Decimal

from .catalogue import CALCULATION_CATALOGUE, TOLERANCE_POLICIES
from .models import IndependentCalculation, ReconciliationResult

LIMITATIONS = (
    "Arithmetic reconciliation is not supplier, engineering, regulatory, production or realized-savings validation.",
    "Synthetic scenario inputs remain demonstration assumptions.",
)


def reconcile(
    *,
    scenario_id: str,
    alternative_id: str,
    independent: IndependentCalculation,
    primary_result: object | None,
) -> ReconciliationResult:
    definition = CALCULATION_CATALOGUE.get(independent.calculation_id)
    policy_id = definition.tolerance_policy_id if definition else "UNSUPPORTED"
    evidence_id = f"EVD-{scenario_id}-{alternative_id}-{independent.calculation_id}"

    if independent.status == "unsupported":
        return _non_numeric(evidence_id, scenario_id, alternative_id, independent, policy_id, "unsupported")
    if independent.status == "insufficient_evidence" or independent.value is None or primary_result is None:
        return _non_numeric(evidence_id, scenario_id, alternative_id, independent, policy_id, "insufficient_evidence")

    try:
        primary = Decimal(str(primary_result))
    except Exception:
        return _non_numeric(
            evidence_id,
            scenario_id,
            alternative_id,
            independent,
            policy_id,
            "insufficient_evidence",
            "INVALID_PRIMARY_RESULT",
            "Primary result is missing or non-numeric.",
        )
    if not primary.is_finite():
        return _non_numeric(
            evidence_id,
            scenario_id,
            alternative_id,
            independent,
            policy_id,
            "insufficient_evidence",
            "INVALID_PRIMARY_RESULT",
            "Primary result must be finite.",
        )

    independent_value = independent.value
    variance = abs(primary - independent_value)
    relative_variance = Decimal("0") if independent_value == 0 else variance / abs(independent_value) * Decimal("100")
    policy = TOLERANCE_POLICIES[policy_id]
    relative_allowance = abs(independent_value) * policy.relative_percent / Decimal("100")
    allowed = max(policy.absolute, relative_allowance)
    if variance == 0:
        state = "matched"
    elif variance <= allowed:
        state = "matched_within_tolerance"
    else:
        state = "mismatch"

    return ReconciliationResult(
        evidence_result_id=evidence_id,
        scenario_id=scenario_id,
        alternative_id=alternative_id,
        calculation_id=independent.calculation_id,
        formula_version=independent.formula_version,
        primary_result=primary,
        independent_result=independent_value,
        unit=independent.unit,
        absolute_variance=variance,
        relative_variance_percent=relative_variance,
        allowed_variance=allowed,
        tolerance_policy_id=policy_id,
        state=state,
        raw_inputs=independent.raw_inputs,
        assumption_ids=independent.assumption_ids,
        limitations=LIMITATIONS,
    )


def _non_numeric(
    evidence_id: str,
    scenario_id: str,
    alternative_id: str,
    independent: IndependentCalculation,
    policy_id: str,
    state: str,
    issue_code: str | None = None,
    issue_message: str | None = None,
) -> ReconciliationResult:
    return ReconciliationResult(
        evidence_result_id=evidence_id,
        scenario_id=scenario_id,
        alternative_id=alternative_id,
        calculation_id=independent.calculation_id,
        formula_version=independent.formula_version,
        primary_result=None,
        independent_result=independent.value,
        unit=independent.unit,
        absolute_variance=None,
        relative_variance_percent=None,
        allowed_variance=None,
        tolerance_policy_id=policy_id,
        state=state,  # type: ignore[arg-type]
        raw_inputs=independent.raw_inputs,
        assumption_ids=independent.assumption_ids,
        limitations=LIMITATIONS,
        issue_code=issue_code or independent.issue_code,
        issue_message=issue_message or independent.issue_message,
    )
