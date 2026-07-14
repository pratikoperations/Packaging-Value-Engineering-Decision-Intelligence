# PVE 1.3 Controlled Build Plan

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current implementation status
- Status: Builds 1 and 2A implemented; Build 2A validation and merge remain pending.
- Implementation started: yes, limited to Builds 1 and 2A.
- Build 1 status: merged, post-merge validated and governance-closed.
- Build 2A status: implementation complete on controlled branch; CI and governance closure pending.
- Build 2B and Builds 3–8: not started and not authorized.
- Release completion: 23.2%.
- Completed planned effort: 16 of 69 hours.
- Pending planned effort: 53 hours, 76.8%.
- Controlled contingency used: 0 of 2 hours.
- Controlled contingency remaining: 2 hours.
- Absolute release cap: 71 hours.

## Budget control
The 69 planned hours remain fixed. The two-hour contingency may be used only for unexpected regression, CI-only failure, migration compatibility repair, cross-module integration defects or release-evidence reconciliation. It cannot fund new functionality, additional categories, deployment or scope expansion.

## Controlled build sequence

| Build | Scope | Hours | Cumulative hours | Planned completion | Status |
|---|---|---:|---:|---:|---|
| 1 | Architecture, governance and release boundary | 6 | 6 | 8.7% | Governance-closed |
| 2A | Drawing, Artwork, Dieline and CAD Evidence Control | 10 | 16 | 23.2% | Implemented; validation pending |
| 2B | Lightweight PDF, SVG and image preview support | 5 | 21 | 30.4% | Not started |
| 3 | Trial planning and validation requirements | 9 | 30 | 43.5% | Not started |
| 4 | Trial execution, results and deviations | 9 | 39 | 56.5% | Not started |
| 5 | Packaging defect and complaint taxonomy | 8 | 47 | 68.1% | Not started |
| 6 | Specification and implementation change control | 8 | 55 | 79.7% | Not started |
| 7 | Supplier qualification evidence register | 7 | 62 | 89.9% | Not started |
| 8 | Demonstration cases, regression and release QA | 7 | 69 | 100% | Not started |

## Build 1 — Architecture, governance and release boundary — 6 hours
Delivered and governance-closed on `main` at `d5e29f9750b7409be8cccd57bd8036eb988c2faf`.

## Build 2A — Drawing, Artwork, Dieline and CAD Evidence Control — 10 hours

### Delivered
- schema v5 immutable drawing-evidence register;
- drawing number, title, revision, issue and effective dates;
- baseline/proposed classification;
- project, SKU, supplier, site and specification linkage;
- governed PDF, DXF, DWG, SVG, PNG, JPEG, AI and EPS references;
- source, validation and approval statuses;
- supersession and related-document links;
- trial applicability, checksum and immutable history;
- project isolation and archived-project protection;
- current-revision lookup;
- focused validation and persistence tests;
- human-only engineering approval boundary.

DXF and DWG remain governed references only. Geometry and dimensions are not interpreted.

### Build 2A exclusions
Build 2A introduces no preview renderer, dimensional extraction, geometry comparison, CAD editing, dieline generation, 3D folding, tooling design or manufacturing approval.

## Build 2B — Lightweight PDF, SVG and image preview support — 5 hours
Planned outcomes include PDF, SVG, PNG and JPEG preview, metadata display, baseline/proposed viewing, unsupported-format fallback and explicit preview limitations. Not started.

## Build 3 — Trial planning and validation requirements — 9 hours
Not started.

## Build 4 — Trial execution, results and deviations — 9 hours
Not started.

## Build 5 — Packaging defect and complaint taxonomy — 8 hours
Not started.

## Build 6 — Specification and implementation change control — 8 hours
Not started.

## Build 7 — Supplier qualification evidence register — 7 hours
Not started.

## Build 8 — Demonstration cases, regression and release QA — 7 hours
Not started.

## Explicit exclusions
PVE 1.3 will not include automatic DXF geometry extraction, automatic dimension extraction, cut/crease/slot recognition, parametric dieline generation, automated blank optimization, full CAD editing, 3D folding, tooling design, manufacturing-ready drawing approval, autonomous engineering approval, supplier ranking/allocation/award, or ungoverned production deployment.

## Authorization boundary
Build 2A alone is authorized beyond governance-closed Build 1. Build 2B and Builds 3–8 require separate explicit authorization. Build 2A must pass CI, review, merge and post-merge controls before it is governance-closed.
