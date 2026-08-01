from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any, Callable

from .catalogue import CALCULATION_CATALOGUE
from .models import IndependentCalculation


class IndependentCalculationError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def decimal_value(value: Any, name: str) -> Decimal:
    if value is None:
        raise IndependentCalculationError("MISSING_INPUT", f"{name} is required.")
    if isinstance(value, bool):
        raise IndependentCalculationError("INVALID_NUMBER", f"{name} must not be boolean.")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise IndependentCalculationError("INVALID_NUMBER", f"{name} must be numeric.") from exc
    if not result.is_finite():
        raise IndependentCalculationError("INVALID_NUMBER", f"{name} must be finite.")
    return result


def _quantize(calculation_id: str, value: Decimal) -> Decimal:
    return value.quantize(CALCULATION_CATALOGUE[calculation_id].quantum, rounding=ROUND_HALF_EVEN)


def _validate_currency(currency: str | None) -> None:
    if currency != "INR":
        raise IndependentCalculationError("UNSUPPORTED_CURRENCY", "Gate 2 supports INR only.")


def _validate_sign(value: Decimal, policy: str, name: str) -> None:
    if policy == "positive" and value <= 0:
        raise IndependentCalculationError("INVALID_SIGN", f"{name} must be positive.")
    if policy == "non_negative" and value < 0:
        raise IndependentCalculationError("INVALID_SIGN", f"{name} must be non-negative.")


def _result(calculation_id: str, value: Decimal, raw_inputs: dict[str, Any], assumption_ids: tuple[str, ...] = ()) -> IndependentCalculation:
    definition = CALCULATION_CATALOGUE[calculation_id]
    quantized = _quantize(calculation_id, value)
    _validate_sign(quantized, definition.sign_policy, definition.business_name)
    return IndependentCalculation(
        calculation_id=calculation_id,
        formula_version=definition.version,
        value=quantized,
        unit=definition.output_unit,
        raw_inputs={key: str(item) for key, item in raw_inputs.items()},
        assumption_ids=assumption_ids,
    )


def calculate(calculation_id: str, inputs: dict[str, Any], *, currency: str | None = None, assumption_ids: tuple[str, ...] = ()) -> IndependentCalculation:
    definition = CALCULATION_CATALOGUE.get(calculation_id)
    if definition is None:
        return IndependentCalculation(calculation_id, "unknown", None, "unknown", {}, assumption_ids, "unsupported", "UNSUPPORTED_CALCULATION", "No authorized independent formula exists.")
    if definition.currency:
        try:
            _validate_currency(currency)
        except IndependentCalculationError as exc:
            return IndependentCalculation(calculation_id, definition.version, None, definition.output_unit, {}, assumption_ids, "unsupported", exc.code, exc.message)
    try:
        value = _CALCULATORS[calculation_id](inputs)
        return _result(calculation_id, value, inputs, assumption_ids)
    except IndependentCalculationError as exc:
        status = "unsupported" if exc.code in {"ZERO_DENOMINATOR", "UNSUPPORTED_UNIT", "UNSUPPORTED_CURRENCY"} else "insufficient_evidence"
        return IndependentCalculation(calculation_id, definition.version, None, definition.output_unit, {key: str(item) for key, item in inputs.items()}, assumption_ids, status, exc.code, exc.message)


def _sum_costs(inputs: dict[str, Any]) -> Decimal:
    values = inputs.get("cost_inputs")
    if not isinstance(values, (list, tuple)) or not values:
        raise IndependentCalculationError("MISSING_INPUT", "cost_inputs must be a non-empty sequence.")
    decimals = [decimal_value(value, "cost_input") for value in values]
    if any(value < 0 for value in decimals):
        raise IndependentCalculationError("INVALID_SIGN", "Cost inputs must be non-negative.")
    return sum(decimals, Decimal("0"))


def _annual_cost(inputs: dict[str, Any]) -> Decimal:
    unit_cost = decimal_value(inputs.get("unit_cost"), "unit_cost")
    volume = decimal_value(inputs.get("annual_volume"), "annual_volume")
    if unit_cost < 0 or volume <= 0:
        raise IndependentCalculationError("INVALID_SIGN", "Unit cost must be non-negative and annual volume positive.")
    return unit_cost * volume


def _unit_savings(inputs: dict[str, Any]) -> Decimal:
    return decimal_value(inputs.get("baseline_unit_cost"), "baseline_unit_cost") - decimal_value(inputs.get("alternative_unit_cost"), "alternative_unit_cost")


def _annual_savings(inputs: dict[str, Any]) -> Decimal:
    volume = decimal_value(inputs.get("annual_volume"), "annual_volume")
    if volume <= 0:
        raise IndependentCalculationError("INVALID_SIGN", "Annual volume must be positive.")
    return decimal_value(inputs.get("unit_savings"), "unit_savings") * volume


def _cost_percent(inputs: dict[str, Any]) -> Decimal:
    baseline = decimal_value(inputs.get("baseline_unit_cost"), "baseline_unit_cost")
    if baseline == 0:
        raise IndependentCalculationError("ZERO_DENOMINATOR", "Baseline unit cost is zero.")
    return (decimal_value(inputs.get("alternative_unit_cost"), "alternative_unit_cost") - baseline) / baseline * Decimal("100")


