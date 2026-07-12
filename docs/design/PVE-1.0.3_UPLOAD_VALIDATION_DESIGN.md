# PVE-1.0.3 Upload and Validation Design

## Objective
Add controlled user-data ingestion for the active corrugated packaging project while preserving deterministic logic, evidence requirements, immutable history, and non-production boundaries.

## Supported Inputs

### Canonical JSON
- One UTF-8 JSON object
- Maximum size: 2 MB
- Full canonical structure supported
- Normalized to `dataset_type = user_upload`

### Limited CSV Templates
Exactly two UTF-8 files:
- `project.csv`
- `alternatives.csv`

No arbitrary CSV mapping, Excel parsing, PDF extraction, OCR, or unstructured document interpretation is included.

## Workflow

```text
Active Project
    ↓
Download Template
    ↓
Upload JSON or Two CSV Templates
    ↓
Parse Safely
    ↓
Normalize Canonical Structure
    ↓
Apply User-Upload Validation Profile
    ↓
Display Field-Level Issues
    ↓
Save Only When Valid
    ↓
Create Immutable Dataset Version
```

## Project Binding
The active SQLite project is authoritative for the project identifier. Uploaded category and currency must match the active project. Archived projects cannot receive new uploads.

## Validation Principles
- Exactly one baseline alternative
- At least one proposed alternative
- Positive dimensions and weights
- Supported board grades and currencies
- Valid cross-record references
- Evidence required for assessed technical qualification
- Uploaded recommendations cannot pre-approve a packaging decision
- Draft integration-contract marker remains mandatory
- Incomplete technical evidence can remain structurally valid but is flagged as eligible for an `insufficient_data` outcome

## Persistence Rules
- Only valid canonical datasets are stored
- Invalid uploads are previewed but not persisted
- Duplicate canonical content is detected per project before insertion
- Duplicate content across JSON and CSV is treated as the same dataset
- Saved versions remain immutable under the PVE-1.0.1 database controls

## Templates
Templates are generated dynamically from the active project:
- JSON template
- `project.csv`
- `alternatives.csv`

## Scope Exclusions
- Configurable thresholds
- Scenario execution
- Decision history interface
- Authentication
- External database
- PDF or Excel extraction
- ERP or supplier integration
- AI approval
- New packaging category
