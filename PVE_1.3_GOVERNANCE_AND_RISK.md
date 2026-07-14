# PVE 1.3 Governance and Risk

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Planning status
- Planning baseline only.
- Implementation started: no.
- Build 1 started: no.
- Completion: 0%.
- Completed effort: 0 of 69 planned hours.
- Pending effort: 69 hours, 100%.
- Controlled contingency used: 0 of 2 hours.
- Absolute release cap: 71 hours.

## Mandatory governance controls
- Engineering validation remains mandatory.
- Explicit human approval remains mandatory.
- Autonomous engineering approval is prohibited.
- Drawing preview is not drawing validation.
- File presence is not evidence quality.
- A current revision must be matched to the correct project, SKU, supplier, site and specification.
- Superseded drawings must not be used for trials or implementation.
- DXF and DWG references must not be represented as interpreted geometry.
- Trial results must preserve source, units, method, conditions and deviations.
- Commercial, logistics or sustainability benefits cannot override technical, safety, evidence, revision or validation blockers.
- Supplier qualification evidence must not become supplier ranking, allocation or award recommendation.
- Historical records must remain project-scoped and immutable or append-only as applicable.
- Archived projects remain read-only.
- Cross-project references are rejected unless a separately governed global reference is explicitly permitted.

## Evidence classes
The release must preserve distinctions among:
- uploaded fact;
- manually entered fact;
- supplier-declared value;
- laboratory-tested value;
- observed trial result;
- predicted value;
- assumption;
- synthetic demonstration data.

No class may be silently converted into another. Previewed content is not automatically accepted as a validated fact.

## Drawing and CAD governance
Every governed drawing or CAD reference should retain, where applicable:
- project and SKU;
- supplier and manufacturing site;
- document type;
- drawing number and title;
- revision;
- issue date and effective date;
- specification version;
- baseline or proposed classification;
- artwork, dieline and tooling relationships;
- source classification;
- validation and approval status;
- superseded and replacement links;
- trial applicability;
- file checksum;
- immutable revision history.

Unsupported or unpreviewable files remain valid references only when their metadata, source and checksum are preserved. The system must not imply that a file was technically reviewed merely because it was uploaded or displayed.

## Preview governance
Planned preview support is limited to PDF, SVG, PNG and JPEG.

The preview layer must:
- preserve the original file reference;
- display metadata and revision context;
- disclose unsupported formats;
- avoid automatic dimensional interpretation;
- avoid geometry comparison;
- avoid approval language;
- require human review for engineering conclusions.

## Trial governance
A trial plan should identify:
- objective and trial type;
- protocol and conditions;
- owner and location;
- supplier and manufacturing site;
- material, specification and drawing revision;
- required evidence;
- acceptance criteria;
- prerequisites and blockers;
- planned date and authorization state.

A trial execution record should preserve:
- actual date and conditions;
- observed results and units;
- attachments and source classifications;
- deviations and nonconformances;
- retest requirements;
- unresolved blockers;
- explicit human disposition.

The system must not automatically generate Approved, Rejected or Conditional implementation decisions.

## Change-control governance
Packaging changes must retain:
- affected SKU, project, supplier and site;
- current and proposed specification;
- drawing, artwork, dieline and tooling references;
- technical and commercial rationale;
- required validation;
- transition stock and obsolescence treatment;
- implementation date;
- append-only status history;
- explicit human approval reference.

No implementation may be treated as authorized while mandatory evidence, revision consistency or trial requirements remain unresolved.

## Supplier qualification governance
Supplier qualification evidence may describe:
- corrugator capability;
- printing and converting capability;
- inspection and laboratory capability;
- external or subcontracted processes;
- scope and applicable materials or styles;
- source and verification status;
- validity and expiry;
- requalification requirements.

The module must not score, rank, allocate, shortlist or award suppliers.

## Controlled contingency
The two-hour contingency may cover only:
- unexpected regression;
- CI-only failure;
- migration compatibility repair;
- cross-module integration defect;
- release-evidence reconciliation.

It cannot fund new scope, extra preview formats, CAD interpretation, additional packaging categories, integrations, deployment or productionization.

## Principal risks and controls

### False drawing authority — High
Risk: A stored or previewed drawing appears approved for manufacture.  
Control: Explicit validation and approval status, human-only approval, visible preview limitations and revision matching.

### Obsolete revision use — High
Risk: A trial or implementation uses a superseded drawing, artwork or specification.  
Control: Supersession links, effective dates, trial applicability and blocking revision checks.

### CAD interpretation overclaim — High
Risk: DXF or DWG files are treated as automatically understood.  
Control: Reference-only handling; no geometry or dimension extraction in PVE 1.3.

### Trial evidence misuse — High
Risk: Supplier declarations or incomplete observations are treated as validated results.  
Control: Source classifications, method and condition fields, deviation records and human disposition.

### Commercial override — High
Risk: Savings drive implementation despite technical or evidence blockers.  
Control: Technical, safety, evidence, revision and trial blockers have higher precedence.

### Unsupported causal inference — Medium
Risk: Defect records are used to claim an unproven root cause.  
Control: Descriptive taxonomy, evidence links and explicit separation of observation from causal conclusion.

### Supplier-ranking drift — Medium
Risk: Qualification evidence becomes an award or allocation score.  
Control: Evidence completeness and compatibility only; ranking and sourcing decisions excluded.

### File-security and integrity risk — Medium
Risk: Files are altered, mismatched or represented under the wrong revision.  
Control: Checksums, metadata, immutable history and controlled references. Security scanning and enterprise storage remain separate future concerns.

### Preview inconsistency — Medium
Risk: Browser rendering differs from the source engineering file.  
Control: Original file remains authoritative; preview labelled as convenience-only and human verification required.

### Scope creep — Medium
Risk: Planning expands into CAD editing, 3D design or production deployment.  
Control: Explicit exclusions, fixed 69-hour plan, two-hour restricted contingency and separate authorization for scope change.

## Explicit exclusions
- automatic DXF geometry extraction;
- automatic dimension extraction;
- cut, crease or slot recognition;
- parametric dieline generation;
- automated blank optimization;
- full CAD editing;
- 3D folding;
- tooling design;
- manufacturing-ready drawing generation or approval;
- autonomous engineering approval;
- supplier ranking, allocation or sourcing award;
- ungoverned deployment, activation or production-use claims.

## Acceptance boundary for planning baseline
The planning baseline is complete only when:
- the build plan totals 69 planned hours;
- contingency is fixed at 2 hours;
- the absolute cap is fixed at 71 hours;
- all builds are marked not started;
- 0% completion and 69 pending hours are recorded;
- CAD and preview boundaries are explicit;
- exclusions are explicit;
- no implementation code, schema, migration or tests are introduced;
- the planning PR remains draft until separately authorized.

## Authorization control
This document does not authorize Build 1. Separate explicit authorization is required before any PVE 1.3 implementation activity begins.