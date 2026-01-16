from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Optional

import httpx


_server_thread: Optional[threading.Thread] = None
_started: bool = False


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_backend_healthy(base_url: str) -> bool:
    try:
        with httpx.Client(timeout=1.0) as client:
            r = client.get(f"{base_url.rstrip('/')}/health")
            return r.status_code == 200
    except Exception:
        return False


def _run_uvicorn() -> None:
    import sys

    backend_dir = _project_root() / "backend"
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    import uvicorn

    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.run()


def ensure_backend_started(api_base_url: str) -> None:
    global _server_thread, _started

    if _started:
        return

    if not api_base_url.startswith("http://127.0.0.1:8000") and not api_base_url.startswith("http://localhost:8000"):
        return

    if _is_backend_healthy(api_base_url):
        _started = True
        return

    if _server_thread and _server_thread.is_alive():
        return

    t = threading.Thread(target=_run_uvicorn, name="embedded-uvicorn", daemon=True)
    _server_thread = t
    t.start()

    deadline = time.time() + 10
    while time.time() < deadline:
        if _is_backend_healthy(api_base_url):
            _started = True
            return
        time.sleep(0.25)
