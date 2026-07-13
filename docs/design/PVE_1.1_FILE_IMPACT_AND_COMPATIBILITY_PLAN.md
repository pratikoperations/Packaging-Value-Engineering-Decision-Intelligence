# PVE 1.1 File Impact and Compatibility Plan

## Planned Existing Files to Modify

### Build 2 — Project Creation Expansion
- `pages/01_Project_Dashboard.py`
- `src/application/project_service.py`
- `src/persistence/project_repository.py`
- `src/persistence/migrations.py`
- `src/application/runtime.py`
- `tests/application/test_project_dashboard.py`
- `tests/persistence/test_foundation.py`

### Build 3 — Category Input Definitions
- `src/category_registry/models.py`
- `src/category_registry/registry.py`
- `src/category_registry/objectives.py`
- `src/category_registry/change_types.py`
- `CATEGORY_REGISTRY.md`
- category-registry tests

### Build 4 — Excel Template Generation
- `requirements.txt` only if `openpyxl` is not already declared
- `src/application/runtime.py` only for service factory wiring
- no existing upload parser is replaced

### Build 5 — Excel Upload and Normalization
- `pages/02_Upload_Validate.py`
- `src/uploads/models.py`
- `src/uploads/normalizer.py`
- `src/uploads/service.py`
- `src/uploads/validation.py`
- `src/uploads/__init__.py`
- `src/application/runtime.py`
- `tests/uploads/test_upload_validation.py`

### Build 6 — Readiness and Blocking Engine
- `src/application/runtime.py`
- persistence migration/repository files for append-only readiness records
- no existing recommendation engine is weakened or replaced

### Build 7 — Commercial and ROI Extension
- existing cost/material engine files only when reuse requires a thin compatible extension
- scenario and recommendation engines remain unchanged unless an explicitly documented adapter is required

### Build 8 — Streamlit UI and Reports
- `app.py` only for navigation/disclosure updates if necessary
- `pages/01_Project_Dashboard.py`
- `pages/02_Upload_Validate.py`
- new pages for guidance, readiness, commercial analysis, testing, and executive report
- `src/exports/decision_package.py` only through backward-compatible additive sections or a versioned PVE 1.1 exporter
- `src/application/runtime.py`

### Build 9 — Testing and Release QA
- `.github/workflows/foundation-ci.yml` only to include new tests/static gates
- `tests/README.md`
- project/version/change/build/activity/recovery governance records
- README, QA report, release checklist, and interview demo documents

## Planned New Module Paths
- `src/category_registry/categories/`
- `src/intake/`
- `src/templates/`
- `src/uploads/excel_parser.py`
- `src/commercial/`
- `src/validation_readiness/`
- `src/reports/`
- new persistence repositories for intake, documents, readiness, and checklists
- new Streamlit guidance/readiness/commercial/testing/report pages
- category, template, Excel, readiness, commercial, report, migration, and regression tests

## Backward-Compatibility Rules
1. PVE 1.0.6 decision snapshots remain byte-for-byte unchanged.
2. Existing dataset, scenario, threshold, and decision repository interfaces remain valid.
3. Existing JSON and CSV uploads remain supported.
4. Existing corrugated project records load without requiring PVE 1.1-only fields.
5. New project columns are nullable at database level for historical compatibility.
6. New PVE 1.1 creation workflow enforces mandatory intake fields at the service/UI boundary.
7. Existing category value `corrugated_shipping_case` is accepted as a legacy alias and normalized carefully without rewriting historical rows.
8. Existing exported decision packages remain readable; PVE 1.1 additions use additive/versioned sections.
9. Archived projects remain viewable and reject all new writes.
10. No readiness score can alter or imply approval of an existing decision snapshot.

## Historical Snapshot Protection Plan
- Record counts, IDs, content hashes, and canonical JSON for all historical immutable tables before migration tests.
- Apply migration in a transaction.
- Re-read and compare all protected records after migration.
- Add regression tests that direct SQL update/delete operations still fail on immutable tables.
- Add service/repository tests proving no PVE 1.1 method updates historical dataset, scenario, threshold, or decision rows.
- Keep readiness assessments and checklists separate from decision snapshots.

## Scope-Leakage Controls
The following fail Build 1 review if introduced:
- OCR, PDF/Word/image extraction, AI document interpretation
- authentication, RBAC, cloud database, ERP, email, supplier portal
- Power BI implementation
- supplier ranking, allocation, or negotiation
- machine learning or live pricing
- advanced category engineering prediction
- automatic approval or language implying tested/verified status without matching source classification

Any new request must replace approved scope within the same 80-hour cap and be recorded in the decision log before coding.
