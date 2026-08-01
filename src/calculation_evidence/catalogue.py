from __future__ import annotations

from decimal import Decimal

from .models import CalculationDefinition, TolerancePolicy

ROUNDING_MODE = "ROUND_HALF_EVEN"

TOLERANCE_POLICIES = {
    "TOL-UNIT-CURRENCY-001": TolerancePolicy("TOL-UNIT-CURRENCY-001", Decimal("0.000001"), Decimal("0.000001")),
    "TOL-ANNUAL-CURRENCY-001": TolerancePolicy("TOL-ANNUAL-CURRENCY-001", Decimal("0.01"), Decimal("0.000001")),
    "TOL-WEIGHT-001": TolerancePolicy("TOL-WEIGHT-001", Decimal("0.000001"), Decimal("0.000001")),
    "TOL-MATERIAL-001": TolerancePolicy("TOL-MATERIAL-001", Decimal("0.000001"), Decimal("0.000001")),
    "TOL-PERCENT-001": TolerancePolicy("TOL-PERCENT-001", Decimal("0.000001"), Decimal("0.000001")),
    "TOL-FACTOR-001": TolerancePolicy("TOL-FACTOR-001", Decimal("0.000001"), Decimal("0.000001")),
}


def _definition(
    calculation_id: str,
    business_name: str,
    expression: str,
    required_inputs: tuple[str, ...],
    accepted_units: tuple[str, ...],
    output_unit: str,
    quantum: str,
    tolerance_policy_id: str,
    sign_policy: str,
    primary_location: str,
    evidence_location: str,
    currency: str | None = None,
    limitations: tuple[str, ...] = (),
) -> CalculationDefinition:
    return CalculationDefinition(
        calculation_id=calculation_id,
        version="1.0.0",
        business_name=business_name,
        expression=expression,
        required_inputs=required_inputs,
        accepted_units=accepted_units,
        output_unit=output_unit,
        quantum=Decimal(quantum),
        rounding_mode=ROUNDING_MODE,
        tolerance_policy_id=tolerance_policy_id,
        sign_policy=sign_policy,
        currency=currency,
        primary_location=primary_location,
        evidence_location=evidence_location,
        limitations=limitations,
    )


