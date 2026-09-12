import os
import sqlite3
import json
import time
import uuid
import inspect
from functools import wraps
from pathlib import Path
from contextlib import closing
from typing import Any, Callable, Dict, Optional, TypeVar
from contextvars import ContextVar

# Issue #3: Absolute, user-configurable DB path without import-time side effects
DB_PATH = os.environ.get("AGENTLENS_DB_PATH", str(Path.cwd() / "agentlens.db"))

# Context variables for concurrent execution tracking
_run_id_ctx: ContextVar[str] = ContextVar("run_id", default="system")
_parent_id_ctx: ContextVar[Optional[str]] = ContextVar("parent_id", default=None)
_db_initialized: bool = False


def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection with WAL journaling and explicit busy timeouts."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_db_initialized() -> None:
    """Lazily initializes the database schema to prevent unexpected import-time artifacts."""
    global _db_initialized
    if _db_initialized:
        return
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    agent_name TEXT,
                    step_type TEXT,
                    content TEXT,
                    details TEXT,
                    latency REAL,
                    parent_id TEXT,
                    timestamp REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_run_id ON traces(run_id)")
    _db_initialized = True


def _safe_serialize(obj: Any) -> Any:
    """Issue #1: Ensures non-serializable objects (generators, Pydantic models) do not crash telemetry."""
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        return str(obj)


def log_trace(
    agent_name: str, 
    step_type: str, 
    content: str, 
    details: Optional[Dict[str, Any]] = None, 
    latency: Optional[float] = None,
    parent_id: Optional[str] = None
) -> None:
    ensure_db_initialized()
    current_run = _run_id_ctx.get()
    if current_run == "system":
        current_run = f"run_{int(time.time())}_{uuid.uuid4().hex[:5]}"

    # Issue #8: Resolve hierarchy from explicit argument or ContextVar
    resolved_parent = parent_id or _parent_id_ctx.get()

    # Issue #4: Bulletproof serialization boundary around details payload
    try:
        clean_details = {k: _safe_serialize(v) for k, v in (details or {}).items()}
        details_json = json.dumps(clean_details, default=str)
    except Exception:
        details_json = json.dumps({"_serialization_error": "Payload contained un-serializable binary or complex objects."})

    # Issue #2: Explicit connection closure via contextlib.closing
    with closing(get_db_connection()) as conn:
        with conn:
            conn.execute("""
                INSERT INTO traces (id, run_id, agent_name, step_type, content, details, latency, parent_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                uuid.uuid4().hex, 
                current_run, 
                agent_name, 
                step_type, 
                content, 
                details_json, 
                latency, 
                resolved_parent,
                time.time()
            ))


F = TypeVar('F', bound=Callable[..., Any])


def trace(agent_name: str) -> Callable[[F], F]:
    """Dual async/sync decorator supporting strict parent-child execution tracking."""
    def decorator(func: F) -> F:
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                run_token = None
                if _run_id_ctx.get() == "system":
                    run_token = _run_id_ctx.set(f"run_{int(time.time())}_{uuid.uuid4().hex[:5]}")
                
                step_id = uuid.uuid4().hex
                parent_token = _parent_id_ctx.set(step_id)
                
                start = time.time()
                log_trace(agent_name, "START", "Agent initiated", parent_id=step_id)
                try:
                    result = await func(*args, **kwargs)
                    latency = round(time.time() - start, 3)
                    log_trace(agent_name, "SUCCESS", "Agent completed", details={"result": _safe_serialize(result)}, latency=latency, parent_id=step_id)
                    return result
                except Exception as e:
                    latency = round(time.time() - start, 3)
                    log_trace(agent_name, "ERROR", "Agent crashed", details={"error": str(e)}, latency=latency, parent_id=step_id)
                    raise
                finally:
                    _parent_id_ctx.reset(parent_token)
                    if run_token:
                        _run_id_ctx.reset(run_token)
            return async_wrapper # type: ignore
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                run_token = None
                if _run_id_ctx.get() == "system":
                    run_token = _run_id_ctx.set(f"run_{int(time.time())}_{uuid.uuid4().hex[:5]}")
                
                step_id = uuid.uuid4().hex
                parent_token = _parent_id_ctx.set(step_id)

                start = time.time()
                log_trace(agent_name, "START", "Agent initiated", parent_id=step_id)
                try:
                    result = func(*args, **kwargs)
                    latency = round(time.time() - start, 3)
                    log_trace(agent_name, "SUCCESS", "Agent completed", details={"result": _safe_serialize(result)}, latency=latency, parent_id=step_id)
                    return result
                except Exception as e:
                    latency = round(time.time() - start, 3)
                    log_trace(agent_name, "ERROR", "Agent crashed", details={"error": str(e)}, latency=latency, parent_id=step_id)
                    raise
                finally:
                    _parent_id_ctx.reset(parent_token)
                    if run_token:
                        _run_id_ctx.reset(run_token)
            return sync_wrapper # type: ignore
    return decorator