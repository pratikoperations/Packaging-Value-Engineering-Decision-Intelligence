# Enhancement Branch Strategy

## Status

Planning only. Feature implementation is not yet authorized.

## Protected historical state

- `main` remains unchanged.
- `showcase-handoff-development` remains frozen at `2954c293ca09882cadd7f23b5862f50334170a11`.
- Existing Build 6 branches remain retained.

## Programme branch

`enhancement/browser-data-calculation-programme`

This branch was created directly from the frozen source SHA and is the integration point for the controlled enhancement programme.

## Planned feature branches

1. `enhancement/governed-synthetic-data`
2. `enhancement/calculation-evidence-reconciliation`
3. `enhancement/browser-acceptance`

Each feature branch must start from the accepted programme-branch SHA current at authorization time.

## Planned merge order

1. governed synthetic data;
2. independent Calculation Evidence reconciliation;
3. browser acceptance;
4. final evidence and freeze record on the programme branch.

## Pull-request controls

- draft first;
- exact base and head SHAs recorded;
- narrow authorized file scope;
- full regression required;
- feature-specific tests required;
- no external reviewers unless separately authorized;
- merge commit preferred for traceability;
- no branch deletion without separate authorization.

## Publication strategy

The original frozen showcase branch should remain unchanged. If the programme is accepted, publish through a distinct branch such as `showcase-enhanced-v2` rather than moving the historical frozen branch.

## Stop conditions

Stop work if:

- the frozen source branch moves;
- `main` changes unexpectedly;
- scope exceeds the authorized capability;
- projected effort exceeds 100 hours;
- synthetic data loses mandatory labelling;
- evidence-engine independence cannot be demonstrated;
- existing business-engine outputs change without explicit authorization.
