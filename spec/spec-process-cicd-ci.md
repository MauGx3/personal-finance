# CI specification

Status: **deactivated**. `.github/workflows/ci.yml` was removed, so no CI jobs run on
pushes or pull requests. The steps below are kept as the reference to restore from
git history (`git show 77b32e7:.github/workflows/ci.yml`) when CI is wanted again.

When it was active, the workflow ran on pushes to `main` and all pull requests.

| Step | Command | Fails the build when |
| --- | --- | --- |
| Install | `uv sync --frozen` | `uv.lock` is out of date with `pyproject.toml` |
| Lint | `uv run ruff check .` and `uv run ruff format --check .` | any finding or unformatted file |
| Django checks | `manage.py check`, `makemigrations --check --dry-run` | configuration error or a model change without a migration |
| Tests | `uv run pytest --cov=apps` | any test fails |
| Audit | `uv run pip-audit` | a dependency has a known vulnerability |

- Matrix: Python 3.12 and 3.13.
- Permissions: `contents: read`.
- Tests need no services and no network.
- `codeql.yml` runs CodeQL separately. Dependabot updates actions, uv and Docker weekly.

Removed in the 0.2 restructure because they targeted code or platforms that no
longer exist here: Render deploy, Sphinx docs, requirements lock regeneration,
Codacy, Codecov, AquilaX, Copilot setup, and the two pytest/Django PR checks
that this workflow now covers.
