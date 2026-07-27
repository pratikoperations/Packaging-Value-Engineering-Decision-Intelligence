"""Deterministic review operations for AI extraction candidates."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Mapping, Tuple

from src.ai_extraction import AmbiguityCode, ExtractionCandidate
from src.document_intake import ParsedDocument, SourceBlock

from .models import (
    CandidateReview,
    FieldReviewGroup,
    ReviewError,
    ReviewState,
    SourceEvidence,
)


BLOCKING_AMBIGUITIES = frozenset(
    {
        AmbiguityCode.MULTIPLE_CANDIDATES,
        AmbiguityCode.INTERNAL_EXTERNAL_UNCLEAR,
        AmbiguityCode.REQUIREMENT_RESULT_UNCLEAR,
        AmbiguityCode.UNIT_CONFLICT,
        AmbiguityCode.DOCUMENT_ROLE_UNCLEAR,
        AmbiguityCode.SOURCE_NOT_FOUND,
        AmbiguityCode.PROMPT_INJECTION_SUSPECTED,
    }
)


def _source_index(document: ParsedDocument) -> Mapping[str, SourceBlock]:
    return {block.block_id: block for block in document.blocks}


def build_candidate_reviews(
    candidates: Iterable[ExtractionCandidate],
    documents: Iterable[ParsedDocument],
) -> Tuple[CandidateReview, ...]:
    """Build pending reviews with structural evidence from parsed documents."""

    by_role = {document.role: document for document in documents}
    reviews: list[CandidateReview] = []
    for candidate in candidates:
        document = by_role.get(candidate.document_role)
        if document is None:
            raise ReviewError(f"No parsed document exists for role {candidate.document_role.value}.")
        block = _source_index(document).get(candidate.source_block_id)
        if block is None:
            raise ReviewError(f"Candidate source block {candidate.source_block_id} is unavailable.")
        if candidate.source_excerpt not in block.text:
            raise ReviewError("Candidate source excerpt is not grounded in the cited block.")
        reviews.append(
            CandidateReview(
                candidate=candidate,
                source=SourceEvidence(
                    block_id=block.block_id,
                    block_type=block.block_type,
                    excerpt=candidate.source_excerpt,
                    location=block.location,
                ),
            )
        )
    return tuple(reviews)


def confirm(review: CandidateReview, *, reviewer_note: str | None = None) -> CandidateReview:
    """Confirm an extracted value only when blocking ambiguity is absent."""

    blockers = BLOCKING_AMBIGUITIES.intersection(review.candidate.ambiguity_codes)
    if blockers:
        raise ReviewError(
            "Candidate cannot be confirmed until blocking ambiguity is resolved: "
            + ", ".join(sorted(code.value for code in blockers))
        )
    if review.candidate.normalized_value is None:
        raise ReviewError("Candidate has no normalized value to confirm.")
    return replace(
        review,
        state=ReviewState.CONFIRMED,
        corrected_value=None,
        corrected_unit=None,
        reviewer_note=reviewer_note,
    )


def correct_and_confirm(
    review: CandidateReview,
    corrected_value: object,
    corrected_unit: str | None,
    *,
    reviewer_note: str,
) -> CandidateReview:
    """Preserve the original candidate while recording an explicit correction."""

    if corrected_value is None or corrected_value == "":
        raise ReviewError("Corrected value must be supplied.")
    if not reviewer_note or not reviewer_note.strip():
        raise ReviewError("A correction note is required.")
    return replace(
        review,
        state=ReviewState.CORRECTED_CONFIRMED,
        corrected_value=corrected_value,
        corrected_unit=corrected_unit,
        reviewer_note=reviewer_note.strip(),
    )


def intentionally_omit(review: CandidateReview, *, reviewer_note: str) -> CandidateReview:
    if not reviewer_note or not reviewer_note.strip():
        raise ReviewError("An omission note is required.")
    return replace(
        review,
        state=ReviewState.INTENTIONALLY_OMITTED,
        corrected_value=None,
        corrected_unit=None,
        reviewer_note=reviewer_note.strip(),
    )


def reject(review: CandidateReview, *, reviewer_note: str) -> CandidateReview:
    if not reviewer_note or not reviewer_note.strip():
        raise ReviewError("A rejection note is required.")
    return replace(
        review,
        state=ReviewState.REJECTED,
        corrected_value=None,
        corrected_unit=None,
        reviewer_note=reviewer_note.strip(),
    )


def group_reviews(reviews: Iterable[CandidateReview]) -> Tuple[FieldReviewGroup, ...]:
    grouped: dict[tuple[str, object], list[CandidateReview]] = {}
    for review in reviews:
        key = (review.candidate.field_name, review.candidate.document_role)
        grouped.setdefault(key, []).append(review)
    return tuple(
        FieldReviewGroup(field_name=field, document_role=role, reviews=tuple(items))
        for (field, role), items in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1].value))
    )


def resolve_candidate(group: FieldReviewGroup, candidate_index: int) -> FieldReviewGroup:
    """Select one candidate after duplicate-candidate review."""

    if len(group.reviews) < 2:
        if candidate_index != 0:
            raise ReviewError("Single-candidate group can resolve only index 0.")
    if not 0 <= candidate_index < len(group.reviews):
        raise ReviewError("Resolved candidate index is out of range.")
    selected = group.reviews[candidate_index]
    if not selected.is_accepted:
        raise ReviewError("Resolved candidate must be confirmed or corrected-confirmed.")
    return replace(group, resolved_candidate_index=candidate_index)


def unresolved_reason(group: FieldReviewGroup) -> str | None:
    accepted = tuple(review for review in group.reviews if review.is_accepted)
    if group.has_multiple_candidates and group.resolved_candidate_index is None:
        return "multiple_candidates_unresolved"
    if len(accepted) > 1 and group.resolved_candidate_index is None:
        return "multiple_accepted_candidates"
    if any(review.state is ReviewState.PENDING for review in group.reviews):
        return "pending_review"
    if group.resolved_candidate_index is not None and group.selected_review is None:
        return "invalid_resolution"
    return None
