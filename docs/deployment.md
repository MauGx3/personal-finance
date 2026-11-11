# Deployment

## Docker Compose or Portainer stack

1. Copy `.env.example` to `.env` and set:
   - `DJANGO_SECRET_KEY`: a long random string.
   - `DJANGO_ALLOWED_HOSTS`: the NAS host name or IP.
2. `docker compose up -d --build` (in Portainer: create a stack from this
   repository and load the same variables).
3. Create your login once: `docker compose exec web python manage.py createsuperuser`.

The `web` container applies migrations on start. The `prices` container runs
`sync_prices` every `PRICE_SYNC_INTERVAL_SECONDS` (default six hours).

## Data and backups

Everything is in the `data` volume: `personal_finance.sqlite3`. Back it up by
copying that file while the stack is stopped, or with
`docker compose exec web python manage.py dumpdata --natural-foreign -o /data/backup.json`.

## HTTPS

On a home network the app works over plain HTTP. If a reverse proxy serves it
over HTTPS, set `HTTPS=true` and `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-host`
so cookies are marked secure.

## PostgreSQL

Set `DATABASE_URL=postgres://user:password@host:5432/dbname`. The image already
includes the driver.

## Not verified

The image and compose file were written but not built in the environment
where this was developed (the Docker daemon was not running there). The same steps (frozen install, `collectstatic`, migrate, gunicorn with the production settings) were run outside Docker and worked. Build once and report
any failure.
