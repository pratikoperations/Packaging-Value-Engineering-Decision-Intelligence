# PVE 1.3 Build 2A — Drawing, Artwork, Dieline and CAD Evidence Control

## Status
Build 2A is implemented on the controlled branch and pending CI, review, merge and post-merge validation.

## Delivered capability
- additive SQLite schema v5 for immutable `drawing_evidence` records;
- project, SKU, supplier, manufacturing-site and specification-version linkage;
- document type, number, title, revision, issue date and effective date;
- baseline/proposed classification;
- governed references for PDF, DXF, DWG, SVG, PNG, JPEG, AI and EPS;
- source classification, validation status and approval status;
- content checksum and duplicate-content protection within a project;
- supersession links and current-revision lookup;
- related drawing, artwork, dieline and tooling relationships;
- trial-applicability references;
- project isolation and archived-project write protection;
- immutable database triggers and repository update/delete rejection;
- validation preventing approval without validation;
- explicit prohibition of DXF/DWG geometry interpretation.

## Human authority boundary
Stored or previewable file references are not engineering approval. Final validation and approval remain human decisions. A file upload, checksum match or current-revision result must not be represented as manufacturing authorization.

## Explicit Build 2A exclusions
- file rendering or preview UI;
- PDF, SVG, PNG or JPEG preview;
- DXF/DWG parsing;
- automatic dimension extraction;
- cut, crease or slot recognition;
- geometry comparison;
- parametric dieline generation;
- CAD editing;
- manufacturing-ready drawing approval.

These exclusions remain reserved for separately authorized future work. Build 2B and Builds 3–8 have not started.

## Acceptance evidence required
- schema migration from versions 1–4 to version 5;
- focused validation and repository tests;
- complete regression suite with zero failures and zero errors;
- exact changed-file audit;
- immutable-record, project-isolation and archived-project tests;
- PR and post-merge CI evidence.

## Effort accounting
- Build 1 completed: 6 hours.
- Build 2A allocation: 10 hours.
- PVE 1.3 completed on branch: 16 of 69 hours.
- PVE 1.3 completion: 23.2%.
- Pending: 53 hours.
- Controlled contingency used: 0 of 2 hours.
