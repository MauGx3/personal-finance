Leapcell deploy PR template
===========================

Minimal placeholder for Leapcell branch-based deploys. Add details as needed in follow-up PRs.
Leapcell deploy: env example and healthcheck alias
===============================================

Purpose
-------

Provide minimal artifacts and guidance to make branch-based deployments to Leapcell straightforward. Changes are limited to deploy-time helpers (env example and docs) and an optional health-check alias; they do not alter core runtime behavior.

Summary of changes
------------------

- deploy/leapcell/stack.env.example — environment template (no secrets).
- deploy/leapcell/README_LEAPCELL.md — deploy notes and migration checklist.
- Optional healthcheck alias: /kaithhealth (add in config/urls.py if needed).

Deployment checklist
--------------------

1. Add secrets in the Leapcell environment UI (do not commit secrets in the repo):

   - DJANGO_SECRET_KEY
   - DATABASE_URL

2. (Optional) Run a staging deploy from this branch to verify build and startup.

3. Verify the health probe: HTTP GET /kaithhealth -> 200

Quick verification (local)
--------------------------

Install dependencies and run the app locally. Example (fish shell):

    set -x DJANGO_SETTINGS_MODULE config.settings.production
    set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
    python -m django check

Files touched
-------------

- config/urls.py (optional)
- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md

Security notes
--------------

- Never commit secrets. Use the environment/secret manager for deploy targets.

Optional follow-ups
-------------------

- Add a deploy hook to run migrations during deploy
- Add a lightweight GitHub Action that runs `python -m django check` on PRs

Please review and merge when ready.
Leapcell deploy: env example and healthcheck alias
=================================================

Purpose
-------

Provide minimal artifacts and guidance to make branch-based deployments to Leapcell straightforward. Changes are limited to deploy-time helpers (env example and docs) and a health-check alias; they do not alter core runtime behavior.

Summary of changes
------------------

- deploy/leapcell/stack.env.example — environment template (no secrets).
- deploy/leapcell/README_LEAPCELL.md — deploy notes and migration checklist.
- Small healthcheck alias (/kaithhealth) in config/urls.py (if required).

Deployment checklist
--------------------

1. Add secrets in the Leapcell environment UI (do not commit secrets in the repo):

   - DJANGO_SECRET_KEY
   - DATABASE_URL

2. (Optional) Run a staging deploy from this branch to verify build and startup.

3. Verify the health probe: HTTP GET /kaithhealth -> 200

Quick verification (local)
--------------------------

Install dependencies and run the app locally. Example (fish shell):

  set -x DJANGO_SETTINGS_MODULE config.settings.production
  set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
  python -m django check

Files touched
-------------

- config/urls.py
- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md

Security notes
--------------

- Never commit secrets. Use the environment/secret manager for deploy targets.

If you want extra automation I can add a deploy hook script or a lightweight PR check that runs `python -m django check`.

Please review and merge when ready.
---

If you want additional automation, I can:

- add a deploy hook script to run migrations during deploy
- add a lightweight PR check that runs `python -m django check`

Please review and merge when ready.
---
title: chore(deploy): add Leapcell deploy env example and healthcheck alias
---

## Purpose

Provide minimal artifacts and runtime guidance to make branch-based deployments to Leapcell straightforward. The changes are limited to deploy-time helpers (env example and docs) and a health-check alias used by Leapcell; they do not alter core runtime behavior.

## Summary of changes

- Add `deploy/leapcell/stack.env.example` — an environment template (no secrets included).
- Add `deploy/leapcell/README_LEAPCELL.md` — deploy notes, required env vars, and migration checklist.
- Ensure the application exposes a Leapcell-friendly health endpoint (alias `/kaithhealth`) via `config/urls.py`.

## Deployment checklist (before merging)

