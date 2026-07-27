from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from src.data_models import validate_dataset
from src.intake_mapping import build_canonical_dataset_draft
from src.review_comparison import FieldReviewGroup, ReviewState, group_reviews

from .pairing import SpecificationPair
from .review_view import CommonReviewView, all_reviews_resolved

_ACCEPTED = {ReviewState.CONFIRMED, ReviewState.CORRECTED_CONFIRMED}


@dataclass(frozen=True)
class UnifiedCanonicalDraft:
    canonical_data: dict[str, Any]
    validation_issues: tuple[dict[str, Any], ...]
    is_valid: bool


def review_groups(views: Iterable[CommonReviewView]) -> tuple[FieldReviewGroup, ...]:
    items = tuple(views)
    if not all_reviews_resolved(items):
        raise ValueError("All extraction candidates must be reviewed before canonical mapping.")
    return group_reviews(tuple(item.review for item in items))


def _lineage_by_role(
    pair: SpecificationPair,
    views: Iterable[CommonReviewView],
) -> dict[str, dict[str, dict[str, Any]]]:
    documents = {
        pair.existing.document_role.value: pair.existing,
        pair.proposed.document_role.value: pair.proposed,
    }
    lineage: dict[str, dict[str, dict[str, Any]]] = {"existing": {}, "proposed": {}}
    for view in views:
        review = view.review
        if review.state not in _ACCEPTED:
            continue
        document = documents[view.document_role.value]
        lineage[view.document_role.value][view.field_name] = {
            "review_state": review.state.value,
            "raw_value": review.candidate.raw_value,
            "normalized_value": review.candidate.normalized_value,
            "original_unit": review.candidate.unit,
            "corrected_value": review.corrected_value,
            "corrected_unit": review.corrected_unit,
            "effective_value": review.effective_value,
            "effective_unit": review.effective_unit,
            "source_format": document.document_format.value,
            "document_sha256": document.sha256,
            "parser_name": view.parser_name,
            "parser_version": view.parser_version,
            "source_block_id": view.source_block_id,
            "source_excerpt": view.source_excerpt,
            "source_location": dict(view.source_location),
            "confidence": view.confidence,
            "confidence_band": view.confidence_band,
            "ambiguity_codes": list(view.ambiguity_codes),
            "reviewer_note": review.reviewer_note,
        }
    return lineage


def _evidence(role: str, document) -> dict[str, Any]:
    suffix = role.upper()
    return {
        "evidence_id": f"EVID-SPEC-{suffix}",
        "evidence_type": f"uploaded_{document.document_format.value}_specification",
        "reference": (
            f"{role.title()} {document.document_format.value.upper()} specification; "
            "field-level source traceability is retained in confirmed intake metadata."
        ),
    }


def build_unified_canonical_draft(
    *,
    project: dict[str, Any],
    pair: SpecificationPair,
    views: Iterable[CommonReviewView],
    source_repository: str,
    source_commit: str,
) -> UnifiedCanonicalDraft:
    items = tuple(views)
    groups = review_groups(items)

    draft, _, _ = build_canonical_dataset_draft(
        project=project,
        groups=groups,
        source_repository=source_repository,
        source_commit=source_commit,
    )

    lineage = _lineage_by_role(pair, items)
    alternatives = {item["status"]: item for item in draft["packaging_alternatives"]}
    alternatives["baseline"].pop("word_intake_confirmed_fields", None)
    alternatives["proposed"].pop("word_intake_confirmed_fields", None)
    alternatives["baseline"]["specification_intake_confirmed_fields"] = lineage["existing"]
    alternatives["proposed"]["specification_intake_confirmed_fields"] = lineage["proposed"]

    draft["decision_evidence"] = [
        _evidence("existing", pair.existing),
        _evidence("proposed", pair.proposed),
    ]
    draft["baseline_specification"] = {
        "baseline_id": "BASE-SPEC-INTAKE",
        "alternative_id": "ALT-BASE",
        "evidence_id": "EVID-SPEC-EXISTING",
    }
    draft["synthetic_notice"] = (
        "Unified specification-intake portfolio data is synthetic and requires "
        "engineering validation and human approval."
    )
    draft["decision_recommendation"] = {
        "recommendation_id": "REC-SPEC-INTAKE-DRAFT",
        "status": "insufficient_data",
        "rationale": (
            "Document intake creates a canonical draft only; engineering validation "
            "and human approval remain mandatory."
        ),
    }

    validation = validate_dataset(draft)
    issues = tuple(
        {"code": issue.code, "path": issue.path, "message": issue.message}
        for issue in validation.issues
    )
    return UnifiedCanonicalDraft(draft, issues, validation.is_valid)
