# Decision Log

## DEC-PVE-001 — Separate Repository
PVE uses an independent repository and file system from AI Procurement Copilot.

## DEC-PVE-002 — GitHub Is Canonical
All code, plans, logs, decisions, QA evidence, and recovery records live in GitHub.

## DEC-PVE-003 — Deterministic Decision Logic
Costing, qualification, recommendation, and risk logic remain explicit and testable. AI cannot grant packaging approval.

## DEC-PVE-004 — Technical Qualification First
No packaging option can be commercially recommended before technical qualification or conditional qualification.

## DEC-PVE-005 — Versioned Integration Contracts
PVE communicates through versioned read-only packages. Neither repository writes into the other's source files.

## DEC-PVE-006 — Scope-Gated Build
Development progresses through approved, independently validated builds.

## DEC-PVE-007 — One Category First
PVE 1.0 retains the existing corrugated category before adding category breadth.

## DEC-PVE-008 — SQLite Behind Repository Interfaces
PVE 1.0 uses SQLite only through repository classes. Application and analytical layers must not issue ad-hoc SQL.

Rationale:
- keeps the portfolio implementation lightweight
- allows later replacement with a durable database
- supports isolated tests
- limits cloud persistence claims

## DEC-PVE-009 — Immutable Decision Evidence
Datasets, threshold profiles, scenarios, and decision snapshots are append-only after creation. Corrections create new versions rather than rewriting history.

## DEC-PVE-010 — Restrictive Foreign Keys
Historical records use restrictive foreign keys. Archiving a project does not delete datasets, scenarios, decisions, or export records.

## DEC-PVE-011 — Demonstration Persistence Boundary
SQLite history on public Streamlit hosting is demonstration persistence and is not represented as durable enterprise storage.

## DEC-PVE-012 — PVE-1.0.1 Infrastructure Only
PVE-1.0.1 does not add dashboard UI, uploads, configurable threshold UI, history UI, authentication, external integrations, supplier workflows, AI approval, or new packaging categories.

## DEC-PVE-013 — Dashboard Through Service and Repository Boundaries
The PVE-1.0.2 Streamlit page uses `ProjectService` and `ProjectRepository`. The page must not issue SQL directly.

## DEC-PVE-014 — Metadata-Only Project Duplication
Duplicating a project copies only project metadata. It does not copy datasets, threshold profiles, scenarios, decisions, or export records.

## DEC-PVE-015 — Archive Instead of Delete
The dashboard archives projects rather than deleting them. Archived projects are read-only and retain historical evidence.

## DEC-PVE-016 — Portfolio Metrics Are Evidence Counts
Dashboard metrics describe project records, dataset versions, and saved decision snapshots. They do not claim realized savings, approved packaging changes, or supplier allocation.

## DEC-PVE-017 — PVE-1.0.2 Dashboard Scope
PVE-1.0.2 adds project portfolio navigation only. Uploads, parsing, thresholds, scenario execution, decision-history UI, authentication, external databases, supplier workflows, AI approval, and new categories remain excluded.

## DEC-PVE-018 — JSON Is the Canonical Upload Format
CSV is a constrained entry method only; all uploaded content normalizes to the canonical JSON structure.

## DEC-PVE-019 — Invalid Uploads Are Not Persisted
Only validated canonical datasets can create immutable dataset versions.

## DEC-PVE-020 — Configurable Business Thresholds Are Separate From Engineering Controls
Business thresholds may screen savings, material reduction, and business risk. They cannot alter qualification, evidence, engineering-validation, critical-risk, or approval controls.

## DEC-PVE-021 — Controlled Default Profile Is Read-Only
A global default profile is available to every project and cannot be edited. Customization requires a project-specific immutable profile version.

## DEC-PVE-022 — Threshold Changes Create New Versions
Threshold profiles are append-only. Changed content creates a new version; identical content returns the existing version.

## DEC-PVE-023 — Mandatory Controls Are Outside Editable Profile Schema
Engineering validation, prohibition of autonomous approval, critical-risk blocking, technical-failure blocking, and insufficient-data controls are fixed constants and cannot be submitted as editable threshold fields.

## DEC-PVE-024 — PVE-1.0.4 Scope
PVE-1.0.4 adds threshold creation, selection, validation, versioning, templates, and business screening only. It does not execute scenarios or modify recommendation-engine logic.

## DEC-PVE-025 — Scenarios Bind Exact Immutable Versions
Every controlled scenario references one immutable dataset version and one immutable threshold-profile version. Cross-project references are rejected in both service and repository layers.

## DEC-PVE-026 — Scenario Assumptions Are Explicit and Bounded
Annual volume and alternative-level cost and material adjustments are entered explicitly. Hidden defaults, forecasts, optimization, and AI-generated assumptions remain excluded.

## DEC-PVE-027 — Scenario Outcomes Are Not Approvals
Scenario control statuses indicate evidence readiness only. Engineering validation and human approval remain mandatory, and autonomous approval remains prohibited.

## DEC-PVE-028 — Mandatory Controls Precede Business Thresholds
Not-qualified technical status and critical risk remain blocking. Insufficient technical or risk data cannot become eligible even when business thresholds pass.

## DEC-PVE-029 — PVE-1.0.5 Scope
PVE-1.0.5 adds controlled scenario execution and immutable scenario evidence only. It does not create decision snapshots, decision-history UI, or modify the recommendation engine.

## DEC-PVE-030 — PVE-1.0.5 Post-Merge Closure Is Governance-Only
The post-merge closure records PR #21, final CI, test evidence, actual effort, remaining budget, branch deletion, and recovery state directly on `main`. It does not change application logic, scenario logic, thresholds, persistence schema, recommendation logic, or approved scope boundaries.
