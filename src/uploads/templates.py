from __future__ import annotations

import csv
import io
import json
from typing import Any


def build_json_template(project: dict[str, Any]) -> str:
    template = {
        "dataset_type": "user_upload",
        "schema_version": "1.0-user",
        "packaging_project": {
            "project_id": project["project_id"],
            "project_name": project["project_name"],
            "category": project["category"],
            "annual_volume": project["annual_volume"],
            "annual_volume_unit": "cases_per_year",
            "currency": project["currency"],
            "status": "active",
        },
        "decision_evidence": [],
        "baseline_specification": {
            "baseline_id": "BASE-UPLOAD-001",
            "alternative_id": "ALT-BASE",
        },
        "packaging_alternatives": [
            {
                "alternative_id": "ALT-BASE",
                "name": "Current corrugated shipping case",
                "status": "baseline",
                "length_mm": 600,
                "width_mm": 400,
                "height_mm": 350,
                "case_weight_g": 980,
                "board_grade": "5PLY_BC_FLUTE",
            },
            {
                "alternative_id": "ALT-A",
                "name": "Proposed corrugated shipping case",
                "status": "proposed",
                "length_mm": 575,
                "width_mm": 385,
                "height_mm": 330,
                "case_weight_g": 880,
                "board_grade": "5PLY_BC_FLUTE",
            },
        ],
        "material_components": [],
        "cost_inputs": [],
        "logistics_inputs": [],
        "technical_requirements": [],
        "technical_qualification_results": [],
        "risk_records": [],
        "sustainability_indicators": [],
        "validation_requirements": [],
        "decision_recommendation": {
            "recommendation_id": "REC-UPLOAD-PLACEHOLDER",
            "status": "insufficient_data",
            "rationale": "User-upload placeholder. No autonomous packaging approval is granted.",
        },
        "export_metadata": {
            "contract_version": "PVE-CONTRACT-v1.0-DRAFT",
            "source_repository": "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
            "source_commit": "USER-UPLOAD",
        },
    }
    return json.dumps(template, indent=2, ensure_ascii=False) + "\n"


def _csv_text(fieldnames: list[str], rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def build_project_csv_template(project: dict[str, Any]) -> str:
    fields = ["project_name", "category", "annual_volume", "currency"]
    return _csv_text(
        fields,
        [
            {
                "project_name": project["project_name"],
                "category": project["category"],
                "annual_volume": project["annual_volume"],
                "currency": project["currency"],
            }
        ],
    )


def build_alternatives_csv_template() -> str:
    fields = [
        "alternative_id",
        "name",
        "status",
        "length_mm",
        "width_mm",
        "height_mm",
        "case_weight_g",
        "board_grade",
    ]
    return _csv_text(
        fields,
        [
            {
                "alternative_id": "ALT-BASE",
                "name": "Current corrugated shipping case",
                "status": "baseline",
                "length_mm": 600,
                "width_mm": 400,
                "height_mm": 350,
                "case_weight_g": 980,
                "board_grade": "5PLY_BC_FLUTE",
            },
            {
                "alternative_id": "ALT-A",
                "name": "Proposed corrugated shipping case",
                "status": "proposed",
                "length_mm": 575,
                "width_mm": 385,
                "height_mm": 330,
                "case_weight_g": 880,
                "board_grade": "5PLY_BC_FLUTE",
            },
        ],
    )
