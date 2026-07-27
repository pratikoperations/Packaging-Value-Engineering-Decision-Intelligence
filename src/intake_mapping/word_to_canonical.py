"""Map only confirmed Word-intake values into a canonical dataset draft.

The adapter invokes the existing canonical validator unchanged. A two-document
intake can remain invalid or insufficient; validation issues are preserved rather
than bypassed or silently filled.
"""

from __future__ import annotations

from typing import Any, Iterable

from src.data_models import validate_dataset
from src.review_comparison import FieldReviewGroup

from .models import IntakeMappingError
from .snapshot import collect_confirmed_fields

_BOARD_GRADE = {
    (3, "B"): "3PLY_B_FLUTE",
    (5, "BC"): "5PLY_BC_FLUTE",
    (3, "C"): "3PLY_C_FLUTE",
    (5, "EB"): "5PLY_EB_FLUTE",
}


def _role_values(groups: Iterable[FieldReviewGroup]) -> dict[str, dict[str, tuple[Any, str | None]]]:
    values: dict[str, dict[str, tuple[Any, str | None]]] = {"existing": {}, "proposed": {}}
    for field in collect_confirmed_fields(groups):
        values[field.document_role][field.field_name] = (field.effective_value, field.effective_unit)
    return values


def _value(role_values: dict[str, tuple[Any, str | None]], name: str) -> Any:
    item = role_values.get(name)
    return item[0] if item is not None else None


def _board_grade(role_values: dict[str, tuple[Any, str | None]]) -> str | None:
    ply = _value(role_values, "ply_count")
    flute = _value(role_values, "flute_combination")
    if isinstance(ply, bool) or not isinstance(ply, (int, float)) or flute is None:
        return None
    normalized_flute = str(flute).upper().replace("-", "").replace(" ", "")
    return _BOARD_GRADE.get((int(ply), normalized_flute))


def _alternative(role: str, role_values: dict[str, tuple[Any, str | None]]) -> dict[str, Any]:
    alternative: dict[str, Any] = {
        "alternative_id": "ALT-BASE" if role == "existing" else "ALT-PROPOSED",
        "name": "Existing specification" if role == "existing" else "Proposed specification",
        "status": "baseline" if role == "existing" else "proposed",
    }
    field_map = {
        "internal_length": "length_mm",
        "internal_width": "width_mm",
        "internal_height": "height_mm",
        "box_weight": "case_weight_g",
    }
    for source, destination in field_map.items():
        value = _value(role_values, source)
        if value is not None:
            alternative[destination] = value
    grade = _board_grade(role_values)
    if grade is not None:
        alternative["board_grade"] = grade

    # Preserve confirmed fields that are not part of the historical canonical
    # validator as explicit intake metadata without treating them as validated.
    alternative["word_intake_confirmed_fields"] = {
        name: {"value": value, "unit": unit}
        for name, (value, unit) in sorted(role_values.items())
    }
    return alternative


def build_canonical_dataset_draft(
    *,
    project: dict[str, Any],
    groups: Iterable[FieldReviewGroup],
    source_repository: str,
    source_commit: str,
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...], bool]:
    if project.get("archived_at") is not None:
        raise IntakeMappingError("Archived projects are read-only.")
    project_id = str(project.get("project_id") or "").strip()
    if not project_id:
        raise IntakeMappingError("Project record must contain project_id.")

    values = _role_values(groups)
    existing = _alternative("existing", values["existing"])
    proposed = _alternative("proposed", values["proposed"])
    evidence = [
        {
            "evidence_id": "EVID-WORD-EXISTING",
            "evidence_type": "uploaded_word_specification",
            "reference": "Existing DOCX specification; field-level source traceability is retained in the intake snapshot.",
        },
        {
            "evidence_id": "EVID-WORD-PROPOSED",
            "evidence_type": "uploaded_word_specification",
            "reference": "Proposed DOCX specification; field-level source traceability is retained in the intake snapshot.",
        },
    ]
    draft: dict[str, Any] = {
        "dataset_type": "synthetic_demo",
        "synthetic_notice": "PVE 2.0 Word-intake portfolio data is synthetic and requires engineering validation and human approval.",
        "packaging_project": {
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "category": project.get("category"),
            "annual_volume": project.get("annual_volume"),
            "annual_volume_unit": project.get("volume_unit") or "cases_per_year",
            "currency": project.get("currency"),
            "status": project.get("status"),
        },
        "decision_evidence": evidence,
        "packaging_alternatives": [existing, proposed],
        "baseline_specification": {
            "baseline_id": "BASE-WORD-INTAKE",
            "alternative_id": "ALT-BASE",
            "evidence_id": "EVID-WORD-EXISTING",
        },
        "material_components": [],
        "cost_inputs": [],
        "logistics_inputs": [],
        "technical_requirements": [],
        "technical_qualification_results": [],
        "risk_records": [],
        "sustainability_indicators": [],
        "validation_requirements": [],
        "decision_recommendation": {
            "recommendation_id": "REC-WORD-INTAKE-DRAFT",
            "status": "insufficient_data",
            "rationale": "Document intake creates a canonical draft only; engineering validation and human approval remain mandatory.",
        },
        "export_metadata": {
            "contract_version": "PVE-CONTRACT-v1.0-DRAFT",
            "source_repository": source_repository,
            "source_commit": source_commit,
        },
    }
    validation = validate_dataset(draft)
    issues = tuple(
        {"code": issue.code, "path": issue.path, "message": issue.message}
        for issue in validation.issues
    )
    return draft, issues, validation.is_valid
