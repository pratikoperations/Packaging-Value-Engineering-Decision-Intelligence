# PVE 1.3 Architecture

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current state
Build 1 architecture and governance boundaries are implemented on the controlled branch. PVE 1.3 is 8.7% complete with 6 of 69 planned hours consumed and 63 hours pending. Builds 2A–8 have not started and remain unauthorized.

## Objective
Extend the frozen PVE 1.2 decision-intelligence foundation into governed drawing control, lightweight document preview, validation execution, defect intelligence, specification change control and supplier qualification evidence management.

The release remains a decision-support and governance system. It does not become a CAD-authoring platform, autonomous engineering authority or sourcing-award engine.

## Frozen dependency
PVE 1.3 must preserve the validated PVE 1.2 foundation:
- project-scoped records and cross-project isolation;
- archived-project write protection;
- deterministic outputs;
- explicit source classifications;
- immutable or append-only history;
- technical and evidence blockers overriding commercial benefit;
- explicit human engineering validation and approval.

## Architectural flow

```text
Frozen PVE 1.2 project, specification, evidence and technical assessment
→ Drawing, artwork, dieline and CAD evidence register
→ Lightweight PDF, SVG and image preview
→ Trial planning and validation requirements
→ Trial execution, results and deviations
→ Packaging defect and complaint records
→ Specification and implementation change control
→ Supplier qualification evidence register
→ Updated engineering-review evidence package
→ Explicit human engineering validation and approval
```

## Module boundaries

### 1. Drawing and CAD evidence control
Planned responsibilities:
- register drawing, artwork, dieline, tooling and CAD references;
- preserve drawing number, title, revision, issue and effective dates;
- link project, SKU, specification, supplier and manufacturing site;
- classify baseline and proposed records;
- preserve source, approval and validation status;
- retain checksum, supersession and immutable revision history;
- identify the exact drawing revision applicable to each trial or change.

DXF and DWG remain governed file references only. Geometry and dimensions are not interpreted automatically.

### 2. Preview service
Planned responsibilities:
- present PDF, SVG, PNG and JPEG content for human review;
- show metadata and baseline/proposed context;
- provide controlled fallback for unsupported formats;
- preserve the original file reference and checksum;
- state visibly that preview does not constitute engineering validation.

The preview layer must not extract or approve dimensions, geometry, tooling or structural performance.

### 3. Trial planning
Planned responsibilities:
- define trial type, purpose, protocol, prerequisites and acceptance criteria;
- identify owner, site, supplier, material, specification and drawing revisions;
- link required evidence and unresolved blockers;
- maintain planned dates and authorization state.

### 4. Trial execution and deviations
Planned responsibilities:
- create append-only execution records;
- record observed results, measurements and attachments;
- classify evidence source and preserve units;
- record deviations, nonconformances and retest requirements;
- prohibit automatic acceptance, rejection or implementation approval.

### 5. Defect and complaint intelligence
Planned responsibilities:
- maintain a governed packaging-defect taxonomy;
- capture severity, frequency, location, evidence and affected context;
- link defects to projects, specifications, drawings, trials, suppliers and changes;
- support descriptive analysis without unsupported causal inference.

### 6. Change control
Planned responsibilities:
- record append-only packaging change requests and status history;
- identify affected SKU, supplier, site, specification, drawing, artwork and tooling;
- record required validation and inventory transition treatment;
- retain implementation date and explicit human approval reference;
- prevent commercial benefits from overriding technical blockers.

### 7. Supplier qualification evidence
Planned responsibilities:
- record site and process capability evidence;
- preserve source, scope, validity, expiry and requalification requirements;
- distinguish supplier declarations from independently verified evidence;
- assess evidence completeness and compatibility only;
- exclude supplier scoring, ranking, allocation and award decisions.

### 8. Release QA
Planned responsibilities:
- governed synthetic demonstration data;
- end-to-end regression;
- immutability and project-isolation tests;
- migration validation where schema changes are separately authorized;
- release notes, checklist, QA report and governance reconciliation.

## Record and persistence principles
Future implementation must preserve:
- project-scoped records;
- explicit identifiers and version references;
- append-only history for trials, deviations, changes and qualification evidence;
- immutable historical evidence;
- archived-project write protection;
- cross-project isolation;
- checksums for governed files;
- explicit source classifications;
- traceable human decisions.

The controlling detail is defined in `PVE_1.3_BUILD_1_RECORD_AND_AUTHORITY_MODEL.md`.

## Decision hierarchy
1. Safety and compliance blockers.
2. Technical and evidence blockers.
3. Drawing and specification revision consistency.
4. Trial and validation completeness.
5. Supplier-site capability evidence.
6. Operational, commercial, logistics and sustainability benefits.
7. Explicit human engineering and business approval.

Commercial or sustainability attractiveness cannot override a technical, evidence, revision or trial blocker.

## File and preview support boundary

### Governed references planned
- PDF;
- DXF;
- DWG;
- SVG;
- PNG;
- JPEG;
- artwork and tooling references.

### Preview formats planned
- PDF;
- SVG;
- PNG;
- JPEG.

### Excluded
- automatic DXF or DWG interpretation;
- automatic dimension extraction;
- geometry comparison;
- cut, crease or slot recognition;
- parametric dieline generation;
- CAD editing;
- 3D folding;
- tooling design;
- manufacturing-ready drawing approval.

## Human authority boundary
The system may identify missing evidence, revision conflicts, failed criteria, deviations and required validation. It may prepare an engineering-review package. It must never autonomously approve a drawing, dieline, tooling, trial result, packaging specification, supplier qualification or packaging-change implementation.

## Integration and deployment boundary
PVE 1.3 may define internal references and exportable evidence packages. Live PLM, ERP, CAD-platform, supplier-portal or workflow integrations remain outside scope unless separately governed. Deployment, pilot, activation and production use remain separately unauthorized.

## Acceptance control
Universal and build-specific gates are defined in `PVE_1.3_BUILD_1_ACCEPTANCE_GATES.md`. Each build must pass focused tests where code exists, the complete regression suite, review controls and post-merge validation of the exact `main` commit.

## Release budget
- Planned effort: 69 hours.
- Controlled contingency: 2 hours.
- Absolute release cap: 71 hours.
- Completed: 6 hours.
- Pending: 63 hours.
- Completion: 8.7%.

## Authorization control
Build 1 alone is authorized and implemented on the controlled branch. No schema, migration, product data model, file-processing code, preview renderer or UI capability is introduced by Build 1. Builds 2A–8 require separate explicit authorization.
