from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class AvailableOutput:
    name: str
    status: str
    value: Any
    unit: str
    supporting_inputs: tuple[str, ...]
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class UnavailableOutput:
    name: str
    status: str
    reason: str
    missing_inputs: tuple[str, ...]
    blocking_conditions: tuple[str, ...] = ()


@dataclass(frozen=True)
class PalletPattern:
    orientation: str
    cases_per_layer: int
    layers_per_pallet: int
    cases_per_pallet: int
    footprint_utilisation_percent: float
    pallet_height_mm: float
    pallet_gross_weight_kg: float
    annual_pallet_movements: int
    status: str
    limitations: tuple[str, ...]


def _positive(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _percent(value: Any) -> float | None:
    number = _positive(value)
    if number is None or number > 100:
        return None
    return number


def board_area_from_supplied_blank(specification: Mapping[str, Any]) -> AvailableOutput | UnavailableOutput:
    """Calculate board area only from explicit blank dimensions; never infer geometry."""
    length = _positive(specification.get("blank_length_mm"))
    width = _positive(specification.get("blank_width_mm"))
    missing = tuple(
        key for key, value in (("blank_length_mm", length), ("blank_width_mm", width)) if value is None
    )
    if missing:
        return UnavailableOutput(
            "board_area",
            "unavailable",
            "Supplied blank dimensions are required; case geometry is not inferred.",
            missing,
        )
    return AvailableOutput(
        "board_area",
        "available",
        round(length * width / 1_000_000.0, 6),
        "m2/case",
        ("blank_length_mm", "blank_width_mm"),
        ("Area is based on the supplied rectangular blank only.",),
    )


def material_comparison(
    *,
    annual_volume_cases: Any,
    baseline: Mapping[str, Any],
    proposed: Mapping[str, Any],
    technical_blockers: Sequence[str] = (),
) -> Mapping[str, AvailableOutput | UnavailableOutput]:
    """Compare supplied case weights and blank areas without optimizing construction."""
    volume = _positive(annual_volume_cases)
    baseline_weight = _positive(baseline.get("case_weight_g"))
    proposed_weight = _positive(proposed.get("case_weight_g"))
    outputs: dict[str, AvailableOutput | UnavailableOutput] = {
        "baseline_board_area": board_area_from_supplied_blank(baseline),
        "proposed_board_area": board_area_from_supplied_blank(proposed),
    }
    missing = tuple(
        key
        for key, value in (
            ("annual_volume_cases", volume),
            ("baseline.case_weight_g", baseline_weight),
            ("proposed.case_weight_g", proposed_weight),
        )
        if value is None
    )
    if missing:
        for name in ("baseline_annual_material", "proposed_annual_material", "annual_material_change"):
            outputs[name] = UnavailableOutput(
                name,
                "unavailable",
                "Annual volume and supplied baseline/proposed case weights are required.",
                missing,
                tuple(technical_blockers),
            )
        return outputs

    baseline_kg = baseline_weight * volume / 1000.0
    proposed_kg = proposed_weight * volume / 1000.0
    change_kg = proposed_kg - baseline_kg
    limitation = (
        "Technical blockers remain controlling and cannot be overridden by material benefit.",
    ) if technical_blockers else ()
    outputs["baseline_annual_material"] = AvailableOutput(
        "baseline_annual_material", "available", round(baseline_kg, 6), "kg/year",
        ("annual_volume_cases", "baseline.case_weight_g"), limitation,
    )
    outputs["proposed_annual_material"] = AvailableOutput(
        "proposed_annual_material", "available", round(proposed_kg, 6), "kg/year",
        ("annual_volume_cases", "proposed.case_weight_g"), limitation,
    )
    outputs["annual_material_change"] = AvailableOutput(
        "annual_material_change", "blocked" if technical_blockers else "available",
        round(change_kg, 6), "kg/year",
        ("annual_volume_cases", "baseline.case_weight_g", "proposed.case_weight_g"),
        limitation,
    )
    return outputs


def _orientation_pattern(
    *,
    label: str,
    case_length_mm: float,
    case_width_mm: float,
    case_height_mm: float,
    case_weight_kg: float,
    pallet_length_mm: float,
    pallet_width_mm: float,
    pallet_height_limit_mm: float,
    pallet_weight_limit_kg: float,
    empty_pallet_weight_kg: float,
    validated_stack_layers: int,
    annual_volume_cases: float,
) -> PalletPattern:
    along_length = floor(pallet_length_mm / case_length_mm)
    along_width = floor(pallet_width_mm / case_width_mm)
    cases_per_layer = max(0, along_length * along_width)
    if cases_per_layer == 0:
        return PalletPattern(label, 0, 0, 0, 0.0, 0.0, empty_pallet_weight_kg, 0, "unavailable", (
            "Case footprint does not fit the supplied pallet orientation.",
        ))
    height_layers = floor(pallet_height_limit_mm / case_height_mm)
    weight_capacity = pallet_weight_limit_kg - empty_pallet_weight_kg
    weight_layers = floor(weight_capacity / (case_weight_kg * cases_per_layer)) if weight_capacity > 0 else 0
    layers = min(height_layers, weight_layers, validated_stack_layers)
    if layers <= 0:
        return PalletPattern(label, cases_per_layer, 0, 0, round(cases_per_layer * case_length_mm * case_width_mm / (pallet_length_mm * pallet_width_mm) * 100, 6), 0.0, empty_pallet_weight_kg, 0, "unavailable", (
            "Supplied height, weight, or validated stacking limits allow no complete layer.",
        ))
    cases_per_pallet = cases_per_layer * layers
    footprint = cases_per_layer * case_length_mm * case_width_mm / (pallet_length_mm * pallet_width_mm) * 100
    pallet_height = layers * case_height_mm
    gross_weight = empty_pallet_weight_kg + cases_per_pallet * case_weight_kg
    movements = ceil(annual_volume_cases / cases_per_pallet)
    return PalletPattern(
        label, cases_per_layer, layers, cases_per_pallet, round(footprint, 6),
        round(pallet_height, 6), round(gross_weight, 6), movements, "available",
        ("Simple rectangular orientation only; this is not global pallet optimisation.",),
    )


def compare_simple_pallet_patterns(
    inputs: Mapping[str, Any], *, technical_blockers: Sequence[str] = ()
) -> tuple[PalletPattern, ...] | UnavailableOutput:
    """Compare length-width and width-length rectangular layouts using supplied limits."""
    keys = (
        "case_external_length_mm", "case_external_width_mm", "case_external_height_mm",
        "case_weight_kg", "pallet_length_mm", "pallet_width_mm", "pallet_height_limit_mm",
        "pallet_weight_limit_kg", "empty_pallet_weight_kg", "validated_stack_layers",
        "annual_volume_cases",
    )
    values = {key: _positive(inputs.get(key)) for key in keys}
    missing = tuple(key for key, value in values.items() if value is None)
    if missing:
        return UnavailableOutput(
            "simple_pallet_pattern_comparison", "unavailable",
            "All case, pallet, stacking, weight, and annual-volume inputs must be supplied.",
            missing, tuple(technical_blockers),
        )
    layers = int(values["validated_stack_layers"])
    common = dict(
        case_height_mm=values["case_external_height_mm"],
        case_weight_kg=values["case_weight_kg"],
        pallet_length_mm=values["pallet_length_mm"],
        pallet_width_mm=values["pallet_width_mm"],
        pallet_height_limit_mm=values["pallet_height_limit_mm"],
        pallet_weight_limit_kg=values["pallet_weight_limit_kg"],
        empty_pallet_weight_kg=values["empty_pallet_weight_kg"],
        validated_stack_layers=layers,
        annual_volume_cases=values["annual_volume_cases"],
    )
    patterns = (
        _orientation_pattern(
            label="length x width",
            case_length_mm=values["case_external_length_mm"],
            case_width_mm=values["case_external_width_mm"],
            **common,
        ),
        _orientation_pattern(
            label="width x length",
            case_length_mm=values["case_external_width_mm"],
            case_width_mm=values["case_external_length_mm"],
            **common,
        ),
    )
    if technical_blockers:
        patterns = tuple(
            PalletPattern(
                p.orientation, p.cases_per_layer, p.layers_per_pallet, p.cases_per_pallet,
                p.footprint_utilisation_percent, p.pallet_height_mm, p.pallet_gross_weight_kg,
                p.annual_pallet_movements, "blocked", p.limitations + (
                    "Technical blockers remain controlling; logistics benefit cannot authorize the proposal.",
                ),
            ) for p in patterns
        )
    return patterns


def logistics_comparison(
    baseline: Mapping[str, Any], proposed: Mapping[str, Any]
) -> Mapping[str, AvailableOutput | UnavailableOutput]:
    """Compare only explicitly supplied logistics scenario values."""
    definitions = {
        "annual_pallet_movements": "movements/year",
        "annual_freight_cube_m3": "m3/year",
        "warehouse_positions": "positions",
        "annual_vehicle_spaces": "vehicle-spaces/year",
    }
    outputs: dict[str, AvailableOutput | UnavailableOutput] = {}
    for key, unit in definitions.items():
        base = _positive(baseline.get(key))
        prop = _positive(proposed.get(key))
        name = f"{key}_change"
        if base is None or prop is None:
            outputs[name] = UnavailableOutput(
                name, "unavailable", "Baseline and proposed scenario values must be supplied.",
                tuple(part for part, value in ((f"baseline.{key}", base), (f"proposed.{key}", prop)) if value is None),
            )
        else:
            outputs[name] = AvailableOutput(
                name, "available", round(prop - base, 6), unit,
                (f"baseline.{key}", f"proposed.{key}"),
                ("This is an explicit-input scenario comparison, not a transport optimisation.",),
            )
    return outputs


def physical_sustainability_indicators(
    *,
    annual_volume_cases: Any,
    baseline: Mapping[str, Any],
    proposed: Mapping[str, Any],
    pallet_movements_baseline: Any = None,
    pallet_movements_proposed: Any = None,
    emission_factor_dataset: Mapping[str, Any] | None = None,
) -> Mapping[str, AvailableOutput | UnavailableOutput]:
    """Return physical indicators only; carbon remains unavailable without governed factors."""
    volume = _positive(annual_volume_cases)
    base_weight = _positive(baseline.get("case_weight_g"))
    prop_weight = _positive(proposed.get("case_weight_g"))
    product_weight = _positive(proposed.get("product_weight_per_case_kg"))
    recycled = _percent(proposed.get("recycled_content_percent"))
    virgin = _percent(proposed.get("virgin_fibre_percent"))
    outputs: dict[str, AvailableOutput | UnavailableOutput] = {}
    if volume and base_weight and prop_weight:
        baseline_kg = base_weight * volume / 1000.0
        proposed_kg = prop_weight * volume / 1000.0
        outputs["annual_paper_consumption"] = AvailableOutput(
            "annual_paper_consumption", "available", round(proposed_kg, 6), "kg/year",
            ("annual_volume_cases", "proposed.case_weight_g"),
        )
        outputs["annual_paper_reduction"] = AvailableOutput(
            "annual_paper_reduction", "available", round(baseline_kg - proposed_kg, 6), "kg/year",
            ("annual_volume_cases", "baseline.case_weight_g", "proposed.case_weight_g"),
        )
        outputs["packaging_weight_per_shipped_unit"] = AvailableOutput(
            "packaging_weight_per_shipped_unit", "available", round(prop_weight, 6), "g/case",
            ("proposed.case_weight_g",),
        )
    else:
        missing = tuple(key for key, value in (("annual_volume_cases", volume), ("baseline.case_weight_g", base_weight), ("proposed.case_weight_g", prop_weight)) if value is None)
        for name in ("annual_paper_consumption", "annual_paper_reduction", "packaging_weight_per_shipped_unit"):
            outputs[name] = UnavailableOutput(name, "unavailable", "Volume and supplied case weights are required.", missing)
    if prop_weight and product_weight:
        outputs["packaging_to_product_weight_ratio"] = AvailableOutput(
            "packaging_to_product_weight_ratio", "available",
            round((prop_weight / 1000.0) / product_weight, 6), "ratio",
            ("proposed.case_weight_g", "proposed.product_weight_per_case_kg"),
        )
    else:
        outputs["packaging_to_product_weight_ratio"] = UnavailableOutput(
            "packaging_to_product_weight_ratio", "unavailable",
            "Supplied packaging and product weights are required.",
            tuple(key for key, value in (("proposed.case_weight_g", prop_weight), ("proposed.product_weight_per_case_kg", product_weight)) if value is None),
        )
    for name, value in (("recycled_content_percent", recycled), ("virgin_fibre_percent", virgin)):
        if value is None:
            outputs[name] = UnavailableOutput(name, "unavailable", "A percentage between 0 and 100 must be supplied.", (f"proposed.{name}",))
        else:
            outputs[name] = AvailableOutput(name, "available", value, "%", (f"proposed.{name}",))
    if recycled is not None and virgin is not None and recycled + virgin > 100:
        outputs["fibre_content_validation"] = UnavailableOutput(
            "fibre_content_validation", "unavailable",
            "Recycled and virgin fibre percentages cannot total more than 100%.",
            (), ("invalid fibre-content total",),
        )
    base_movements = _positive(pallet_movements_baseline)
    prop_movements = _positive(pallet_movements_proposed)
    if base_movements and prop_movements:
        avoided = base_movements - prop_movements
        outputs["pallets_avoided"] = AvailableOutput("pallets_avoided", "available", round(avoided, 6), "pallets/year", ("pallet_movements_baseline", "pallet_movements_proposed"))
        outputs["transport_movements_avoided"] = AvailableOutput("transport_movements_avoided", "available", round(avoided, 6), "movements/year", ("pallet_movements_baseline", "pallet_movements_proposed"))
    else:
        for name in ("pallets_avoided", "transport_movements_avoided"):
            outputs[name] = UnavailableOutput(name, "unavailable", "Baseline and proposed movement values are required.", ("pallet_movements_baseline", "pallet_movements_proposed"))
    governed = emission_factor_dataset or {}
    if governed.get("validation_status") == "valid" and governed.get("source_reference") and governed.get("version"):
        outputs["carbon_emissions"] = UnavailableOutput(
            "carbon_emissions", "unavailable",
            "Carbon calculation is outside PVE 1.2 Build 5 even when a governed dataset is supplied.", (),
        )
    else:
        outputs["carbon_emissions"] = UnavailableOutput(
            "carbon_emissions", "unavailable",
            "No governed, versioned, validated emission-factor dataset is available.",
            ("emission_factor_dataset",),
        )
    return outputs
