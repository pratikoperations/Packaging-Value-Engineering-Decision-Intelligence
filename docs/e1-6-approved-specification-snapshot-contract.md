# E1.6 Approved Specification Snapshot Governance Contract

## Purpose

E1.6 creates one immutable, project-scoped Approved Specification Snapshot from the latest eligible persisted specification-review revision.

The snapshot is the controlled handoff between governed human review and any future downstream sourcing, costing, scenario, recommendation, or decision workflow. Those downstream consumers are not implemented in E1.6.

## Scope

E1.6 includes:

- deterministic approved-value materialization;
- immutable append-only persistence;
- exact project, review, revision, and dataset lineage;
- project-scoped creation and reads;
- latest-revision enforcement;
- independent eligibility recomputation;
- human actor and rationale provenance;
- idempotent safe retry;
- read-only Streamlit presentation;
- integrity verification through canonical content hashing.

E1.6 does not create a new review status named `APPROVED`. Candidate review status and snapshot authorization remain separate concepts.

## Deterministic Materialization Rules

The governed field registry defines the complete ordered field boundary.

| Governed field state | Snapshot result |
|---|---|
| Accepted changed field | Use the Proposed original value |
| Corrected changed field | Use the human-corrected value |
| Rejected changed field | Retain the Existing baseline value |
| Unchanged governed field | Retain the common Existing/Proposed value |
| Intentionally absent optional field | Record the field in `excluded_fields` |
| Pending mandatory field | Block snapshot creation |
| Unresolved validation issue | Block snapshot creation |

Output ordering is deterministic by field key. A field cannot be both approved and excluded.

## Latest-Revision Control

Only the latest persisted revision of a specification review may generate a snapshot.

The creation service:

1. loads the latest review within the explicit project scope;
2. compares its revision identity with the requested source revision;
3. rejects historical revisions;
4. independently recomputes eligibility from persisted review state;
5. rejects inconsistent stored eligibility;
6. requires the recomputed result to be eligible.

Historical revisions remain immutable and read-only.

## Project, Review, and Dataset Lineage

Every snapshot records:

- `project_id`;
- `review_id`;
- exact `source_review_revision_id`;
- exact source revision number;
- Existing dataset ID;
- Proposed dataset ID.

Creation fails closed unless:

- the project exists and is active;
- both datasets exist;
- both datasets belong to the same project;
- the exact review revision exists;
- the revision belongs to the stated review and project;
- the revision dataset lineage exactly matches the snapshot lineage;
- source dataset values match persisted review comparisons.

Every read operation requires `project_id`. Cross-project access is rejected.

## Human Authorization and Claim Boundary

Actor reference and approval rationale are mandatory. The Streamlit UI also requires an explicit confirmation checkbox before creation.

The snapshot records a human-authorized controlled artifact. It does not autonomously provide:

- engineering approval;
- technical validation;
- commercial approval;
- supplier award;
- sourcing approval;
- production authorization;
- electronic signature;
- multi-level approval.

The artifact proves that a governed review state was frozen with human attribution and rationale. It does not prove fitness for use, realized savings, supplier capability, regulatory compliance, or production readiness.

## Idempotency

The persistence layer enforces one snapshot per source review revision.

A retry is safe only when the existing and candidate snapshots match on all critical content and authorization fields, including:

- project and review identity;
- source revision identity and number;
- source dataset lineage;
- approved values and exclusions;
- schema version;
- actor reference;
- approval rationale;
- content hash.

An identical retry returns the existing snapshot. A conflicting retry fails closed and creates no second artifact.

## Immutability and Integrity

The `approved_specification_snapshots` table is append-only.

Controls include:

- no repository update method;
- no repository delete method;
- database triggers rejecting update;
- database triggers rejecting delete;
- unique source review revision;
- canonical approved-values JSON;
- canonical exclusions JSON;
- SHA-256 content hash over approved content and critical lineage;
- content-hash verification on every read.

Tampered or malformed stored content fails integrity verification.

## Optional Exclusions

An exclusion is valid only when:

- the field exists in the governed registry;
- the registry marks it optional;
- the field is intentionally absent;
- the field is not also materialized as an approved value.

Mandatory fields cannot be excluded. Unknown exclusions fail closed.

## Read Boundary

The approved-specification read model supports only project-scoped read operations:

- get a snapshot by ID;
- get the snapshot associated with a review;
- list snapshots for a project.

Existing snapshots are rendered read-only. Public presentation does not expose raw JSON. The content hash appears only in a collapsed audit section.

## Downstream Non-Consumption Boundary

E1.6 does not connect the approved snapshot to:

- scenario engines;
- cost engines;
- material engines;
- risk engines;
- recommendation engines;
- decision engines;
- exports;
- notifications;
- deployment workflows.

Future downstream integration must consume only the immutable approved snapshot through a separately authorized slice. It must not consume raw Proposed data, partial review state, Streamlit session state, or historical review revisions.

## Integration Acceptance Flow

The E1.6 integration test verifies the persisted sequence:

1. create an active project;
2. persist valid Existing and Proposed datasets;
3. initialize a review;
4. confirm the Existing baseline;
5. accept one field;
6. correct one field;
7. reject one field;
8. reach eligibility;
9. create the snapshot;
10. recreate runtime services;
11. reload the snapshot;
12. verify values, exclusions, exact lineage, and content hash;
13. retry identical creation;
14. verify one persisted artifact;
15. attempt conflicting creation and verify fail-closed behavior.

## Protected Boundaries

E1.6 does not add snapshot amendment, update, deletion, rollback, branching, supersession, review reopening, deployment, release, tag, dependency changes, workflow changes, or modifications to `main`.
