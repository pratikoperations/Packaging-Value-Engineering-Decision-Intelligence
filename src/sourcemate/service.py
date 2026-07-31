from __future__ import annotations

import json
from dataclasses import replace
from typing import Callable, Mapping

from .domain import (
    ERROR_MESSAGES,
    ExplanationContext,
    ExplanationError,
    ExplanationQuestion,
    ExplanationRequest,
    ExplanationResponse,
    SourceReference,
    ordered,
    require_text,
)

ContextLoader = Callable[[str, str, str], ExplanationContext | None]


class ExplanationContextAssembler:
    """Fail-closed project-scoped adapter over existing governed read models."""

    def __init__(self, loaders: Mapping[str, ContextLoader]) -> None:
        self._loaders = dict(loaders)

    def assemble(self, request: ExplanationRequest, target_type: str) -> ExplanationContext:
        project_id = require_text(request.project_id, "project_id")
        target_id = require_text(request.target_id, "target_id")
        target_type = require_text(target_type, "target_type")
        loader = self._loaders.get(target_type)
        if loader is None:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        context = loader(project_id, target_id, request.revision_reference)
        if context is None:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        if context.project_id != project_id:
            raise ExplanationError(
                "PROJECT_SCOPE_VIOLATION", ERROR_MESSAGES["PROJECT_SCOPE_VIOLATION"]
            )
        if context.target_id != target_id:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        if request.revision_reference and context.revision_reference != request.revision_reference:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        if not context.source_hash:
            raise ExplanationError("INTEGRITY_FAILURE", ERROR_MESSAGES["INTEGRITY_FAILURE"])
        return context


class SourceMateExplanationService:
    SCHEMA_VERSION = "sourcemate-explanation-v1"

    def explain(
        self, request: ExplanationRequest, context: ExplanationContext
    ) -> ExplanationResponse:
        if not isinstance(request.question, ExplanationQuestion):
            raise ExplanationError(
                "UNSUPPORTED_QUESTION", ERROR_MESSAGES["UNSUPPORTED_QUESTION"]
            )
        self._validate_scope(request, context)
        answer = self._answer(request.question, context)
        if not answer:
            raise ExplanationError(
                "INSUFFICIENT_CONTEXT", ERROR_MESSAGES["INSUFFICIENT_CONTEXT"]
            )
        sources = tuple(
            sorted(context.sources, key=lambda item: (item.field, item.source_record, item.classification.value))
        )
        return ExplanationResponse(
            schema_version=self.SCHEMA_VERSION,
            question=request.question,
            answer_summary=answer,
            project_reference=context.project_id,
            target_reference=context.target_id,
            target_type=context.target_type,
            revision_reference=context.revision_reference,
            status=context.status,
            source_fields=sources,
            assumptions=ordered(context.assumptions),
            evidence_gaps=ordered(context.evidence_gaps),
            blocking_controls=ordered(context.blockers),
            required_validation=ordered(context.required_validation),
            required_human_action=ordered(context.required_human_action),
            proven_claims=ordered(context.proven_claims),
            claim_limitations=ordered(context.claim_limitations),
            source_hash=context.source_hash,
            archived=context.archived,
        )

    def canonical_json(self, response: ExplanationResponse) -> str:
        return json.dumps(
            response.canonical(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )

    @staticmethod
    def _validate_scope(request: ExplanationRequest, context: ExplanationContext) -> None:
        if request.project_id != context.project_id:
            raise ExplanationError(
                "PROJECT_SCOPE_VIOLATION", ERROR_MESSAGES["PROJECT_SCOPE_VIOLATION"]
            )
        if request.target_id != context.target_id:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        if request.revision_reference and request.revision_reference != context.revision_reference:
            raise ExplanationError("RECORD_NOT_FOUND", ERROR_MESSAGES["RECORD_NOT_FOUND"])
        if not context.source_hash:
            raise ExplanationError("INTEGRITY_FAILURE", ERROR_MESSAGES["INTEGRITY_FAILURE"])

    @staticmethod
    def _answer(question: ExplanationQuestion, context: ExplanationContext) -> str:
        answers = {
            ExplanationQuestion.STATUS_REASON: context.status_reason,
            ExplanationQuestion.INPUTS_AFFECTING_RESULT: SourceMateExplanationService._join_sources(context.sources),
            ExplanationQuestion.APPLIED_ASSUMPTIONS: SourceMateExplanationService._join(context.assumptions),
            ExplanationQuestion.MISSING_EVIDENCE: SourceMateExplanationService._join(context.evidence_gaps),
            ExplanationQuestion.OVERRIDING_BLOCKERS: SourceMateExplanationService._join(context.blockers),
            ExplanationQuestion.REQUIRED_VALIDATION: SourceMateExplanationService._join(context.required_validation),
            ExplanationQuestion.PROVEN_CLAIMS: SourceMateExplanationService._join(context.proven_claims),
            ExplanationQuestion.UNPROVEN_CLAIMS: SourceMateExplanationService._join(context.claim_limitations),
            ExplanationQuestion.STATUS_IMPROVEMENT_REQUIREMENTS: SourceMateExplanationService._join(context.status_improvement_requirements),
        }
        return answers[question]

    @staticmethod
    def _join(values: tuple[str, ...]) -> str:
        return "; ".join(ordered(values))

    @staticmethod
    def _join_sources(values: tuple[SourceReference, ...]) -> str:
        return "; ".join(
            f"{item.field} [{item.classification.value}]"
            for item in sorted(values, key=lambda item: (item.field, item.classification.value))
        )
