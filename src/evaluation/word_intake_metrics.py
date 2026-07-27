"""Deterministic evaluation metrics for PVE 2.0 Word intake."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class GroundTruthField:
    pair_id: str
    document_role: str
    field_name: str
    value: object
    source_block_id: str
    present: bool = True
    high_priority: bool = True


@dataclass(frozen=True)
class PredictedField:
    pair_id: str
    document_role: str
    field_name: str
    value: object
    source_block_id: str | None
    accepted: bool = True


@dataclass(frozen=True)
class EvaluationResult:
    precision: float
    recall: float
    source_grounding_accuracy: float
    document_role_accuracy: float
    missing_field_accuracy: float
    accepted_invented_values: int
    accepted_unsourced_values: int
    unconfirmed_values_mapped: int

    def meets_thresholds(self) -> bool:
        return (
            self.precision >= 0.95
            and self.recall >= 0.90
            and self.source_grounding_accuracy == 1.0
            and self.document_role_accuracy >= 0.98
            and self.accepted_invented_values == 0
            and self.accepted_unsourced_values == 0
            and self.unconfirmed_values_mapped == 0
        )


def evaluate(
    truth: Iterable[GroundTruthField],
    predictions: Iterable[PredictedField],
    *,
    unconfirmed_values_mapped: int = 0,
) -> EvaluationResult:
    truth_items = tuple(item for item in truth if item.high_priority)
    predicted_items = tuple(item for item in predictions if item.accepted)
    truth_present = {
        (item.pair_id, item.document_role, item.field_name): item
        for item in truth_items
        if item.present
    }
    truth_missing = {
        (item.pair_id, item.document_role, item.field_name)
        for item in truth_items
        if not item.present
    }
    predicted = {
        (item.pair_id, item.document_role, item.field_name): item
        for item in predicted_items
    }
    true_positive = 0
    grounded = 0
    role_correct = 0
    invented = 0
    unsourced = 0
    for key, item in predicted.items():
        expected = truth_present.get(key)
        if expected is None:
            invented += 1
            continue
        if item.value == expected.value:
            true_positive += 1
        if item.source_block_id == expected.source_block_id:
            grounded += 1
        if item.document_role == expected.document_role:
            role_correct += 1
        if item.source_block_id is None:
            unsourced += 1
    precision = true_positive / len(predicted) if predicted else 1.0
    recall = true_positive / len(truth_present) if truth_present else 1.0
    grounding = grounded / len(predicted) if predicted else 1.0
    role_accuracy = role_correct / len(predicted) if predicted else 1.0
    missing_correct = sum(1 for key in truth_missing if key not in predicted)
    missing_accuracy = missing_correct / len(truth_missing) if truth_missing else 1.0
    return EvaluationResult(
        precision=precision,
        recall=recall,
        source_grounding_accuracy=grounding,
        document_role_accuracy=role_accuracy,
        missing_field_accuracy=missing_accuracy,
        accepted_invented_values=invented,
        accepted_unsourced_values=unsourced,
        unconfirmed_values_mapped=unconfirmed_values_mapped,
    )
