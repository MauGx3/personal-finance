# Leapcell deployment — checklist and notes

This document captures the exact steps and verification items required to deploy
the Personal Finance Django app on Leapcell. It complements `deploy/leapcell/stack.env.example`.

## Pre-reqs

- A Leapcell project connected to this repository.
- Secrets configured in Leapcell for `DJANGO_SECRET_KEY`, `DATABASE_URL`, and any cloud storage creds.

## Build & Run

1. Set the repository and branch (recommended: `leapcell/deploy`) in Leapcell.
2. Configure build command: `pip install -r requirements.txt` (or use `pip install .` with wheels)
3. Configure the startup command (we recommend the image CMD to handle ${PORT}):

   `gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 4 --worker-class uvicorn.workers.UvicornWorker config.asgi:application`

## Environment variables (minimum)

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DJANGO_SECRET_KEY` (secret)
- `DATABASE_URL` (secret)
- `PORT` (optional — Leapcell supplies this)
- `REDIS_URL` (optional)
- `S3_ACCESS_KEY` / `S3_SECRET_KEY` etc (if using object storage)

## Health check

- Leapcell probes `/kaithhealth` by default. This app exposes `/kaithhealth` as an alias for `/health/` in `config/urls.py`.
- Ensure the Docker image's HTTP server responds to `GET /kaithhealth` quickly (code already queries DB; consider making this a lightweight check if DB slowness is acceptable).

## Database migrations

- Run `python manage.py migrate --noinput` as a one-off task after deploying a new release.
- Optionally enable automatic migrations by setting `RUN_MIGRATIONS_ON_START=1` but be cautious with production migrations.

## Static files

- For production, prefer S3/MinIO via `django-storages`. If using `collectstatic` in the image, set `AWS_*` env vars.

## Security

- Do not expose database ports to the public network.
- Keep `DEBUG=False` and set `ALLOWED_HOSTS` appropriately.

## Checklist before creating a Leapcell release

- [ ] Image builds locally with `docker build -t pf:test .`
- [ ] `curl http://localhost:8000/kaithhealth` returns 200
- [ ] `DJANGO_SETTINGS_MODULE` points to production settings
- [ ] Secrets stored in Leapcell
- [ ] One-off migration ran successfully
- [ ] Static/media configured
