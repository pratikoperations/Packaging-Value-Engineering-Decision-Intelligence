# E1.7 Approved Specification Consumption Governance Contract

## Business Purpose

E1.7 creates a controlled, immutable handoff from an E1.6 Approved Specification Snapshot to future downstream analytical workflows.

The slice establishes a governed input boundary. It does not execute cost, scenario, risk, material, recommendation, sourcing, supplier-award, engineering-approval, commercial-approval, or production workflows.

Its business purpose is to ensure that future procurement and packaging analysis begins only from a human-authorized, immutable, project-scoped specification with complete lineage and integrity verification.

## Controlled Artifact Distinctions

### Approved Specification Snapshot

The snapshot is the E1.6 human-authorized frozen specification. It contains the approved field values, optional exclusions, exact project and review lineage, source dataset identities, approval provenance, schema version, and content hash.

### Consumption Envelope

The envelope is the deterministic downstream input package derived only from one approved snapshot.

It copies:

- project ID;
- snapshot ID;
- review ID;
- source review revision ID and number;
- Existing and Proposed dataset IDs;
- snapshot schema version;
- approved values and value sources;
- optional exclusions;
- source snapshot content hash.

It adds a consumption-contract version, envelope ID, creation timestamp, and deterministic envelope content hash.

### Consumption Authorization

The authorization records a human actor's permission to prepare or use the envelope for one controlled purpose and stated business reason.

It does not prove that the named analytical workflow executed, produced a result, or approved a decision.

## Sole-Source Approved-Snapshot Boundary

The E1.7 application service must load source content only through the project-scoped E1.6 Approved Specification Read Model.

E1.7 must not reconstruct or obtain governed values from:

- the Existing dataset;
- the Proposed dataset;
- raw dataset repositories;
- specification-review state;
- review comparisons;
- historical review revisions;
- Streamlit session state;
- caller-provided dictionaries or JSON;
- direct SQL reads that bypass the approved-snapshot repository.

Future downstream consumers must receive only a validated authorized envelope or a controlled projection derived from it.

## Supported Governed Purposes

The controlled purpose registry is:

- `cost_analysis_input`;
- `scenario_analysis_input`;
- `risk_analysis_input`;
- `material_analysis_input`;
- `sourcing_input_preparation`;
- `recommendation_input_preparation`;
- `governance_demonstration`.

These identifiers describe intended input use. They do not represent engine execution, analytical completion, supplier approval, award, or production authorization.

Unknown or arbitrary purpose values fail closed.

## Deterministic Envelope Rules

The envelope must:

1. preserve exact snapshot lineage;
2. use deterministic approved-field ordering by field key;
3. use deterministic optional-exclusion ordering;
4. reject duplicate fields;
5. reject duplicate exclusions;
6. reject overlap between approved and excluded fields;
7. retain each approved value's governed source classification;
8. use canonical JSON with sorted keys, compact separators, UTF-8 encoding, and NaN rejection;
9. calculate SHA-256 over all critical lineage, approved values, exclusions, snapshot hash, and contract version;
10. verify its hash before persistence and after every read.

One deterministic envelope is permitted per snapshot and consumption-contract version.

## Authorization Rules

Every authorization requires:

- project ID;
- snapshot ID;
- envelope ID;
- controlled purpose;
- non-empty actor reference;
- non-empty business reason;
- source snapshot content hash;
- envelope content hash;
- authorization schema version;
- creation timestamp.

Separate authorizations are permitted for different purposes or business reasons while reusing the same deterministic envelope.

## Idempotency and Concurrency

### Envelope retry

An identical retry for the same snapshot and contract version returns the existing envelope only when every critical lineage and content field matches.

A conflicting retry fails closed and creates no replacement envelope.

### Authorization retry

An identical retry with the same project, snapshot, envelope, purpose, actor, business reason, hashes, and authorization schema version returns the existing authorization.

A different purpose or business reason may create a separate immutable authorization.

### Concurrent requests

Database uniqueness is the final concurrency control.

The application service:

1. checks for an existing record;
2. attempts insertion;
3. catches a uniqueness conflict;
4. reloads the persisted record;
5. compares all critical fields;
6. returns only an identical record;
7. otherwise fails closed.

No update, overwrite, or silent replacement is permitted.

## Project-Scoped Read Boundary

