# Controlled Enhancement Acceptance Criteria

## Baseline preservation

- frozen source SHA remains `2954c293ca09882cadd7f23b5862f50334170a11`;
- `main` remains unchanged;
- original frozen showcase branch is not moved;
- PR #79 closes without merge after planning acceptance;
- existing 746-test regression baseline remains passing;
- primary business-engine outputs do not change without separate authorization.

## Browser acceptance

- 13 of 13 pages accessible;
- direct navigation and four sidebar groups verified;
- five-minute route completes;
- synthetic disclosure and Capabilities & Limits visible;
- Markdown export decodes, contains required headings and synthetic limitations;
- JSON export parses, contains required keys and synthetic limitations;
- desktop and Android-sized viewport tests pass;
- zero unexplained `pageerror`, console-error or relevant failed-request events;
- three consecutive clean CI runs at the same exact SHA, without retry-dependent passes;
- CI retains exact SHA, browser version, startup log, result summary and artifact digest.

## Synthetic-data acceptance

- every dataset and record explicitly declares or inherits synthetic status;
- no real supplier identity or implied current market rate;
- three complete positive scenarios;
- at least eight invalid or contradictory cases;
- manifests contain dataset/schema versions, generation method, provenance, currency basis, period and counts;
- zero duplicate IDs or orphaned references;
- deterministic fixture regeneration passes;
- accidental real-company-name and identifiable-data checks pass;
- schemas, disclosures and export-preservation tests pass.

## Calculation Evidence acceptance

- static and dependency-boundary checks prove no prohibited primary-engine reuse;
- formula registry is versioned;
- decimal arithmetic, precision, rounding stage/mode and tolerance type are explicit;
- zero, negative and unsupported currency cases are tested;
- independent fixtures are separately owned;
- every core calculation demonstrates `MATCH` and `FAIL`;
- selected representative calculations demonstrate `WARNING`;
- unsupported calculations demonstrate `NOT SUPPORTED`;
- deliberate mismatches and mutation tests are detected;
- primary and independent results, absolute/percentage variance and tolerance are visible;
- no engineering, commercial or realized-savings validation claim is made.

## Programme acceptance

- actual planning and feature effort are separately recorded and combined actual effort does not exceed 100 hours;
- all cumulative forecast gates are met or immediate scope reduction is documented;
- complete existing regression and all new feature-specific tests pass;
- hosted desktop and Android-sized final smoke acceptance passes;
- exact final SHA and artifacts are recorded;
- original frozen branch and evidence history remain retained;
- enhanced version is published through a separate accepted branch;
- production readiness is not claimed.

## Stop rule

Failure of any mandatory measurable criterion blocks acceptance unless a documented scope reduction is separately authorized and does not remove a non-reducible control.
