# PVE 1.3 Controlled Build Plan

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current implementation status
- Status: Builds 1, 2A, 2B, 3, 4 and 5 implemented; Build 5 validation and governance closure remain pending.
- Implementation started: yes, limited to Builds 1, 2A, 2B, 3, 4 and 5.
- Build 1 status: merged, post-merge validated and governance-closed.
- Build 2A status: merged, post-merge validated and governance-closed.
- Build 2B status: merged, post-merge validated and governance-closed.
- Build 3 status: merged, post-merge validated and governance-closed.
- Build 4 status: merged, post-merge validated and governance-closed.
- Build 5 status: implementation complete on controlled branch; CI and governance closure pending.
- Builds 6–8: not started and not authorized.
- Release completion on branch: 68.1%.
- Completed planned effort on branch: 47 of 69 hours.
- Pending planned effort: 22 hours, 31.9%.
- Controlled contingency used: 0 of 2 hours.
- Controlled contingency remaining: 2 hours.
- Absolute release cap: 71 hours.

## Budget control
The 69 planned hours remain fixed. The two-hour contingency may be used only for unexpected regression, CI-only failure, migration compatibility repair, cross-module integration defects or release-evidence reconciliation. It cannot fund new functionality, additional categories, deployment or scope expansion.

## Controlled build sequence

| Build | Scope | Hours | Cumulative hours | Planned completion | Status |
|---|---|---:|---:|---:|---|
| 1 | Architecture, governance and release boundary | 6 | 6 | 8.7% | Governance-closed |
| 2A | Drawing, Artwork, Dieline and CAD Evidence Control | 10 | 16 | 23.2% | Governance-closed |
| 2B | Lightweight PDF, SVG and image preview support | 5 | 21 | 30.4% | Governance-closed |
| 3 | Trial planning and validation requirements | 9 | 30 | 43.5% | Governance-closed |
| 4 | Trial execution, results and deviations | 9 | 39 | 56.5% | Governance-closed |
| 5 | Packaging defect and complaint taxonomy | 8 | 47 | 68.1% | Implemented; validation pending |
| 6 | Specification and implementation change control | 8 | 55 | 79.7% | Not started |
| 7 | Supplier qualification evidence register | 7 | 62 | 89.9% | Not started |
| 8 | Demonstration cases, regression and release QA | 7 | 69 | 100% | Not started |

## Build 1 — Architecture, governance and release boundary — 6 hours
Delivered and governance-closed on `main` at `d5e29f9750b7409be8cccd57bd8036eb988c2faf`.

## Build 2A — Drawing, Artwork, Dieline and CAD Evidence Control — 10 hours
Delivered and governance-closed on `main` at `d3a5fcd513e7c954537980926463cd30bc6083b1`.

DXF and DWG remain governed references only. Geometry and dimensions are not interpreted.

## Build 2B — Lightweight PDF, SVG and image preview support — 5 hours
Delivered and governance-closed on `main` at `590347f6d83a3040114925af5002eb01f4f9353e`.

DXF, DWG, AI and EPS remain governed references with no inline preview. Build 2B introduces no OCR, text extraction, geometry interpretation, dimensional extraction, CAD conversion, editing or approval automation.

## Build 3 — Trial planning and validation requirements — 9 hours
Delivered and governance-closed on `main` at `3f06f8707e05d32e73a9067a379b88319c82c074`.

Build 3 stores planning and validation requirements only. It introduces no execution records, measurements, observed results, deviations, disposition, retest decisions or implementation approval.

## Build 4 — Trial execution, results and deviations — 9 hours
Delivered and governance-closed on `main` at `e206b7ab62d386cb8d32def2b20aa71f96b4ea68`.

Build 4 records execution evidence and deviations only. It introduces no defect taxonomy, complaint classification, specification approval, supplier qualification or sourcing decision.

## Build 5 — Packaging defect and complaint taxonomy — 8 hours

### Delivered
- schema v8 immutable defect-classification and complaint registers;
- governed, versioned packaging taxonomy;
- evidence-linked human-reviewed classification and complaint intake;
- project-scoped repositories and linked-record isolation;
- archived-project protection;
- repository and database immutability;
- focused migration, persistence, archive and isolation tests.

Build 5 records defects, complaints, severity and containment as governed evidence. It introduces no specification-change approval, implementation authorization, supplier qualification, sourcing decision, automatic root cause or corrective-action approval.

## Build 6 — Specification and implementation change control — 8 hours
Not started.

## Build 7 — Supplier qualification evidence register — 7 hours
Not started.

## Build 8 — Demonstration cases, regression and release QA — 7 hours
Not started.

## Explicit exclusions
PVE 1.3 will not include automatic DXF geometry extraction, automatic dimension extraction, cut/crease/slot recognition, parametric dieline generation, automated blank optimization, full CAD editing, 3D folding, tooling design, manufacturing-ready drawing approval, autonomous engineering approval, supplier ranking/allocation/award, or ungoverned production deployment.

## Authorization boundary
Build 5 alone is authorized beyond governance-closed Builds 1, 2A, 2B, 3 and 4. Builds 6–8 require separate explicit authorization. Build 5 must pass CI, review, merge and post-merge controls before it is governance-closed.
