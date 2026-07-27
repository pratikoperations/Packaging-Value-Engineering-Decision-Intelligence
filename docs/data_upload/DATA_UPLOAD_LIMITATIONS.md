# Data Upload — Limitations and Claim Boundaries

## Supported controlled workflows

- XLSX, JSON and governed two-file CSV structured project-data intake.
- DOCX and searchable-PDF specification intake.
- PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF comparison pairs.
- Exactly one Existing and one Proposed specification.
- Deterministic extraction against the governed 25-field registry.
- Human review and confirmed-only canonical mapping.
- Append-only unified specification snapshots.

## Rejected or unsupported inputs

- unsupported extensions or signature mismatches;
- malformed DOCX or PDF files;
- encrypted PDFs;
- scanned or image-only PDFs;
- documents without sufficient searchable text;
- duplicate specification content;
- missing, duplicated or invalid document roles;
- mixed structured and specification processing in one execution;
- more or fewer than two specification documents.

## Interpretation limits

The system does not perform:

- OCR;
- engineering-drawing interpretation;
- chart, diagram or embedded-image interpretation;
- general semantic extraction from arbitrary prose;
- live large-language-model calls;
- autonomous unit inference beyond controlled deterministic rules;
- autonomous engineering approval;
- autonomous procurement award or supplier commitment.

## Canonical-data boundary

A document-derived canonical draft can remain invalid or insufficient. Specification intake normally does not establish complete cost, logistics, qualification, risk, sustainability or approval evidence.

An immutable snapshot records what was uploaded, extracted, reviewed and validated at that point. It is not evidence that the packaging design is technically qualified or commercially approved.

## Data and security boundary

Use synthetic or sanitized content only. The portfolio demonstration is not approved for confidential pricing, supplier, customer, employee, production or regulated information.

## Runtime and scale boundary

Automated tests verify deterministic repository behaviour. They do not establish:

- production-scale throughput;
- concurrent-user performance;
- hosted persistence durability;
- disaster recovery;
- cybersecurity certification;
- ERP, PLM or supplier-platform integration resilience.

## Business-impact boundary

The application demonstrates workflow and governance capability. It does not prove realized savings, supplier-performance improvement, cycle-time reduction or return on investment without independently verified implementation evidence.
