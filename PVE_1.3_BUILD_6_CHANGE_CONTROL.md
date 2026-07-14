# PVE 1.3 Build 6 — Specification and Implementation Change Control

## Status
Build 6 implementation has started on the controlled branch. This document establishes the governed change-control and authority boundary before persistence and workflow integration.

## Objective
Provide traceable, evidence-linked control for specification changes and implementation authorization without automatically qualifying suppliers, awarding business, changing sourcing allocation, or authorizing production without named human approval.

## Governed specification-change dimensions
- project and change-request identity;
- change type: specification, implementation or combined;
- title, rationale and business justification;
- current and proposed specification versions;
- affected SKU, supplier, site and packaging component where known;
- linked trial execution, defect classification and complaint evidence;
- technical, commercial, quality, regulatory and sustainability impact assessments;
- requested effective date;
- review status, approval status and named human approver;
- evidence references and decision reference.

## Governed implementation-control dimensions
- linked authorized change request;
- implementation site and owner;
- planned and actual implementation dates;
- implementation status;
- verification status and evidence;
- rollback or containment reference where required;
- named human authorizer and verifier.

## Governance rules
- approved change requests require a named human approver and approval reference;
- implementation authorization requires an approved change request;
- linked records must belong to the same project;
- archived projects are read-only;
- uncertainty and pending decisions are preserved rather than inferred;
- approved and implemented records become immutable evidence snapshots;
- effective dates are recorded facts, not autonomously selected recommendations.

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

## Effort accounting
- Builds 1 through 5 governance-closed: 47 hours.
- Build 6 allocation: 8 hours.
- Build 6 implementation started; no completion hours claimed yet.
- PVE 1.3 governance-closed completion remains 47 of 69 hours, 68.1%.
- Pending planned effort remains 22 hours.
- Controlled contingency used remains 0 of 2 hours.
