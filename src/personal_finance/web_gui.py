"""Minimal FastAPI web GUI exposing CRUD endpoints for the finance DB.

Run with (from repo root):

PYTHONPATH=src uvicorn personal_finance.web_gui:app --reload

Ensure DATABASE_URL is exported for PostgreSQL in production. For local testing
you can pass a sqlite URL by instantiating GUIService(database_url=...) in code.
"""
from typing import List, Optional
import os
from urllib.parse import urlparse
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response, JSONResponse
from pydantic import BaseModel

from .gui_service import GUIService

@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Lifespan context to run startup-like actions without deprecated on_event.

    This replaces the deprecated @app.on_event("startup") usage and runs
    migrations/connectivity checks during app startup.
    """
    # If a module-global `service` was created at import time (for tests), reuse it.
    svc = globals().get('service')
    if svc is None:
        svc = GUIService()  # uses env DATABASE_URL by default
        # Update the module-global reference as well for backwards compatibility
        globals()['service'] = svc

    # Attach service to app state so route handlers can access it
    app.state.service = svc

    db_host = _extract_db_host(getattr(service.db, 'database_url', None))
    if os.getenv("RUN_MIGRATIONS_IN_APP_WORKER") == "1":
        try:
            service.db.run_migrations()
            print(f"[startup] Alembic migrations applied (host={db_host})")
        except Exception as exc:  # pragma: no cover - runtime
            print(f"[startup][warning] Migration failed: {exc}")
    try:
        if service.db.ping():
            print(f"[startup] DB connectivity OK (host={db_host})")
        else:
            print(f"[startup][warning] DB ping failed (host={db_host})")
    except Exception as exc:
        print(f"[startup][warning] DB connectivity failed (host={db_host}) -> {exc}")

    try:
        yield
    finally:
        # Optional cleanup for service/db clients
        try:
            svc = getattr(app.state, 'service', None)
            if svc and getattr(svc.db, '_mongo_client', None):
                svc.db._mongo_client.close()
        except Exception:
            pass


app = FastAPI(title="Personal Finance GUI", lifespan=_lifespan)
# Backwards-compatible reference used by tests and other modules.
# Create a module-global service at import time when DATABASE_URL is set so
# tests that import this module can access web_gui.service immediately.
service = None
if os.getenv("DATABASE_URL"):
    try:
        service = GUIService()
    except Exception:
        # Defer failures to runtime checks; keep import-time robust for tests.
        service = None


def _extract_db_host(dsn: Optional[str]) -> Optional[str]:
    if not dsn:
        return None
    try:
        parsed = urlparse(dsn)
        return parsed.hostname
    except Exception:  # pragma: no cover - defensive
        return None


# Lifespan handler above performs startup checks and attaches service to app.state


class TickerIn(BaseModel):
    symbol: str
    name: str
    price: Optional[float] = None


class PositionIn(BaseModel):
    symbol: str
    name: str
    quantity: float
    buy_price: float
    buy_date: datetime


class PriceIn(BaseModel):
    symbol: str
    date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None


@app.get("/tickers")
def list_tickers():
    try:
        return service.list_tickers()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


@app.get("/", include_in_schema=False)
def landing():
        """Serve a small landing page with links to the API docs and health check."""
        html = """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width,initial-scale=1" />
            <title>Personal Finance</title>
            <style>
                body { font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; margin: 40px; color:#0f172a }
                a { color: #2563eb; text-decoration: none }
                .card { border: 1px solid #e6e9ef; padding: 18px; border-radius: 8px; max-width:720px }
            </style>
        </head>
        <body>
            <h1>Personal Finance</h1>
            <div class="card">
                <p>A minimal web GUI for your personal finance data.</p>
                <ul>
                    <li><a href="/docs">Interactive API docs (OpenAPI)</a></li>
                    <li><a href="/tickers">GET /tickers</a></li>
                    <li><a href="/positions">GET /positions (raw JSON)</a></li>
                    <li><a href="/portfolio">Portfolio Manager UI</a></li>
                </ul>
                <p>Health: <a href="/health">/health</a></p>
            </div>
            <footer style="margin-top:18px;color:#6b7280">Deployed service</footer>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)


@app.get('/favicon.ico', include_in_schema=False)
def favicon():
        """Return empty 204 so browsers don't hit a 404 for favicon requests."""
        return Response(status_code=204)


@app.post("/tickers")
def create_ticker(payload: TickerIn):
    t = service.add_ticker(payload.symbol.upper(), payload.name, payload.price)
    if not t:
        raise HTTPException(status_code=400, detail="Could not create ticker")
    return t


@app.get("/positions")
def list_positions():
    try:
        positions = service.list_positions()
        # Serialize SQLAlchemy objects to plain dicts for JSON responses
        result = []
        for p in positions:
            result.append({
                "symbol": p.symbol,
                "name": p.name,
                "quantity": p.quantity,
                "buy_price": p.buy_price,
                "buy_date": p.buy_date.strftime("%Y-%m-%dT%H:%M:%S") if getattr(p, 'buy_date', None) else None,
            })
        return result
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


@app.post("/positions")
def create_position(payload: PositionIn):
    p = service.add_position(payload.symbol.upper(), payload.name, payload.quantity, payload.buy_price, payload.buy_date)
    # p may be None, an ORM instance, or a plain mapping; normalize to dict
    if p is None:
        raise HTTPException(status_code=400, detail="Could not create position")

    # If the service returned a plain mapping (e.g., Mongo SimpleNamespace -> dict), accept it
    if isinstance(p, dict):
        return p

    # Try to read attributes from ORM-like object safely
    symbol = getattr(p, 'symbol', None)
    name = getattr(p, 'name', None)
    quantity = getattr(p, 'quantity', None)
    buy_price = getattr(p, 'buy_price', None)
    buy_date_val = getattr(p, 'buy_date', None)

    # Format buy_date if it's a datetime; if it's already a string, leave as-is
    try:
        if hasattr(buy_date_val, 'strftime'):
            buy_date = buy_date_val.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            buy_date = buy_date_val
    except Exception:
        buy_date = None

    return {
        "symbol": symbol,
        "name": name,
        "quantity": quantity,
        "buy_price": buy_price,
        "buy_date": buy_date,
    }


@app.post("/prices")
def add_price(payload: PriceIn):
    p = service.add_price(payload.symbol.upper(), payload.date, payload.open, payload.high, payload.low, payload.close, payload.volume)
    return p


# --- Additional Portfolio CRUD Endpoints ---

@app.get("/positions/{symbol}")
def get_position(symbol: str):
    symbol = symbol.upper()
    # Directly fetch without modifying anything
    position = service.db.get_portfolio_position(symbol)  # type: ignore[attr-defined]
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return {
        "symbol": position.symbol,
        "name": position.name,
        "quantity": position.quantity,
        "buy_price": position.buy_price,
        "buy_date": position.buy_date.strftime("%Y-%m-%dT%H:%M:%S") if getattr(position, 'buy_date', None) else None,
    }


@app.put("/positions/{symbol}")
def update_position(symbol: str, payload: PositionIn):
    symbol = symbol.upper()
    updated = service.update_position(symbol, payload.quantity, payload.buy_price, payload.buy_date)
    if not updated:
        raise HTTPException(status_code=404, detail="Position not found")
    return {
        "symbol": updated.symbol,
        "name": updated.name,
        "quantity": updated.quantity,
        "buy_price": updated.buy_price,
        "buy_date": updated.buy_date.strftime("%Y-%m-%dT%H:%M:%S") if getattr(updated, 'buy_date', None) else None,
    }


@app.delete("/positions/{symbol}")
def delete_position(symbol: str):
    symbol = symbol.upper()
    removed = service.remove_position(symbol)
    if not removed:
        raise HTTPException(status_code=404, detail="Position not found")
    return {"status": "deleted", "symbol": symbol}


# --- Portfolio Management Page (HTML + JS) ---

@app.get("/portfolio", include_in_schema=False)
def portfolio_page():
        """Return an interactive HTML page to view/add/edit/delete portfolio assets.

        Uses fetch() against JSON endpoints so no server-side templates required.
        """
        html = """
        <!doctype html>
        <html lang=\"en\">
        <head>
            <meta charset=\"utf-8\" />
            <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
            <title>Portfolio Manager</title>
            <style>
                body { font-family: system-ui,-apple-system,'Segoe UI',Roboto,Arial; margin:24px; color:#0f172a; }
                h1 { margin-top:0; }
                table { border-collapse: collapse; width:100%; margin-top:12px; }
                th, td { border:1px solid #e2e8f0; padding:6px 8px; text-align:left; }
                th { background:#f1f5f9; }
                tbody tr:nth-child(even) { background:#f8fafc; }
                form { margin-top:16px; display:grid; gap:8px; max-width:520px; }
                label { font-weight:600; display:flex; flex-direction:column; font-size:14px; }
                input { padding:6px 8px; font:inherit; }
                button { cursor:pointer; padding:6px 12px; font:inherit; border:1px solid #1d4ed8; background:#2563eb; color:#fff; border-radius:4px; }
                button.secondary { background:#fff; color:#1d4ed8; }
                .actions button { margin-right:4px; }
                .inline-edit { background:#fff7ed; }
                .sr-only { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
                #message { margin-top:12px; font-size:14px; }
                #message.error { color:#b91c1c; }
                #message.success { color:#166534; }
            </style>
        </head>
        <body>
            <a href=\"#main\" class=\"sr-only\">Skip to main content</a>
            <h1>Portfolio Manager</h1>
            <p><a href=\"/\">&larr; Home</a></p>
            <main id=\"main\">
                <section aria-labelledby=\"portfolio-heading\">
                    <h2 id=\"portfolio-heading\">Positions</h2>
                    <table role=\"table\" aria-describedby=\"portfolio-desc\" id=\"positions-table\">
                        <caption id=\"portfolio-desc\" style=\"text-align:left; padding:4px 0;\">Followed assets in the portfolio.</caption>
                        <thead>
                            <tr><th scope=\"col\">Symbol</th><th scope=\"col\">Name</th><th scope=\"col\">Quantity</th><th scope=\"col\">Buy Price</th><th scope=\"col\">Buy Date</th><th scope=\"col\">Actions</th></tr>
                        </thead>
                        <tbody id=\"positions-body\"></tbody>
                    </table>
                </section>

                <section aria-labelledby=\"add-heading\" style=\"margin-top:32px;\">
                    <h2 id=\"add-heading\">Add Position</h2>
                    <form id=\"add-form\" aria-describedby=\"add-help\">
                        <div id=\"add-help\" style=\"font-size:12px;color:#475569;\">Add a new asset to track.</div>
                        <label>Symbol <input required name=\"symbol\" maxlength=\"10\" /></label>
                        <label>Name <input required name=\"name\" /></label>
                        <label>Quantity <input required name=\"quantity\" type=\"number\" step=\"0.0001\" min=\"0\" /></label>
                        <label>Buy Price <input required name=\"buy_price\" type=\"number\" step=\"0.0001\" min=\"0\" /></label>
                        <label>Buy Date <input required name=\"buy_date\" type=\"date\" /></label>
                        <div>
                            <button type=\"submit\">Add</button>
                            <button type=\"reset\" class=\"secondary\">Reset</button>
                        </div>
                    </form>
                </section>

                <div id=\"message\" role=\"status\" aria-live=\"polite\"></div>
            </main>

            <script>
            const tbody = document.getElementById('positions-body');
            const messageEl = document.getElementById('message');
            function setMessage(msg, type='success'){ messageEl.textContent = msg; messageEl.className = type ? type : ''; }

            async function loadPositions(){
                tbody.innerHTML = '<tr><td colspan="6">Loading...</td></tr>';
                try {
                    const res = await fetch('/positions');
                    if(!res.ok) throw new Error('Failed to load positions');
                    const data = await res.json();
                    if(!Array.isArray(data)) throw new Error('Unexpected response');
                    if(data.length === 0){ tbody.innerHTML = '<tr><td colspan="6">No positions yet.</td></tr>'; return; }
                    tbody.innerHTML = '';
                    data.forEach(p => tbody.appendChild(renderRow(p)));
                } catch (e){ tbody.innerHTML = '<tr><td colspan="6">Error loading positions</td></tr>'; setMessage(e.message, 'error'); }
            }

            function renderRow(p){
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${p.symbol}</td><td>${escapeHtml(p.name||'')}</td><td>${p.quantity}</td><td>${p.buy_price}</td><td>${p.buy_date ? p.buy_date.split('T')[0] : ''}</td><td class="actions"></td>`;
                const actionsTd = tr.querySelector('.actions');
                const editBtn = document.createElement('button'); editBtn.textContent = 'Edit'; editBtn.type='button'; editBtn.onclick = () => startEdit(tr, p);
                const delBtn = document.createElement('button'); delBtn.textContent = 'Delete'; delBtn.type='button'; delBtn.onclick = () => deletePosition(p.symbol);
                actionsTd.append(editBtn, delBtn);
                return tr;
            }

            function startEdit(tr, p){
                if(tr.classList.contains('inline-edit')) return; // already editing
                tr.classList.add('inline-edit');
                const cells = tr.querySelectorAll('td');
                const [symTd, nameTd, qtyTd, priceTd, dateTd, actionsTd] = cells;
                const symbol = p.symbol;
                nameTd.innerHTML = `<input value="${escapeAttr(p.name||'')}" />`;
                qtyTd.innerHTML = `<input type="number" step="0.0001" min="0" value="${p.quantity}" />`;
                priceTd.innerHTML = `<input type="number" step="0.0001" min="0" value="${p.buy_price}" />`;
                dateTd.innerHTML = `<input type="date" value="${p.buy_date ? p.buy_date.split('T')[0] : ''}" />`;
                actionsTd.innerHTML='';
                const saveBtn = document.createElement('button'); saveBtn.textContent='Save'; saveBtn.type='button'; saveBtn.onclick=()=>saveEdit(symbol, tr);
                const cancelBtn = document.createElement('button'); cancelBtn.textContent='Cancel'; cancelBtn.type='button'; cancelBtn.className='secondary'; cancelBtn.onclick=()=> { tr.classList.remove('inline-edit'); loadPositions(); };
                actionsTd.append(saveBtn, cancelBtn);
            }

            async function saveEdit(symbol, tr){
                try {
                    const inputs = tr.querySelectorAll('input');
                    const [nameEl, qtyEl, priceEl, dateEl] = inputs;
                    const body = {
                        symbol: symbol,
                        name: nameEl.value.trim(),
                        quantity: parseFloat(qtyEl.value),
                        buy_price: parseFloat(priceEl.value),
                        buy_date: dateEl.value ? dateEl.value + 'T00:00:00' : null
                    };
                    const res = await fetch(`/positions/${encodeURIComponent(symbol)}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
                    if(!res.ok) throw new Error('Update failed');
                    setMessage('Updated ' + symbol);
                    loadPositions();
                } catch(e){ setMessage(e.message, 'error'); }
            }

            async function deletePosition(symbol){
                if(!confirm('Delete ' + symbol + '?')) return;
                try {
                    const res = await fetch(`/positions/${encodeURIComponent(symbol)}`, {method:'DELETE'});
                    if(!res.ok) throw new Error('Delete failed');
                    setMessage('Deleted ' + symbol);
                    loadPositions();
                } catch(e){ setMessage(e.message, 'error'); }
            }

            document.getElementById('add-form').addEventListener('submit', async e => {
                e.preventDefault();
                const fd = new FormData(e.target);
                const body = Object.fromEntries(fd.entries());
                body.symbol = body.symbol.toUpperCase();
                body.quantity = parseFloat(body.quantity);
                body.buy_price = parseFloat(body.buy_price);
                body.buy_date = body.buy_date ? body.buy_date + 'T00:00:00' : null;
                try {
                    const res = await fetch('/positions', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
                    if(!res.ok) throw new Error('Create failed');
                    e.target.reset();
                    setMessage('Added ' + body.symbol);
                    loadPositions();
                } catch (err){ setMessage(err.message, 'error'); }
            });

            function escapeHtml(str){ return str.replace(/[&<>"]g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
            function escapeAttr(str){ return escapeHtml(str).replace(/'/g,'&#39;'); }
            loadPositions();
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html, status_code=200)


@app.get("/health")
def health():
    """Lightweight health check — verifies the app and DB connectivity.

    Returns 200 with {status: 'ok', db: 'ok'} when a simple SELECT 1 succeeds.
    Returns 503 with error details if the DB check fails.
    """
    dsn = getattr(service.db, 'database_url', None)
    host = _extract_db_host(dsn)
    try:
        ok = service.db.ping()
        if ok:
            return JSONResponse(status_code=200, content={
                "status": "ok",
                "db": "ok",
                "db_host": host,
            })
        else:
            return JSONResponse(status_code=503, content={
                "status": "fail",
                "db": "error",
                "db_host": host,
                "detail": "Ping failed",
                "hint": "Check DATABASE_URL — ensure it is reachable."
            })
    except Exception as exc:  # pragma: no cover
        return JSONResponse(status_code=503, content={
            "status": "fail",
            "db": "error",
            "db_host": host,
            "detail": str(exc),
            "hint": "Check DATABASE_URL — ensure it is reachable."
        })