CALCULATION_CATALOGUE = {
    "CALC-COST-001": _definition("CALC-COST-001", "Unit-cost aggregation", "sum(cost_inputs)", ("cost_inputs",), ("INR_per_case",), "INR_per_case", "0.000001", "TOL-UNIT-CURRENCY-001", "non_negative", "src/cost_engine/engine.py", "src/calculation_evidence/formulas.py", "INR"),
    "CALC-COST-002": _definition("CALC-COST-002", "Annual cost", "unit_cost * annual_volume", ("unit_cost", "annual_volume"), ("INR_per_case", "cases_per_year"), "INR_per_year", "0.01", "TOL-ANNUAL-CURRENCY-001", "non_negative", "src/cost_engine/engine.py", "src/calculation_evidence/formulas.py", "INR"),
    "CALC-COST-003": _definition("CALC-COST-003", "Unit savings versus baseline", "baseline_unit_cost - alternative_unit_cost", ("baseline_unit_cost", "alternative_unit_cost"), ("INR_per_case",), "INR_per_case", "0.000001", "TOL-UNIT-CURRENCY-001", "signed", "src/cost_engine/engine.py", "src/calculation_evidence/formulas.py", "INR"),
    "CALC-COST-004": _definition("CALC-COST-004", "Annual savings versus baseline", "unit_savings * annual_volume", ("unit_savings", "annual_volume"), ("INR_per_case", "cases_per_year"), "INR_per_year", "0.01", "TOL-ANNUAL-CURRENCY-001", "signed", "src/cost_engine/engine.py", "src/calculation_evidence/formulas.py", "INR"),
    "CALC-COST-005": _definition("CALC-COST-005", "Cost variance percentage", "(alternative_unit_cost - baseline_unit_cost) / baseline_unit_cost * 100", ("alternative_unit_cost", "baseline_unit_cost"), ("INR_per_case",), "percent", "0.000001", "TOL-PERCENT-001", "signed", "src/cost_engine/engine.py", "src/calculation_evidence/formulas.py", "INR", ("Zero baseline is unsupported.",)),
    "CALC-MAT-001": _definition("CALC-MAT-001", "Component-weight aggregation", "sum(component_weights_g)", ("component_weights_g",), ("g_per_case",), "g_per_case", "0.000001", "TOL-WEIGHT-001", "positive", "src/material_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-MAT-002": _definition("CALC-MAT-002", "Component variance", "component_total_g - case_weight_g", ("component_total_g", "case_weight_g"), ("g_per_case",), "g_per_case", "0.000001", "TOL-WEIGHT-001", "signed", "src/material_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-MAT-003": _definition("CALC-MAT-003", "Annual material", "case_weight_g * annual_volume / 1000", ("case_weight_g", "annual_volume"), ("g_per_case", "cases_per_year"), "kg_per_year", "0.000001", "TOL-MATERIAL-001", "positive", "src/material_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-MAT-004": _definition("CALC-MAT-004", "Material change versus baseline", "alternative_weight_g - baseline_weight_g", ("alternative_weight_g", "baseline_weight_g"), ("g_per_case",), "g_per_case", "0.000001", "TOL-WEIGHT-001", "signed", "src/material_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-MAT-005": _definition("CALC-MAT-005", "Material variance percentage", "(alternative_weight_g - baseline_weight_g) / baseline_weight_g * 100", ("alternative_weight_g", "baseline_weight_g"), ("g_per_case",), "percent", "0.000001", "TOL-PERCENT-001", "signed", "src/material_engine/engine.py", "src/calculation_evidence/formulas.py", limitations=("Zero baseline is unsupported.",)),
    "CALC-SCN-001": _definition("CALC-SCN-001", "Adjustment factor", "1 + adjustment_percent / 100", ("adjustment_percent",), ("percent",), "factor", "0.000001", "TOL-FACTOR-001", "positive", "src/scenario_engine/engine.py", "src/calculation_evidence/formulas.py", limitations=("Adjustment must be between -50 and 100 percent.",)),
    "CALC-SCN-002": _definition("CALC-SCN-002", "Adjusted cost input", "raw_cost * adjustment_factor", ("raw_cost", "adjustment_factor"), ("INR_per_case", "factor"), "INR_per_case", "0.000001", "TOL-UNIT-CURRENCY-001", "non_negative", "src/scenario_engine/engine.py", "src/calculation_evidence/formulas.py", "INR"),
    "CALC-SCN-003": _definition("CALC-SCN-003", "Adjusted case weight", "raw_case_weight_g * adjustment_factor", ("raw_case_weight_g", "adjustment_factor"), ("g_per_case", "factor"), "g_per_case", "0.000001", "TOL-WEIGHT-001", "positive", "src/scenario_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-SCN-004": _definition("CALC-SCN-004", "Adjusted component weight", "raw_component_weight_g * adjustment_factor", ("raw_component_weight_g", "adjustment_factor"), ("g_per_case", "factor"), "g_per_case", "0.000001", "TOL-WEIGHT-001", "positive", "src/scenario_engine/engine.py", "src/calculation_evidence/formulas.py"),
    "CALC-ADP-001": _definition("CALC-ADP-001", "Board component derivation", "case_weight_g - adhesive_ink_weight_g", ("case_weight_g", "adhesive_ink_weight_g"), ("g_per_case",), "g_per_case", "0.000001", "TOL-WEIGHT-001", "non_negative", "src/synthetic_data/compatibility_adapter.py", "src/calculation_evidence/formulas.py", limitations=("Uses synthetic assumption ASM-SYN-ADH-001.",)),
    "CALC-ADP-002": _definition("CALC-ADP-002", "Component reconciliation", "board_weight_g + adhesive_ink_weight_g", ("board_weight_g", "adhesive_ink_weight_g"), ("g_per_case",), "g_per_case", "0.000001", "TOL-WEIGHT-001", "positive", "src/synthetic_data/compatibility_adapter.py", "src/calculation_evidence/formulas.py", limitations=("Uses synthetic assumption ASM-SYN-ADH-001.",)),
}

RULE_LINEAGE = {
    "RULE-RISK-001": "Probability-to-risk band classification",
    "RULE-RISK-002": "Declared-versus-probability severity maximum",
    "RULE-RISK-003": "Overall risk maximum",
    "RULE-QUAL-001": "Qualification-status precedence",
    "RULE-REC-001": "Recommendation gate",
    "RULE-REC-002": "Preferred-alternative ordering",
}

ASSUMPTIONS = {
    "ASM-SYN-ADH-001": {"name": "Synthetic adhesive-and-ink weight", "value": "25", "unit": "g_per_case", "classification": "synthetic_assumption"},
    "ASM-SYN-FRT-001": {"name": "Synthetic freight distance", "value": "650", "unit": "km", "classification": "synthetic_assumption"},
    "ASM-CUR-INR-001": {"name": "INR-only currency basis", "value": "INR", "unit": "currency", "classification": "governed_constraint"},
    "ASM-ROUND-001": {"name": "Evidence rounding policy", "value": ROUNDING_MODE, "unit": "rounding_mode", "classification": "governed_policy"},
}


def validate_catalogue() -> None:
    if len(CALCULATION_CATALOGUE) != 16:
        raise ValueError("The independent calculation catalogue must contain exactly 16 numeric formulas.")
    if len(RULE_LINEAGE) != 6:
        raise ValueError("The rule-lineage catalogue must contain exactly six rules.")
    for calculation_id, definition in CALCULATION_CATALOGUE.items():
        if calculation_id != definition.calculation_id:
            raise ValueError(f"Calculation catalogue key mismatch: {calculation_id}.")
        if definition.tolerance_policy_id not in TOLERANCE_POLICIES:
            raise ValueError(f"Unknown tolerance policy for {calculation_id}.")
        if definition.currency not in {None, "INR"}:
            raise ValueError(f"Unsupported currency in {calculation_id}.")
