# Calculation Evidence Governance Contract

## Purpose

Calculation Evidence is a deterministic, read-only presentation and reconciliation layer over existing persisted governed scenario results. It explains how a stored numeric result is constructed from recorded assumptions and engine-produced outputs. It does not run, replace, modify, or extend any analytical engine.

## Supported records and results

The current contract supports persisted project-scoped scenario records and exactly four stored result families:

- `annual_cost`;
- `annual_savings_vs_baseline`;
- `annual_material_kg`;
- `material_change_percent_vs_baseline`.

Unsupported result families fail closed.

## Mandatory lineage

Every explanation requires:

- exact project and scenario identity;
- selected alternative;
- persisted assumptions payload;
- persisted result payload;
- immutable scenario content hash;
- a supported formula and rule reference;
- compatible units;
- deterministic precision and rounding rules.

Missing or invalid lineage is disclosed through a controlled error. No value, formula, unit, assumption, or evidence reference is invented.

## Reconciliation

The workspace reconstructs presentation arithmetic only and compares it with the stored result using decimal round-half-even precision. A mismatch fails closed as `RECONCILIATION_FAILURE`. Reconciliation does not create a new business result and does not persist any generated evidence.

## Source classification

The workspace reuses Build 2 SourceMate source-classification vocabulary. Scenario inputs are explicitly classified as assumptions. Engine-produced stored values used by the presentation chain are classified as derived. These labels do not rewrite source records.

## Separation from SourceMate

SourceMate explains why a governed status or outcome exists. Calculation Evidence shows how a stored numeric scenario result was constructed. Neither service calls the other as an analytical engine, and neither creates or changes a recommendation, status, scenario, approval, or award.

## Project scope and archived records

All reads require explicit project scope. Cross-project access fails closed. Archived-project records may be displayed read-only; no reactivation or mutation is implied.

## Prohibited capability

The workspace includes no editable assumption, formula, threshold, or numeric input; no arbitrary expression evaluator; no `eval`; no LLM, RAG, embeddings, vector database, internet access, external API, PDF export, Excel export, supplier ranking, allocation, award, negotiation, autonomous approval, deployment, release, or tagging.

## Human control and claim limitations

Engineering validation and explicit human approval remain mandatory. Reconciled calculation evidence proves only that the displayed arithmetic agrees with the selected stored result under the governed precision rule. It does not prove supplier evidence, laboratory validation, production fitness, regulatory compliance, realized savings, commercial approval, or production readiness.

## Known governance exception

The pre-existing stale Build 1 post-merge wording in canonical governance records remains untouched under explicit authorization. Build 3 does not correct or reinterpret those records.
