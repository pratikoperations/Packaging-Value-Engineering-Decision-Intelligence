from __future__ import annotations

from copy import deepcopy
from typing import Any

_COLLECTIONS = (
    "decision_evidence", "packaging_alternatives", "material_components",
    "cost_inputs", "logistics_inputs", "technical_requirements",
    "technical_qualification_results", "risk_records", "sustainability_indicators",
    "validation_requirements", "intake_values", "quality_tests", "document_register",
    "specification_tolerances", "corrugated_evidence", "supplier_capabilities",
    "governed_factors", "warehouse_profiles", "packing_line_profiles",
    "corrugated_material_profiles", "pallet_pattern_inputs", "logistics_scenarios",
    "physical_sustainability_profiles", "should_cost_inputs", "failure_cost_inputs",
    "inventory_inputs", "one_time_costs",
)

_NUMERIC_FIELDS = {
    "annual_volume", "annual_volume_cases", "annual_cases", "length_mm", "width_mm", "height_mm",
    "internal_length_mm", "internal_width_mm", "internal_height_mm",
    "external_length_mm", "external_width_mm", "external_height_mm",
    "case_external_length_mm", "case_external_width_mm", "case_external_height_mm",
    "blank_length_mm", "blank_width_mm", "manufacturers_joint_mm",
    "board_caliper_mm", "gross_packed_weight_kg", "case_pack_quantity",
    "print_colour_count", "ply", "layer_gsm", "stack_height",
    "stack_layers_required", "validated_stack_layers", "proposed_stack_layers", "storage_duration_days",
    "storage_temperature_min_c", "storage_temperature_max_c", "humidity_percent",
    "route_duration_days", "handling_touches", "maximum_pallet_height_mm",
    "maximum_pallet_weight_kg", "pallet_load_kg", "compression_requirement_n",
    "ect_requirement_kn_m", "ect_kn_m", "bct_n", "burst_kpa",
    "case_weight_g", "case_weight_kg", "product_weight_per_case_kg", "weight_g",
    "recycled_content_percent", "virgin_fibre_percent", "value", "value_per_case",
    "damage_rate_percent", "loss_per_damaged_case", "inventory_days",
    "unit_inventory_value", "transition_stock_units", "obsolete_stock_units",
    "write_off_percent", "production_batch_units", "moq_units",
    "cases_per_layer", "layers_per_pallet", "cases_per_pallet", "freight_distance_km",
    "minimum_value", "probability_percent", "nominal", "minimum", "maximum",
    "maximum_ply", "corrugator_width_mm", "minimum_sheet_length_mm",
    "maximum_sheet_length_mm", "minimum_sheet_width_mm", "maximum_sheet_width_mm",
    "maximum_print_colours", "result_value", "pallet_overhang_mm", "pallet_underhang_mm",
    "pallet_length_mm", "pallet_width_mm", "pallet_height_limit_mm",
    "pallet_weight_limit_kg", "empty_pallet_weight_kg", "pallet_height_mm",
    "pallet_gross_weight_kg", "footprint_utilisation_percent", "annual_pallet_movements",
    "annual_freight_cube_m3", "warehouse_positions", "annual_vehicle_spaces",
    "minimum_length_mm", "maximum_length_mm", "minimum_width_mm", "maximum_width_mm",
    "minimum_height_mm", "maximum_height_mm", "machine_speed_cases_per_min",
    "maximum_speed_cases_per_min",
}


def _coerce_number(value: Any) -> Any:
    """Normalize equivalent integer, float, and numeric-string values identically."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        number = float(value)
    elif isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return value
        try:
            number = float(stripped)
        except ValueError:
            return value
    else:
        return value
    return int(number) if number.is_integer() else number


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in record.items():
        clean_key = str(key).strip()
        if clean_key in _NUMERIC_FIELDS:
            normalized[clean_key] = _coerce_number(value)
        elif isinstance(value, str):
            normalized[clean_key] = value.strip()
        else:
            normalized[clean_key] = value
    return normalized


def normalize_user_dataset(raw: dict[str, Any], project: dict[str, Any]) -> dict[str, Any]:
    """Normalize JSON or template input into the canonical PVE dataset shape."""
    data = deepcopy(raw)
    data["dataset_type"] = "user_upload"
    data["schema_version"] = str(data.get("schema_version") or "1.0-user")
    data.pop("synthetic_notice", None)

    uploaded_project = data.get("packaging_project")
    if not isinstance(uploaded_project, dict):
        uploaded_project = {}
    uploaded_project = _normalize_record(uploaded_project)
    uploaded_project["project_id"] = project["project_id"]
    uploaded_project.setdefault("project_name", project["project_name"])
    uploaded_project.setdefault("category", project["category"])
    uploaded_project.setdefault("annual_volume", _coerce_number(project["annual_volume"]))
    uploaded_project.setdefault("annual_volume_unit", "cases_per_year")
    uploaded_project.setdefault("currency", project["currency"])
    uploaded_project.setdefault("status", "active")
    data["packaging_project"] = uploaded_project

    for name in _COLLECTIONS:
        records = data.get(name)
        if not isinstance(records, list):
            records = []
        data[name] = [_normalize_record(record) for record in records if isinstance(record, dict)]

    baseline = data.get("baseline_specification")
    if not isinstance(baseline, dict):
        baseline_alternative = next(
            (alternative for alternative in data["packaging_alternatives"] if alternative.get("status") == "baseline"),
            {},
        )
        baseline = {"baseline_id": "BASE-UPLOAD-001", "alternative_id": baseline_alternative.get("alternative_id")}
    data["baseline_specification"] = _normalize_record(baseline)

    recommendation = data.get("decision_recommendation")
    if not isinstance(recommendation, dict):
        recommendation = {}
    recommendation = _normalize_record(recommendation)
    recommendation.setdefault("recommendation_id", "REC-UPLOAD-PLACEHOLDER")
    recommendation.setdefault("status", "insufficient_data")
    recommendation.setdefault("rationale", "User-upload placeholder. No autonomous packaging approval is granted.")
    data["decision_recommendation"] = recommendation

    export = data.get("export_metadata")
    if not isinstance(export, dict):
        export = {}
    export = _normalize_record(export)
    export.setdefault("contract_version", "PVE-CONTRACT-v1.0-DRAFT")
    export.setdefault("source_repository", "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence")
    export.setdefault("source_commit", "USER-UPLOAD")
    data["export_metadata"] = export
    return data
