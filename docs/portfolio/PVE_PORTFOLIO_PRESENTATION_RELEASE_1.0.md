# PVE Portfolio Presentation Release 1.0

## Release purpose

This release is a separately authorized public portfolio-presentation enhancement derived from the permanently frozen PVE 1.4 baseline. It improves demonstration usability without reopening, modifying, or reclassifying the frozen PVE 1.4 planning and governance record.

## Frozen source baseline

- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Frozen baseline branch: `main`
- Frozen baseline SHA: `4d1658207763dd6feac4dd2b78dd377a93f238f5`
- Frozen baseline status: `PVE 1.4 — COMPLETED AND GOVERNANCE CLOSED`
- Planning closure: `PLANNING COMPLETE WITH DOCUMENTED LIMITATIONS`
- Future pilot recommendation: `DECISION DEFERRED`
- Deployment readiness: `NOT APPROVED`

This presentation release does not alter any of those determinations.

## Pull request and branch

- Pull request: `PR #50 — PVE Portfolio Presentation Release 1.0`
- Branch: `portfolio/pve-demonstration-seed-release`
- Pull request state at Build 3 preparation: draft, open, unmerged

## Authorized objective

Add one explicit, idempotent `Load demonstration project` workflow that creates or reuses one complete synthetic project chain:

1. project workspace;
2. validated immutable dataset;
3. project-specific threshold profile;
4. deterministic controlled scenario;
5. immutable decision snapshot.

The release does not change scenario calculations, recommendation logic, technical-qualification logic, risk logic, threshold policy, decision-ranking logic, persistence schemas, migrations, dependencies, CI workflows, or deployment configuration.

## Build 1 — Synthetic data and seed orchestration

Build 1 added:

1. `data/demo/pve_portfolio_project.json`
2. `src/demo_portfolio/__init__.py`
3. `src/demo_portfolio/seeder.py`
4. `tests/demo_portfolio/__init__.py`
5. `tests/demo_portfolio/test_portfolio_seed.py`

### Build 1 behaviour

The seeder:

- uses existing application and persistence services;
- does not write directly through custom SQL;
- creates or resumes one linked synthetic demonstration record chain;
- validates the seed as `synthetic_demo`;
- reuses immutable records only when identities and references match;
- stops on conflicting project, threshold, or scenario content;
- stops when the controlled demonstration project is archived;
- never overwrites, unarchives, or silently modifies existing records;
- returns success only after the complete linked chain exists.

### Build 1 test evidence

- Build 1 accepted head: `445d304f4da9e9dd6cef119d851fd80cdb52a31c`
- PVE CI run number: `1132`
- Workflow run ID: `30234821370`
- Job ID: `89880544689`
- Test result: `387 tests, 0 failures, 0 errors`
- Artifact ID: `8641291840`
- Artifact digest: `sha256:a3512055c52c577f95c143da2b92a39c0c887b3d390e2d41aa0f8dfba779d333`

## Build 2 — Dashboard presentation

Build 2 changed only:

1. `pages/01_Project_Dashboard.py`
2. `tests/application/test_project_dashboard.py`

### Build 2 user experience

The dashboard now provides a prominent `Load demonstration project` action before portfolio metrics and manual project creation.

After the action is selected, the dashboard:

- calls the existing Build 1 seed orchestration;
- verifies that the complete project, dataset, threshold, scenario, and decision chain exists;
- selects the synthetic project as the active workspace;
- reports whether each record was created or reused;
- provides a guided workflow sequence covering Project Dashboard, Upload and Validate, Business Thresholds, Controlled Scenarios, and Decision History;
- shows success only after complete-chain validation;
- preserves existing project creation, duplication, archive, and selection behaviour.

Repeated loading is idempotent. Existing matching records are reused and no duplicate project, dataset, threshold profile, scenario, or decision snapshot is created.

### Build 2 final test evidence

- Build 2 accepted head: `b573a9e7805b342b8a2673bd02f3d45f08c5118c`
- PVE CI run number: `1135`
- Workflow run ID: `30235213584`
- Job ID: `89881647048`
- Test result: `391 tests, 0 failures, 0 errors`
- Artifact ID: `8641413345`
- Artifact digest: `sha256:f0cb8af39af05a82228479343ad4ef90aef2c6e0bb54b0578358de8b3b302883`

