"""
claude-agile Orchestrator
Central hub that manages per-project dashboard server subprocesses.
Port 4000 — spawns project servers on 4001+.
"""

import atexit
import json
import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

log = logging.getLogger("claude-agile.orchestrator")

DASHBOARD_DIR = Path(__file__).resolve().parent
WORKSPACES_CONFIG = Path.home() / ".claude-agile" / "workspaces.json"
HUB_PORT = int(os.environ.get("CLAUDE_AGILE_HUB_PORT", "4000"))
BASE_PORT = 4001

app = FastAPI(title="claude-agile Hub")

# In-memory registry: {name: {"process": Popen, "port": int, "path": str}}
_servers: dict[str, dict] = {}


# ─── Workspace Config ────────────────────────────────────────────────

def _load_workspaces() -> dict:
    if WORKSPACES_CONFIG.exists():
        try:
            return json.loads(WORKSPACES_CONFIG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            pass
    return {"workspaces": [], "active": ""}


def _save_workspaces(config: dict):
    WORKSPACES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    WORKSPACES_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def _port_for_index(idx: int) -> int:
    return BASE_PORT + idx


# ─── Server Management ───────────────────────────────────────────────

def _start_server(name: str, path: str, port: int) -> bool:
    """Spawn a project server as a subprocess."""
    if name in _servers and _servers[name]["process"].poll() is None:
        return True  # Already running

    env = {**os.environ,
           "CLAUDE_AGILE_PORT": str(port),
           "CLAUDE_AGILE_PROJECT": path,
           "CLAUDE_AGILE_MODE": "project"}

    log_file = Path(f"/tmp/claude-agile-{name}.log")
    try:
        proc = subprocess.Popen(
            [sys.executable, str(DASHBOARD_DIR / "server.py"), path],
            env=env,
            stdout=open(log_file, "w"),
            stderr=subprocess.STDOUT,
        )
        _servers[name] = {"process": proc, "port": port, "path": path, "pid": proc.pid}
        log.info(f"Started {name} on port {port} (PID {proc.pid})")
        return True
    except Exception as e:
        log.error(f"Failed to start {name}: {e}")
        return False


def _stop_server(name: str):
    """Stop a project server subprocess."""
    if name not in _servers:
        return
    proc = _servers[name]["process"]
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
    del _servers[name]
    log.info(f"Stopped {name}")


def _stop_all():
    """Stop all project servers."""
    for name in list(_servers.keys()):
        _stop_server(name)


def _is_running(name: str) -> bool:
    if name not in _servers:
        return False
    return _servers[name]["process"].poll() is None


# ─── API ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def hub_page():
    return FileResponse(DASHBOARD_DIR / "hub.html")


@app.get("/api/projects")
async def list_projects():
    config = _load_workspaces()
    projects = []
    for i, ws in enumerate(config.get("workspaces", [])):
        port = _port_for_index(i)
        name = ws["name"]
        running = _is_running(name)
        # Get git info
        branch = None
        try:
            r = subprocess.run(["git", "branch", "--show-current"],
                               capture_output=True, text=True, timeout=3, cwd=ws["path"])
            branch = r.stdout.strip() if r.returncode == 0 else None
        except Exception:
            pass

        projects.append({
            "name": name,
            "path": ws["path"],
            "port": port,
            "running": running,
            "pid": _servers.get(name, {}).get("pid"),
            "modules": ws.get("modules", []),
            "branch": branch,
            "url": f"http://localhost:{port}" if running else None,
        })
    return {"projects": projects, "hub_port": HUB_PORT}


@app.post("/api/projects/{name}/start")
async def start_project(name: str):
    config = _load_workspaces()
    ws = next((w for w in config["workspaces"] if w["name"] == name), None)
    if not ws:
        return {"error": f"Project '{name}' not found"}
    idx = next(i for i, w in enumerate(config["workspaces"]) if w["name"] == name)
    port = _port_for_index(idx)
    ok = _start_server(name, ws["path"], port)
    if ok:
        return {"ok": True, "port": port, "url": f"http://localhost:{port}"}
    return {"error": "Failed to start server"}


@app.post("/api/projects/{name}/stop")
async def stop_project(name: str):
    _stop_server(name)
    return {"ok": True}


@app.post("/api/projects")
async def add_project(body: dict):
    name = body.get("name", "").strip()
    path = body.get("path", "").strip()
    if not name or not path:
        return {"error": "name and path required"}

    resolved = Path(path).resolve()
    if not resolved.is_dir():
        try:
            resolved.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"error": f"Cannot create {path}: {e}"}

    config = _load_workspaces()
    if any(w["name"] == name for w in config["workspaces"]):
        return {"error": f"Project '{name}' already exists"}

    config["workspaces"].append({"name": name, "path": str(resolved), "modules": []})
    _save_workspaces(config)

    # Auto-start
    idx = len(config["workspaces"]) - 1
    port = _port_for_index(idx)
    _start_server(name, str(resolved), port)

    return {"ok": True, "port": port, "url": f"http://localhost:{port}"}


@app.delete("/api/projects/{name}")
async def remove_project(name: str):
    _stop_server(name)
    config = _load_workspaces()
    config["workspaces"] = [w for w in config["workspaces"] if w["name"] != name]
    _save_workspaces(config)
    return {"ok": True}


# ─── Lifecycle ───────────────────────────────────────────────────────

@app.on_event("startup")
async def auto_start_all():
    """Auto-start all project servers on orchestrator boot."""
    config = _load_workspaces()
    for i, ws in enumerate(config.get("workspaces", [])):
        port = _port_for_index(i)
        if Path(ws["path"]).is_dir():
            _start_server(ws["name"], ws["path"], port)
            time.sleep(0.5)  # Stagger startup


def _signal_handler(sig, frame):
    log.info("Shutting down all project servers...")
    _stop_all()
    sys.exit(0)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
atexit.register(_stop_all)


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    config = _load_workspaces()
    ws_count = len(config.get("workspaces", []))

    print(f"\n  claude-agile Hub v1.0")
    print(f"  http://localhost:{HUB_PORT}")
    print(f"  Projects: {ws_count}")
    print(f"  Project ports: {BASE_PORT}-{BASE_PORT + max(ws_count - 1, 0)}\n")

    uvicorn.run(app, host="127.0.0.1", port=HUB_PORT, log_level="warning")
