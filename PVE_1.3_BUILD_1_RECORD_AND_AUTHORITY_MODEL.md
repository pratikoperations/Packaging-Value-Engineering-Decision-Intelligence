# PVE 1.3 Build 1 — Record and Authority Model

## Purpose
Define ownership, lifecycle, immutability, project isolation and human-authority rules before any PVE 1.3 schema or product implementation begins.

## Record families and ownership

| Record family | Owning context | Planned lifecycle | Human authority required |
|---|---|---|---|
| Drawing/CAD reference | Project + SKU + supplier site + specification version | Versioned, supersession-linked | Validation and approval |
| Preview metadata | Governed file reference | Rebuildable convenience data | Engineering interpretation |
| Trial plan | Project + specification + drawing revision | Versioned before authorization | Trial authorization |
| Trial execution | Authorized trial plan | Append-only | Result disposition |
| Deviation/nonconformance | Trial execution or implementation event | Append-only | Closure or retest decision |
| Defect/complaint | Project/SKU/supplier/site context | Append-only observations | Root-cause and action approval |
| Change request | Project + affected specification/drawing | Append-only status history | Implementation approval |
| Supplier qualification evidence | Supplier site + process + scope | Versioned with validity/expiry | Qualification decision |

## Identity requirements
Every governed record must use explicit identifiers and retain applicable references to:
- project;
- SKU or packaging item;
- supplier and manufacturing site;
- material or board structure;
- specification version;
- drawing, artwork, dieline and tooling revision;
- parent trial, defect, change or qualification record;
- source classification;
- author/actor and timestamp where supported.

## Immutability policy
- Historical evidence is never overwritten.
- Trial executions, observed results, deviations, status events and approval references are append-only.
- Corrective records reference the superseded or corrected record rather than mutating history.
- File checksums bind metadata to the governed source file.
- Update/delete operations must be rejected for immutable record families.
- Archived projects remain read-only.

## Project isolation
- All operational PVE 1.3 records are project-scoped unless a separately governed global reference is explicitly defined.
- Cross-project linking is rejected by default.
- Supplier-site evidence may be reusable only through an explicit governed reference with scope, validity and applicability checks.
- A file, trial or decision from one project must not silently satisfy another project’s evidence requirement.

## Evidence classes
The implementation must preserve these distinct classes:
- uploaded fact;
- manually entered fact;
- supplier-declared value;
- laboratory-tested value;
- observed trial result;
- predicted value;
- assumption;
- synthetic demonstration data.

No class may be silently promoted to another. A previewed file is not automatically validated evidence.

## Decision hierarchy
1. Safety and compliance blockers.
2. Technical and evidence blockers.
3. Drawing/specification revision consistency.
4. Trial and validation completeness.
5. Supplier-site capability evidence.
6. Operational, commercial, logistics and sustainability benefits.
7. Explicit human engineering and business approval.

Lower-level benefits cannot override higher-level blockers.

## Human-only decisions
The application must not autonomously issue final approval, rejection, conditional approval, qualification, implementation authorization, supplier award, ranking or allocation.

Human authority remains mandatory for:
- drawing and specification approval;
- trial authorization and disposition;
- deviation acceptance or retest;
- root-cause confirmation;
- supplier qualification;
- packaging-change implementation;
- production release.

## Determinism and traceability
- Identical governed inputs must produce deterministic screening and reporting outputs.
- Every derived output must identify its source inputs, rules and version where practical.
- Missing or conflicting evidence must remain visible.
- Unsupported inference must be prohibited.

## Build boundary
This model defines future implementation constraints only. Build 1 creates no schema, migration, persistence code, file processor, preview renderer, product UI or new automated test. Builds 2A–8 require separate authorization.
