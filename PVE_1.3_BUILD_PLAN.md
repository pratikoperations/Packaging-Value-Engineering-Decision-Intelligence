# PVE 1.3 Controlled Build Plan

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current implementation status
- Status: Build 1 implemented on the controlled branch; validation and merge remain pending.
- Implementation started: yes, limited to Build 1.
- Build 1 status: implementation complete, pending CI and governance closure.
- Builds 2A–8: not started and not authorized.
- Release completion: 8.7%.
- Completed planned effort: 6 of 69 hours.
- Pending planned effort: 63 hours, 91.3%.
- Controlled contingency used: 0 of 2 hours.
- Controlled contingency remaining: 2 hours.
- Absolute release cap: 71 hours.

## Budget control
The 69 planned hours remain fixed. The two-hour contingency may be used only for unexpected regression, CI-only failure, migration compatibility repair, cross-module integration defects or release-evidence reconciliation. It cannot fund new functionality, additional categories, deployment or scope expansion.

## Controlled build sequence

| Build | Scope | Hours | Cumulative hours | Planned completion | Status |
|---|---|---:|---:|---:|---|
| 1 | Architecture, governance and release boundary | 6 | 6 | 8.7% | Implemented; validation pending |
| 2A | Drawing, Artwork, Dieline and CAD Evidence Control | 10 | 16 | 23.2% | Not started |
| 2B | Lightweight PDF, SVG and image preview support | 5 | 21 | 30.4% | Not started |
| 3 | Trial planning and validation requirements | 9 | 30 | 43.5% | Not started |
| 4 | Trial execution, results and deviations | 9 | 39 | 56.5% | Not started |
| 5 | Packaging defect and complaint taxonomy | 8 | 47 | 68.1% | Not started |
| 6 | Specification and implementation change control | 8 | 55 | 79.7% | Not started |
| 7 | Supplier qualification evidence register | 7 | 62 | 89.9% | Not started |
| 8 | Demonstration cases, regression and release QA | 7 | 69 | 100% | Not started |

## Build 1 — Architecture, governance and release boundary — 6 hours

### Delivered
- scope and exclusions locked in `PVE_1.3_BUILD_1_RELEASE_BOUNDARY.md`;
- dependencies on frozen PVE 1.2 defined;
- module and record ownership, immutability, project isolation and human authority defined in `PVE_1.3_BUILD_1_RECORD_AND_AUTHORITY_MODEL.md`;
- universal and build-specific acceptance gates defined in `PVE_1.3_BUILD_1_ACCEPTANCE_GATES.md`;
- deterministic, evidence-governed decision-support boundary preserved;
- canonical architecture and governance records reconciled.

### Prohibited in Build 1
Build 1 introduces no schema, migration, data model, persistence code, file processor, preview renderer, UI feature, product functionality or new test. Builds 2A–8 remain separately controlled.

## Build 2A — Drawing, Artwork, Dieline and CAD Evidence Control — 10 hours
Planned outcomes:
- governed drawing and CAD document register;
- drawing number, title, revision, issue date and effective date;
- baseline-versus-proposed classification;
- project, SKU, supplier, manufacturing-site and specification-version linkage;
- references for PDF, DXF, DWG, SVG and artwork files;
- dieline, artwork and tooling relationships;
- source classification, approval and validation status;
- superseded and replacement relationships;
- trial applicability, checksum and immutable revision history;
- human engineering validation and approval requirements.

DXF and DWG remain governed references only; geometry is not automatically interpreted.

## Build 2B — Lightweight PDF, SVG and image preview support — 5 hours
Planned outcomes:
- PDF, SVG, PNG and JPEG preview;
- drawing metadata panel;
- baseline/proposed document viewing;
- controlled file or source-reference access;
- unsupported-file fallback;
- explicit preview limitations;
- no dimensional, geometric or engineering interpretation.

## Build 3 — Trial planning and validation requirements — 9 hours
Planned outcomes include governed trial objectives, protocols, owners, sites, evidence, acceptance criteria, revision linkage, prerequisites, blockers and explicit human authorization.

## Build 4 — Trial execution, results and deviations — 9 hours
Planned outcomes include append-only execution records, observed results, measurements, attachments, deviations, nonconformances, retest requirements and human-only disposition.

## Build 5 — Packaging defect and complaint taxonomy — 8 hours
Planned outcomes include governed defect families, severity, evidence, affected context and descriptive analysis without unsupported causal inference.

## Build 6 — Specification and implementation change control — 8 hours
Planned outcomes include append-only change requests, affected references, validation requirements, inventory transition, status history and explicit human approval.

## Build 7 — Supplier qualification evidence register — 7 hours
Planned outcomes include supplier-site capability evidence, validity, expiry, requalification and evidence matching without ranking, allocation or award decisions.

## Build 8 — Demonstration cases, regression and release QA — 7 hours
Planned outcomes include governed synthetic cases, end-to-end regression, immutability and isolation validation, release checklist, QA report, notes and governance reconciliation.

## Explicit exclusions
PVE 1.3 will not include:
- automatic DXF geometry extraction;
- automatic dimension extraction;
- automatic cut, crease or slot recognition;
- parametric dieline generation;
- automated blank optimization;
- full CAD editing;
- 3D folding or tooling design;
- manufacturing-ready drawing generation or approval;
- autonomous engineering approval;
- supplier ranking, allocation or sourcing-award decisions;
- deployment, pilot, activation or production-readiness claims without separate authorization.

## Authorization boundary
Build 1 alone is authorized. Builds 2A–8 must not begin without separate explicit authorization. Build 1 must pass CI, review and merge controls before it is treated as governance-closed on `main`.