def _sum_weights(inputs: dict[str, Any]) -> Decimal:
    values = inputs.get("component_weights_g")
    if not isinstance(values, (list, tuple)) or not values:
        raise IndependentCalculationError("MISSING_INPUT", "component_weights_g must be a non-empty sequence.")
    decimals = [decimal_value(value, "component_weight_g") for value in values]
    if any(value <= 0 for value in decimals):
        raise IndependentCalculationError("INVALID_SIGN", "Component weights must be positive.")
    return sum(decimals, Decimal("0"))


def _component_variance(inputs: dict[str, Any]) -> Decimal:
    return decimal_value(inputs.get("component_total_g"), "component_total_g") - decimal_value(inputs.get("case_weight_g"), "case_weight_g")


def _annual_material(inputs: dict[str, Any]) -> Decimal:
    weight = decimal_value(inputs.get("case_weight_g"), "case_weight_g")
    volume = decimal_value(inputs.get("annual_volume"), "annual_volume")
    if weight <= 0 or volume <= 0:
        raise IndependentCalculationError("INVALID_SIGN", "Case weight and annual volume must be positive.")
    return weight * volume / Decimal("1000")


def _material_change(inputs: dict[str, Any]) -> Decimal:
    return decimal_value(inputs.get("alternative_weight_g"), "alternative_weight_g") - decimal_value(inputs.get("baseline_weight_g"), "baseline_weight_g")


def _material_percent(inputs: dict[str, Any]) -> Decimal:
    baseline = decimal_value(inputs.get("baseline_weight_g"), "baseline_weight_g")
    if baseline == 0:
        raise IndependentCalculationError("ZERO_DENOMINATOR", "Baseline material weight is zero.")
    return (decimal_value(inputs.get("alternative_weight_g"), "alternative_weight_g") - baseline) / baseline * Decimal("100")


def _adjustment_factor(inputs: dict[str, Any]) -> Decimal:
    percent = decimal_value(inputs.get("adjustment_percent"), "adjustment_percent")
    if percent < Decimal("-50") or percent > Decimal("100"):
        raise IndependentCalculationError("OUT_OF_RANGE", "Adjustment percent must be between -50 and 100.")
    return Decimal("1") + percent / Decimal("100")


def _adjusted_cost(inputs: dict[str, Any]) -> Decimal:
    raw = decimal_value(inputs.get("raw_cost"), "raw_cost")
    factor = decimal_value(inputs.get("adjustment_factor"), "adjustment_factor")
    if raw < 0 or factor <= 0:
        raise IndependentCalculationError("INVALID_SIGN", "Raw cost must be non-negative and factor positive.")
    return raw * factor


def _adjusted_weight(inputs: dict[str, Any]) -> Decimal:
    raw = decimal_value(inputs.get("raw_weight_g"), "raw_weight_g")
    factor = decimal_value(inputs.get("adjustment_factor"), "adjustment_factor")
    if raw <= 0 or factor <= 0:
        raise IndependentCalculationError("INVALID_SIGN", "Raw weight and factor must be positive.")
    return raw * factor


def _board_weight(inputs: dict[str, Any]) -> Decimal:
    case = decimal_value(inputs.get("case_weight_g"), "case_weight_g")
    adhesive = decimal_value(inputs.get("adhesive_ink_weight_g"), "adhesive_ink_weight_g")
    result = case - adhesive
    if result < 0:
        raise IndependentCalculationError("INVALID_SIGN", "Derived board weight must be non-negative.")
    return result


def _component_reconciliation(inputs: dict[str, Any]) -> Decimal:
    board = decimal_value(inputs.get("board_weight_g"), "board_weight_g")
    adhesive = decimal_value(inputs.get("adhesive_ink_weight_g"), "adhesive_ink_weight_g")
    if board < 0 or adhesive < 0:
        raise IndependentCalculationError("INVALID_SIGN", "Component weights must be non-negative.")
    return board + adhesive


_CALCULATORS: dict[str, Callable[[dict[str, Any]], Decimal]] = {
    "CALC-COST-001": _sum_costs,
    "CALC-COST-002": _annual_cost,
    "CALC-COST-003": _unit_savings,
    "CALC-COST-004": _annual_savings,
    "CALC-COST-005": _cost_percent,
    "CALC-MAT-001": _sum_weights,
    "CALC-MAT-002": _component_variance,
    "CALC-MAT-003": _annual_material,
    "CALC-MAT-004": _material_change,
    "CALC-MAT-005": _material_percent,
    "CALC-SCN-001": _adjustment_factor,
    "CALC-SCN-002": _adjusted_cost,
    "CALC-SCN-003": lambda inputs: _adjusted_weight({"raw_weight_g": inputs.get("raw_case_weight_g"), "adjustment_factor": inputs.get("adjustment_factor")}),
    "CALC-SCN-004": lambda inputs: _adjusted_weight({"raw_weight_g": inputs.get("raw_component_weight_g"), "adjustment_factor": inputs.get("adjustment_factor")}),
    "CALC-ADP-001": _board_weight,
    "CALC-ADP-002": _component_reconciliation,
}
