from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommercialAnalysis:
    saving_per_unit: float
    annual_gross_saving: float
    expected_realized_saving: float
    first_year_net_benefit: float
    payback_months: float | None
    material_reduction_per_unit: float | None
    annual_material_reduction: float | None
    percentage_cost_reduction: float
    percentage_material_reduction: float | None
    labels: dict[str, str]
    assumptions: tuple[str, ...]


def _non_negative(name: str, value: float) -> float:
    number = float(value)
    if number < 0:
        raise ValueError(f"{name} must be greater than or equal to zero.")
    return number


def calculate_commercial_analysis(
    *,
    current_unit_cost: float,
    proposed_unit_cost: float,
    annual_volume: float,
    realization_percent: float = 100.0,
    testing_cost: float = 0.0,
    tooling_cost: float = 0.0,
    implementation_cost: float = 0.0,
    qualification_cost: float = 0.0,
    current_material_weight: float | None = None,
    proposed_material_weight: float | None = None,
    assumptions: tuple[str, ...] = (),
) -> CommercialAnalysis:
    current_cost = _non_negative("current_unit_cost", current_unit_cost)
    proposed_cost = _non_negative("proposed_unit_cost", proposed_unit_cost)
    volume = _non_negative("annual_volume", annual_volume)
    realization = float(realization_percent)
    if not 0 <= realization <= 100:
        raise ValueError("realization_percent must be between 0 and 100.")

    investment = sum(
        _non_negative(name, value)
        for name, value in {
            "testing_cost": testing_cost,
            "tooling_cost": tooling_cost,
            "implementation_cost": implementation_cost,
            "qualification_cost": qualification_cost,
        }.items()
    )

    saving_per_unit = current_cost - proposed_cost
    annual_gross = saving_per_unit * volume
    realized = annual_gross * (realization / 100.0)
    first_year_net = realized - investment
    monthly_realized = realized / 12.0
    payback_months = investment / monthly_realized if investment > 0 and monthly_realized > 0 else None
    cost_reduction = (saving_per_unit / current_cost * 100.0) if current_cost > 0 else 0.0

    material_per_unit = None
    annual_material = None
    material_percent = None
    if current_material_weight is not None or proposed_material_weight is not None:
        if current_material_weight is None or proposed_material_weight is None:
            raise ValueError("Both current and proposed material weights are required together.")
        current_weight = _non_negative("current_material_weight", current_material_weight)
        proposed_weight = _non_negative("proposed_material_weight", proposed_material_weight)
        material_per_unit = current_weight - proposed_weight
        annual_material = material_per_unit * volume
        material_percent = (material_per_unit / current_weight * 100.0) if current_weight > 0 else 0.0

    labels = {
        "annual_gross_saving": "Estimate based on entered unit costs and annual volume.",
        "expected_realized_saving": "Estimate after applying the entered realization percentage.",
        "first_year_net_benefit": "Estimate after deducting entered testing, tooling, implementation, and qualification costs.",
        "payback_months": "Estimate based on monthly realized saving; unavailable when monthly realized saving is not positive.",
        "material_reduction": "Estimate based on entered current and proposed material weights.",
    }

    return CommercialAnalysis(
        saving_per_unit=saving_per_unit,
        annual_gross_saving=annual_gross,
        expected_realized_saving=realized,
        first_year_net_benefit=first_year_net,
        payback_months=payback_months,
        material_reduction_per_unit=material_per_unit,
        annual_material_reduction=annual_material,
        percentage_cost_reduction=cost_reduction,
        percentage_material_reduction=material_percent,
        labels=labels,
        assumptions=tuple(assumptions),
    )
