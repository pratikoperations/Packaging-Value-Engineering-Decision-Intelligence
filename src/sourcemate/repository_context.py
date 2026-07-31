from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable

from src.application.runtime import (
    build_approved_specification_consumption_read_model,
    build_approved_specification_read_model,
    build_project_repository,
    build_specification_review_read_model,
)
from src.persistence.database import Database
from src.persistence.decision_repository import DecisionRepository
from src.sourcemate.domain import (
    ExplanationContext,
    ExplanationError,
    SourceClassification,
    SourceReference,
)


class SourceMateRepositoryContextProvider:
    """Read-only composition over existing governed repositories and read models."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.projects = build_project_repository(self.database_path)
        self.reviews = build_specification_review_read_model(self.database_path)
        self.snapshots = build_approved_specification_read_model(self.database_path)
        self.consumption = build_approved_specification_consumption_read_model(
            self.database_path
        )
        self.decisions = DecisionRepository(Database(self.database_path))

    def list_contexts(self) -> tuple[ExplanationContext, ...]:
        contexts: list[ExplanationContext] = []
        for project in self.projects.list(archived=None):
            project_id = str(project["project_id"])
            archived = project.get("archived_at") is not None
            contexts.extend(self._decision_contexts(project_id, archived))
            contexts.extend(self._review_contexts(project_id, archived))
            contexts.extend(self._snapshot_contexts(project_id, archived))
            contexts.extend(self._consumption_contexts(project_id, archived))
        return tuple(sorted(contexts, key=lambda item: (item.project_id, item.target_type, item.target_id, item.revision_reference)))

    def _decision_contexts(self, project_id: str, archived: bool) -> list[ExplanationContext]:
        return [self._decision_context(row, archived) for row in self.decisions.list_for_project(project_id)]

    def _decision_context(self, row: dict[str, Any], archived: bool) -> ExplanationContext:
        project_id = str(row["project_id"])
        target_id = str(row["decision_snapshot_id"])
        recommendation = _json_mapping(row.get("recommendation_json"))
        gates = _json_mapping(row.get("gate_results_json"))
        blockers = _strings(gates.get("blockers") or gates.get("blocking_controls"))
        evidence_gaps = _strings(gates.get("evidence_gaps") or gates.get("missing_evidence"))
        validation = _strings(gates.get("required_validation") or gates.get("validation_actions"))
        assumptions = _strings(recommendation.get("assumptions"))
        reason = str(
            recommendation.get("reason")
            or recommendation.get("rationale")
            or recommendation.get("summary")
            or f"Recorded governed decision status: {row.get('status', '')}."
        )
        sources = (
            SourceReference("status", row.get("status"), SourceClassification.DERIVED, target_id, "stored_decision_snapshot"),
            SourceReference("recommendation", recommendation, SourceClassification.DERIVED, target_id, "stored_recommendation_payload"),
            SourceReference("gate_results", gates, SourceClassification.OBSERVED, target_id, "stored_gate_results"),
            SourceReference("scenario_id", row.get("scenario_id"), SourceClassification.OBSERVED, target_id),
            SourceReference("dataset_id", row.get("dataset_id"), SourceClassification.OBSERVED, target_id),
        )
        return ExplanationContext(
            project_id=project_id,
            target_id=target_id,
            target_type="decision_snapshot",
            revision_reference=str(row.get("created_at") or target_id),
            status=str(row.get("status") or "recorded"),
            status_reason=reason,
            sources=sources,
            assumptions=assumptions,
            evidence_gaps=evidence_gaps,
            blockers=blockers,
            required_validation=validation,
            required_human_action=("Human review and approval remain mandatory.",),
            proven_claims=("This is an immutable stored decision snapshot.",),
            claim_limitations=("This record is recommendation-for-review evidence, not autonomous approval or supplier award.",),
            status_improvement_requirements=tuple(sorted(set(blockers + evidence_gaps + validation))),
            source_hash=str(row.get("content_hash") or ""),
            archived=archived,
        )

    def _review_contexts(self, project_id: str, archived: bool) -> list[ExplanationContext]:
        contexts: list[ExplanationContext] = []
        for summary in self.reviews.list_reviews_for_project(project_id):
            for revision in self.reviews.list_history(summary.review_id, project_id=project_id):
                data = _record(revision)
                state = _record(data.get("state"))
                eligibility = _record(state.get("eligibility"))
                blockers = _strings(eligibility.get("blockers"))
                pending = [
                    str(_record(item).get("field_key") or _record(_record(item).get("candidate")).get("field_key") or "field")
                    for item in state.get("comparisons", ())
                    if str(_record(_record(item).get("candidate")).get("status", "")).lower().endswith("pending")
                ]
                revision_id = str(data.get("review_revision_id") or f"{summary.review_id}:{data.get('revision_number')}")
                source_hash = str(data.get("content_hash") or data.get("state_hash") or revision_id)
                status = "eligible" if eligibility.get("eligible") else "blocked"
                contexts.append(
                    ExplanationContext(
                        project_id=project_id,
                        target_id=summary.review_id,
                        target_type="specification_review",
                        revision_reference=revision_id,
                        status=status,
                        status_reason=("The persisted review satisfies its recorded eligibility controls." if status == "eligible" else "The persisted review remains blocked by recorded eligibility controls."),
                        sources=(
                            SourceReference("revision_number", data.get("revision_number"), SourceClassification.OBSERVED, revision_id, "immutable_review_revision"),
                            SourceReference("eligibility", eligibility, SourceClassification.DERIVED, revision_id, "specification_review_eligibility"),
                            SourceReference("existing_dataset_id", state.get("existing_dataset_id"), SourceClassification.OBSERVED, revision_id),
                            SourceReference("proposed_dataset_id", state.get("proposed_dataset_id"), SourceClassification.OBSERVED, revision_id),
                        ),
                        evidence_gaps=tuple(sorted(pending)),
                        blockers=blockers,
                        required_validation=("Complete all pending governed field reviews and eligibility controls.",) if status != "eligible" else (),
                        required_human_action=("A named human reviewer must authorize any review action or approved snapshot.",),
                        proven_claims=("This explanation refers to an immutable persisted review revision.",),
                        claim_limitations=("Review eligibility does not constitute autonomous engineering approval.",),
                        status_improvement_requirements=tuple(sorted(set(blockers + tuple(pending)))),
                        source_hash=source_hash,
                        archived=archived,
                    )
                )
        return contexts

    def _snapshot_contexts(self, project_id: str, archived: bool) -> list[ExplanationContext]:
        contexts: list[ExplanationContext] = []
        for snapshot in self.snapshots.list_snapshots_for_project(project_id):
            values = tuple(snapshot.approved_values)
            sources = tuple(
                SourceReference(item.field_key, item.value, SourceClassification.APPROVED_SNAPSHOT, snapshot.snapshot_id, item.source)
                for item in values
            )
            contexts.append(
                ExplanationContext(
                    project_id=project_id,
                    target_id=snapshot.snapshot_id,
                    target_type="approved_specification_snapshot",
                    revision_reference=snapshot.source_review_revision_id,
                    status="approved_snapshot",
                    status_reason="A named human actor created this immutable snapshot from an eligible governed review revision.",
                    sources=sources,
                    required_human_action=("Downstream engineering and business use still requires purpose-specific human authorization.",),
                    proven_claims=("The listed values are contained in the immutable approved specification snapshot.",),
                    claim_limitations=("The snapshot does not autonomously approve production, supplier award, regulatory compliance, or deployment.",),
                    source_hash=snapshot.content_hash,
                    archived=archived,
                )
            )
        return contexts

    def _consumption_contexts(self, project_id: str, archived: bool) -> list[ExplanationContext]:
        contexts: list[ExplanationContext] = []
        for envelope in self.consumption.list_envelopes_for_project(project_id):
            authorizations = self.consumption.list_authorizations_for_snapshot(envelope.snapshot_id, project_id=project_id)
            purposes = tuple(sorted(item.purpose.value for item in authorizations if item.envelope_id == envelope.envelope_id))
            sources = tuple(
                SourceReference(item.field_key, item.value, SourceClassification.AUTHORIZED_HANDOFF, envelope.envelope_id, item.source)
                for item in envelope.approved_values
            )
            contexts.append(
                ExplanationContext(
                    project_id=project_id,
                    target_id=envelope.envelope_id,
                    target_type="governed_consumption_envelope",
                    revision_reference=envelope.source_review_revision_id,
                    status="authorized_handoff" if purposes else "authorization_required",
                    status_reason=(f"Purpose-specific authorizations exist for: {', '.join(purposes)}." if purposes else "The governed envelope exists, but no purpose-specific authorization is recorded."),
                    sources=sources,
                    blockers=() if purposes else ("Purpose-specific consumption authorization is missing.",),
                    required_validation=("Verify the downstream consumer uses the exact immutable envelope and authorized purpose.",),
                    required_human_action=("A named human actor must authorize each permitted consumption purpose.",),
                    proven_claims=("The envelope reproduces values from the linked approved specification snapshot.",),
                    claim_limitations=("Authorization permits input preparation only; it does not execute analysis, approve a recommendation, rank a supplier, or award business.",),
                    status_improvement_requirements=() if purposes else ("Create a governed purpose-specific authorization through the existing authorized workflow.",),
                    source_hash=envelope.envelope_content_hash,
                    archived=archived,
                )
            )
        return contexts


def _json_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, dict):
        return tuple(sorted(str(key) for key, enabled in value.items() if enabled))
    if isinstance(value, Iterable):
        return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))
    return (str(value),)


def _record(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if is_dataclass(value):
        return asdict(value)
    return dict(vars(value)) if hasattr(value, "__dict__") else {}
