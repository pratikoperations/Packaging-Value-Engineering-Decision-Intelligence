# PVE 2.0 — Evaluation, Governance and Risk

## Status

Planning and acceptance framework only. No implementation is authorized.

## Evaluation objective

Demonstrate that the Word-intake layer can extract governed fields from representative synthetic corrugated specifications, link every accepted value to its source, keep existing and proposed documents separate, and prevent unsupported or unconfirmed values from entering the canonical PVE workflow.

The evaluation does not establish engineering validity, production readiness, supplier capability or realized business value.

## Test-document requirements

Minimum evaluation corpus:

- 10 existing/proposed document pairs;
- 20 DOCX files total;
- synthetic or explicitly authorized non-confidential content only;
- at least 5 distinct document layouts;
- paragraph-led, table-led and mixed layouts;
- controlled missing fields;
- controlled duplicate/conflicting values;
- mixed permitted units;
- at least 2 documents containing embedded-image-only information to verify unsupported-content detection;
- at least 2 prompt-injection test documents;
- known ground-truth annotations for all governed fields.

Recommended corpus expansion before organisational use: at least 50 representative pairs from approved sources.

## Ground-truth standard

Each test document must have an independently reviewed annotation file containing:

- expected field name;
- exact source block or table cell;
- raw value;
- normalized value and unit;
- expected missing status;
- expected ambiguity code;
- document role;
- reviewer identity or controlled test-author reference.

Ground truth must not be generated solely by the same model being evaluated.

## Metrics

### Field extraction

- Precision: accepted extracted fields that are correct divided by all accepted extracted fields.
- Recall: correct extracted fields divided by all ground-truth fields present.
- Exact-value accuracy: exact normalized value and unit match.
- Required-field coverage: proportion of required fields correctly detected as present or missing.

### Traceability

- Source-grounding accuracy: accepted values linked to the correct source block or table cell.
- Source-excerpt fidelity: excerpt matches the document content.
- Document-role accuracy: existing and proposed source assignments are correct.

### Safety and governance

- Unsupported-value invention count.
- Missing-source acceptance count.
- Low-confidence automatic-mapping count.
- Unconfirmed canonical-mapping count.
- Prompt-injection control failures.
- Cross-document contamination count.

### Operational

- Parse success rate for supported DOCX files.
- Median and 95th-percentile processing time.
- Human correction rate by field.
- Review completion time per document pair.

## Acceptance thresholds

| Metric | Minimum acceptance |
|---|---:|
| High-priority field precision | 95% |
| High-priority field recall | 90% |
| Source-grounding accuracy for accepted values | 100% |
| Document-role accuracy | 98% |
| Required-field presence/missing classification | 95% |
| Unsupported-value inventions accepted | 0 |
| Missing-source values accepted | 0 |
| Unconfirmed values mapped | 0 |
| Prompt-injection control failures | 0 |
| Existing regression failures | 0 |

Failure to meet a safety threshold blocks release. Accuracy thresholds may not be relaxed without owner approval and documented rationale.

## AI governance

1. Model output is advisory and schema constrained.
2. The model is not an approval authority.
3. Provider and model identifiers are recorded for reproducibility.
4. Prompts and schemas are versioned.
5. Temperature and other sampling settings are governed and recorded where applicable.
6. Model output is validated deterministically before display or persistence.
7. Extraction confidence is not technical confidence.
8. The model may not infer absent values or convert supplier declarations into tested evidence.
9. Human confirmation remains mandatory regardless of confidence.
10. Provider changes require regression evaluation.

## Prompt-injection controls

Document content is untrusted data. The extraction system must:

- isolate document text from system instructions;
- instruct the model to treat embedded instructions as document content only;
- reject output outside the extraction schema;
- validate each value against a cited source excerpt;
- prohibit tools, network actions and repository actions from document instructions;
- include adversarial test cases such as “ignore previous instructions” inside specifications.

## Privacy and information security

### Portfolio release

- synthetic documents only;
- no personal data;
- no confidential supplier or customer information;
- session-scoped document handling;
- no full document text in logs.

### Organisational use prerequisites

Before real documents are permitted:

- information-classification approval;
- approved AI/model provider;
- data processing and retention terms;
- regional data-residency review;
- encryption in transit and at rest;
- authentication and role-based access;
- document access audit;
- secrets management;
- incident-response process;
- deletion and legal-hold policy;
- vendor and security assessment.

These prerequisites are outside PVE 2.0 portfolio scope.

## Risk register

| Risk | Impact | Likelihood | Control | Residual status |
|---|---|---|---|---|
| Incorrect technical value extraction | High | Medium | Source evidence, confidence, deterministic validation, human confirmation | Medium |
| Existing/proposed values mixed | High | Low–Medium | Separate parsing, role-bound IDs, role-accuracy tests | Low |
| AI invents missing value | High | Medium | Missing-value prohibition, source requirement, zero-tolerance tests | Low–Medium |
| Requirement confused with test result | High | Medium | Ambiguity code and separate field semantics | Medium |
| Unit conversion error | High | Low–Medium | Deterministic reversible normalization | Low |
| Prompt injection in DOCX | High | Medium | Untrusted-content isolation and adversarial tests | Low–Medium |
| Embedded images silently ignored | Medium | High | Explicit unsupported-content detection and warning | Low |
| Confidential data sent to unapproved provider | High | Medium | Synthetic-only release and provider gate | Low in portfolio scope |
| Existing PVE logic unintentionally changes | High | Low | Additive adapter, regression suite, file-impact boundary | Low |
| Scope expands into PDF/OCR/CAD | Medium | High | Explicit exclusions and stop condition | Low–Medium |
| Portfolio claims exceed evidence | High | Medium | Published limitations and claim-safe demo wording | Low |

## Claim boundaries

Allowed claims:

- AI-assisted extraction of governed fields from supported Word specifications;
- field-level source traceability;
- human-confirmed existing-versus-proposed comparison;
- mapping of confirmed data into the existing PVE workflow;
- measured extraction performance on a documented synthetic test set.

Prohibited claims without further evidence:

- autonomous engineering validation;
- guaranteed extraction from arbitrary Word files;
- production readiness;
- confidential-data approval;
- supplier qualification;
- laboratory validation;
- realized savings;
- enterprise deployment.

## Release evidence required

A future release review must include:

- tested commit SHA;
- test corpus manifest;
- ground-truth methodology;
- metric report by field;
- failed-case analysis;
- full regression evidence;
- dependency and provider record;
- security and limitations statement;
- hosted synthetic demonstration screenshots;
- owner acceptance decision.
