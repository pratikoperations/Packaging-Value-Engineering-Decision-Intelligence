# PVE 1.3 Build 1 — Acceptance Gates

## Purpose
Define the mandatory evidence required before each PVE 1.3 build may be declared complete or merged.

## Universal gates
Every implementation build must satisfy all applicable gates:

### G1 — Authorized scope
- Work is limited to the separately authorized build.
- No later build is started implicitly.
- Exclusions and hour limits remain unchanged unless a separately approved scope change exists.

### G2 — Repository integrity
- Changes are made on a dedicated branch from the latest validated baseline.
- The diff contains only authorized files and functionality.
- Historical release evidence remains preserved.

### G3 — Governance and authority
- Human engineering approval remains mandatory.
- Autonomous approval, supplier ranking, allocation and award decisions remain prohibited.
- Preview, file presence or calculated output is not represented as engineering validation.

### G4 — Data and record control
- Records are project-scoped.
- Source classifications remain explicit.
- Immutable or append-only histories cannot be silently changed or deleted.
- Archived-project and cross-project protections remain enforced.

### G5 — Deterministic behavior
- Identical inputs produce consistent outputs.
- Derived outputs retain traceable source and rule context.
- Missing, conflicting or unsupported evidence remains visible.

### G6 — Tests and regression
- New behavior has focused automated tests where implementation code exists.
- Existing automated tests remain passing.
- No reduction in test count is accepted without documented justification.
- Final CI result is 0 failures and 0 errors.

### G7 — Demonstration and evidence integrity
- Demonstration data is synthetic and explicitly labelled.
- Supplier, production, laboratory or regulatory validation is not falsely claimed.
- Diagnostic artifacts and relevant logs are retained for release evidence.

### G8 — Documentation reconciliation
- Architecture, build plan, governance/risk and release records agree.
- Completed and pending hours are reconciled.
- Contingency use is recorded and justified.
- Known limitations and exclusions remain explicit.

### G9 — Review and merge control
- Pull request head is verified immediately before merge.
- No unresolved review threads or merge blockers remain.
- Merge method is squash unless separately authorized.
- Post-merge CI validates the exact resulting `main` commit.

## Build-specific acceptance evidence

### Build 1
Build 1 is complete only when:
- release scope and exclusions are locked;
- dependencies on frozen PVE 1.2 are explicit;
- module ownership and lifecycle boundaries are defined;
- immutability, project isolation and evidence classes are defined;
- human authority and prohibited autonomous decisions are explicit;
- acceptance and release-evidence gates are documented;
- no Build 2A–8 implementation is introduced;
- CI passes with the existing full suite.

### Build 2A
Requires governed record model, validation, persistence, revision and checksum controls for drawing/CAD references, plus focused tests. No preview renderer or geometry interpretation may be introduced unless separately authorized.

### Build 2B
Requires controlled PDF/SVG/PNG/JPEG preview behavior, unsupported-format fallback, visible limitations and security-safe file handling. It must not infer dimensions or approval.

### Builds 3–7
Each requires authorized domain records, validations, persistence rules, human-decision boundaries, focused tests and end-to-end linkage to existing governed project context.

### Build 8
Requires governed synthetic demonstrations, complete regression, release checklist, QA report, release notes, governance reconciliation and successful post-merge CI.

## Release evidence package
Each completed build should record:
- authorized scope and branch;
- final branch head;
- changed files;
- completed hours and pending hours;
- focused and full-suite test results;
- workflow number, run ID and job ID;
- artifact name and ID;
- known limitations;
- exact merge commit after authorization;
- exact post-merge validated commit.

## Failure handling
A build remains incomplete when any mandatory gate fails. Failed gates must be corrected within the authorized scope. Contingency may be used only under the approved contingency policy and must not fund new features.

## Authorization boundary
These gates govern future work but do not authorize Builds 2A–8. Separate explicit authorization remains mandatory for each build or approved grouped sequence.