1. Add secrets in the Leapcell environment UI (do not commit secrets in the repo):

  ---
  title: chore(deploy): add Leapcell deploy env example and healthcheck alias
  ---

  ## Purpose

  Provide minimal artifacts and runtime guidance to make branch-based deployments to Leapcell straightforward. The changes are limited to deploy-time helpers (env example and docs) and a health-check alias used by Leapcell; they do not alter core runtime behavior.

  ## Summary of changes

  - Add `deploy/leapcell/stack.env.example` — an environment template (no secrets included).
  - Add `deploy/leapcell/README_LEAPCELL.md` — deploy notes, required env vars, and migration checklist.
  - Ensure the application exposes a Leapcell-friendly health endpoint (alias `/kaithhealth`) via `config/urls.py`.

  ## Deployment checklist (before merging)

  1. Add secrets in the Leapcell environment UI (do not commit secrets in the repo):

    - `DJANGO_SECRET_KEY`
    - `DATABASE_URL`

  2. (Optional) Run a staging deploy from this branch to verify the build and startup.

  3. Verify the health probe (Leapcell default):

    - HTTP GET /kaithhealth -> 200

  4. (Optional) Add reviewers or CI checks if you want extra gatekeeping.

  ## Quick verification (local)

  1. Install dependencies and run the app locally.
  2. Run migrations: `python manage.py migrate --noinput`.
  3. Confirm: `curl -fsS http://localhost:8000/kaithhealth` returns success.

  ## Files touched by this PR

  - `config/urls.py` — healthcheck alias (if present).
  - `deploy/leapcell/stack.env.example` — environment template (example values only).
  - `deploy/leapcell/README_LEAPCELL.md` — deploy notes and checklist.

  ## Security notes

  - Never commit secrets. Use the host's/Leapcell's secrets management or GitHub Secrets.

  ---

  If you want additional automation, I can:

  - add a deploy hook script to run migrations during deploy
  - add a lightweight PR check that runs `python -m django check`

  Please review and merge when ready.
  (`/kaithhealth`) succeeds for Leapcell.

Why

---

Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed

---

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---

1. Locally (fast smoke):

   ```fish
   set -x DJANGO_SETTINGS_MODULE config.settings.production
   set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
   python -m django check
   ```

2. On Leapcell (recommended flow):

   - Configure the service to build from branch `leapcell/deploy`.
   - Add env vars from `deploy/leapcell/stack.env.example` (do not paste
     secrets in the repo).
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind :$PORT config.wsgi`
   - After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the
   app responds using the existing health check implementation.

Checklist before merging

---

- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes

---

- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

If you want me to also:

- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.

---

Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed

---

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---

1. Locally (fast smoke):

```fish
set -x DJANGO_SETTINGS_MODULE config.settings.production
set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
python -m django check
```

2. On Leapcell (recommended flow):

- Configure the service to build from branch `leapcell/deploy`.
- Add env vars from `deploy/leapcell/stack.env.example` (do not paste
  secrets in the repo).
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind :$PORT config.wsgi`
- After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the
   app responds using the existing health check implementation.

Checklist before merging

---

- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes

---

- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

If you want me to also:

- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.

---

Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed

---

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---

1. Locally (fast smoke):

   ```fish
   set -x DJANGO_SETTINGS_MODULE config.settings.production
   set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
   python -m django check
   ```

