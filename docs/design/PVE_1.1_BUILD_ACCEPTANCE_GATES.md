# PVE 1.1 Build Acceptance Gates

## Program Controls
- Hard cap: 80 hours.
- Build 1 allocation: 6 hours.
- No build starts until the previous build has recorded acceptance evidence.
- Scope additions require an equal or greater approved scope removal.
- PR #25 remains draft until final release QA.

## Build 1 — Architecture and Scope Lock (6h)
Pass only when:
- branch is synchronized with current `main`
- reusable components are documented against actual repository paths
- eight-category registry and objective/change-type mappings are validated
- additive migration plan is approved
- exact planned file impact is documented
- backward compatibility and historical snapshot protection are explicit
- full existing tests plus registry tests pass
- no Build 2 code is present

## Build 2 — Project Creation Expansion (7h)
Pass only when:
- all eight categories can create projects
- category/objective/change-type combinations are validated by registry services
- common metadata is saved through service/repository boundaries
- legacy project rows still load
- duplication preserves metadata only and does not copy evidence/history
- archived-project protections pass

## Build 3 — Category Input Definitions (14h)
Pass only when:
- every category defines mandatory/recommended/optional fields and documents
- units, types, ranges, tests, blockers, warnings, and available analyses are configuration-driven
- source classifications are fixed and distinct
- no category business logic exists in Streamlit pages

## Build 4 — Excel Template Generation (10h)
Pass only when:
- eight category templates generate with the eight approved sheets
- objective/change type influence guidance without changing schema safety
- mandatory/recommended/optional indicators, units, examples, dropdowns, source classification, evidence, dates, supplier, and status fields exist
- no macros are used

## Build 5 — Excel Upload and Normalization (10h)
Pass only when:
- workbook structure and columns are validated
- fields normalize into canonical records wherever possible
- exactly one baseline and at least one proposal are enforced
- invalid units, numbers, category mismatches, and source-status conflicts are reported
- invalid uploads are not saved
- existing JSON/CSV upload tests remain passing

## Build 6 — Readiness and Blocking Engine (9h)
Pass only when:
- weighted readiness components total 100%
- component scores and missing inputs are transparent
- blockers override percentage and stage
- output availability gives explicit reasons
- readiness never becomes automatic approval
- append-only assessment persistence and project isolation pass

## Build 7 — Commercial and ROI Extension (5h)
Pass only when:
- unit saving, gross annual saving, realized saving, first-year net saving, payback, material reduction, and percentages are correct
- divide-by-zero and missing-input cases are controlled
- estimates and assumptions are labelled
- commercial attractiveness cannot override technical blockers

## Build 8 — Streamlit UI and Reports (8h)
Pass only when:
- guided flow prevents a blank upload experience
- category guidance, upload errors, readiness, blockers, outputs, commercial opportunity, tests, and reports are accessible
- JSON and Markdown reports contain the approved 18 sections
- colour/status conventions are consistent
- no autonomous approval language appears

## Build 9 — Testing and Release QA (11h)
Pass only when:
- all existing 179 tests pass
- all new category, template, parser, readiness, commercial, archive, immutability, and historical-protection tests pass
- one sample project per category exists
- three detailed demonstration cases pass expected outcomes
- QA report and release checklist are complete
- deferred features and future 130-hour roadmap are current
- final-head CI succeeds with zero failures/errors

## Release Stop Conditions
Stop and do not merge when:
- existing tests regress
- historical snapshots or immutable datasets change
- any unsupported technical-feasibility claim is generated
- supplier-declared/predicted/assumed data is presented as laboratory-tested
- archived-project writes succeed
- a blocker can be bypassed by a high readiness score or commercial saving
- total estimated effort exceeds 80 hours without approved scope removal
