# CI specification

Workflow: `.github/workflows/ci.yml`. Triggers: pushes to `main`, all pull requests.

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
