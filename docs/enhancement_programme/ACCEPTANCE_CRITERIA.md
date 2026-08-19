# Controlled Enhancement Acceptance Criteria

## Baseline preservation

- frozen source SHA remains `2954c293ca09882cadd7f23b5862f50334170a11`;
- `main` remains unchanged;
- original frozen showcase branch is not moved;
- PR #79 closes without merge after planning acceptance;
- existing 746-test regression baseline remains passing;
- primary business-engine outputs do not change without separate authorization.

## Browser acceptance

- 13 of 13 pages accessible;
- direct navigation and four sidebar groups verified;
- five-minute route completes;
- synthetic disclosure and Capabilities & Limits visible;
- Markdown export decodes, contains required headings and synthetic limitations;
- JSON export parses, contains required keys and synthetic limitations;
- desktop and Android-sized viewport tests pass;
- zero unexplained `pageerror`, console-error or relevant failed-request events;
- three consecutive clean CI runs at the same exact SHA, without retry-dependent passes;
- CI retains exact SHA, browser version, startup log, result summary and artifact digest.

## Synthetic-data acceptance

- every dataset and record explicitly declares or inherits synthetic status;
- no real supplier identity or implied current market rate;
- three complete positive scenarios;
- at least eight invalid or contradictory cases;
- manifests contain dataset/schema versions, generation method, provenance, currency basis, period and counts;
- zero duplicate IDs or orphaned references;
- deterministic fixture regeneration passes;
- accidental real-company-name and identifiable-data checks pass;
- schemas, disclosures and export-preservation tests pass.

## Calculation Evidence acceptance

- static and dependency-boundary checks prove no prohibited primary-engine reuse;
- formula registry is versioned;
- decimal arithmetic, precision, rounding stage/mode and tolerance type are explicit;
- zero, negative and unsupported currency cases are tested;
- independent fixtures are separately owned;
- every core calculation demonstrates `MATCH` and `FAIL`;
- selected representative calculations demonstrate `WARNING`;
- unsupported calculations demonstrate `NOT SUPPORTED`;
- deliberate mismatches and mutation tests are detected;
- primary and independent results, absolute/percentage variance and tolerance are visible;
- no engineering, commercial or realized-savings validation claim is made.

## Programme acceptance

- actual planning and feature effort are separately recorded and combined actual effort does not exceed 100 hours;
- all cumulative forecast gates are met or immediate scope reduction is documented;
- complete existing regression and all new feature-specific tests pass;
- hosted desktop and Android-sized final smoke acceptance passes;
- exact final SHA and artifacts are recorded;
- original frozen branch and evidence history remain retained;
- enhanced version is published through a separate accepted branch;
- production readiness is not claimed.

## Final browser-acceptance supersession record — 2026-08-19

The browser-acceptance bullets above are preserved as the original programme-planning contract. They are historical planning evidence and are not deleted or rewritten.

A later governed decision replaced the failed Gate 3 / Gate 3A implementation path with Gate 3B — Governed Responsive Final Closure. The final accepted browser contract therefore uses the exact Gate 3B Stage 3 candidate `993c8e8820f8f25495ea54f0e3322cd6c15c6462` and one frozen-SHA physical Chromium acceptance run with zero automatic retries, exact-SHA verification, deterministic evidence capture, desktop grouped-navigation coverage, and the governed `412 × 915` responsive route contract.

Accepted final browser evidence:

- Gate 3B feature PR: #93;
- exact Stage 3 candidate: `993c8e8820f8f25495ea54f0e3322cd6c15c6462`;
- exact-head standard CI: run `32267843278`, job `96116618326`, 4 focused Build 8 tests plus 852 complete-suite tests, 0 failures, 0 errors;
- physical Chromium workflow: `Gate 3B Governed Responsive Browser Acceptance`;
- physical run: `32285939960`, job `96175362745`, conclusion `success`;
- focused browser contracts: 42 passed;
- narrow viewport: `412 × 915`;
- 13 of 13 unique routes verified;
- physical responsive route navigation passed;
- narrow Calculation Evidence verification passed;
- governed JSON and Markdown export validation passed;
- page errors: 0;
- material console errors: 0;
- visible exceptions: 0;
- tracked-file cleanliness: passed;
- acceptance disposition: `PASS`;
- retained browser evidence artifact: `9377636828`, SHA-256 `fdbe38dffa73f941a0b8c9dfae59c0a512c9296b75224275531fa56e8bd6e59c`.

This supersession does not claim three-run repeatability, cross-browser certification, performance/load certification, accessibility certification, production certification, or enterprise production readiness. PR #85 and PR #82 are retained only as superseded historical implementation attempts.

## Stop rule

Failure of any mandatory measurable criterion blocks acceptance unless a documented scope reduction is separately authorized and does not remove a non-reducible control.
