# PVE 1.3 Build 3 — Trial Planning and Validation Requirements

## Status
Build 3 is implemented on the controlled branch and pending CI, review, merge and post-merge validation.

## Delivered capability
- additive SQLite schema v6 for immutable `trial_plans`;
- project-scoped trial code, title, objective, protocol, owner and trial site;
- planned start and end dates;
- drawing-evidence and specification-version linkage;
- governed evidence requirements;
- measurable acceptance criteria with required evidence;
- prerequisites and blockers;
- explicit plan and authorization statuses;
- human authorizer identity and authorization reference;
- archived-project protection and cross-project evidence isolation;
- repository and database immutability.

## Human authority boundary
A trial plan does not authorize execution by itself. Status `authorized` requires explicit human authorization and an identified authorizer. Planning records cannot represent trial completion, technical acceptance, commercial approval or implementation approval.

## Explicit Build 3 exclusions
- trial execution records;
- measurements or observations;
- pass/fail results;
- deviations or nonconformances;
- retest decisions;
- engineering disposition;
- specification change approval;
- supplier qualification decisions;
- Build 4 or later-build functionality.

## Acceptance evidence required
- schema migration from versions 1–5 to version 6;
- focused validation and persistence tests;
- complete regression suite with zero failures and zero errors;
- exact changed-file audit;
- immutability, project-isolation and archived-project tests;
- measurable-criteria and human-authorization tests;
- explicit rejection of execution and result data;
- PR and post-merge CI evidence.

## Effort accounting
- Builds 1, 2A and 2B completed: 21 hours.
- Build 3 allocation: 9 hours.
- PVE 1.3 completed on branch: 30 of 69 hours.
- PVE 1.3 completion: 43.5%.
- Pending: 39 hours.
- Controlled contingency used: 0 of 2 hours.
