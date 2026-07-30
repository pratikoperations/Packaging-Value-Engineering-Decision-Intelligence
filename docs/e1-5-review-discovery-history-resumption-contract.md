# E1.5 Specification Review Discovery, History and Resumption Contract

## Scope

E1.5 adds project-scoped discovery of persisted specification reviews, controlled resumption from the latest immutable revision, and read-only revision-history presentation.

## Read boundary

`SpecificationReviewReadModel` is read-only. It:

- requires an existing project;
- returns one latest-revision summary per review;
- filters all discovery, latest-load, and history reads by project;
- validates sequential revision numbers and parent lineage;
- translates missing or invalid records into presentation-safe application errors.

## Discovery contract

Each summary contains:

- review and project identity;
- Existing and Proposed dataset identity;
- latest revision number, action, actor, and timestamp;
- latest eligibility state;
- pending and terminal candidate counts.

Ordering is deterministic: latest activity first, then review identity.

## Resumption contract

- A user selects one active project.
- The UI offers Create new review and, when reviews exist, Resume persisted review.
- Resumption always loads the latest revision through the read model.
- Historical revisions are never actionable.
- Changing project clears an incompatible session selection.
- Existing E1.4 write-token protection remains the mutation boundary.

## History contract

History is immutable and ordered from revision 1 upward. The UI exposes revision number, action type, field, actor, rationale, eligibility, timestamp, parent revision, and content hash.

## Protected boundaries

E1.5 does not add:

- snapshot creation;
- approved-specification generation;
- scenario, decision, recommendation, or export changes;
- rollback, deletion, revision editing, branching, or history mutation;
- deployment, release, tag, dependency, workflow, or main-branch changes.

## Acceptance tests

- project-scoped discovery excludes other projects;
- one latest summary is returned per review;
- empty discovery is safe;
- unknown projects and cross-project access fail closed;
- history is sequential and lineage-valid;
- latest state can be resumed after a simulated new service/read-model instance;
- summary labels and history rows are deterministic;
- the existing full regression suite remains green in CI.
