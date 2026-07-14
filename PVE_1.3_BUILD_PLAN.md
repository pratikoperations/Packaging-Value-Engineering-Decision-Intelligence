# PVE 1.3 Controlled Build Plan

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current implementation status
- Status: Builds 1, 2A, 2B, 3, 4, 5 and 6 governance-closed; Build 7 implementation started on a controlled branch.
- Implementation started: yes, limited to Builds 1, 2A, 2B, 3, 4, 5, 6 and authorized Build 7.
- Build 1 status: merged, post-merge validated and governance-closed.
- Build 2A status: merged, post-merge validated and governance-closed.
- Build 2B status: merged, post-merge validated and governance-closed.
- Build 3 status: merged, post-merge validated and governance-closed.
- Build 4 status: merged, post-merge validated and governance-closed.
- Build 5 status: merged, post-merge validated and governance-closed.
- Build 6 status: merged, post-merge validated and governance-closed.
- Build 7 status: initial supplier-qualification validation tranche implemented on controlled branch; persistence and governance closure pending.
- Build 8: not started and not authorized.
- Governance-closed release completion: 79.7%.
- Governance-closed planned effort: 55 of 69 hours.
- Pending planned effort: 14 hours, 20.3%.
- Build 7 completion hours claimed: 0 of 7 hours.
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
| 5 | Packaging defect and complaint taxonomy | 8 | 47 | 68.1% | Governance-closed |
| 6 | Specification and implementation change control | 8 | 55 | 79.7% | Governance-closed |
| 7 | Supplier qualification evidence register | 7 | 62 | 89.9% | Started; initial validation tranche |
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
Delivered and governance-closed on `main` at `b5590d57180d9aefc1155ecc68c293bb42119029`.

Build 5 records defects, complaints, severity and containment as governed evidence. It introduces no specification-change approval, implementation authorization, supplier qualification, sourcing decision, automatic root cause or corrective-action approval.

## Build 6 — Specification and implementation change control — 8 hours
Delivered and governance-closed on `main` at `a52cd4bcbb5309f8c8c21e49e0e50be35e78e1a2`.

Build 6 records human-controlled change approval and implementation evidence. It introduces no supplier qualification, supplier scoring, approved-supplier-list decision, sourcing award, allocation, ranking or autonomous production release.

## Build 7 — Supplier qualification evidence register — 7 hours

### Initial tranche
- governed supplier qualification validation;
- supplier, site and scope-specific decision identity;
- qualification status, validity, conditions and review dates;
- evidence references and named human assessor/approver;
- linked trial, defect, complaint and change-control evidence;
- explicit Build 8 release, sourcing and commercial-decision rejection;
- focused validation tests.

Persistence, additive migration, immutable repository, project/archive isolation and full regression remain pending within Build 7.

## Build 8 — Demonstration cases, regression and release QA — 7 hours
Not started.

## Explicit exclusions
PVE 1.3 will not include automatic DXF geometry extraction, automatic dimension extraction, cut/crease/slot recognition, parametric dieline generation, automated blank optimization, full CAD editing, 3D folding, tooling design, manufacturing-ready drawing approval, autonomous engineering approval, supplier ranking/allocation/award, or ungoverned production deployment.

## Authorization boundary
Build 7 alone is authorized beyond governance-closed Builds 1, 2A, 2B, 3, 4, 5 and 6. Build 8 requires separate explicit authorization. Build 7 must pass CI, review, merge and post-merge controls before it is governance-closed.
