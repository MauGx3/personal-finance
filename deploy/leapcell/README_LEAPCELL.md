Leapcell deployment notes
=========================

This directory contains minimal artifacts to help deploy the project on Leapcell
from a dedicated branch (recommended: `leapcell/deploy`).

Files
-----

- `stack.env.example` — template for environment variables (DO NOT commit secrets).

Quick branch-based workflow
---------------------------

1. Create the branch locally and switch to it:

   git checkout -b leapcell/deploy

2. Optionally edit `deploy/leapcell/stack.env.example` to provide example placeholders.

3. Commit and push the branch to origin:

   git add deploy/leapcell
   git commit -m "chore(deploy): add leapcell deploy env example and docs"
   git push -u origin leapcell/deploy

Configuring Leapcell
--------------------

In the Leapcell service/project settings:

- Set the Git repository to your repo and the Branch to `leapcell/deploy`.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind :$PORT config.wsgi`
- Port: leave as default (`$PORT`) — Leapcell injects this env.
- Add environment variables (copy values from your secrets store):
  - `DATABASE_URL` (example form):
    `postgres://USER:PASSWORD@HOST:PORT/NAME?sslmode=require`
  - `DJANGO_SETTINGS_MODULE=config.settings.production`
  - `DJANGO_SECRET_KEY` (set to a long random secret)
  - Any other production envs (e.g. `REDIS_URL`, `SENTRY_DSN`, etc.)

Healthchecks
------------

Leapcell probes `http://0.0.0.0:$PORT/kaithhealth` by default. This repo now
exposes `GET /kaithhealth` (aliasing the existing `/health/` endpoint). No
further action should be required. If you prefer a different path, update the
service health probe in the Leapcell settings.

Database migrations
-------------------

After the image builds, run migrations (one-off command in Leapcell):

  python manage.py migrate --noinput

Secrets and safety
------------------

- Never commit real secrets. Use Leapcell's secret/env UI or a vault.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

Support
-------

If the service fails to start, check the logs in Leapcell's UI. Typical
problems: missing `DJANGO_SECRET_KEY`, incorrect `DATABASE_URL`, or the app
using `config.settings.local` instead of `config.settings.production`.