The first Build 2 CI attempt, run `1134`, failed one newly added static source assertion because a warning was split across adjacent Python string literals. The correction changed only the authorized dashboard test file and did not weaken or remove the warning or modify application behaviour. The subsequent complete run `1135` passed.

## Synthetic and non-production boundaries

All demonstration content is synthetic.

The release must not be treated as evidence of:

- validated supplier data;
- laboratory evidence;
- engineering-trial evidence;
- production data;
- commercial approval;
- real-user UAT;
- live integration;
- AI-model validation;
- pilot readiness;
- deployment readiness;
- production readiness;
- Finance-validated savings;
- realized business value.

Displayed savings are synthetic analytical opportunities only. They are not approved or realized benefits.

## Engineering and human-approval boundaries

The release preserves the following controls:

- engineering validation remains mandatory;
- documented human approval remains mandatory;
- autonomous approval remains prohibited;
- no dashboard action approves a packaging design;
- no scenario or decision snapshot authorizes supplier ranking, award, or allocation;
- no recommendation bypasses existing technical, risk, or business-threshold logic.

## Demonstration persistence boundary

The Streamlit dashboard uses local SQLite demonstration persistence. It is not production storage.

The loader is intentionally explicit rather than automatic. Merely opening the dashboard does not silently create records. A visitor must select `Load demonstration project`.

## Exact release file scope

The complete PR is authorized to contain only these eight files:

1. `data/demo/pve_portfolio_project.json`
2. `src/demo_portfolio/__init__.py`
3. `src/demo_portfolio/seeder.py`
4. `pages/01_Project_Dashboard.py`
5. `tests/demo_portfolio/__init__.py`
6. `tests/demo_portfolio/test_portfolio_seed.py`
7. `tests/application/test_project_dashboard.py`
8. `docs/portfolio/PVE_PORTFOLIO_PRESENTATION_RELEASE_1.0.md`

Any requirement to modify another file requires a stop and separate owner authorization.

## Rollback

### Before merge

Rollback requires no change to `main`:

1. close PR #50;
2. delete branch `portfolio/pve-demonstration-seed-release`;
3. retain frozen baseline SHA `4d1658207763dd6feac4dd2b78dd377a93f238f5` unchanged.

### After merge, before hosted acceptance

Create a dedicated revert pull request that reverts only the Portfolio Presentation Release 1.0 squash merge. Do not modify PVE 1.4 closure records.

### Runtime reset

The runtime SQLite database is demonstration persistence and is not committed as release evidence. If runtime storage is reset, the explicit loader can recreate the same controlled synthetic record chain. The loader must remain idempotent and must not overwrite conflicting or archived records.

## Hosted and mobile acceptance criteria

Hosted acceptance is not complete until all of the following are verified against the merged final `main` SHA:

1. the Project Dashboard visibly presents `Load demonstration project` without requiring manual project entry;
2. the action completes without an unhandled error;
3. the dashboard shows non-zero project, dataset, scenario, and decision counts after loading;
4. the synthetic project becomes the active workspace;
5. created-versus-reused status is visible;
6. the active project is available on Upload and Validate, Business Thresholds, Controlled Scenarios, and Decision History pages;
7. repeated loading creates no duplicate records;
8. synthetic-data, non-production, engineering-validation, human-approval, and autonomous-approval warnings remain visible;
9. no page claims approved packaging design, realized savings, supplier allocation, AI validation, pilot readiness, deployment readiness, or production readiness;
10. the dashboard and guided workflow are readable and operable on a mobile viewport;
11. final post-merge CI succeeds on the exact resulting `main` SHA;
12. a diagnostic artifact is tied to that same final SHA.

## Release governance decision

Builds 1 and 2 are implemented and test-validated on the draft pull-request branch. Build 3 records release evidence and acceptance boundaries only.

PR #50 must remain draft and unmerged until the owner separately authorizes formal acceptance and merge. No tag, release, deployment, hosted acceptance, pilot, or production activity is authorized by this document.
