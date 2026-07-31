# SourceMate Governance Contract

## Purpose

SourceMate is a deterministic, read-only explanation facade over existing governed records. It explains recorded outcomes; it does not create, recalculate, approve, rank, award, negotiate, deploy or execute.

## Supported questions

Exactly nine intents are supported: `STATUS_REASON`, `INPUTS_AFFECTING_RESULT`, `APPLIED_ASSUMPTIONS`, `MISSING_EVIDENCE`, `OVERRIDING_BLOCKERS`, `REQUIRED_VALIDATION`, `PROVEN_CLAIMS`, `UNPROVEN_CLAIMS`, and `STATUS_IMPROVEMENT_REQUIREMENTS`.

## Mandatory request boundary

Every request requires `project_id`, `target_id`, a supported question and, where selected, the exact historical revision reference. Project mismatch fails closed. Missing records, unsupported questions, insufficient context and integrity failures produce controlled errors without invented assumptions.

## Determinism and lineage

Identical governed context plus an identical question produces identical canonical JSON. Canonical output excludes dynamic timestamps, sorts collections and fields, and preserves source classification, source record, rule reference, revision and source hash.

## Source classifications

`OBSERVED`, `DECLARED`, `DERIVED`, `ASSUMED`, `MISSING`, `VALIDATION_PENDING`, `APPROVED_SNAPSHOT`, and `AUTHORIZED_HANDOFF` are explanation classifications only. They do not rewrite source records.

## Precedence and claim boundaries

Existing technical and evidence blockers retain precedence over commercial benefit. SourceMate lists only existing unmet controls when describing possible status improvement. It does not provide autonomous engineering advice or assign a new status.

Approved-snapshot explanations preserve approval scope and limitations. Governed-consumption explanations preserve non-execution boundaries. Archived records may be explained read-only; no mutation or reactivation is implied.

## Prohibited capability

No unrestricted prompt box, LLM, RAG, embeddings, vector database, internet search, external API, multilingual generation, voice, PDF export, Excel explanation export, persisted generated narrative, revision comparison, portfolio-wide search, telemetry or explanation scoring is included.

## Human control

Human engineering validation and explicit human approval remain mandatory. Autonomous approval and autonomous supplier selection or award remain prohibited.

## Known governance exception

The pre-existing stale Build 1 post-merge wording in canonical governance records remains untouched under explicit user instruction. Build 2 does not correct or reinterpret that record.
