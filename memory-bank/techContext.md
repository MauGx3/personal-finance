# Tech context

- Python 3.12+, Django 5.2 LTS, DRF, drf-spectacular, django-filter.
- uv (`pyproject.toml`, `uv.lock`), ruff, pytest, pytest-django.
- yfinance for prices; openpyxl for spreadsheets.
- WhiteNoise for static files, gunicorn in Docker.
- Settings: `config.settings.dev` (manage.py default), `prod` (WSGI default), `test` (pytest).
- Environment variables are listed in `.env.example`.
