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

---

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing and verification

---

Locally (fast smoke):

```fish
set -x DJANGO_SETTINGS_MODULE config.settings.production
set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
python -m django check
```

Leapcell (recommended flow):

- Configure the service to build from branch `leapcell/deploy`.
- Add env vars from `deploy/leapcell/stack.env.example` (do not paste
  secrets in the repo).
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind :$PORT config.wsgi`
- After build, run one-off: `python manage.py migrate --noinput`

Health check

Leapcell probes `/kaithhealth` by default; the app responds using the
existing health check implementation.

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

---

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md
- config/urls.py

Testing / verification steps

---

### Locally (fast smoke)

```fish
set -x DJANGO_SETTINGS_MODULE config.settings.production
set -x DATABASE_URL 'postgres://USER:PASS@HOST:PORT/NAME?sslmode=require'
python -m django check
```

### On Leapcell (recommended flow)

- Configure the service to build from branch `leapcell/deploy`.
- Add env vars from `deploy/leapcell/stack.env.example` (do not paste
  secrets in the repo).
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind :$PORT config.wsgi`
- After build, run one-off: `python manage.py migrate --noinput`

### Validate the health check

Leapcell probes `/kaithhealth` by default; the app responds using the
existing health check implementation.

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
