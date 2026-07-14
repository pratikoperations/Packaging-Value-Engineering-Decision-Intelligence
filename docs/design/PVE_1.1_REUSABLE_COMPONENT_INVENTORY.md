# PVE 1.1 Reusable Component Inventory

## Purpose
Record the existing PVE 1.0 components that PVE 1.1 will retain and extend rather than rebuild.

## Application and UI
- `app.py`: existing portfolio demonstration entry point and governance disclaimers.
- `pages/01_Project_Dashboard.py`: project creation, active-workspace selection, metadata duplication, archive workflow, active/archived views, and portfolio metrics.
- `pages/02_Upload_Validate.py`: guided active-project upload pattern and validation issue presentation.
- Existing decision-history and scenario pages: preserve read-only history and controlled scenario execution patterns.

## Application Services
- `src/application/project_service.py`: project lifecycle validation and repository boundary.
- `src/application/runtime.py`: initialized service factories over one SQLite database.
- Existing upload, threshold, scenario, and decision-snapshot services: preserve service/repository separation and archived-project controls.

## Persistence
- `src/persistence/database.py`: transaction and connection boundary.
- `src/persistence/migrations.py`: current schema initialization and immutability triggers; must be upgraded to ordered additive migrations for PVE 1.1.
- `src/persistence/project_repository.py`: project CRUD, archive, portfolio summary, and dashboard queries.
- `src/persistence/dataset_repository.py`: immutable project dataset versions and duplicate-content protection.
- `src/persistence/scenario_repository.py`: immutable scenario records and project-scoped references.
- `src/persistence/threshold_repository.py`: immutable threshold profiles.
- `src/persistence/decision_repository.py`: immutable decision snapshots and project-scoped history.
- `src/persistence/export_repository.py`: traceable export records.

## Upload and Validation
- `src/uploads/service.py`: prepare-then-validate-then-save workflow.
- `src/uploads/normalizer.py`: canonical dataset normalization pattern.
- `src/uploads/validation.py`: field-level issues, project/category/currency matching, baseline/proposal controls, unit validation, evidence validation, and unsafe recommendation prevention.
- `src/uploads/models.py`: prepared-upload and validation-result patterns.
- Existing JSON/CSV parsers and templates remain supported for backward compatibility while Excel is added.

## Analytical and Decision Components
- Existing deterministic cost and material engines: reuse common annual cost, unit savings, annual savings, and material calculations.
- Existing scenario architecture: preserve immutable dataset/threshold references and bounded assumptions.
- Existing technical-qualification and risk engines: continue to govern corrugated PVE 1.0 decisions; PVE 1.1 readiness must not imitate full all-category engineering feasibility.
- Existing recommendation and decision-snapshot controls: preserve insufficient-data blocking, critical-risk blocking, baseline exclusion, human approval, engineering validation, and autonomous-approval prohibition.

## Reporting
- `src/exports/decision_package.py`: deterministic JSON and Markdown export pattern.
- Existing export metadata and source-commit traceability.
- Existing decision history must remain readable and immutable.

## Tests and CI
- `.github/workflows/foundation-ci.yml`: complete repository validation entry point.
- Existing persistence, upload, scenario, threshold, decision, export, release, and Streamlit static tests.
- Baseline requirement: all previously passing 179 tests remain passing throughout PVE 1.1.

## Reuse Rules
1. No SQL inside Streamlit pages.
2. No category-specific rules inside UI files.
3. Existing immutable records are never rewritten.
4. Existing JSON and CSV upload routes remain valid unless an explicit deprecation release is approved.
5. New Excel normalization must converge on the canonical dataset model wherever possible.
6. Readiness indicates input and evidence preparedness, not engineering approval.
