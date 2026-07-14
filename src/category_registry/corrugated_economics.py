from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .corrugated_evidence import SOURCE_CLASSIFICATIONS

SHOULD_COST_COMPONENTS = (
    "board_or_paper", "conversion", "printing", "coating_or_treatment",
    "manufacturing_waste", "quality_inspection", "freight",
)
ONE_TIME_COST_COMPONENTS = ("tooling", "artwork", "trials", "implementation")


@dataclass(frozen=True)
class EconomicOutput:
    name: str
    status: str
    value: float | None
    currency: str | None
    supporting_inputs: tuple[str, ...]
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    blocking_conditions: tuple[str, ...]


@dataclass(frozen=True)
class EconomicAssessment:
    outputs: Mapping[str, EconomicOutput]
    source_traceability: tuple[Mapping[str, Any], ...]
    technical_blockers: tuple[str, ...]


def _number(value: Any, name: str, *, allow_zero: bool = True) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric.")
    number = float(value)
    if number < 0 or (number == 0 and not allow_zero):
        raise ValueError(f"{name} must be {'non-negative' if allow_zero else 'positive'}.")
    return number


def _validate_currency(records: Sequence[Mapping[str, Any]], currency: str) -> None:
    for index, record in enumerate(records):
        if record.get("currency") != currency:
            raise ValueError(f"record {index} currency must match project currency {currency}.")


def _trace(records: Sequence[Mapping[str, Any]], collection: str) -> tuple[Mapping[str, Any], ...]:
    traced = []
    for index, record in enumerate(records):
        source = str(record.get("source_classification") or "").strip()
        if source not in SOURCE_CLASSIFICATIONS:
            raise ValueError(f"{collection}.{index}.source_classification is invalid.")
        reference = str(record.get("source_reference") or "").strip()
        if not reference:
            raise ValueError(f"{collection}.{index}.source_reference is required.")
        traced.append({
            "collection": collection,
            "record_id": record.get("record_id") or record.get("component") or str(index),
            "source_classification": source,
            "source_reference": reference,
            "source_role": record.get("source_role"),
            "validation_status": record.get("validation_status"),
        })
    return tuple(traced)


def _component_total(records: Sequence[Mapping[str, Any]], context: str, currency: str) -> tuple[float, tuple[str, ...]]:
    selected = [record for record in records if record.get("context") == context]
    if not selected:
        raise ValueError(f"No should-cost records supplied for {context}.")
    _validate_currency(selected, currency)
    names: list[str] = []
    total = 0.0
    seen: set[str] = set()
    for index, record in enumerate(selected):
        component = str(record.get("component") or "").strip()
        if component not in SHOULD_COST_COMPONENTS:
            raise ValueError(f"should_cost_inputs.{index}.component is invalid.")
        if component in seen:
            raise ValueError(f"Duplicate should-cost component for {context}: {component}.")
        seen.add(component)
        total += _number(record.get("value_per_case"), f"{context}.{component}.value_per_case")
        names.append(component)
    return total, tuple(sorted(names))


def _failure_cost(record: Mapping[str, Any], context: str, currency: str) -> float:
    if record.get("context") != context:
        raise ValueError(f"Failure-cost context must be {context}.")
    if record.get("currency") != currency:
        raise ValueError("Failure-cost currency must match project currency.")
    annual_cases = _number(record.get("annual_cases"), f"{context}.annual_cases", allow_zero=False)
    damage_rate = _number(record.get("damage_rate_percent"), f"{context}.damage_rate_percent")
    if damage_rate > 100:
        raise ValueError("damage_rate_percent cannot exceed 100.")
    loss = _number(record.get("loss_per_damaged_case"), f"{context}.loss_per_damaged_case")
    return annual_cases * damage_rate / 100.0 * loss


