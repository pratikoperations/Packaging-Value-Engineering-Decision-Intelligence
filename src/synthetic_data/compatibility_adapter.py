from __future__ import annotations

from typing import Any

from .domain import SYNTHETIC_DISCLOSURE, SyntheticDataError


def build_legacy_dataset(package: dict[str, Any], scenario_id: str) -> dict[str, Any]:
    scenarios = {item["scenario_id"]: item for item in package["scenarios"]}
    scenario = scenarios.get(scenario_id)
    if scenario is None:
        raise SyntheticDataError("UNKNOWN_SCENARIO", f"Unknown governed scenario: {scenario_id}.")

    specifications = {item["specification_id"]: item for item in package["specifications"]}
    quotations = {item["quotation_id"]: item for item in package["quotations"]}
    selected_spec_ids = [scenario["baseline_specification_id"], *scenario["proposed_specification_ids"]]
    selected_specs = [specifications[value] for value in selected_spec_ids]
    alt_by_spec = {item["specification_id"]: item["alternative_id"] for item in selected_specs}

    evidence = []
    cost_inputs = []
    for quote_id in scenario["quotation_ids"]:
        quote = quotations[quote_id]
        evidence_id = f"EV-{quote_id}"
        evidence.append({"evidence_id": evidence_id, "evidence_type": "supplier_quote", "reference": quote_id})
        cost_inputs.append({
            "cost_id": f"COST-{quote_id}",
            "alternative_id": alt_by_spec[quote["specification_id"]],
            "input_name": "Governed synthetic quoted unit price",
            "value": quote["unit_price"],
            "unit": "INR_per_case",
            "currency": "INR",
            "evidence_id": evidence_id,
        })

    technical_results = []
    for result in package["technical_results"]:
        if result["specification_id"] not in alt_by_spec:
            continue
        evidence_id = f"EV-{result['technical_result_id']}" if result.get("status") == "qualified" else None
        if evidence_id:
            evidence.append({"evidence_id": evidence_id, "evidence_type": "test_report", "reference": result["technical_result_id"]})
        technical_results.append({
            "qualification_id": result["technical_result_id"],
            "alternative_id": alt_by_spec[result["specification_id"]],
            "requirement_id": result["requirement_id"],
            "status": result["status"],
            "evidence_id": evidence_id,
        })

    risk_records = []
    for risk in package["risk_events"]:
        spec_id = risk.get("specification_id")
        if spec_id not in alt_by_spec:
            continue
        risk_records.append({
            "risk_id": risk["risk_event_id"],
            "alternative_id": alt_by_spec[spec_id],
            "risk_type": risk["risk_type"],
            "level": risk["level"],
            "probability_percent": risk["probability_percent"],
        })

    alternatives = []
    components = []
    logistics = []
    sustainability = []
    validations = []
    for spec in selected_specs:
        alternative_id = spec["alternative_id"]
        alternatives.append({
            "alternative_id": alternative_id,
            "name": spec["name"],
            "status": spec["status"],
            "length_mm": spec["length_mm"],
            "width_mm": spec["width_mm"],
            "height_mm": spec["height_mm"],
            "case_weight_g": spec["case_weight_g"],
            "board_grade": spec["board_grade"],
        })
        components.extend((
            {"component_id": f"MC-{alternative_id}-1", "alternative_id": alternative_id, "material_name": "Corrugated board blank", "weight_g": spec["case_weight_g"] - 25, "recycled_content_percent": spec["recycled_content_percent"]},
            {"component_id": f"MC-{alternative_id}-2", "alternative_id": alternative_id, "material_name": "Adhesive and ink", "weight_g": 25, "recycled_content_percent": 0},
        ))
        logistics.append({"logistics_id": f"LOG-{alternative_id}", "alternative_id": alternative_id, "cases_per_pallet": spec["cases_per_pallet"], "freight_distance_km": 650, "evidence_id": None})
        sustainability.append({"indicator_id": f"SUS-{alternative_id}", "alternative_id": alternative_id, "metric": "material_weight_g", "value": spec["case_weight_g"], "unit": "g"})
        if spec["status"] == "proposed":
            validations.append({"validation_id": f"VAL-{alternative_id}", "alternative_id": alternative_id, "activity": spec["validation_activity"], "status": "planned"})

    manifest = package["manifest"]
    return {
        "dataset_type": "synthetic_demo",
        "dataset_id": manifest["dataset_id"],
        "dataset_version": manifest["dataset_version"],
        "synthetic_notice": SYNTHETIC_DISCLOSURE,
        "schema_version": manifest["schema_version"],
        "packaging_project": {
            "project_id": scenario["project_id"],
            "project_name": scenario["title"],
            "category": "corrugated_shipping_case",
            "annual_volume": scenario["annual_volume"],
            "annual_volume_unit": "cases_per_year",
            "currency": "INR",
            "status": "active",
        },
        "decision_evidence": evidence,
        "baseline_specification": {"baseline_id": scenario["baseline_specification_id"], "alternative_id": selected_specs[0]["alternative_id"], "evidence_id": None},
        "packaging_alternatives": alternatives,
        "material_components": components,
        "cost_inputs": cost_inputs,
        "logistics_inputs": logistics,
        "technical_requirements": [
            {"requirement_id": "REQ-BCT", "name": "Minimum box compression strength", "minimum_value": 520, "unit": "kgf"},
            {"requirement_id": "REQ-STACK", "name": "Minimum pallet stack layers", "minimum_value": 4, "unit": "unitless"},
        ],
        "technical_qualification_results": technical_results,
        "risk_records": risk_records,
        "sustainability_indicators": sustainability,
        "validation_requirements": validations,
        "decision_recommendation": {"recommendation_id": f"REC-{scenario_id}", "status": "insufficient_data", "rationale": scenario["decision_message"]},
        "export_metadata": {
            "contract_version": "PVE-CONTRACT-v1.0-DRAFT",
            "source_repository": "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
            "source_commit": "GOVERNED-SYNTHETIC-DATASET",
            "synthetic_disclosure": SYNTHETIC_DISCLOSURE,
        },
    }
