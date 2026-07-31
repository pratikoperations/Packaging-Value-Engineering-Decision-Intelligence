from __future__ import annotations

import pytest

from src.domain.approved_specification import (
    ApprovedSpecificationError,
    GovernedSpecificationField,
    approved_specification_content_hash,
    materialize_approved_specification,
)
from src.domain.specification_review import ReviewStatus


def field(
    key: str,
    existing: object,
    proposed: object,
    *,
    status: ReviewStatus | None = None,
    mandatory: bool = True,
    corrected: object | None = None,
    excluded: bool = False,
) -> GovernedSpecificationField:
    return GovernedSpecificationField(
        field_key=key,
        existing_value=existing,
        proposed_value=proposed,
        status=status,
        mandatory=mandatory,
        corrected_value=corrected,
        intentionally_excluded=excluded,
    )


def test_accepted_candidate_uses_proposed_value() -> None:
    result = materialize_approved_specification(
        [field("gsm", 120, 140, status=ReviewStatus.ACCEPTED)],
        eligible=True,
    )
    assert result.as_mapping() == {"gsm": 140}
    assert result.approved_values[0].source == "accepted_proposed"


def test_corrected_candidate_uses_corrected_value() -> None:
    result = materialize_approved_specification(
        [field("caliper", 1.0, 0.8, status=ReviewStatus.CORRECTED, corrected=0.9)],
        eligible=True,
    )
    assert result.as_mapping() == {"caliper": 0.9}
    assert result.approved_values[0].source == "corrected"


def test_rejected_candidate_retains_existing_baseline() -> None:
    result = materialize_approved_specification(
        [field("burst_strength", 8.0, 7.0, status=ReviewStatus.REJECTED)],
        eligible=True,
    )
    assert result.as_mapping() == {"burst_strength": 8.0}
    assert result.approved_values[0].source == "retained_existing"


def test_unchanged_governed_field_is_preserved() -> None:
    result = materialize_approved_specification(
        [field("flute", "B", "B")],
        eligible=True,
    )
    assert result.as_mapping() == {"flute": "B"}
    assert result.approved_values[0].source == "unchanged"


def test_absent_optional_field_can_be_explicitly_excluded() -> None:
    result = materialize_approved_specification(
        [field("coating", None, None, mandatory=False, excluded=True)],
        eligible=True,
    )
    assert result.approved_values == ()
    assert result.excluded_fields == ("coating",)


def test_mandatory_field_cannot_be_excluded() -> None:
    with pytest.raises(ValueError, match="mandatory fields"):
        field("gsm", None, None, excluded=True)


def test_output_order_is_deterministic() -> None:
    first = materialize_approved_specification(
        [
            field("z_field", 1, 2, status=ReviewStatus.ACCEPTED),
            field("a_field", 5, 5),
        ],
        eligible=True,
    )
    second = materialize_approved_specification(
        [
            field("a_field", 5, 5),
            field("z_field", 1, 2, status=ReviewStatus.ACCEPTED),
        ],
        eligible=True,
    )
    assert first == second
    assert tuple(item.field_key for item in first.approved_values) == (
        "a_field",
        "z_field",
    )


def test_ineligible_review_is_rejected() -> None:
    with pytest.raises(ApprovedSpecificationError, match="ineligible"):
        materialize_approved_specification(
            [field("gsm", 120, 140, status=ReviewStatus.ACCEPTED)],
            eligible=False,
        )


def test_pending_changed_field_fails_closed() -> None:
    with pytest.raises(ApprovedSpecificationError, match="no terminal"):
        materialize_approved_specification(
            [field("gsm", 120, 140, status=ReviewStatus.PENDING)],
            eligible=True,
        )


def test_hash_is_deterministic_and_lineage_sensitive() -> None:
    materialization = materialize_approved_specification(
        [
            field("gsm", 120, 140, status=ReviewStatus.ACCEPTED),
            field("flute", "B", "B"),
        ],
        eligible=True,
    )
    arguments = dict(
        project_id="project-1",
        review_id="review-1",
        source_review_revision_id="revision-4",
        source_review_revision_number=4,
        existing_dataset_id="dataset-existing",
        proposed_dataset_id="dataset-proposed",
        materialization=materialization,
    )
    first = approved_specification_content_hash(**arguments)
    second = approved_specification_content_hash(**arguments)
    changed = approved_specification_content_hash(
        **{**arguments, "source_review_revision_number": 5}
    )
    assert first == second
    assert len(first) == 64
    assert first != changed