Every read operation requires an explicit project ID.

Supported reads include:

- get envelope by ID;
- get envelope for a snapshot and contract version;
- list envelopes for a project;
- get authorization by ID;
- list authorizations for a snapshot;
- list authorizations for a project;
- get the validated authorized envelope for an authorization.

Cross-project access fails closed.

Archived projects remain readable but cannot create new envelopes or authorizations.

## Immutability and Integrity Controls

Persistence is append-only.

Controls include:

- no effective repository update method;
- no effective repository delete method;
- database triggers rejecting envelope update and deletion;
- database triggers rejecting authorization update and deletion;
- restrictive project and snapshot foreign-key lineage;
- canonical approved-values and exclusions JSON;
- source snapshot hash preservation;
- deterministic envelope hash;
- envelope hash verification before write and on every read;
- authorization-to-envelope lineage verification;
- project-scoped retrieval.

Tampered, malformed, cross-project, or lineage-inconsistent content fails closed.

## Controlled UI and Human Confirmation

The Streamlit page must:

- list active projects;
- list only approved snapshots within the selected project;
- show snapshot identity and lineage read-only;
- allow only controlled purpose selection;
- require actor reference;
- require business reason;
- require explicit confirmation;
- create the handoff only through the E1.7 runtime service;
- show envelope and authorization records read-only;
- place hashes in collapsed audit details;
- avoid raw JSON exposure;
- suppress duplicate Streamlit rerun mutations through an action token.

The confirmation must state that the action prepares an approved input package and authorization record but does not execute or approve downstream analysis or decisions.

## Claim Boundary

E1.7 proves that:

- one immutable approved snapshot was selected;
- its integrity and project scope were validated;
- one deterministic envelope was prepared;
- one human actor authorized a declared governed purpose;
- exact lineage and hashes were preserved;
- the resulting records can be reloaded and verified.

E1.7 does not prove that:

- any analytical engine ran;
- any analytical result is correct;
- a cost or savings estimate is valid;
- a scenario is feasible;
- supplier capability was assessed;
- a recommendation was generated or accepted;
- a supplier was approved or awarded;
- engineering, commercial, sourcing, regulatory, or production approval occurred;
- realized savings or production readiness exist.

## Prohibited Bypass Routes

Downstream services must not consume:

- raw Existing or Proposed datasets;
- review comparisons;
- review repositories;
- historical revisions;
- raw snapshot repository objects without the authorized-envelope boundary;
- direct database rows;
- session-state values;
- manually constructed approved-value dictionaries;
- unverified exported JSON.

Future engine constructors should depend on an authorized-envelope provider rather than dataset, review, or raw snapshot repositories.

## Downstream Non-Execution Boundary

E1.7 does not implement or invoke:

- cost engines;
- scenario engines;
- risk engines;
- material engines;
- recommendation engines;
- decision engines;
- supplier comparison;
- RFQ transmission;
- supplier award;
- notifications;
- external APIs;
- exports to suppliers;
- deployment workflows.

A later, separately authorized slice must implement the first governed analytical consumer.

## Scope Exclusions

E1.7 excludes:

- analytical calculations and outputs;
- autonomous approval;
- electronic signature;
- multi-level approval workflow;
- amendment, deletion, rollback, revocation, or supersession of snapshots, envelopes, or authorizations;
- changes to dependencies or GitHub workflows;
- deployment, release, or tagging;
- modification of `main`.

## Integration Acceptance Flow

The E1.7 integration test verifies the persisted sequence:

1. create an active project;
2. persist valid Existing and Proposed datasets;
3. initialize and complete a governed specification review;
4. create the immutable approved specification snapshot;
5. create a governed consumption handoff;
6. recreate runtime services;
7. reload the envelope and authorization;
8. verify exact project, review, revision, dataset, snapshot-hash, and envelope-hash lineage;
9. retry the identical handoff;
10. verify one envelope and one authorization;
11. create a second authorization for a different governed purpose;
12. verify one envelope and two authorizations;
13. reject cross-project access;
14. reject creation after the source project is archived;
15. verify that no scenario, decision, or analytical output record was created.

## Protected Boundaries

This slice does not modify dependencies, workflows, `main`, or `e1-development`; does not deploy, release, or tag; and does not open a pull request until the focused E1.7 suite passes.
