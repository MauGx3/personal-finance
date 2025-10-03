# [TASK006] - Rationalize test suite coverage

**Status:** In Progress
**Added:** 2025-10-02
**Updated:** 2025-10-02

## Original Request
Review the entire test suite, retire irrelevant cases, execute the remaining tests, address any failures, and add new code/tests to close coverage gaps.

## Thought Process
- The repository contains a large collection of legacy/placeholder tests with many `.disabled` files.
- Several active tests exercise infrastructure that no longer exists (e.g., Copilot setup installers, inline math demos) or rely on outdated assumptions about the Django settings package.
- We need a streamlined, realistic suite that maps directly to maintained code paths: assets models, data profiler services/validators, dependency policy checks, and logging infrastructure.

## Implementation Plan
- Inventory every active test module and classify it as "keep", "update", or "retire" based on present code coverage.
- Remove or quarantine irrelevant tests (Copilot dependency sweeps, inline math demos, outdated Django config checks).
- Keep and, if needed, adjust legitimate coverage for assets models, logging security, dependency policies, and data profiler utilities.
- Run `pytest` on the curated suite, triage failures, and implement code fixes (including migrations) where behaviour should exist.
- Add targeted tests/code to ensure remaining critical modules (e.g., data sources) are covered.
- Update documentation and Memory Bank with the new baseline and follow-up items.

## Progress Tracking

**Overall Status:** In Progress - 75%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 6.1 | Classify active test modules (keep/update/retire) | Complete | 2025-10-02 | Tagged Copilot/Django config suites as legacy; identified core coverage targets |
| 6.2 | Prune/adjust tests and align code as needed | In Progress | 2025-10-02 | Skipped legacy Copilot + expanded calc suites, added focused metrics coverage |
| 6.3 | Run pytest, fix failures, add coverage where missing | In Progress | 2025-10-02 | New analytics metrics tests green; full pytest run passes with targeted skips |
| 6.4 | Update documentation and Memory Bank | In Progress | 2025-10-02 | Analytics module docs published; README refreshed; final docs pass pending |

## Progress Log
### 2025-10-02
- Created task plan; began auditing `tests/` directory to flag obsolete modules (Copilot setup, inline math demos, outdated Django config assertions).
- Added reusable analytics metrics module + focused test suite; marked legacy Copilot + expanded calculation suites as skipped; full `pytest` run clean aside from recorded skips.
- Documented analytics helpers in Sphinx, updated test README to reflect active vs legacy suites, and captured follow-up plan for `.disabled` files.
