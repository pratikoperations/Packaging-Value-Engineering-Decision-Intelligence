# PVE 1.3 Build 6 — Specification and Implementation Change Control

## Status
Build 6 implementation is complete on the controlled branch and remains pending CI, audit, merge and post-merge validation.

## Objective
Provide traceable, evidence-linked control for specification changes and implementation authorization without automatically qualifying suppliers, awarding business, changing sourcing allocation, or authorizing production without named human approval.

## Delivered capability
- additive SQLite schema v9;
- immutable `specification_change_requests` and `implementation_controls`;
- project-scoped create, read and list repositories;
- current and proposed specification-version traceability;
- linked trial execution, defect classification and complaint evidence;
- requested effective-date control;
- named human approver, approval reference and approval date;
- approved-change prerequisite for implementation authorization;
- implementation site, owner, authorization, actual date and verification evidence;
- archived-project protection and cross-project evidence isolation;
- repository and database update/delete prohibition;
- focused migration, persistence, authorization, immutability and isolation tests.

## Governance rules
- approved change requests require a named human approver, approval reference and evidence;
- implementation authorization, execution or completion requires an approved change request;
- linked trials, defects and complaints must belong to the same project;
- archived projects are read-only;
- uncertainty and pending decisions are preserved rather than inferred;
- records are immutable evidence snapshots; new facts require new records;
- effective dates are recorded human decisions, not autonomously selected recommendations.

## Human authority boundary
Build 6 may record change proposals, reviews, approvals, implementation authorization and verification. It does not qualify or disqualify suppliers, score supplier capability, award or allocate business, determine sourcing strategy, or authorize autonomous production release.

## Explicit Build 7 and later exclusions
- supplier qualification or disqualification;
- supplier capability scoring;
- approved supplier list decisions;
- sourcing award or allocation;
- supplier ranking;
- autonomous production release;
- automatic change approval;
- automatic effective-date selection.

## Acceptance evidence required
- additive migration from schema v8 to schema v9;
- complete regression suite with zero failures and zero errors;
- exact changed-file audit;
- original Build 6 validation tests retained;
- persistence, approval prerequisite, archive, isolation and immutability tests;
- explicit rejection of Build 7 and later-build fields;
- PR and post-merge CI evidence.

## Effort accounting
- Builds 1 through 5 governance-closed: 47 hours.
- Build 6 allocation: 8 hours.
- PVE 1.3 completed on branch: 55 of 69 hours.
- PVE 1.3 completion on branch: 79.7%.
- Pending planned effort: 14 hours.
- Controlled contingency used remains 0 of 2 hours.
