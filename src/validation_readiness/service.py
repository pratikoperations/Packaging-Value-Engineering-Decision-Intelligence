from __future__ import annotations

from collections import Counter
from typing import Any

from src.category_registry import default_registry
from .models import ComponentScore, OutputStatus, ReadinessAssessment

_WEIGHTS = {
    "project_metadata": 10.0,
    "baseline_specification": 20.0,
    "proposed_specification": 20.0,
    "commercial_data": 15.0,
    "logistics_application": 10.0,
    "quality_test_data": 20.0,
    "document_traceability": 5.0,
}

_APPROVAL_LIMITATION = (
    "Readiness is an intake and evidence-completeness indicator only. "
    "Engineering validation and human approval remain mandatory; autonomous approval is prohibited."
)


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _score_rows(key: str, label: str, rows: list[dict[str, Any]], *, required_only: bool = True) -> ComponentScore:
    relevant = [row for row in rows if not required_only or row.get("requirement") == "mandatory"]
    completed = sum(1 for row in relevant if _present(row.get("value") or row.get("result_value") or row.get("file_reference")))
    return ComponentScore(key, label, _WEIGHTS[key], completed, len(relevant))


def assess_readiness(*, project: dict[str, Any], canonical_data: dict[str, Any], dataset_id: str | None = None) -> ReadinessAssessment:
    category = str(project["category"])
    definition = default_registry().get("corrugated" if category == "corrugated_shipping_case" else category)
    values = canonical_data.get("intake_values") or []
    baseline = [row for row in values if row.get("context") == "baseline"]
    proposed = [row for row in values if row.get("context") == "proposed"]
    commercial = [row for row in values if row.get("context") == "commercial"]
    logistics = [row for row in values if row.get("context") == "logistics"]
    tests = canonical_data.get("quality_tests") or []
    documents = canonical_data.get("document_register") or []

    metadata_fields = ("project_id", "project_name", "category", "objective", "change_type", "annual_volume", "currency")
    metadata_completed = sum(1 for field in metadata_fields if _present((canonical_data.get("packaging_project") or {}).get(field)))
    components = (
        ComponentScore("project_metadata", "Project metadata", _WEIGHTS["project_metadata"], metadata_completed, len(metadata_fields)),
        _score_rows("baseline_specification", "Baseline specification", baseline),
        _score_rows("proposed_specification", "Proposed specification", proposed),
        _score_rows("commercial_data", "Commercial data", commercial),
        _score_rows("logistics_application", "Logistics and application data", logistics, required_only=False),
        _score_rows("quality_test_data", "Quality and test data", tests),
        _score_rows("document_traceability", "Document traceability", documents),
    )
    score = round(sum(item.weighted_score for item in components), 1)

    blockers: list[str] = []
    if not any(_present(row.get("value")) for row in baseline): blockers.append("No baseline specification")
    if not any(_present(row.get("value")) for row in proposed): blockers.append("No proposed specification")
    p = canonical_data.get("packaging_project") or {}
    if not _present(p.get("annual_volume")): blockers.append("Missing annual volume")
    commercial_map = {row.get("field_key"): row.get("value") for row in commercial}
    if not _present(commercial_map.get("current_unit_cost")): blockers.append("Missing current cost")
    if p.get("category") not in {category, "corrugated" if category == "corrugated_shipping_case" else category}:
        blockers.append("Baseline and proposed category mismatch")
    for row in tests:
        if row.get("requirement") == "mandatory" and not _present(row.get("result_value")):
            blockers.append(f"Missing mandatory laboratory test: {row.get('test_name')}")
        if row.get("source_classification") == "supplier_declared" and row.get("validation_status") == "valid":
            blockers.append(f"Supplier-declared data presented as tested: {row.get('test_name')}")
    for row in documents:
        if row.get("requirement") == "mandatory" and row.get("upload_status") != "uploaded":
            blockers.append(f"Missing mandatory document: {row.get('document_type')}")
        if row.get("verification_status") == "expired":
            blockers.append(f"Expired document: {row.get('document_type')}")

    if blockers:
        stage = "Insufficient Data"
    elif score >= 95:
        stage = "Ready for Approval Review"
    elif score >= 85:
        stage = "Ready for Trial Validation"
    elif score >= 70:
        stage = "Ready for Laboratory Testing"
    elif score >= 50:
        stage = "Ready for Technical Screening"
    elif score >= 30:
        stage = "Ready for Commercial Screening"
    else:
        stage = "Draft"

    available = []
    available.append(OutputStatus("document_completeness", True))
    available.append(OutputStatus("test_requirement_checklist", True))
    commercial_ready = _present(commercial_map.get("current_unit_cost")) and _present(commercial_map.get("proposed_unit_cost")) and _present(p.get("annual_volume"))
    available.append(OutputStatus("commercial_analysis", commercial_ready, () if commercial_ready else ("Current cost, proposed cost and annual volume are required.",)))
    technical_reasons = tuple(blockers) or ("PVE 1.1 does not provide final category engineering feasibility.",)
    available.append(OutputStatus("technical_feasibility", False, technical_reasons))
    available.append(OutputStatus("approval_decision", False, ("Human approval and engineering validation are mandatory.",)))

    sources = Counter(str(row.get("source_classification")) for row in [*baseline, *proposed, *commercial, *logistics, *tests] if row.get("source_classification"))
    return ReadinessAssessment(project["project_id"], dataset_id, category, score, stage, components, tuple(dict.fromkeys(blockers)), tuple(available), dict(sources), _APPROVAL_LIMITATION)
