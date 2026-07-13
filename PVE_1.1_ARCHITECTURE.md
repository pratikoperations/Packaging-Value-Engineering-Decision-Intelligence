# PVE 1.1 Architecture

## Release
PVE 1.1 — All-Category Project Intake and Validation Readiness.

## Scope Boundary
This release extends the existing Streamlit, Python, and SQLite architecture for all-category project intake, structured Excel templates and uploads, transparent readiness, common commercial analysis, category-specific testing checklists, and traceable reporting. It does not claim full technical feasibility across all categories.

## Reused Components
- Streamlit navigation and project dashboard
- project lifecycle, duplication, archiving, and active workspace
- SQLite connection and repositories
- immutable dataset, threshold, scenario, and decision records
- upload-service and validation-result patterns
- deterministic commercial/material engines
- JSON and Markdown exports
- decision history and archived-project write protection

## New Modules
- `src/category_registry/` — configuration-driven categories, objectives, and change types
- `src/intake/` — field/document requirements, readiness, and output availability
- `src/templates/` — Excel workbook generation
- `src/uploads/` — Excel parsing and normalization
- `src/commercial/` — common savings and ROI extensions
- `src/validation_readiness/` — completeness, blockers, source traceability, tests, and stage
- `src/reports/` — intake, readiness, and executive reports

## Governance
Engineering validation and human approval remain mandatory. Autonomous approval is prohibited. Supplier-declared, predicted, assumed, manually entered, uploaded, and laboratory-tested values remain distinct. Historical snapshots and dataset versions remain immutable.