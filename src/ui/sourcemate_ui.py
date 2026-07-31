from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from src.sourcemate.domain import ExplanationContext, ExplanationQuestion, ExplanationRequest
from src.sourcemate.service import SourceMateExplanationService


def render_sourcemate_page(
    st,
    *,
    contexts: Iterable[ExplanationContext],
    service: SourceMateExplanationService | None = None,
) -> None:
    """Render one controlled selector-based SourceMate page with no write path."""
    service = service or SourceMateExplanationService()
    available = tuple(contexts)
    st.title("SourceMate — Understand This Decision")
    st.caption(
        "Deterministic, read-only explanation of existing governed records. "
        "SourceMate does not calculate, approve, rank, award, negotiate, deploy, or execute."
    )
    if not available:
        st.info("No governed records are available for explanation.")
        _limitations(st)
        return

    project_ids = sorted({item.project_id for item in available})
    project_id = st.selectbox("Project", project_ids)
    project_contexts = tuple(item for item in available if item.project_id == project_id)
    target_ids = [item.target_id for item in project_contexts]
    target_id = st.selectbox("Decision, alternative, snapshot or envelope", target_ids)
    context = next(item for item in project_contexts if item.target_id == target_id)
    question = st.selectbox(
        "Governed question",
        list(ExplanationQuestion),
        format_func=lambda item: item.value.replace("_", " ").title(),
    )
    if st.button("Generate deterministic explanation", type="primary"):
        response = service.explain(
            ExplanationRequest(
                project_id=project_id,
                target_id=target_id,
                question=question,
                revision_reference=context.revision_reference,
            ),
            context,
        )
        st.subheader("Answer")
        st.write(response.answer_summary)
        if response.archived:
            st.warning("Archived project record — read-only explanation; no reactivation is implied.")
        with st.expander("Evidence and assumptions", expanded=True):
            st.write([item.canonical() for item in response.source_fields])
            st.write({"assumptions": list(response.assumptions), "evidence_gaps": list(response.evidence_gaps)})
        with st.expander("Blocking controls and required human action"):
            st.write({
                "blocking_controls": list(response.blocking_controls),
                "required_validation": list(response.required_validation),
                "required_human_action": list(response.required_human_action),
            })
        with st.expander("Sources, rules and claim limitations"):
            st.write({
                "proven_claims": list(response.proven_claims),
                "claim_limitations": list(response.claim_limitations),
                "source_hash": response.source_hash,
                "revision_reference": response.revision_reference,
            })
        canonical_json = service.canonical_json(response)
        st.download_button(
            "Export canonical JSON",
            data=canonical_json,
            file_name=f"sourcemate-{target_id}.json",
            mime="application/json",
        )
    _limitations(st)


def _limitations(st) -> None:
    with st.expander("Capabilities and limitations"):
        st.markdown(
            "- Fixed catalogue of nine governed questions only.\n"
            "- No unrestricted chat, LLM, RAG, internet search or external API.\n"
            "- No new recommendation, status calculation, approval, supplier ranking or award.\n"
            "- Human engineering validation and human approval remain mandatory."
        )
