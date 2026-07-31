# E1 Risk Register

## Governance Baseline

Frozen baseline SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`

## Scoring

- Probability: Low / Medium / High
- Impact: Low / Medium / High / Critical
- Owners are functional roles until individual assignment is approved.

| ID | Risk | Probability | Impact | Mitigation | Owner | Trigger / indicator |
|---|---|---|---|---|---|---|
| E1-R01 | Frozen baseline is modified or rebased accidentally | Low | Critical | Develop only on `e1-development`; verify ancestry and changed files before every merge; prohibit force updates to `main` | Governance / DevOps | Main SHA changes without an authorized merge |
| E1-R02 | E1 scope expands without explicit approval | Medium | High | Require authoritative scope, non-goals, and acceptance criteria before implementation | Product Owner / Architect | New feature work lacks traceability to approved scope |
| E1-R03 | Existing deterministic decision behaviour regresses | Medium | Critical | Preserve current regression suite; add golden-case tests and before/after output comparisons | QA / Engineering | Existing scenario outcome changes unexpectedly |
| E1-R04 | Explainability or auditability is weakened | Medium | High | Treat decision rationale, state transitions, and immutable records as release gates | Governance / Procurement SME | User cannot reconstruct why a decision was produced |
| E1-R05 | Data-role assignment or review-state logic becomes inconsistent | Medium | High | Test Existing/Proposed roles, Pending/Resolved transitions, blocked downstream states, and snapshot eligibility | QA / Packaging SME | Snapshot appears while unresolved candidates remain |
| E1-R06 | Persistence changes create incompatible or corrupt data | Low–Medium | Critical | Require explicit migration design, backup/rollback procedure, and migration tests before schema changes | Architect / DevOps | Existing records fail to load or lose traceability |
| E1-R07 | Error handling exposes tracebacks, raw JSON, exception classes, or internals | Medium | High | Add negative-path UI tests and hosted acceptance checks | UX / QA | Internal implementation details appear to users |
| E1-R08 | Mobile or tablet usability regresses | Medium | Medium | Cross-device acceptance matrix and responsive navigation checks | UX / QA | Clipped controls, inaccessible navigation, horizontal overflow |
| E1-R09 | CI coverage is insufficient for new behaviour | Medium | High | Add focused tests per slice; enforce full-suite pass and artifact capture | QA / DevOps | Feature merged without automated acceptance evidence |
| E1-R10 | Hosted deployment differs from reviewed commit | Low–Medium | Critical | Record deployed branch/SHA and perform post-deployment acceptance against exact release SHA | DevOps / Governance | Hosted version cannot be tied to the approved commit |
| E1-R11 | Procurement or packaging claims exceed evidence | Medium | High | Maintain synthetic-data disclaimers, mandatory human approval, and evidence classification | Procurement SME / Packaging SME | UI implies realized savings or engineering approval |
| E1-R12 | Performance degradation affects workflow usability | Low–Medium | Medium | Benchmark critical flows and large representative datasets before release | Engineering / QA | Noticeable increase in startup or interaction latency |
| E1-R13 | Documentation diverges from implemented behaviour | Medium | Medium | Update documentation within the same feature PR and verify at release candidate | Product Owner / QA | User guide describes unavailable or obsolete behaviour |
| E1-R14 | Parallel changes cause merge or governance conflicts | Medium | Medium | Keep feature slices small; serialize writes to shared modules; use expected-head merge protection | Architect / GitHub Reviewer | Multiple PRs modify the same protected subsystem |

## Escalation Rules

- Any Critical-impact risk with Medium or High probability blocks implementation or release until mitigated.
- Any unresolved High-impact risk requires explicit TSG acceptance before release.
- Risk acceptance must identify owner, rationale, expiry, and compensating control.
