# PVE 2.0 — Controlled Word Intake Evaluation Report

## Status

Build Group F evaluation uses a synthetic, independently defined 10-pair corpus. No live model provider was connected. Therefore the report validates the evaluation framework, deterministic adapters, safety gates, migration compatibility and reference predictions; it does **not** claim measured accuracy for a production LLM.

## Corpus

- 10 existing-versus-proposed pairs
- 20 logical DOCX documents
- paragraph, table and mixed layouts
- missing fields and mixed units
- duplicate candidates and unit conflicts
- prompt-injection text
- unsupported embedded image content
- malformed provider output
- malformed and oversized DOCX cases
- migration and immutable-snapshot regression cases

The corpus manifest is stored at `evaluation/pve_2_0_word/corpus_manifest.json`.

## Evaluation gates

| Metric | Required | Reference result |
|---|---:|---:|
| High-priority-field precision | ≥95% | 100% |
| High-priority-field recall | ≥90% | 100% |
| Source grounding | 100% | 100% |
| Document-role accuracy | ≥98% | 100% |
| Missing-field accuracy | reported | 100% |
| Accepted invented values | 0 | 0 |
| Accepted unsourced values | 0 | 0 |
| Unconfirmed values mapped | 0 | 0 |
| Existing regression failures | 0 | 0 |

These results describe deterministic reference predictions and safety tests, not a live provider benchmark.

## Safety findings

The controlled suite verifies that invented, unsourced and unconfirmed values fail the release gate. Prompt-injection content is represented in the corpus and remains untrusted document evidence. Malformed and oversized DOCX packages are rejected. Unsupported image content is flagged rather than interpreted.

## Migration and persistence findings

The Word-intake subsystem migration remains additive. The legacy PVE schema version remains unchanged, legacy tables remain available, and the new immutable snapshot table is added separately. Existing canonical validation remains unchanged.

## Claim boundary

The repository may claim:

- governed DOCX parsing;
- source-grounded provider-neutral extraction contracts;
- deterministic review and comparison;
- confirmed-only canonical draft mapping;
- immutable snapshot persistence;
- a reproducible synthetic evaluation framework.

The repository may not claim:

- independently measured production-model accuracy;
- confidential-document readiness;
- engineering approval;
- autonomous recommendation;
- supplier qualification;
- production deployment;
- realized cost savings.
