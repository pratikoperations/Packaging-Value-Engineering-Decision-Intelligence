# Decision Evidence Ledger Governance Contract

## Purpose

The Decision Evidence Ledger is a deterministic, read-only, project-scoped projection over existing persisted governed records. It shows chronology, record identity, revision lineage, source classification, hashes, blockers, pending validation and claim limitations. It does not create a new audit event or modify any source record.

## Supported record families

The ledger may display existing projects, datasets, specification reviews and revisions, approved specification snapshots, governed consumption envelopes and authorizations, persisted scenarios, and decision snapshots.

## Source-record boundary

Every event maps to a concrete persisted source record. Project scope is mandatory. Cross-project access, missing record identity and duplicate event identity fail closed. Source timestamps are preserved. Records without timestamps use deterministic fallback ordering and are explicitly distinguishable from timestamped events.

## Integrity

Where a source record provides a content hash, the hash is preserved. Missing optional hashes are disclosed as integrity warnings and are never invented. Parent and related-record references are validated against the selected project's projected records. Broken lineage is disclosed and cannot be represented as verified integrity.

## Separation of responsibilities

SourceMate explains why a governed status or outcome exists. Calculation Evidence shows how a supported stored numeric result was constructed. The Decision Evidence Ledger shows lifecycle chronology and governed record relationships. It does not duplicate narrative explanation or calculation reconstruction.

## Claim limitations

Review eligibility is not engineering approval. Approved snapshots do not prove production, regulatory or supplier-award approval. Consumption authorization permits governed input preparation only and does not execute an analytical engine. Scenarios do not prove realized savings. Decision snapshots are recommendation-for-review evidence and not autonomous approval or award.

## Project and archived-state controls

All reads require explicit project scope. Archived projects remain readable but fully read-only. The ledger exposes no create, update, delete, approve, execute, rank, allocate, award or reactivation capability.

## Determinism and export

Identical persisted project state produces identical event ordering and canonical JSON. Canonical output contains no generated timestamp and uses stable field and collection ordering.

## Prohibited capability

No database migration, persisted ledger, generated audit event, event-sourcing framework, graph database, analytical-engine execution, calculation reconstruction, new recommendation or status, cross-project aggregation, unrestricted prompt, LLM, RAG, embeddings, external API, internet access, PDF export, Excel export, supplier ranking, allocation, award, autonomous approval, deployment, release or tag is included.

## Human control

Human engineering validation, commercial review and explicit approval remain mandatory. The ledger improves traceability only; it does not increase the authority of any underlying record.

## Known governance exception

The pre-existing stale Build 1 wording in canonical governance records remains untouched under explicit authorization. Build 4 does not correct or reinterpret those records.