2. On Leapcell (recommended flow):

   - Configure the service to build from branch `leapcell/deploy`.
   - Add env vars from `deploy/leapcell/stack.env.example` (do not paste
     secrets in the repo).
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind :$PORT config.wsgi`
   - After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the
   app responds using the existing health check implementation.

Checklist before merging

---

- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes

---

- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

If you want me to also:

- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.
Title: chore(deploy): add Leapcell deploy env example and healthcheck alias

Summary
This PR adds minimal artifacts and a small runtime tweak to make deploying
this repository to Leapcell straightforward from a dedicated branch
(`leapcell/deploy`). It does not change runtime behavior beyond exposing a
health-check alias used by Leapcell.

Changes

- Added `deploy/leapcell/stack.env.example` to provide example environment
  variables for Leapcell deployments (no secrets included).
- Added `deploy/leapcell/README_LEAPCELL.md` with required environment
  variables, healthcheck, and migration notes.
- Updated `config/urls.py` to ensure the health check probe path
  (`/kaithhealth`) succeeds for Leapcell.

Why

---

Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed

-------------

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---------------------------

1. Locally (fast smoke):

  ```fish
  set -x DJANGO_SETTINGS_MODULE config.settings.production
  set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
  python -m django check
  ```

2. On Leapcell (recommended flow):
  - Configure the service to build from branch `leapcell/deploy`.
  - Add env vars from `deploy/leapcell/stack.env.example` (do not paste
    secrets in the repo).
  - Build command: `pip install -r requirements.txt`
  - Start command: `gunicorn --bind :$PORT config.wsgi`
  - After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the
   app responds using the existing health check implementation.

Checklist before merging

------------------------

- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes

--------------

- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

If you want me to also:

- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.
Title: chore(deploy): add Leapcell deploy env example and healthcheck alias

Summary
This PR adds minimal artifacts and a small runtime tweak to make deploying
this repository to Leapcell straightforward from a dedicated branch
(`leapcell/deploy`). It does not change runtime behavior beyond exposing a
health-check alias used by Leapcell.

Changes

- Added `deploy/leapcell/stack.env.example` to provide example environment variables for Leapcell deployments (no secrets included).
- Added `deploy/leapcell/README_LEAPCELL.md` with required environment variables, healthcheck, and migration notes.
- Updated `config/urls.py` to ensure the health check probe path (`/kaithhealth`) succeeds for Leapcell.


Why

---

Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed

-------------

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---------------------------

1. Locally (fast smoke):

  ```fish
  set -x DJANGO_SETTINGS_MODULE config.settings.production
  set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
  python -m django check
  ```

2. On Leapcell (recommended flow):
  - Configure the service to build from branch `leapcell/deploy`.
  - Add env vars from `deploy/leapcell/stack.env.example` (do not paste
    secrets in the repo).
  - Build command: `pip install -r requirements.txt`
  - Start command: `gunicorn --bind :$PORT config.wsgi`
  - After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the app responds using the existing health check implementation.

Checklist before merging

------------------------

- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes
--------------

- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements to keep the
  runtime image minimal.

If you want me to also:

- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.
Why
---
Leapcell clones a branch and runs a build + start process. By providing a
branch with a clear minimal deploy guide and an env template we make it easy
to point Leapcell at the repo and deploy without touching `main`.

Files changed
-------------
- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps
---------------------------
1. Locally (fast smoke):

   ```fish
   set -x DJANGO_SETTINGS_MODULE config.settings.production
   set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
   python -m django check
   ```

2. On Leapcell (recommended flow):
   - Configure the service to build from branch `leapcell/deploy`.
   - Add env vars from `deploy/leapcell/stack.env.example` (do not paste
     secrets in the repo).
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind :$PORT config.wsgi`
   - After build, run one-off: `python manage.py migrate --noinput`

3. Validate the health check: Leapcell probes `/kaithhealth` by default; the
   app responds using the existing health check implementation.

Checklist before merging
------------------------
- [ ] Confirm `DJANGO_SECRET_KEY` is set in Leapcell secrets (not committed here)
- [ ] Confirm `DATABASE_URL` is set and reachable from Leapcell
- [ ] Optionally run a staging deploy from this branch to verify builds
- [ ] (Optional) Add reviewers or CI checks if you want extra gatekeeping

Security notes
--------------
- Do not commit real secrets. Use Leapcell's environment/secret UI.
- Keep dev-only dependencies out of production requirements.

If you want me to also:
- add a small GitHub Action that runs `python -m django check` on PRs
- create a script that runs migrations automatically as a deploy hook

Please review and merge when ready.
