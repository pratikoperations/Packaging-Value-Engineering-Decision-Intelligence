# PVE 1.1 Validation Readiness Logic

## Purpose

PVE 1.1 measures intake and evidence completeness. It does not determine final engineering feasibility and cannot approve a packaging change.

## Weighted components

| Component | Weight |
|---|---:|
| Project metadata | 10% |
| Baseline specification | 20% |
| Proposed specification | 20% |
| Commercial data | 15% |
| Logistics and application data | 10% |
| Quality and test data | 20% |
| Document traceability | 5% |

Each component records completed items, total applicable items, completion ratio, and weighted contribution. The score is therefore reproducible and explainable.

## Blocking override

Blocking issues override the percentage and force `Insufficient Data`. Current blockers include missing baseline or proposal, missing annual volume or current cost, category mismatch, missing mandatory tests or documents, expired evidence, and supplier-declared data presented as tested.

## Stages

- Draft
- Ready for Commercial Screening
- Ready for Technical Screening
- Ready for Laboratory Testing
- Ready for Trial Validation
- Ready for Approval Review
- Insufficient Data

`Approved`, `Rejected`, and `Conditional` remain human decision outcomes and are not assigned by the readiness engine.

## Source traceability

The assessment retains counts of uploaded facts, manually entered facts, supplier-declared values, laboratory-tested values, predicted values, and assumptions. Source labels are preserved; they are not upgraded automatically.

## Persistence

Readiness assessments are stored as append-only snapshots. Database triggers prohibit update and deletion. A write is rejected for archived projects and when a referenced dataset belongs to another project.

## Approval limitation

A high score never authorizes implementation. Engineering validation and human approval remain mandatory, and autonomous approval remains prohibited.
