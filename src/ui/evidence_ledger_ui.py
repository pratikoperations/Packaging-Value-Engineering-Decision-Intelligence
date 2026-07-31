from __future__ import annotations

from src.evidence_ledger import EvidenceLedgerError, EvidenceLedgerService


def render_evidence_ledger_page(st, *, projects: tuple[dict, ...], service: EvidenceLedgerService) -> None:
    st.title("Decision Evidence Ledger")
    st.caption("Read-only chronology and lineage over persisted governed project records")
    st.info("This workspace does not create audit events, execute analyses, approve designs, rank suppliers or award business.")
    if not projects:
        st.warning("No governed projects are available.")
        return

    labels = {
        str(item["project_id"]): str(item.get("name") or item.get("project_name") or item["project_id"])
        for item in projects
    }
    project_id = st.selectbox("Project", tuple(labels), format_func=lambda value: labels[value])
    try:
        ledger = service.build(project_id)
    except EvidenceLedgerError as exc:
        st.error(f"{exc.code}: {exc}")
        return

    if ledger.archived:
        st.warning("This project is archived. All ledger information is read-only.")

    left, middle, right = st.columns(3)
    left.metric("Governed records", len(ledger.events))
    middle.metric("Unresolved blockers", len(ledger.unresolved_blockers))
    right.metric("Pending validation", len(ledger.pending_validation))
    st.caption(f"Integrity status: {ledger.integrity_status}")

    event_types = tuple(sorted({event.event_type.value for event in ledger.events}))
    statuses = tuple(sorted({event.status for event in ledger.events}))
    classifications = tuple(sorted({event.source_classification.value for event in ledger.events}))
    col1, col2, col3 = st.columns(3)
    selected_types = tuple(col1.multiselect("Record family", event_types))
    selected_statuses = tuple(col2.multiselect("Status", statuses))
    selected_classes = tuple(col3.multiselect("Source classification", classifications))
    events = service.filter_events(
        ledger,
        record_types=selected_types,
        statuses=selected_statuses,
        classifications=selected_classes,
    )

    if ledger.unresolved_blockers:
        with st.expander("Unresolved blockers", expanded=True):
            for item in ledger.unresolved_blockers:
                st.write(f"- {item}")
    if ledger.pending_validation:
        with st.expander("Pending validation"):
            for item in ledger.pending_validation:
                st.write(f"- {item}")

    st.subheader("Chronological evidence")
    for event in events:
        when = event.occurred_at or "deterministic fallback order"
        with st.expander(f"{when} — {event.title} — {event.status}"):
            st.write(event.summary)
            st.write(f"**Record:** `{event.event_type.value}:{event.record_id}`")
            if event.revision_reference:
                st.write(f"**Revision:** `{event.revision_reference}`")
            st.write(f"**Classification:** `{event.source_classification.value}`")
            if event.actor_reference:
                st.write(f"**Actor:** `{event.actor_reference}`")
            if event.source_hash:
                st.write(f"**Source hash:** `{event.source_hash}`")
            if event.integrity_warning:
                st.warning(event.integrity_warning)
            if event.parent_references:
                st.write("**Parents**")
                for ref in event.parent_references:
                    st.write(f"- `{ref.record_type}:{ref.record_id}`")
            if event.related_references:
                st.write("**Related records**")
                for ref in event.related_references:
                    st.write(f"- `{ref.record_type}:{ref.record_id}`")
            if event.claim_limitations:
                st.write("**Claim limitations**")
                for item in event.claim_limitations:
                    st.write(f"- {item}")

    st.download_button(
        "Download canonical ledger JSON",
        data=ledger.canonical_json(),
        file_name=f"{project_id}-decision-evidence-ledger.json",
        mime="application/json",
        width="stretch",
    )
