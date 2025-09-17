Render deployment notes

1) Connect repository to Render
   - Go to https://render.com and create a new Web Service.
   - Connect your GitHub/GitLab repo and select the `main` branch.

2) Build & start commands
   - Render will read `render.yaml` automatically. The manifest uses:
     buildCommand: pip install -r requirements.txt
     startCommand: uvicorn personal_finance.web_gui:app --host 0.0.0.0 --port $PORT
   - A `Procfile` is included as a fallback for other platforms.

3) Environment variables / secrets
   - In the Render dashboard for the service, add the env var `DATABASE_URL` (set to your PostgreSQL connection string, e.g. `postgresql://user:pass@hostname:5432/dbname`).
   - Do NOT put DB credentials in the repository.

4) Local testing
   - Install deps: `pip install -r requirements.txt`
   - Run app locally (point to local DB or SQLite for dev):

     PYTHONPATH=src uvicorn personal_finance.web_gui:app --reload

   - If you want to test with sqlite locally, edit `src/personal_finance/web_gui.py` to instantiate `GUIService(database_url='sqlite:///./test.db')` instead of the default.

5) Notes & next steps
   - The project enforces PostgreSQL in production code paths; local sqlite is supported via explicit `database_url` to `GUIService` for development only.
   - If you want automated database migrations on deploy, we can add a small `start` wrapper script that runs Alembic migrations before starting uvicorn (recommended). I can add that next.
