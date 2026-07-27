"""Deterministic extraction-confidence classification."""

from __future__ import annotations

from .extraction_contract import ConfidenceBand, ExtractionContractError


def classify_confidence(value: float) -> ConfidenceBand:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExtractionContractError("confidence must be numeric.")
    numeric = float(value)
    if numeric < 0 or numeric > 100:
        raise ExtractionContractError("confidence must be between 0 and 100.")
    if numeric >= 90:
        return ConfidenceBand.HIGH
    if numeric >= 70:
        return ConfidenceBand.REVIEW
    return ConfidenceBand.BLOCKED
