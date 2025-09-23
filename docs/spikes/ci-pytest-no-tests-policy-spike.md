---
title: "CI: pytest no-tests exit-code policy spike"
category: "Technical"
status: "🔴 Not Started"
priority: "High"
timebox: "3 days"
created: 2025-09-23
updated: 2025-09-23
owner: "MauGx3"
tags: ["technical-spike", "ci", "pytest", "testing-policy"]
---

## CI: pytest no-tests exit-code policy spike

## Summary

**Spike Objective:** Decide whether the CI workflow should treat pytest exit code 5 (no tests collected) as a non-failure, and define a safe policy and remediation path.

**Why This Matters:** The repository's CI currently contains a guard that treats pytest exit code 5 as an allowed outcome. That policy affects merge gating, developer feedback, and risk of shipping untested code. Establishing a clear policy prevents silent regressions and aligns CI behavior with team expectations.

**Timebox:** 3 days

**Decision Deadline:** 2025-09-26

## Research Question(s)

**Primary Question:** Should the CI treat pytest exit code 5 (no tests collected) as success (non-failure), fail the job, or adopt a hybrid policy (e.g., warn but block merges)?

**Secondary Questions:**

- What are the common causes for pytest to exit with code 5 in this repository (misconfiguration, missing test discovery patterns, accidental deletions)?
- How often do tests run across the matrix (3.10/3.11) and is there a chance only one matrix axis reports no tests?
- Can we reliably detect an unintended 'no tests' condition vs intentional empty test runs (e.g., documentation-only changes)?
- What remediation UX should we provide to authors (annotated logs, automated test collection report, fail-fast vs informational)?

## Investigation Plan

### Research Tasks

- [ ] Review current workflow: `.github/workflows/ci.yml` and locate the pytest invocation and guard.
- [ ] Search repo for patterns that affect test discovery (pytest.ini, conftest.py, tests dir structure, tox configurations).
- [ ] Run local reproductions: execute pytest in an isolated environment with the same env vars used in CI and intentionally alter discovery to reproduce exit code 5.
- [ ] Run matrix permutations to see whether exit code 5 can be platform/version-specific.
- [ ] Evaluate mitigation options:
  - fail CI on exit code 5
  - fail CI unless a PR label or commit message marker allows empty tests
  - convert to a dedicated 'no-tests' check that posts a warning comment but doesn't block
  - require a follow-up jobs that assert at least one test was collected across the matrix
- [ ] Create a small proof-of-concept workflow change implementing the recommended approach (e.g., treat exit code 5 as failure and add allow-list or label-based bypass) and run it on a feature branch.
- [ ] Document findings, propose policy, include implementation playbook and rollout steps.

### Success Criteria

**This spike is complete when:**

- [ ] A clear, evidence-backed recommendation is documented (fail/warn/allow) for pytest exit code 5.
- [ ] Proof-of-concept workflow changes exist in a feature branch demonstrating the behavior.
- [ ] Implementation notes and follow-up tasks are created (if implementation is approved).

## Technical Context

**Related Components:**

- `.github/workflows/ci.yml` (current CI implementation)
- pytest, pytest-django configuration in repo
- test suites under `tests/` and any test helpers under `personal_finance/` or `src/`

**Dependencies:**

- Decision may affect PR gating and other CI workflows that assume tests ran.
- Any change must be compatible with the matrixed test runners and caching strategy.

**Constraints:**

- CI runtime and flakiness: we should avoid policies that greatly increase CI reruns.
- Backwards compatibility: avoid immediate hard-failure that breaks many open PRs without notice.

## Research Findings

### Investigation Results

[Add findings here after running the research tasks.]

### Prototype/Testing Notes

[Add PoC notes: commands used, branches, workflow runs and results.]

### External Resources

- pytest docs: exit codes and meaning
- GitHub Actions docs: job exit codes and workflow guards
- Community discussions on how other repos treat 'no tests collected'

## Decision

### Recommendation

[Record final recommendation here after research is complete.]

### Rationale

[Rationale details go here.]

### Implementation Notes

[Notes about how to change `.github/workflows/ci.yml`, required labels, and rollout plan.]

### Follow-up Actions

- [ ] Implement workflow change on a feature branch and run validation
- [ ] Update repository CONTRIBUTING.md and developer docs to describe the policy
- [ ] Notify maintainers and open PR to enforce the policy

## Status History

| Date | Status | Notes |
|------|--------|-------|
| 2025-09-23 | 🔴 Not Started | Spike created and scoped |

---

Last updated: 2025-09-23 by MauGx3