def _working_capital(record: Mapping[str, Any], context: str, currency: str) -> tuple[float, float]:
    if record.get("context") != context:
        raise ValueError(f"Inventory context must be {context}.")
    if record.get("currency") != currency:
        raise ValueError("Inventory currency must match project currency.")
    annual_cases = _number(record.get("annual_cases"), f"{context}.annual_cases", allow_zero=False)
    inventory_days = _number(record.get("inventory_days"), f"{context}.inventory_days")
    unit_value = _number(record.get("unit_inventory_value"), f"{context}.unit_inventory_value")
    transition_stock = _number(record.get("transition_stock_units", 0), f"{context}.transition_stock_units")
    obsolete_stock = _number(record.get("obsolete_stock_units", 0), f"{context}.obsolete_stock_units")
    write_off_rate = _number(record.get("write_off_percent", 100), f"{context}.write_off_percent")
    if write_off_rate > 100:
        raise ValueError("write_off_percent cannot exceed 100.")
    average_inventory = annual_cases / 365.0 * inventory_days * unit_value
    transition_value = transition_stock * unit_value
    write_off = obsolete_stock * unit_value * write_off_rate / 100.0
    return average_inventory + transition_value, write_off


def analyze_corrugated_economics(
    *,
    currency: str,
    annual_cases: float,
    should_cost_inputs: Sequence[Mapping[str, Any]],
    failure_cost_inputs: Sequence[Mapping[str, Any]],
    inventory_inputs: Sequence[Mapping[str, Any]],
    one_time_costs: Sequence[Mapping[str, Any]],
    technical_blockers: Sequence[str] = (),
) -> EconomicAssessment:
    """Calculate explicit commercial scenarios; never infers prices, rates or approval."""
    if not currency:
        raise ValueError("currency is required.")
    volume = _number(annual_cases, "annual_cases", allow_zero=False)
    blockers = tuple(dict.fromkeys(str(item) for item in technical_blockers if str(item)))
    traceability = (
        _trace(should_cost_inputs, "should_cost_inputs")
        + _trace(failure_cost_inputs, "failure_cost_inputs")
        + _trace(inventory_inputs, "inventory_inputs")
        + _trace(one_time_costs, "one_time_costs")
    )
    assumptions = tuple(sorted({
        str(record.get("source_reference"))
        for records in (should_cost_inputs, failure_cost_inputs, inventory_inputs, one_time_costs)
        for record in records
        if record.get("source_classification") in {"predicted", "assumption"}
    }))
    limitations = (
        "No market price, supplier margin, paper price, conversion rate or waste factor is inferred.",
        "Economic outputs cannot override technical blockers or constitute approval.",
    )
    outputs: dict[str, EconomicOutput] = {}

    try:
        baseline_unit, baseline_components = _component_total(should_cost_inputs, "baseline", currency)
        proposed_unit, proposed_components = _component_total(should_cost_inputs, "proposed", currency)
        gross_benefit = (baseline_unit - proposed_unit) * volume
        status = "blocked" if blockers else "available"
        outputs["should_cost"] = EconomicOutput(
            "should_cost", status, proposed_unit, currency,
            baseline_components + proposed_components, assumptions, limitations, blockers,
        )
        outputs["gross_annual_benefit"] = EconomicOutput(
            "gross_annual_benefit", status, gross_benefit, currency,
            ("baseline unit cost", "proposed unit cost", "annual cases"), assumptions, limitations, blockers,
        )
    except ValueError as exc:
        gross_benefit = None
        outputs["should_cost"] = EconomicOutput("should_cost", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)
        outputs["gross_annual_benefit"] = EconomicOutput("gross_annual_benefit", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)

    failure_by_context = {str(record.get("context")): record for record in failure_cost_inputs}
    try:
        baseline_failure = _failure_cost(failure_by_context["baseline"], "baseline", currency)
        proposed_failure = _failure_cost(failure_by_context["proposed"], "proposed", currency)
        incremental_failure = proposed_failure - baseline_failure
        risk_adjusted = None if gross_benefit is None else gross_benefit - incremental_failure
        status = "blocked" if blockers else "available"
        outputs["incremental_failure_cost"] = EconomicOutput(
            "incremental_failure_cost", status, incremental_failure, currency,
            ("baseline damage rate", "proposed damage rate", "loss per damaged case", "annual cases"), assumptions, limitations, blockers,
        )
        outputs["risk_adjusted_annual_benefit"] = EconomicOutput(
            "risk_adjusted_annual_benefit", status if risk_adjusted is not None else "unavailable", risk_adjusted, currency,
            ("gross annual benefit", "incremental failure cost"), assumptions, limitations, blockers,
        )
    except (KeyError, ValueError) as exc:
        outputs["incremental_failure_cost"] = EconomicOutput("incremental_failure_cost", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)
        outputs["risk_adjusted_annual_benefit"] = EconomicOutput("risk_adjusted_annual_benefit", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)
        risk_adjusted = None

    inventory_by_context = {str(record.get("context")): record for record in inventory_inputs}
    try:
        baseline_wc, baseline_write_off = _working_capital(inventory_by_context["baseline"], "baseline", currency)
        proposed_wc, proposed_write_off = _working_capital(inventory_by_context["proposed"], "proposed", currency)
        incremental_wc = proposed_wc - baseline_wc
        write_off = proposed_write_off + baseline_write_off
        status = "blocked" if blockers else "available"
        outputs["incremental_working_capital"] = EconomicOutput("incremental_working_capital", status, incremental_wc, currency, ("inventory days", "unit inventory value", "transition stock"), assumptions, limitations, blockers)
        outputs["obsolete_stock_write_off"] = EconomicOutput("obsolete_stock_write_off", status, write_off, currency, ("obsolete stock", "unit inventory value", "write-off percent"), assumptions, limitations, blockers)
    except (KeyError, ValueError) as exc:
        incremental_wc = None
        write_off = None
        outputs["incremental_working_capital"] = EconomicOutput("incremental_working_capital", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)
        outputs["obsolete_stock_write_off"] = EconomicOutput("obsolete_stock_write_off", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)

    try:
        _validate_currency(one_time_costs, currency)
        seen: set[str] = set()
        one_time_total = 0.0
        for index, record in enumerate(one_time_costs):
            component = str(record.get("component") or "").strip()
            if component not in ONE_TIME_COST_COMPONENTS:
                raise ValueError(f"one_time_costs.{index}.component is invalid.")
            if component in seen:
                raise ValueError(f"Duplicate one-time component: {component}.")
            seen.add(component)
            one_time_total += _number(record.get("value"), f"one_time_costs.{index}.value")
        if risk_adjusted is None or incremental_wc is None or write_off is None:
            raise ValueError("Risk-adjusted benefit and inventory outputs are required.")
        first_year = risk_adjusted - one_time_total - incremental_wc - write_off
        payback = None if risk_adjusted <= 0 else one_time_total / risk_adjusted * 12.0
        status = "blocked" if blockers else "available"
        outputs["first_year_net_benefit"] = EconomicOutput("first_year_net_benefit", status, first_year, currency, ("risk-adjusted annual benefit", "one-time costs", "working capital", "write-off"), assumptions, limitations, blockers)
        outputs["payback_months"] = EconomicOutput("payback_months", status if payback is not None else "unavailable", payback, "months" if payback is not None else None, ("one-time costs", "risk-adjusted annual benefit"), assumptions, limitations, blockers)
    except ValueError as exc:
        outputs["first_year_net_benefit"] = EconomicOutput("first_year_net_benefit", "unavailable", None, currency, (), assumptions, limitations + (str(exc),), blockers)
        outputs["payback_months"] = EconomicOutput("payback_months", "unavailable", None, None, (), assumptions, limitations + (str(exc),), blockers)

    return EconomicAssessment(outputs, traceability, blockers)
