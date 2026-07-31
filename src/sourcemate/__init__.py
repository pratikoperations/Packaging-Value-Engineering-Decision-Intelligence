"""Deterministic, read-only SourceMate explanation boundary."""

from .domain import (
    ExplanationContext,
    ExplanationError,
    ExplanationQuestion,
    ExplanationRequest,
    ExplanationResponse,
    SourceClassification,
    SourceReference,
)
from .service import ExplanationContextAssembler, SourceMateExplanationService

__all__ = [
    "ExplanationContext",
    "ExplanationContextAssembler",
    "ExplanationError",
    "ExplanationQuestion",
    "ExplanationRequest",
    "ExplanationResponse",
    "SourceClassification",
    "SourceMateExplanationService",
    "SourceReference",
]
