# Build History

## PVE-0.1 — Repository Foundation
**Status:** Completed and merged

## PVE-0.2 — Data Model and Demo Data
**Status:** Completed and merged

## PVE-0.3 — Cost and Material Engine
**Status:** Completed and merged

## PVE-0.4 — Technical Qualification and Risk
**Status:** Completed and merged

## PVE-0.5 — Scenario and Recommendation UI
**Status:** Completed and merged

## PVE-0.6 — Decision Package Export
**Status:** Completed and merged

## PVE-0.7 — QA and Interview Release
**Status:** Completed and merged through PR #13
- Merge commit: `fb0962ba611fcf59ae7ab194dd2514970a19909d`
- Tests: 58 passed, 0 failed, 0 errors

## PVE-0.7.1 — Streamlit Deployment Disclaimer
**Status:** Completed and merged through PR #15

## PVE-0.7.2 — Live Demo and Streamlit Compatibility
**Status:** Completed and merged through PR #16
- Merge commit: `a45cabc37aada9e57febe7687617146d2da65fd0`
- Tests: 60 passed, 0 failed, 0 errors

---

## PVE-1.0.1 — Foundation and Persistence
**Status:** Completed and merged through PR #17

### Implemented Scope
- SQLite connection and transaction management
- Schema initialization with version recording
- Project lifecycle repository and service
- Immutable datasets, threshold profiles, scenarios, and decision snapshots
- Cross-project integrity validation

### Completion Record
- Merge commit: `3ad821c33f382f6f58e954ce0efbc3d50a1836a0`
- Tests: 85 passed, 0 failed, 0 errors
- Effort used: 14.5 hours
- Program budget after build: 75.5 hours
- Source branch: Deleted

---

## PVE-1.0.2 — Project Dashboard
**Status:** Completed and merged through PR #18

### Implemented Scope
- Portfolio summary metrics
- Project creation and explicit active selection
- Metadata-only duplication
- Project archiving and read-only archived view
- Runtime SQLite service initialization

### Completion Record
- Merge commit: `87f3897c68503cddc2c7e64827d8c395b45065a5`
- Tests: 100 passed, 0 failed, 0 errors
- Effort used: 11.5 hours
- Program budget after build: 64.0 hours
- Source branch: Deleted

---

## PVE-1.0.3 — Upload and Validation
**Status:** Completed and merged through PR #19

### Implemented Scope
- Canonical JSON upload
- Limited `project.csv` and `alternatives.csv` ingestion
- Canonical normalization and validation
- Immutable dataset-version storage
- Duplicate detection across JSON and CSV

### Completion Record
- Merge commit: `c3e5247510c062fe64ac1da171dcc2f107ff4967`
- Tests: 126 passed, 0 failed, 0 errors
- Effort used: 16.5 hours
- Program budget after build: 47.5 hours
- Source branch: Deleted

---

## PVE-1.0.4 — Configurable Business Thresholds
**Status:** Completed and merged through PR #20

### Implemented Scope
- Controlled global default profile
- Project-specific immutable profile versions
- Threshold validation and duplicate suppression
- Active threshold selection
- Mandatory non-disableable engineering controls

### Completion Record
- Merge commit: `301a0d92d41f46a15e37c5bd059e8673c3f666a6`
- Tests: 143 passed, 0 failed, 0 errors
- Effort used: 12.5 hours
- Program budget after build: 35.0 hours
- Source branch: Deleted

---

## PVE-1.0.5 — Controlled Scenario Execution
**Status:** Completed, validated, merged, and governance-closed through PR #21

### Objective
Run deterministic scenarios from immutable project dataset and threshold-profile versions and save immutable scenario evidence.

### Implemented Scope
- Project-scoped immutable dataset selection
- Global or project-specific immutable threshold selection
- Explicit bounded annual-volume, cost, and material assumptions
- Existing deterministic scenario-engine execution
- Existing technical-qualification and risk evaluation
- Explainable business-threshold evaluation
- Mandatory engineering-control outcomes
- Immutable scenario-record storage
- Cross-project protection in service and repository layers
- Streamlit execution and review page
- Automated tests and documentation

### Design Rules
- Existing deterministic engines remain authoritative
- Critical risk and not-qualified status remain blocking
- Insufficient technical or risk data cannot become eligible
- Scenario statuses are not approvals
- Engineering validation and human approval remain mandatory
- Saved scenarios bind exact immutable dataset and threshold versions

### Completion Record
- Pull request: PR #21 merged and closed
- Merge method: Squash merge
- Merge commit: `99416d91025b6cfbff40142ce9fbcd462eb1028f`
- Final CI: PVE CI #455
- Run ID: `29192749111`
- Validated head commit: `fb3b2421a457081d83631f5952510e7c533c7f8b`
- Tests: 160 passed, 0 failed, 0 errors
- Source branch: Deleted

### Budget
- Planned allocation: 18.0 hours
- Actual effort used: 17.5 hours
- Program budget before build: 35.0 hours
- Confirmed program budget after build: 17.5 hours

### Scope Exclusions
No decision snapshots, decision-history UI, recommendation-engine modification, authentication, external database, supplier ranking or allocation, ERP integration, AI approval, or new packaging category.

### Closure Result
Post-merge governance closure completed directly on `main`. No application logic, scenario logic, thresholds, persistence schema, or scope boundary was changed.
