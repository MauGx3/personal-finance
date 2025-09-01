# Devcontainer for personal-finance

How to use

- Open this folder in VS Code
- When prompted, reopen in container
- The container will provide a running PostgreSQL service at `localhost:5432` (mapped to host). The dev container will also set `DATABASE_URL` to point to the DB service.

Notes

- The `postStartCommand` will install dependencies and initialize the database. If you need to re-run database initialization, run:

```bash
python setup_database.py
```
