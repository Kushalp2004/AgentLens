import sqlite3
from pathlib import Path
from contextlib import closing
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from agentlens_ui.core import DB_PATH, ensure_db_initialized

app = FastAPI()


def get_db() -> sqlite3.Connection:
    ensure_db_initialized()
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/api/runs")
def get_runs():
    try:
        with closing(get_db()) as conn:
            runs = conn.execute("SELECT DISTINCT run_id FROM traces ORDER BY timestamp DESC").fetchall()
            return [dict(run) for run in runs]
    except sqlite3.OperationalError:
        return []


@app.get("/api/traces/{run_id}")
def get_traces(run_id: str):
    try:
        with closing(get_db()) as conn:
            traces = conn.execute("SELECT * FROM traces WHERE run_id = ? ORDER BY timestamp ASC", (run_id,)).fetchall()
            return [dict(t) for t in traces]
    except sqlite3.OperationalError:
        return []


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="UI artifact missing from wheel.")
    return html_path.read_text(encoding="utf-8")


def start_ui():
    import uvicorn
    print("👁️ AgentLens UI starting at http://localhost:8000")
    uvicorn.run("agentlens_ui.server:app", host="127.0.0.1", port=8000, reload=False, log_level="warning")