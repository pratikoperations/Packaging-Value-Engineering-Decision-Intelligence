# PVE 1.3 Governance and Risk

## Release
PVE 1.3 — Validation Execution, Drawing Control and Packaging Change Governance

## Current implementation status
- Build 1 governance implementation: complete on the controlled branch; validation and merge pending.
- Builds 2A–8: not started and not authorized.
- Completion: 8.7%.
- Completed effort: 6 of 69 planned hours.
- Pending effort: 63 hours, 91.3%.
- Controlled contingency used: 0 of 2 hours.
- Controlled contingency remaining: 2 hours.
- Absolute release cap: 71 hours.

## Controlling Build 1 records
- `PVE_1.3_BUILD_1_RELEASE_BOUNDARY.md`
- `PVE_1.3_BUILD_1_RECORD_AND_AUTHORITY_MODEL.md`
- `PVE_1.3_BUILD_1_ACCEPTANCE_GATES.md`

## Mandatory governance controls
- Engineering validation and explicit human approval remain mandatory.
- Autonomous engineering approval is prohibited.
- Drawing preview is not drawing validation.
- File presence is not evidence quality.
- A current revision must match the correct project, SKU, supplier, site and specification.
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

No class may be silently converted into another. Previewed content is not automatically accepted as validated evidence.

## Drawing and CAD governance
Every governed drawing or CAD reference should retain, where applicable:
- project and SKU;
- supplier and manufacturing site;
- document type;
- drawing number and title;
- revision, issue date and effective date;
- specification version;
- baseline or proposed classification;
- artwork, dieline and tooling relationships;
- source classification;
- validation and approval status;
- superseded and replacement links;
- trial applicability;
- file checksum;
- immutable revision history.

Unsupported or unpreviewable files remain references only when metadata, source and checksum are preserved. Upload or display must never imply technical review.

## Preview governance
Planned preview support is limited to PDF, SVG, PNG and JPEG. The preview layer must preserve the source reference, display revision context, disclose unsupported formats, avoid geometry or dimension inference, avoid approval language and require human engineering review.

## Trial governance
A trial plan should identify objective, type, protocol, conditions, owner, location, supplier site, material, specification and drawing revision, required evidence, acceptance criteria, prerequisites, blockers, planned date and authorization state.

A trial execution record should preserve actual conditions, observations, units, attachments, source classes, deviations, nonconformances, retest requirements, unresolved blockers and explicit human disposition.

The system must not automatically generate final implementation approval, rejection or conditional approval.

## Change-control governance
Packaging changes must retain affected SKU, project, supplier, site, current and proposed specification, drawing/artwork/dieline/tooling references, rationale, validation requirements, transition stock treatment, implementation date, append-only status history and explicit human approval reference.

No implementation is authorized while mandatory evidence, revision consistency or trial requirements remain unresolved.

## Supplier qualification governance
Supplier qualification evidence may describe process capability, inspection and laboratory capability, subcontracting, scope, source, verification status, validity, expiry and requalification requirements. The module must not score, rank, shortlist, allocate or award suppliers.

## Controlled contingency
The two-hour contingency may cover only unexpected regression, CI-only failure, migration compatibility repair, cross-module integration defects or release-evidence reconciliation. It cannot fund new scope, additional preview formats, CAD interpretation, extra categories, integrations, deployment or productionization.

## Principal risks and controls

### False drawing authority — High
Risk: A stored or previewed drawing appears approved for manufacture.  
Control: Explicit validation/approval state, human-only approval, visible preview limitations and revision matching.

### Obsolete revision use — High
Risk: A trial or implementation uses a superseded drawing, artwork or specification.  
Control: Supersession links, effective dates, trial applicability and blocking revision checks.

### CAD interpretation overclaim — High
Risk: DXF or DWG files are treated as automatically understood.  
Control: Reference-only handling; no geometry or dimension extraction.

### Trial evidence misuse — High
Risk: Supplier declarations or incomplete observations are treated as validated results.  
Control: Source classes, method/condition fields, deviations and human disposition.

### Commercial override — High
Risk: Savings drive implementation despite technical or evidence blockers.  
Control: Safety, technical, evidence, revision and trial blockers have precedence.

### Unsupported causal inference — Medium
Risk: Defect records are used to claim an unproven root cause.  
Control: Descriptive taxonomy, evidence links and separation of observation from causal conclusion.

### Supplier-ranking drift — Medium
Risk: Qualification evidence becomes an award or allocation score.  
Control: Evidence completeness and compatibility only; sourcing decisions excluded.

### File-security and integrity risk — Medium
Risk: Files are altered, mismatched or represented under the wrong revision.  
Control: Checksums, metadata, immutable history and controlled references. Enterprise scanning/storage remain separate future controls.

### Preview inconsistency — Medium
Risk: Browser rendering differs from the source engineering file.  
Control: Original file remains authoritative; preview is convenience-only.

### Scope creep — Medium
Risk: Work expands into CAD editing, 3D design or production deployment.  
Control: Locked release boundary, fixed 69-hour plan, restricted contingency and separate authorization.

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

## Build 1 acceptance status
Build 1 deliverables now define the release boundary, frozen dependency, record ownership, immutability, project isolation, evidence classes, human authority and acceptance gates. Build 1 remains subject to CI, review and post-merge validation before governance closure.

## Authorization control
Build 1 alone is authorized. Builds 2A–8 remain prohibited until separate explicit authorization. Build 1 introduces no implementation schema, migration, data model, product code, preview renderer or UI functionality.
