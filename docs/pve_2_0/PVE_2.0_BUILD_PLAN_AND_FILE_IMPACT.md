# PVE 2.0 — Build Plan and Repository File Impact

## Status

Planning only. No implementation, merge, tag, release or deployment is authorized.

## Effort envelope

- Total controlled estimate: **66 hours**
- Planning and architecture: **8 hours**
- Future implementation and validation: **58 hours**
- Contingency: not included; any overrun requires separate approval

## Build groups

### Build Group A — Architecture and contracts — 8 hours

Deliverables:

- intake architecture;
- 25-field governed schema;
- extraction and mapping contract;
- traceability model;
- confidence and ambiguity policy;
- human-confirmation state model;
- security and retention boundaries;
- evaluation strategy;
- exact file-impact and rollback plan.

Acceptance gate:

- owner approval required before implementation;
- no runtime or dependency changes;
- frozen `main` unchanged.

### Build Group B — Deterministic DOCX parser — 9 hours

Planned capabilities:

- `.docx` file validation;
- content hash and duplicate detection;
- paragraph, heading and table extraction;
- stable source block identifiers;
- role assignment for existing/proposed;
- malformed and unsupported-content handling.

Acceptance gate:

- parser output deterministic;
- no AI call required;
- no embedded object execution;
- parser unit tests pass.

### Build Group C — AI extraction adapter — 12 hours

Planned capabilities:

- provider-neutral extraction interface;
- schema-constrained output;
- source-grounded candidates;
- alias-aware field recognition;
- ambiguity codes;
- confidence generation;
- prompt-injection resistance controls;
- no-value-invention validation.

Acceptance gate:

- malformed model output rejected;
- candidate without source rejected;
- no canonical write performed;
- provider credentials remain outside source control.

### Build Group D — Review and comparison workflow — 10 hours

Planned capabilities:

- side-by-side existing/proposed table;
- source excerpt and table-cell view;
- confidence and ambiguity display;
- confirm, correct, omit and reject actions;
- unit conflict and duplicate candidate resolution;
- change summary.

Acceptance gate:

- no field mapped without explicit confirmation;
- original and corrected values preserved;
- unresolved conflicts block completion.

### Build Group E — Canonical mapping and persistence — 8 hours

Planned capabilities:

- confirmed intake snapshot;
- append-only persistence;
- confirmed-field canonical adapter;
- source classification preservation;
- downstream invocation of existing validation.

Acceptance gate:

- existing readiness, threshold, scenario and decision logic unchanged;
- cross-project and archived-project protections retained;
- existing immutable records unaffected.

### Build Group F — Evaluation and release QA — 11 hours

Planned capabilities:

- representative synthetic DOCX test corpus;
- field-level accuracy evaluation;
- source-grounding evaluation;
- existing/proposed role accuracy;
- prompt-injection tests;
- malformed/oversized/password-protected document tests;
- full regression suite;
- limitations and demo guide.

Acceptance gate:

- high-priority-field precision at least 95%;
- source-grounding accuracy 100% for accepted values;
- document-role accuracy at least 98%;
- zero accepted unsupported-value inventions;
- all existing tests pass.

### Build Group G — Hosted presentation and closure — 8 hours

Planned capabilities:

- synthetic demonstration pair;
- hosted workflow validation;
- mobile and desktop presentation check;
- human-readable evidence presentation;
- release checklist and owner acceptance record.

Acceptance gate:

- no confidential data;
- no autonomous approval claim;
- no production-readiness claim;
- owner approval required before merge or release.

## Effort summary

| Build group | Hours | Cumulative |
|---|---:|---:|
| A — Architecture and contracts | 8 | 8 |
| B — Deterministic DOCX parser | 9 | 17 |
| C — AI extraction adapter | 12 | 29 |
| D — Review and comparison | 10 | 39 |
| E — Mapping and persistence | 8 | 47 |
| F — Evaluation and QA | 11 | 58 |
| G — Hosted presentation and closure | 8 | 66 |

## Planned repository file impact

