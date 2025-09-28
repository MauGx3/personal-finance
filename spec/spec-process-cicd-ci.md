---
title: CI/CD Workflow Specification - CI
version: 1.1
date_created: 2025-09-23
last_updated: 2025-09-28
owner: DevOps Team
tags: [process, cicd, github-actions, automation, python, testing, security]
---

## Workflow Overview

Purpose: Provide continuous integration for the Python/Django project: run unit tests, a focused lint step, and a security audit on pull requests and pushes.

Trigger Events:

- push (all branches)

- pull_request

Target Environments: CI runner pool (Linux/ubuntu), matrixed Python interpreters (3.10, 3.11).

## Execution Flow Diagram

```mermaid
graph TD
    A[push / pull_request] --> B[Test job (matrix: py 3.10,3.11)]
    B --> C[Security audit: pip-audit]
    style A fill:#e1f5fe
    style C fill:#e8f5e8
```

## Jobs & Dependencies

| Job Name | Purpose | Dependencies | Execution Context | Security Permissions |
|----------|---------|--------------|-------------------|---------------------|
| test | Install dependencies, run focused lint, run test suite under 2 Python versions | none (triggered directly) | ubuntu-latest, matrix python 3.10 & 3.11 | contents: read |
| security-audit | Run dependency security scan via pip-audit | needs: test | ubuntu-latest, python 3.11 | contents: read |

## Requirements Matrix

### Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|--------------------|
| REQ-001 | Run test suite on new changes | High | Tests complete successfully or report allowed no-tests condition; job exit code indicates pass |
| REQ-002 | Lint high-severity errors before merging | Medium | Lint step fails on selected severe categories (E9,F63,F7,F82) |
| REQ-003 | Perform dependency security audit | Medium | `pip-audit` runs and returns no critical findings (policy defined by team) |

### Security Requirements

| ID | Requirement | Implementation Constraint | Status |
|----|-------------|---------------------------|--------|
| SEC-001 | Limit default token permissions used by workflow | GITHUB_TOKEN scope: contents: read (minimal) | ✅ Implemented |
| SEC-002 | Scan dependencies for known vulnerabilities | Use SCA tool (pip-audit) with non-interactive mode | ✅ Implemented |

### Performance Requirements

| ID | Metric | Target | Measurement Method |
|----|--------|--------|-------------------|
| PERF-001 | CI runtime | Keep < 15 min for typical runs | Measure job run times in CI dashboard |
| PERF-002 | Cache hit rate for pip cache | Aim > 70% | Monitor cache action hits in workflow logs |

## Input/Output Contracts

### Inputs

Environment variables (used in `test` job):

```yaml
PYTHONPATH: src
DATABASE_URL: string  # in CI: sqlite:///test.db (test-only DB)
DJANGO_SETTINGS_MODULE: string  # e.g. config.settings.test
DJANGO_SECRET_KEY: string  # test secret key used only in CI
DJANGO_DEBUG: boolean
```

Repository triggers:

- paths: none (workflow triggers on all pushes and PRs)

- branches: all

### Outputs

Job outputs: none persisted as artifacts by the workflow. The workflow emits logs and exit codes only.

### Secrets & Variables

| Type | Name | Purpose | Scope | Implementation |
|------|------|---------|-------|----------------|
| Variable | DJANGO_SECRET_KEY | CI-only secret value used to bootstrap Django in tests | Workflow (repo) | ✅ Implemented |
| Token | GITHUB_TOKEN | API actions the workflow may call; limited to contents: read | Workflow | ✅ Implemented via workflow-level permissions |

## Execution Constraints

### Runtime Constraints

- Timeout: not explicitly set in the workflow; recommend per-job timeout (e.g., 30m) to avoid hung runs.

- Concurrency: no concurrency key defined; consider adding concurrency to avoid overlapping runs on branch.

- Resource Limits: uses `ubuntu-latest` hosted runners (no explicit CPU/memory constraints).

### Environmental Constraints

- Runner Requirements: Linux (ubuntu-latest) with Python 3.10/3.11 available via setup action.

- Network Access: Access to PyPI to install packages; access to pip-audit feeds as required.

- Permissions: `contents: read` for GITHUB_TOKEN; no elevated repo write permissions.

## Error Handling Strategy