Exact paths are provisional until Build Group B begins, but implementation must remain within the following additive boundaries.

### New application page

- `pages/07_PVE_2_0_AI_Word_Intake.py`

Purpose: upload, parse, extract, review and confirm two DOCX specifications.

### New source packages

- `src/document_intake/__init__.py`
- `src/document_intake/docx_parser.py`
- `src/document_intake/document_models.py`
- `src/document_intake/file_validation.py`
- `src/document_intake/source_blocks.py`
- `src/document_intake/comparison.py`

- `src/ai_extraction/__init__.py`
- `src/ai_extraction/extraction_contract.py`
- `src/ai_extraction/extraction_service.py`
- `src/ai_extraction/provider_interface.py`
- `src/ai_extraction/confidence_policy.py`
- `src/ai_extraction/ambiguity.py`
- `src/ai_extraction/prompt_templates.py`

- `src/intake_mapping/__init__.py`
- `src/intake_mapping/word_to_canonical.py`
- `src/intake_mapping/confirmation.py`

### New governed configuration

- `config/pve_2_0_word_fields.json`
- `config/pve_2_0_field_aliases.json`
- `config/pve_2_0_unit_rules.json`

### Persistence additions

Potential additive changes only:

- `src/persistence/word_intake_repository.py`
- additive schema migration for document metadata, extraction candidates, review actions and confirmed snapshots.

No existing immutable table may be altered destructively.

### Tests

- `tests/document_intake/`
- `tests/ai_extraction/`
- `tests/intake_mapping/`
- `tests/application/test_ai_word_intake_page.py`
- `tests/fixtures/pve_2_0_word/`

### Documentation

- `docs/pve_2_0/PVE_2.0_AI_WORD_INTAKE_ARCHITECTURE.md`
- `docs/pve_2_0/PVE_2.0_EXTRACTION_AND_MAPPING_CONTRACT.md`
- `docs/pve_2_0/PVE_2.0_EVALUATION_GOVERNANCE_AND_RISK.md`
- `docs/pve_2_0/PVE_2.0_BUILD_PLAN_AND_FILE_IMPACT.md`

### Dependency impact

Potential dependency additions, subject to owner approval in Build Group B:

- `python-docx` for deterministic DOCX structure extraction;
- one approved model SDK or an HTTP abstraction, preferably isolated behind a provider-neutral interface.

No dependency is authorized during Build Group A.

## Files that must not change without separate authorization

- existing canonical data models;
- existing validation-readiness scoring;
- threshold logic;
- scenario evaluation logic;
- technical recommendation logic;
- decision snapshot semantics;
- current synthetic portfolio demonstration records;
- frozen release documentation on `main`.

## Branch and pull-request strategy

1. Preserve `main` at the frozen baseline until separately approved work is merged.
2. Build Group A uses `planning/pve-2-ai-word-intake`.
3. Future implementation should use a new branch created from the owner-accepted Build Group A head, for example `feature/pve-2-ai-word-intake`.
4. Keep the implementation pull request in draft through all build groups.
5. Present each build group for owner review before continuing.
6. Use squash merge only after final owner approval and full CI evidence.
7. Do not tag or release automatically.

## Rollback strategy

### Planning rollback

Delete the planning branch. `main` remains unchanged.

### Implementation rollback

- close the draft PR without merge;
- delete the feature branch;
- retain frozen `main` and hosted release;
- no migration is applied to production because production deployment is out of scope.

### Post-merge rollback, if later authorized

- revert the single squash merge;
- ensure additive migrations are backward-compatible;
- keep the Word-intake page feature-gated until acceptance;
- preserve historical intake snapshots without exposing them to the current PVE workflow.

## Stop conditions

Stop and request owner decision when:

- field precision falls below the acceptance threshold;
- source grounding is unreliable;
- provider behaviour cannot be made schema-conformant;
- confidential-data controls are required beyond portfolio scope;
- implementation would require changing the existing decision engine;
- effort is forecast to exceed 66 hours;
- OCR, PDF or image interpretation becomes necessary.