| Error Type | Response | Recovery Action |
|------------|----------|-----------------|
| Lint Failure | Job fails; PR shows failure | Author fixes code and pushes new commit |
| Test Failure | Job fails; PR shows failure | Fix failing tests or adjust test expectations; re-run CI |
| No tests collected (pytest exit code 5) | Treated as acceptable by workflow (explicit shell guard) | Investigate missing tests if unexpected; consider failing the job if this should be blocked |
| Security Scan Failure | Job fails | Investigate vulnerable dependency, update or mitigate (pin/patch) |

Notes:

- The `test` job invokes pytest with a guard `pytest -q || [ $? -eq 5 ]` which treats pytest exit code 5 (no tests collected) as a non-failure condition. This is an explicit policy in the workflow and should be audited against team expectations.

## Quality Gates

### Gate Definitions

| Gate | Criteria | Bypass Conditions |
|------|----------|-------------------|
| Code Quality | Lint step passes (no E9/F63/F7/F82 findings) | Emergency fixes with explicit reviewer approval |
| Tests | Test suite exits with success (or allowed no-tests status) | Feature branches with experimental tests; require explicit reviewer approval |
| Security Scan | pip-audit finds no critical vulnerabilities | Temporary supression with compensating controls and SR approval |

## Monitoring & Observability

Key Metrics:

- Success Rate: percentage of successful runs (target: > 95%)

- Execution Time: median job duration (target: < 15 minutes)

- Cache Hit Rate: percentage of cache hits for pip cache (target: > 70%)

Alerting:

| Condition | Severity | Notification Target |
|-----------|----------|--------------------|
| Regressing test pass rate | High | #dev-alerts / team owners |
| New critical vulnerability (pip-audit) | High | #security-team |

## Integration Points

External Systems:

| System | Integration Type | Data Exchange | SLA |
|--------|------------------|---------------|-----|
| PyPI | Package registry | pip installs packages during run | Best-effort availability |
| pip-audit database(s) | SCA feed | vulnerability metadata | Regular updates required |

Dependent Workflows:

| Workflow | Relationship | Trigger Mechanism |
|----------|--------------|-------------------|
| downstream/deploy | gating | manual or repo-policy driven (not in current workflow) |

## Compliance & Governance

Audit Requirements:

- Execution logs retained by GitHub Actions (default retention policy). Review retention in repo settings if longer retention is needed.

- Changes to CI workflow should be reviewed via normal PR process.

Security Controls:

- Minimal GITHUB_TOKEN permissions (contents: read) to reduce blast radius.

- Use of pip-audit to identify known vulnerable packages.

## Edge Cases & Exceptions

| Scenario | Expected Behavior | Validation Method |
|----------|-------------------|-------------------|
| No tests collected | Workflow treats as non-failure (explicit) | Verify pytest exit handling in logs; decide policy if this should be a failure |
| PyPI outage | Dependency installation fails | Fail job; recommend cached wheels or mirror in private registry |
| Cache miss across concurrent runs | Longer install times | Monitor cache metrics; tune cache keys and retention |

## Validation Criteria

### Workflow Validation

- VLD-001: Test job runs under both python versions and exits with 0 or allowed 5 code.

- VLD-002: security-audit job runs only after test job completion and returns non-zero on findings.

### Performance Benchmarks

- PERF-001: Median test job time < 15 minutes for incremental runs.

## 7. Rationale & Context

### Security Implementation Notes

- **GITHUB_TOKEN Permissions**: Explicit permissions block added at workflow level to comply with GitHub's security best practices and address CodeQL security alerts. This limits the token scope to read-only access, reducing the blast radius of potential token compromise.
- **Dependency Scanning**: pip-audit integration provides automated vulnerability detection in CI pipeline, enabling early identification of security issues in third-party dependencies.
- **Matrix Testing**: Multi-version Python testing ensures compatibility across supported runtime versions while maintaining security patches.

## Change Management

Update Process:

1. Update this specification first.

2. Submit PR with workflow changes and reference this spec.

3. Run CI on a feature branch and verify gates.

4. Merge after approval and observe first 3 runs for regressions.

Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.1 | 2025-09-28 | Updated security requirements to reflect implemented GITHUB_TOKEN permissions and added rationale section documenting security enhancements | DevOps Team |
| 1.0 | 2025-09-23 | Initial specification extracted from `.github/workflows/ci.yml` | DevOps Team |

## Related Specifications

- /spec/spec-process-cicd-pr-django-check.md (if present) - spec for PR-level Django checks
