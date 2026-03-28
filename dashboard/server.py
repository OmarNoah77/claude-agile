"""
claude-agile Dashboard Server
Standalone dashboard for the claude-agile plugin.
Reads BACKLOG.md, SPRINT.md, DAILY.md, RETRO.md from any project directory.
Includes autonomous agent worker that processes user messages via Claude Code.

Usage:
  python dashboard/server.py                        # auto-detect project root (cwd)
  python dashboard/server.py /path/to/project       # explicit project root
  CLAUDE_AGILE_PROJECT=/path python dashboard/server.py  # via env var
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

log = logging.getLogger("claude-agile")

# ─── Config ───────────────────────────────────────────────────────────
DASHBOARD_DIR = Path(__file__).resolve().parent
CLAUDE_AGILE_DIR = DASHBOARD_DIR.parent
PORT = int(os.environ.get("CLAUDE_AGILE_PORT", "4000"))
WORKSPACES_CONFIG = Path.home() / ".claude-agile" / "workspaces.json"

# Project root: CLI arg > env var > workspaces.json active > cwd
if len(sys.argv) > 1 and Path(sys.argv[1]).is_dir():
    PROJECT_ROOT = Path(sys.argv[1]).resolve()
elif os.environ.get("CLAUDE_AGILE_PROJECT"):
    PROJECT_ROOT = Path(os.environ["CLAUDE_AGILE_PROJECT"]).resolve()
else:
    # Try to load from workspaces.json
    _ws_init = Path.home() / ".claude-agile" / "workspaces.json"
    if _ws_init.exists():
        try:
            _ws_data = json.loads(_ws_init.read_text(encoding="utf-8"))
            _ws_active = _ws_data.get("active", "")
            _ws_match = next((w for w in _ws_data.get("workspaces", []) if w["name"] == _ws_active), None)
            if _ws_match and Path(_ws_match["path"]).is_dir():
                PROJECT_ROOT = Path(_ws_match["path"]).resolve()
            else:
                PROJECT_ROOT = Path.cwd()
        except Exception:
            PROJECT_ROOT = Path.cwd()
    else:
        PROJECT_ROOT = Path.cwd()

# Module & Chat state
_active_module: str = ""  # Empty = workspace-level (global context)


def _module_state_dir() -> Path:
    """Return the .claude-agile subdir for the active module, or root .claude-agile if no module."""
    base = PROJECT_ROOT / ".claude-agile"
    if _active_module:
        return base / "modules" / _active_module
    return base


TEAM_CHAT_LOG = _module_state_dir() / "team-chat.jsonl"


# ─── Workspace Management ────────────────────────────────────────────

def _load_workspaces() -> dict:
    """Load workspaces config from ~/.claude-agile/workspaces.json."""
    if WORKSPACES_CONFIG.exists():
        try:
            return json.loads(WORKSPACES_CONFIG.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            pass
    # Default: current PROJECT_ROOT as the only workspace
    return {
        "workspaces": [{"name": PROJECT_ROOT.name, "path": str(PROJECT_ROOT), "modules": []}],
        "active": PROJECT_ROOT.name,
    }


def _save_workspaces(config: dict):
    """Save workspaces config to ~/.claude-agile/workspaces.json."""
    WORKSPACES_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    WORKSPACES_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def _switch_workspace(name: str) -> bool:
    """Switch the active workspace by name. Returns True on success."""
    global PROJECT_ROOT, TEAM_CHAT_LOG, _pipeline, _skill_registry, _active_module

    config = _load_workspaces()
    ws = next((w for w in config["workspaces"] if w["name"] == name), None)
    if not ws:
        return False

    new_root = Path(ws["path"])
    if not new_root.is_dir():
        return False

    with _workspace_lock:
        PROJECT_ROOT = new_root
        _active_module = ""  # Reset to global context
        TEAM_CHAT_LOG = _module_state_dir() / "team-chat.jsonl"

        # Re-initialize pipeline and skills for the new project
        _pipeline = Pipeline(_module_state_dir())
        _skill_registry = SkillRegistry(PROJECT_ROOT, CLAUDE_AGILE_DIR)
        init_skills(PROJECT_ROOT)

        # Update active in config
        config["active"] = name
        _save_workspaces(config)
    return True


def _switch_module(module_name: str) -> bool:
    """Switch the active module context (UI only). Worker runs independently."""
    global _active_module
    _active_module = module_name
    _worker_pool.get_or_create(module_name)  # Ensure worker is running
    return True

app = FastAPI(title="claude-agile Dashboard")


# ─── Chat Store ──────────────────────────────────────────────────────

def _read_chat(limit: int = 50) -> list:
    """Read team chat messages from local JSONL log."""
    if not TEAM_CHAT_LOG.exists():
        return []
    messages = []
    try:
        with open(TEAM_CHAT_LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return messages[-limit:]
    except Exception:
        return []


def _next_chat_id() -> int:
    """Get the next message ID from the chat log."""
    max_id = 0
    if TEAM_CHAT_LOG.exists():
        try:
            with open(TEAM_CHAT_LOG, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        msg = json.loads(line.strip())
                        max_id = max(max_id, msg.get("id", 0))
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception:
            pass
    return max_id + 1


def _add_chat(sender: str, text: str, role: str = "") -> dict:
    """Add a message to the team chat log."""
    TEAM_CHAT_LOG.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    entry = {
        "id": _next_chat_id(),
        "uid": str(uuid.uuid4()),
        "sender": sender,
        "role": role,
        "text": text,
        "type": "chat",
        "timestamp": time.time(),
        "time": now.strftime("%H:%M:%S"),
    }
    with open(TEAM_CHAT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


# ─── Imports & Config ─────────────────────────────────────────────────

_workspace_lock = threading.Lock()

sys.path.insert(0, str(DASHBOARD_DIR))
from pipeline import Pipeline, PHASE_ROLES
from prompts import build_prompt, init_skills
from workers import WorkerManager
from skills import SkillRegistry

_skill_registry = SkillRegistry(PROJECT_ROOT, CLAUDE_AGILE_DIR)
init_skills(PROJECT_ROOT)
NUM_PARALLEL_WORKERS = int(os.environ.get("CLAUDE_AGILE_WORKERS", "2"))
IS_PROJECT_MODE = os.environ.get("CLAUDE_AGILE_MODE") == "project"


# ─── Module Worker (per-module agent) ─────────────────────────────────

class ModuleWorker:
    """Independent agent worker for a single module context."""

    def __init__(self, project_root: Path, module_name: str, claude_agile_dir: Path):
        self.project_root = project_root
        self.module_name = module_name  # "" = global
        self.claude_agile_dir = claude_agile_dir

        base = project_root / ".claude-agile"
        self.state_dir = base / "modules" / module_name if module_name else base
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.chat_log = self.state_dir / "team-chat.jsonl"
        self.pipeline = Pipeline(self.state_dir)

        self._last_id = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._worker_manager: Optional[WorkerManager] = None
        self._label = module_name or "global"

    # ── Chat I/O (scoped to this module) ──

    def read_chat(self, limit: int = 50) -> list:
        if not self.chat_log.exists():
            return []
        messages = []
        try:
            with open(self.chat_log, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            return messages[-limit:]
        except Exception:
            return []

    def _next_chat_id(self) -> int:
        max_id = 0
        if self.chat_log.exists():
            try:
                with open(self.chat_log, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            msg = json.loads(line.strip())
                            max_id = max(max_id, msg.get("id", 0))
                        except (json.JSONDecodeError, ValueError):
                            continue
            except Exception:
                pass
        return max_id + 1

    def add_chat(self, sender: str, text: str, role: str = "") -> dict:
        self.chat_log.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now()
        entry = {
            "id": self._next_chat_id(),
            "uid": str(uuid.uuid4()),
            "sender": sender,
            "role": role,
            "text": text,
            "type": "chat",
            "module": self.module_name,
            "timestamp": time.time(),
            "time": now.strftime("%H:%M:%S"),
        }
        with open(self.chat_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    # ── Claude invocation ──

    def _invoke_claude(self, prompt: str) -> Optional[str]:
        """Invoke Claude Code in interactive mode with full tool access.
        Writes prompt to a temp file to handle large inputs safely.
        Uses the user's OAuth session (not API key) for authentication."""
        # Write prompt to temp file (avoids shell arg length limits)
        prompt_file = self.state_dir / ".prompt-tmp.md"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")

        system_prompt_file = self.claude_agile_dir / "dashboard" / "system-prompt-base.md"
        cmd = [
            "claude", "-p",
            "--permission-mode", "bypassPermissions",
            "--output-format", "stream-json",
            "--verbose",
        ]
        if system_prompt_file.exists():
            cmd.extend(["--append-system-prompt-file", str(system_prompt_file)])
        # Load claude-agile plugin if available
        plugin_dir = str(self.claude_agile_dir)
        if Path(plugin_dir).is_dir():
            cmd.extend(["--plugin-dir", plugin_dir])

        # Strip ANTHROPIC_API_KEY so claude uses OAuth session instead of paid API
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}

        try:
            # Feed prompt via stdin from the temp file
            with open(prompt_file, "r", encoding="utf-8") as f_in:
                result = subprocess.run(
                    cmd,
                    capture_output=True, text=True, timeout=900,
                    cwd=str(self.project_root),
                    stdin=f_in,
                    env=env,
                )

            output = result.stdout.strip()
            if not output:
                log.warning(f"[{self._label}] Claude rc={result.returncode}")
                log.warning(f"[{self._label}] stderr: {result.stderr[:500]!r}")
                return None

            # Parse stream-json: one JSON event per line
            assistant_texts = []
            final_result = ""
            for line in output.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type", "")

                if etype == "assistant":
                    msg = event.get("message", {})
                    if isinstance(msg, dict):
                        for block in msg.get("content", []):
                            if isinstance(block, dict) and block.get("type") == "text":
                                assistant_texts.append(block["text"])

                elif etype == "result":
                    final_result = event.get("result", "")
                    duration = event.get("duration_ms", 0)
                    turns = event.get("num_turns", 0)
                    cost = event.get("total_cost_usd", 0)
                    log.info(f"[{self._label}] Claude: {duration}ms, {turns} turns, cost=${cost}")

            # Use final result if available, otherwise join all assistant texts
            text = final_result or "\n\n".join(assistant_texts)
            if text:
                log.info(f"[{self._label}] Response: {len(text)} chars")
                return text

            log.warning(f"[{self._label}] No text captured from stream output")
            return None

        except subprocess.TimeoutExpired:
            log.warning(f"[{self._label}] Claude timeout (900s)")
            return None
        except FileNotFoundError:
            log.error("'claude' CLI not found in PATH")
            return None
        except Exception as e:
            log.error(f"[{self._label}] Claude error: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                prompt_file.unlink(missing_ok=True)
            except Exception:
                pass

    # ── Pipeline helpers ──

    def _get_methodology(self) -> str:
        config_path = self.project_root / ".claude-agile" / "config.json"
        if config_path.exists():
            try:
                return json.loads(config_path.read_text()).get("methodology", "lean-xp")
            except Exception:
                pass
        return "lean-xp"

    def _run_phase(self, phase: str, state, messages: list):
        role = PHASE_ROLES.get(phase, PHASE_ROLES["intake"])
        label = f"[{role['tag']}]"
        log.info(f"[{self._label}] Pipeline phase: {phase} ({role['name']})")
        self.add_chat("system", f"{label} {role['name']} trabajando...", role=role["tag"])

        prompt = build_prompt(
            phase,
            state_dict=state.to_dict() if state else {},
            chat_history=messages,
            project_root=str(self.project_root),
            methodology=self._get_methodology(),
        )
        if not prompt:
            self.add_chat("system", f"{label} Error: no prompt for phase {phase}", role=role["tag"])
            return None

        response = self._invoke_claude(prompt)
        if not response:
            self.add_chat("system", f"{label} Error: sin respuesta de Claude Code", role=role["tag"])
            return None

        self.add_chat("assistant", response, role=role["tag"])
        return response

    def _auto_advance(self, state, messages: list):
        from pipeline import MAX_FIX_ATTEMPTS
        phases_to_run = ["plan", "exec", "verify"]

        for target_phase in phases_to_run:
            ok, reason = self.pipeline.can_transition(state, target_phase)
            if not ok:
                self.add_chat("system", f"Pipeline no puede avanzar a {target_phase}: {reason}", role="SM")
                break

            state = self.pipeline.transition(state, target_phase, f"Auto-advance")
            self.add_chat("system", self.pipeline.get_status_line(state), role=PHASE_ROLES[target_phase]["tag"])
            messages = self.read_chat(limit=100)

            if target_phase == "exec" and NUM_PARALLEL_WORKERS > 1:
                response = self._run_parallel_exec(state, messages)
            else:
                response = self._run_phase(target_phase, state, messages)

            if not response:
                state = self.pipeline.transition(state, "failed", "No response from agent")
                break

            if target_phase == "plan":
                self.pipeline.save_plan(state, response)

            marker = _detect_pipeline_marker(response)

            if marker == "complete":
                state = self.pipeline.transition(state, "complete", "QA passed")
                self.add_chat("system", f"Pipeline {state.task_id} completado.", role="SM")
                self.pipeline.save_history(state)
                self.pipeline.save_session(state, self.read_chat(limit=200))
                self.pipeline.clear()
                return

            if marker == "failed":
                state = self.pipeline.transition(state, "failed", "Agent declared failure")
                self.add_chat("system", f"Pipeline {state.task_id} falló.", role="SM")
                self.pipeline.save_history(state)
                self.pipeline.save_session(state, self.read_chat(limit=200))
                self.pipeline.clear()
                return

            if marker == "fix" and target_phase == "verify":
                state.fix_reason = response
                self.pipeline.save(state)
                self._run_fix_loop(state, messages)
                return

        if state.phase == "verify":
            state = self.pipeline.transition(state, "complete", "All phases completed")
            self.add_chat("system", f"Pipeline {state.task_id} completado.", role="SM")
            self.pipeline.save_history(state)
            self.pipeline.save_session(state, self.read_chat(limit=200))
            self.pipeline.clear()

    def _run_fix_loop(self, state, messages: list):
        from pipeline import MAX_FIX_ATTEMPTS
        while state.fix_attempts < MAX_FIX_ATTEMPTS:
            ok, reason = self.pipeline.can_transition(state, "fix")
            if not ok:
                state = self.pipeline.transition(state, "failed", reason)
                self.add_chat("system", f"Pipeline {state.task_id} falló: {reason}", role="SM")
                break

            state = self.pipeline.transition(state, "fix", f"Fix attempt {state.fix_attempts}")
            messages = self.read_chat(limit=100)
            response = self._run_phase("fix", state, messages)

            if not response:
                state = self.pipeline.transition(state, "failed", "No fix response")
                break

            marker = _detect_pipeline_marker(response)
            if marker == "failed":
                state = self.pipeline.transition(state, "failed", "Fix declared unfixable")
                break

            state = self.pipeline.transition(state, "verify", "Re-verifying after fix")
            messages = self.read_chat(limit=100)
            response = self._run_phase("verify", state, messages)

            if not response:
                state = self.pipeline.transition(state, "failed", "No verify response")
                break

            marker = _detect_pipeline_marker(response)
            if marker == "complete":
                state = self.pipeline.transition(state, "complete", f"QA passed after {state.fix_attempts} fix(es)")
                self.add_chat("system", f"Pipeline {state.task_id} completado.", role="SM")
                self.pipeline.save_history(state)
                self.pipeline.save_session(state, self.read_chat(limit=200))
                self.pipeline.clear()
                return

            if marker != "fix":
                state = self.pipeline.transition(state, "complete", "Verify passed")
                self.add_chat("system", f"Pipeline {state.task_id} completado.", role="SM")
                self.pipeline.save_history(state)
                self.pipeline.save_session(state, self.read_chat(limit=200))
                self.pipeline.clear()
                return

            state.fix_reason = response
            self.pipeline.save(state)

        if state.phase != "complete":
            state = self.pipeline.transition(state, "failed", f"Max fix attempts reached")
            self.add_chat("system", f"Pipeline {state.task_id} falló.", role="SM")
            self.pipeline.save_history(state)
            self.pipeline.save_session(state, self.read_chat(limit=200))
            self.pipeline.clear()

    def _run_parallel_exec(self, state, messages: list) -> str:
        plan_content = ""
        if state.plan_path and Path(state.plan_path).exists():
            plan_content = Path(state.plan_path).read_text(encoding="utf-8")

        tasks = _parse_plan_tasks(plan_content)
        if not tasks:
            tasks = [{"id": "task-0", "title": state.title, "description": state.user_story}]

        self.add_chat("system", f"[DEV] Plan descompuesto en {len(tasks)} tareas", "DEV")

        if len(tasks) <= 1 or NUM_PARALLEL_WORKERS <= 1:
            return self._run_phase("exec", state, messages)

        self._worker_manager = WorkerManager(
            project_root=self.project_root,
            state_dir=self.state_dir,
            num_workers=min(NUM_PARALLEL_WORKERS, len(tasks)),
            on_chat=self.add_chat,
        )
        self._worker_manager.start(tasks)
        self._worker_manager.wait(timeout=600)
        results = self._worker_manager.results()
        self._worker_manager.shutdown()
        self._worker_manager = None

        completed_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        summary_parts = [f"**[DEV] Ejecución paralela completada**\n", f"- Completadas: {completed_count}/{len(tasks)}"]
        if failed_count:
            summary_parts.append(f"- Fallidas: {failed_count}")
        summary = "\n".join(summary_parts) + "\n\n[PIPELINE:ADVANCE_TO_VERIFY]"
        self.add_chat("assistant", summary, "DEV")
        return summary

    # ── Sprint Execution ──

    def _read_sprint_tasks(self, sprint_name: str) -> list[dict]:
        """Parse BACKLOG.md and extract [S{N}] tasks from Active section."""
        backlog_path = self.project_root / "BACKLOG.md"
        if not backlog_path.exists():
            return []

        tasks = []
        in_active = False
        for line in backlog_path.read_text(encoding="utf-8").split("\n"):
            stripped = line.strip()
            if stripped.startswith("## Active"):
                in_active = True
                continue
            elif stripped.startswith("## "):
                in_active = False
                continue

            if not in_active or not stripped.startswith("- "):
                continue

            if f"[S{sprint_name}]" not in stripped:
                continue

            # Parse: "- **P1** | [S2] T2.1 Backend Presupuestos | [5 SP] | backlog"
            sp_match = re.search(r"\[(\d+)\s*SP\]", stripped)
            sp = int(sp_match.group(1)) if sp_match else 0

            priority_match = re.match(r"- \*\*(\w+)\*\*", stripped)
            priority = priority_match.group(1) if priority_match else "P2"

            parts = stripped.split("|")
            title = parts[1].strip() if len(parts) > 1 else stripped[2:]
            title = re.sub(r"\[\d+\s*SP\]", "", title).strip()

            # Extract task ID like T2.1
            tid_match = re.search(r"(T\d+\.\d+)", title)
            task_id = tid_match.group(1) if tid_match else f"T-{len(tasks)+1}"

            tasks.append({
                "id": task_id,
                "title": title,
                "sp": sp,
                "priority": priority,
                "full_line": stripped,
            })

        return tasks

    def _update_backlog_task(self, task_title_fragment: str, new_status: str):
        """Move a task from Active to Completed in BACKLOG.md or update its status."""
        backlog_path = self.project_root / "BACKLOG.md"
        if not backlog_path.exists():
            return

        content = backlog_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        new_lines = []
        moved_line = None

        for line in lines:
            if task_title_fragment in line and line.strip().startswith("- ") and new_status == "done":
                # Change status to done and save for Completed section
                moved_line = line.rstrip().rsplit("|", 1)[0] + "| done"
                continue  # Remove from current position
            new_lines.append(line)

        if moved_line:
            # Find Completed section and insert
            for i, line in enumerate(new_lines):
                if line.strip().startswith("## Completed"):
                    # Insert after the header (and any blank line)
                    insert_at = i + 1
                    while insert_at < len(new_lines) and not new_lines[insert_at].strip():
                        insert_at += 1
                    new_lines.insert(insert_at, moved_line)
                    break

        backlog_path.write_text("\n".join(new_lines), encoding="utf-8")

    def _update_sprint_progress(self, task_id: str, task_title: str, sp: int, total_tasks: int, completed: int):
        """Update SPRINT.md to reflect progress."""
        sprint_path = self.project_root / "SPRINT.md"
        if not sprint_path.exists():
            return

        content = sprint_path.read_text(encoding="utf-8")

        # Move from In Progress to Done if present
        lines = content.split("\n")
        new_lines = []
        moved = None
        in_progress_section = False
        done_section = False

        for line in lines:
            if "## In Progress" in line:
                in_progress_section = True
                done_section = False
            elif "## Done" in line:
                in_progress_section = False
                done_section = True
            elif line.startswith("## "):
                in_progress_section = False
                done_section = False

            # Check if this task is in progress and should move to done
            if in_progress_section and task_id in line:
                moved = line
                continue

            new_lines.append(line)

        # Insert into Done
        if moved:
            for i, line in enumerate(new_lines):
                if "## Done" in line:
                    new_lines.insert(i + 2, moved)
                    break

        sprint_path.write_text("\n".join(new_lines), encoding="utf-8")

    def _run_sprint(self, sprint_name: str):
        """Execute all tasks in a sprint sequentially with full role coordination."""
        tasks = self._read_sprint_tasks(sprint_name)
        if not tasks:
            self.add_chat("system", f"[SM] No se encontraron tareas para Sprint {sprint_name} en BACKLOG.md", "SM")
            return

        total_sp = sum(t["sp"] for t in tasks)
        self.add_chat("assistant",
            f"[SM] #SPRINT-{sprint_name} INTAKE — Iniciando Sprint {sprint_name}\n\n"
            f"**{len(tasks)} tareas | {total_sp} SP**\n\n"
            + "\n".join(f"- {t['id']} {t['title']} [{t['sp']} SP]" for t in tasks),
            "SM"
        )

        completed = 0
        failed_tasks = []

        for i, task in enumerate(tasks):
            task_num = i + 1
            task_id = task["id"]
            task_title = task["title"]

            self.add_chat("assistant",
                f"[SM] Tarea {task_num}/{len(tasks)}: **{task_id} {task_title}** [{task['sp']} SP]",
                "SM"
            )

            # Create pipeline for this task
            state = self.pipeline.start(task_id, task_title)
            state.user_story = task_title
            state.story_points = task["sp"]
            state.priority = task["priority"]
            self.pipeline.save(state)

            # Run plan → exec → verify → fix
            messages = self.read_chat(limit=50)
            self._auto_advance(state, messages)

            # Check result
            final_state = self.pipeline.load()
            if final_state and final_state.phase == "complete":
                completed += 1
                self.add_chat("assistant",
                    f"[SM] {task_id} completada ({completed}/{len(tasks)})",
                    "SM"
                )
                # Update backlog and sprint
                self._update_backlog_task(task_id, "done")
                self._update_sprint_progress(task_id, task_title, task["sp"], len(tasks), completed)
                self.pipeline.clear()
            elif final_state and final_state.phase == "failed":
                failed_tasks.append(task_id)
                self.add_chat("assistant",
                    f"[SM] {task_id} falló. Continuando con la siguiente tarea.",
                    "SM"
                )
                self.pipeline.clear()
            else:
                # Pipeline in unexpected state, clean up
                self.pipeline.clear()

        # Sprint summary
        summary = (
            f"[SM] #SPRINT-{sprint_name} UPDATE — Sprint {sprint_name} finalizado\n\n"
            f"**Completadas: {completed}/{len(tasks)}**\n"
            f"**SP completados: {sum(t['sp'] for t in tasks if t['id'] not in failed_tasks)}/{total_sp}**\n"
        )
        if failed_tasks:
            summary += f"\nTareas fallidas: {', '.join(failed_tasks)}"
        self.add_chat("assistant", summary, "SM")

    # ── Main worker loop ──

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"worker-{self._label}")
        self._thread.start()
        log.info(f"[{self._label}] Worker started")

    def stop(self):
        self._running = False

    def _run(self):
        existing = self.read_chat(limit=1000)
        if existing:
            self._last_id = max(m.get("id", 0) for m in existing)

        while self._running:
            time.sleep(2)
            try:
                messages = self.read_chat(limit=100)
                if not messages:
                    continue

                new_user_msgs = [
                    m for m in messages
                    if m.get("id", 0) > self._last_id and m.get("sender") == "user"
                ]

                if not new_user_msgs:
                    self._last_id = max(m.get("id", 0) for m in messages)
                    continue

                for msg in new_user_msgs:
                    self._last_id = msg["id"]
                    user_text = msg.get("text", "").strip()
                    if not user_text:
                        continue

                    log.info(f"[{self._label}] Processing: {user_text[:80]}...")

                    # Check for sprint command: "avancemos con sprint 2", "sprint 2", "ejecuta sprint 2"
                    sprint_match = re.search(r"(?:avancemos|ejecuta|arranca|inicia|sprint)\s*(?:con\s*)?(?:sprint\s*)?(\d+)", user_text.lower())
                    if sprint_match:
                        sprint_num = sprint_match.group(1)
                        self._run_sprint(sprint_num)
                        all_msgs = self.read_chat(limit=1000)
                        if all_msgs:
                            self._last_id = max(m.get("id", 0) for m in all_msgs)
                        continue

                    state = self.pipeline.load()

                    if state and state.phase == "intake":
                        # Check if user is confirming to advance
                        confirm_words = ["si", "sí", "confirmo", "confirmar", "si confirmo", "adelante", "avanza", "ok", "dale", "proceed", "yes"]
                        is_confirm = user_text.lower().strip().rstrip(".!") in confirm_words

                        if is_confirm and state.user_story:
                            # User confirmed — advance to plan directly
                            self.add_chat("system", "[SM] Confirmado. Avanzando a planificación...", role="SM")
                            self._auto_advance(state, messages)
                        elif is_confirm and not state.user_story:
                            # User confirmed but no user story yet — extract from chat history
                            last_assistant = ""
                            for m in reversed(messages):
                                if m.get("sender") == "assistant":
                                    last_assistant = m.get("text", "")
                                    break
                            if last_assistant:
                                story, criteria = _extract_user_story(last_assistant)
                                state.user_story = story
                                state.acceptance_criteria = criteria
                                self.pipeline.save(state)
                                self.add_chat("system", "[SM] Confirmado. Avanzando a planificación...", role="SM")
                                self._auto_advance(state, messages)
                            else:
                                self.add_chat("system", "[SM] No encontré User Stories previas. Describe tu requerimiento.", role="SM")
                        else:
                            # Normal intake — send to Claude
                            self.add_chat("system", "[SM] Procesando respuesta...", role="SM")
                            prompt = build_prompt(
                                "intake", user_message=user_text, chat_history=messages,
                                project_root=str(self.project_root), methodology=self._get_methodology(),
                            )
                            response = self._invoke_claude(prompt)
                            if response:
                                self.add_chat("assistant", response, role="SM")
                                # Extract and save user story from response
                                story, criteria = _extract_user_story(response)
                                if story:
                                    state.user_story = story
                                    state.acceptance_criteria = criteria
                                    self.pipeline.save(state)
                                # Check for auto-advance marker
                                target = _detect_pipeline_marker(response)
                                if target == "plan":
                                    self._auto_advance(state, messages)
                            else:
                                self.add_chat("system", "[SM] Error procesando", role="SM")

                    elif state and state.phase not in ("complete", "failed"):
                        self.add_chat("system", f"Pipeline en fase '{state.phase}'.", role="SM")

                    else:
                        task_id = f"TASK-{int(time.time()) % 100000:05d}"
                        state = self.pipeline.start(task_id, user_text[:60])
                        log.info(f"[{self._label}] Started pipeline {task_id}")
                        self.add_chat("system", f"[SM] Iniciando intake para {task_id}...", role="SM")

                        prompt = build_prompt(
                            "intake", user_message=user_text, chat_history=messages,
                            project_root=str(self.project_root), methodology=self._get_methodology(),
                        )
                        response = self._invoke_claude(prompt)
                        if response:
                            self.add_chat("assistant", response, role="SM")
                            target = _detect_pipeline_marker(response)
                            if target == "plan":
                                story, criteria = _extract_user_story(response)
                                state.user_story = story
                                state.acceptance_criteria = criteria
                                self.pipeline.save(state)
                                self._auto_advance(state, messages)
                        else:
                            self.add_chat("system", "[SM] Error: sin respuesta", role="SM")

                    all_msgs = self.read_chat(limit=1000)
                    if all_msgs:
                        self._last_id = max(m.get("id", 0) for m in all_msgs)

            except Exception as e:
                log.error(f"[{self._label}] Worker error: {e}")
                time.sleep(5)


class ModuleWorkerPool:
    """Manages one ModuleWorker per module (plus global)."""

    def __init__(self, project_root: Path, claude_agile_dir: Path):
        self.project_root = project_root
        self.claude_agile_dir = claude_agile_dir
        self._workers: dict[str, ModuleWorker] = {}
        self._lock = threading.Lock()

    def get_or_create(self, module_name: str = "") -> ModuleWorker:
        with self._lock:
            if module_name not in self._workers:
                w = ModuleWorker(self.project_root, module_name, self.claude_agile_dir)
                w.start()
                self._workers[module_name] = w
            return self._workers[module_name]

    def start_all(self, module_names: list[str]):
        """Start workers for global + all listed modules."""
        self.get_or_create("")  # global
        for name in module_names:
            self.get_or_create(name)

    def stop_all(self):
        with self._lock:
            for w in self._workers.values():
                w.stop()


# ─── Initialize Worker Pool ──────────────────────────────────────────

_worker_pool = ModuleWorkerPool(PROJECT_ROOT, CLAUDE_AGILE_DIR)


def _invoke_claude_standalone(prompt: str, cwd: str = None) -> Optional[str]:
    """Standalone Claude invocation with full tool access."""
    work_dir = cwd or str(PROJECT_ROOT)
    cmd = [
        "claude", "-p", prompt,
        "--permission-mode", "bypassPermissions",
        "--plugin-dir", str(CLAUDE_AGILE_DIR),
    ]
    # Strip ANTHROPIC_API_KEY so claude uses OAuth session
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900,
            cwd=work_dir,
            stdin=subprocess.DEVNULL,
            env=env,
        )
        if result.stdout.strip():
            return result.stdout.strip()
        log.warning(f"Claude rc={result.returncode} stdout={result.stdout[:300]!r} stderr={result.stderr[:500]!r}")
        return None
    except subprocess.TimeoutExpired:
        log.warning("Claude invocation timed out (120s)")
        return None
    except FileNotFoundError:
        log.error("'claude' CLI not found in PATH")
        return None
    except Exception as e:
        log.error(f"Claude invocation failed: {e}")
        return None


def _detect_pipeline_marker(response: str) -> Optional[str]:
    """Detect pipeline advancement markers in agent responses."""
    import re as _re
    markers = {
        "[PIPELINE:ADVANCE_TO_PLAN]": "plan",
        "[PIPELINE:ADVANCE_TO_EXEC]": "exec",
        "[PIPELINE:ADVANCE_TO_VERIFY]": "verify",
        "[PIPELINE:ADVANCE_TO_FIX]": "fix",
        "[PIPELINE:COMPLETE]": "complete",
        "[PIPELINE:FAILED]": "failed",
    }
    for marker, target in markers.items():
        if marker in response:
            return target
    return None


def _extract_user_story(response: str) -> tuple[str, str]:
    """Try to extract user story and acceptance criteria from SM response."""
    story = response  # Use full response as fallback
    criteria = ""

    # Try to find structured sections
    if "**As a**" in response or "**Como**" in response:
        story = response
    if "Acceptance Criteria" in response or "Criterios de Aceptación" in response:
        parts = response.split("Acceptance Criteria")
        if len(parts) < 2:
            parts = response.split("Criterios de Aceptación")
        if len(parts) >= 2:
            criteria = parts[1]

    return story, criteria





    # Build phase-specific prompt
    prompt = build_prompt(
        phase,
        state_dict=state.to_dict() if state else {},
        chat_history=messages,
        project_root=str(PROJECT_ROOT),
        methodology=_get_methodology(),
    )

    if not prompt:
        _add_chat("system", f"{label} Error: no se pudo generar el prompt para la fase {phase}", role=role["tag"])
        return None

    response = _invoke_claude(prompt)
    if not response:
        _add_chat("system", f"{label} Error: sin respuesta de Claude Code", role=role["tag"])
        return None

    # Post response to chat
    _add_chat("assistant", response, role=role["tag"])
    return response


def _parse_plan_tasks(plan_text: str) -> list[dict]:
    """Parse numbered tasks from a TL plan response."""
    tasks = []
    import re as _re
    # Match patterns like "1. Task title" or "- Task title" or "### Task 1: title"
    lines = plan_text.split("\n")
    current_task = None

    for line in lines:
        stripped = line.strip()
        # Numbered list: "1. ", "2. ", etc.
        match = _re.match(r"^(\d+)\.\s+\*?\*?(.+?)[\*]*$", stripped)
        if not match:
            # Also try "- **Task**: description"
            match = _re.match(r"^[-•]\s+\*?\*?(.+?)[\*]*$", stripped)
            if match:
                title = match.group(1).strip()
                if len(title) > 10:  # Skip short bullets that aren't tasks
                    if current_task:
                        tasks.append(current_task)
                    current_task = {"id": f"task-{len(tasks)}", "title": title, "description": title}
                elif current_task:
                    current_task["description"] += f"\n{stripped}"
                continue

        if match:
            if current_task:
                tasks.append(current_task)
            title = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()
            current_task = {"id": f"task-{len(tasks)}", "title": title, "description": title}
        elif current_task and stripped:
            current_task["description"] += f"\n{stripped}"

    if current_task:
        tasks.append(current_task)

    # Filter out non-task items (too short, headers, etc.)
    tasks = [t for t in tasks if len(t["title"]) > 15]

    return tasks[:10]  # Cap at 10 tasks






# ─── Markdown Parsers ─────────────────────────────────────────────────


def parse_backlog(content: str) -> dict:
    """Parse BACKLOG.md into structured data."""
    items = {"active": [], "completed": []}
    current_section = None

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## Active"):
            current_section = "active"
        elif line.startswith("## Completed"):
            current_section = "completed"
        elif current_section and line.startswith("- "):
            text = line[2:]
            priority_match = re.match(r"\*\*(\w+)\*\*", text)
            priority = priority_match.group(1) if priority_match else "P3"
            sp_match = re.search(r"\[(\d+)\s*SP\]", text)
            sp = int(sp_match.group(1)) if sp_match else 0
            blocked = "[BLOCKED]" in text or "\U0001f534" in text
            blocker_match = re.search(r"\[BLOCKED(?:\s*by\s+(.+?))?\]", text)
            blocked_by = blocker_match.group(1) if blocker_match and blocker_match.group(1) else None
            parts = text.split("|")
            title = parts[1].strip() if len(parts) > 1 else text.replace(f"**{priority}**", "").strip()
            title = re.sub(r"\[\d+\s*SP\]", "", title).strip()
            title = re.sub(r"\[BLOCKED.*?\]", "", title).strip()
            status = parts[-1].strip() if len(parts) > 2 else "backlog"
            items[current_section].append({
                "priority": priority, "title": title, "status": status,
                "sp": sp, "blocked": blocked, "blocked_by": blocked_by,
            })

    return items


def parse_sprint(content: str) -> dict:
    """Parse SPRINT.md into structured data."""
    result = {
        "goal": "", "in_progress": [], "done": [], "metrics": {},
        "wip_limit": 2, "sprint_start": None, "sprint_end": None,
        "total_sp_planned": 0, "total_sp_done": 0,
    }
    current_section = None

    for line in content.split("\n"):
        line = line.strip()
        if "WIP limit:" in line:
            m = re.search(r"WIP limit:\s*\*\*(\d+)", line)
            if m:
                result["wip_limit"] = int(m.group(1))
        elif line.startswith("## Sprint Goal") or line.startswith("> Goal:"):
            goal_match = re.search(r"Goal:\s*(.+)", line)
            if goal_match:
                result["goal"] = goal_match.group(1).strip()
        elif "Sprint:" in line or "Cycle:" in line:
            date_match = re.findall(r"(\d{4}-\d{2}-\d{2})", line)
            if len(date_match) >= 1:
                result["sprint_start"] = date_match[0]
            if len(date_match) >= 2:
                result["sprint_end"] = date_match[1]
        elif line.startswith("## In Progress"):
            current_section = "in_progress"
        elif line.startswith("## Done"):
            current_section = "done"
        elif line.startswith("## Cycle Metrics") or line.startswith("## Sprint Metrics"):
            current_section = "metrics"
        elif current_section in ("in_progress", "done") and line.startswith("- "):
            text = line[2:]
            if text.startswith("_"):
                continue
            sp_match = re.search(r"\[(\d+)\s*SP\]", text)
            sp = int(sp_match.group(1)) if sp_match else 0
            blocked = "[BLOCKED]" in text
            blocker_match = re.search(r"\[BLOCKED(?:\s*by\s+(.+?))?\]", text)
            blocked_by = blocker_match.group(1) if blocker_match and blocker_match.group(1) else None
            title = re.sub(r"\[\d+\s*SP\]", "", text).strip()
            title = re.sub(r"\[BLOCKED.*?\]", "", title).strip()

            item = {"title": title, "sp": sp, "blocked": blocked, "blocked_by": blocked_by}
            result[current_section].append(item)

            if current_section == "done":
                result["total_sp_done"] += sp
            result["total_sp_planned"] += sp

        elif current_section == "metrics" and "|" in line and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) == 2 and parts[0] != "Metric":
                result["metrics"][parts[0]] = parts[1]

    return result


def parse_daily(content: str) -> list:
    """Parse DAILY.md into session entries."""
    sessions = []
    current_session = None

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("### "):
            if current_session:
                sessions.append(current_session)
            current_session = {"date": line[4:], "entries": [], "blockers": [], "tdd_status": None}
        elif current_session and line.startswith("- "):
            entry = line[2:]
            if entry.lower().startswith("blocker"):
                current_session["blockers"].append(entry)
            elif entry.lower().startswith("tdd"):
                current_session["tdd_status"] = entry
            else:
                current_session["entries"].append(entry)

    if current_session:
        sessions.append(current_session)
    return sessions


def parse_retro(content: str) -> dict:
    """Parse RETRO.md for velocity and burndown data."""
    result = {
        "velocity_history": [], "current_cycle": {"number": 1, "started": None, "points_planned": 0, "points_completed": 0},
        "daily_burndown": [], "blockers_log": [],
    }
    section = None

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## Velocity History"):
            section = "velocity"
        elif line.startswith("## Current Cycle"):
            section = "current"
        elif line.startswith("### Daily Burndown"):
            section = "burndown"
        elif line.startswith("## Blockers Log"):
            section = "blockers"
        elif line.startswith("## ") or line.startswith("### "):
            section = None
        elif section == "velocity" and "|" in line and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4 and parts[0] != "Cycle" and not parts[0].startswith("_"):
                try:
                    result["velocity_history"].append({
                        "cycle": parts[0], "period": parts[1],
                        "points": int(parts[2]) if parts[2].isdigit() else 0,
                        "items": int(parts[3]) if parts[3].isdigit() else 0,
                    })
                except (ValueError, IndexError):
                    pass
        elif section == "current":
            if "**Started**" in line:
                m = re.search(r":\s*(.+)", line)
                if m:
                    result["current_cycle"]["started"] = m.group(1).strip()
            elif "**Points Planned**" in line:
                m = re.search(r":\s*(\d+)", line)
                if m:
                    result["current_cycle"]["points_planned"] = int(m.group(1))
            elif "**Points Completed**" in line:
                m = re.search(r":\s*(\d+)", line)
                if m:
                    result["current_cycle"]["points_completed"] = int(m.group(1))
        elif section == "burndown" and "|" in line and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2 and parts[0] != "Date":
                try:
                    result["daily_burndown"].append({"date": parts[0], "remaining": int(parts[1]) if parts[1].isdigit() else 0})
                except (ValueError, IndexError):
                    pass
        elif section == "blockers" and "|" in line and not line.startswith("|--"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 4 and parts[0] != "Date":
                result["blockers_log"].append({"date": parts[0], "task": parts[1], "flagged_by": parts[2], "status": parts[3]})

    return result


# ─── Computed Metrics ─────────────────────────────────────────────────


def collect_blockers(sprint: dict, daily: list) -> list:
    blockers = []
    for item in sprint.get("in_progress", []):
        if item.get("blocked"):
            blockers.append({"task": item["title"], "source": "sprint"})
    for session in reversed(daily[-5:] if daily else []):
        for b in session.get("blockers", []):
            blockers.append({"task": b, "since": session.get("date"), "source": "daily"})
    return blockers


def compute_sprint_health(sprint: dict, retro: dict) -> dict:
    now = datetime.now()
    start, end = sprint.get("sprint_start"), sprint.get("sprint_end")
    days_remaining, days_total, day_of_sprint = None, None, None

    if start and end:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            end_dt = datetime.strptime(end, "%Y-%m-%d")
            days_total = (end_dt - start_dt).days
            days_remaining = max(0, (end_dt - now).days)
            day_of_sprint = max(0, (now - start_dt).days)
        except ValueError:
            pass

    total_planned = sprint.get("total_sp_planned", 0) or retro.get("current_cycle", {}).get("points_planned", 0)
    total_done = sprint.get("total_sp_done", 0) or retro.get("current_cycle", {}).get("points_completed", 0)
    progress = (total_done / total_planned * 100) if total_planned > 0 else 0
    blocker_count = sum(1 for item in sprint.get("in_progress", []) if item.get("blocked"))

    status = "on_track"
    if blocker_count > 0:
        status = "at_risk"
    if days_remaining is not None and days_total and days_total > 0:
        expected = ((days_total - days_remaining) / days_total) * 100
        if progress < expected - 20:
            status = "behind"
        elif progress < expected - 10:
            status = "at_risk"

    return {
        "goal": sprint.get("goal", ""), "days_remaining": days_remaining,
        "days_total": days_total, "day_of_sprint": day_of_sprint,
        "sp_completed": total_done, "sp_planned": total_planned,
        "progress": round(progress, 1), "blocker_count": blocker_count, "status": status,
    }


def compute_burndown(sprint: dict, retro: dict) -> dict:
    health = compute_sprint_health(sprint, retro)
    total_sp = health["sp_planned"]
    days_total = health["days_total"] or 14

    ideal = [{"day": d, "value": round(total_sp - (total_sp * d / days_total), 1)} for d in range(days_total + 1)]
    actual = [{"date": e["date"], "value": e["remaining"]} for e in retro.get("daily_burndown", [])]

    if not actual and total_sp > 0:
        day_of = health.get("day_of_sprint") or 0
        actual = [{"day": 0, "value": total_sp}, {"day": day_of, "value": total_sp - health["sp_completed"]}]

    return {"ideal": ideal, "actual": actual, "total_sp": total_sp, "days_total": days_total, "status": health["status"]}


def compute_velocity(retro: dict) -> dict:
    history = retro.get("velocity_history", [])
    recent = history[-3:] if len(history) > 3 else history
    points = [h.get("points", 0) for h in recent]
    avg = round(sum(points) / len(points), 1) if points else 0
    return {"history": recent, "average": avg, "estimated_next": round(avg)}


# ─── GitHub Info ──────────────────────────────────────────────────────


def read_github_info() -> dict:
    info = {"repo_url": None, "current_branch": None, "last_commit": None, "open_prs": 0, "ci_status": None}

    def _run(cmd, timeout=5):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(PROJECT_ROOT))
            return r.stdout.strip() if r.returncode == 0 else None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    info["current_branch"] = _run(["git", "branch", "--show-current"])

    log_out = _run(["git", "log", "-1", "--format=%h|%s|%ar"])
    if log_out:
        parts = log_out.split("|", 2)
        if len(parts) == 3:
            info["last_commit"] = {"hash": parts[0], "message": parts[1], "time_ago": parts[2]}

    url = _run(["git", "remote", "get-url", "origin"])
    if url:
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        info["repo_url"] = url.rstrip(".git")

    if info["repo_url"]:
        pr_out = _run(["gh", "pr", "list", "--state", "open", "--json", "number"], timeout=10)
        if pr_out:
            try:
                info["open_prs"] = len(json.loads(pr_out))
            except json.JSONDecodeError:
                pass

        ci_out = _run(["gh", "run", "list", "--limit", "1", "--json", "status,conclusion"], timeout=10)
        if ci_out:
            try:
                runs = json.loads(ci_out)
                if runs:
                    r = runs[0]
                    if r.get("status") == "in_progress":
                        info["ci_status"] = "running"
                    elif r.get("conclusion") == "success":
                        info["ci_status"] = "success"
                    elif r.get("conclusion") == "failure":
                        info["ci_status"] = "failure"
                    else:
                        info["ci_status"] = r.get("conclusion") or r.get("status")
            except json.JSONDecodeError:
                pass

    return info


# ─── Team Roles ───────────────────────────────────────────────────────


def read_team_roles() -> list:
    """Read role configuration from config.json."""
    config_path = PROJECT_ROOT / ".claude-agile" / "config.json"
    if not config_path.exists():
        return []

    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError:
        return []

    roles_config = config.get("roles", {})
    all_roles = []

    ROLE_META = {
        "scrumMaster": {"name": "Scrum Master", "color": "#a855f7", "tag": "SM", "team": "core"},
        "techLead": {"name": "Tech Lead", "color": "#14b8a6", "tag": "TL", "team": "core"},
        "developer": {"name": "Developer", "color": "#3b82f6", "tag": "DEV", "team": "core"},
        "qa": {"name": "QA", "color": "#22c55e", "tag": "QA", "team": "core"},
        "productOwner": {"name": "Product Owner", "color": "#f59e0b", "tag": "PO", "team": "core"},
        "cloudArchitect": {"name": "Cloud Architect", "color": "#f97316", "tag": "ARCH", "team": "infra"},
        "devopsEngineer": {"name": "DevOps Engineer", "color": "#eab308", "tag": "DEVOPS", "team": "infra"},
        "dba": {"name": "DBA", "color": "#92400e", "tag": "DBA", "team": "infra"},
        "observabilityEngineer": {"name": "Observability", "color": "#06b6d4", "tag": "OBS", "team": "infra"},
        "securityEngineer": {"name": "Security Engineer", "color": "#ef4444", "tag": "SEC", "team": "security"},
        "penTester": {"name": "Pen Tester", "color": "#991b1b", "tag": "PENTEST", "team": "security"},
        "uxDesigner": {"name": "UX Designer", "color": "#ec4899", "tag": "UX", "team": "product"},
        "dataEngineer": {"name": "Data Engineer", "color": "#6366f1", "tag": "DATA", "team": "product"},
    }

    for team_key, team_roles in roles_config.items():
        if isinstance(team_roles, dict):
            for role_key, role_val in team_roles.items():
                meta = ROLE_META.get(role_key, {"name": role_key, "color": "#666", "tag": role_key[:3].upper(), "team": team_key})
                if isinstance(role_val, dict):
                    status = role_val.get("status", "standby")
                    relevant = role_val.get("relevant", False)
                else:
                    status = "active" if role_val == "AI" or role_val == "User" else "standby"
                    relevant = True
                all_roles.append({**meta, "status": status, "relevant": relevant, "key": role_key})

    return all_roles


# ─── Project State ────────────────────────────────────────────────────


def read_project_state() -> dict:
    state = {
        "timestamp": time.time(),
        "project_root": str(PROJECT_ROOT),
        "project_name": PROJECT_ROOT.name,
        "methodology": "lean-xp",
        "backlog": {"active": [], "completed": []},
        "sprint": {"goal": "", "in_progress": [], "done": [], "metrics": {}, "wip_limit": 2},
        "daily": [],
        "retro": {"velocity_history": [], "current_cycle": {}, "daily_burndown": [], "blockers_log": []},
        "config": {},
        "blockers": [],
        "sprint_health": {},
        "burndown": {},
        "velocity": {},
        "github": {},
        "team": [],
    }

    files = {
        "backlog": PROJECT_ROOT / "BACKLOG.md",
        "sprint": PROJECT_ROOT / "SPRINT.md",
        "daily": PROJECT_ROOT / "DAILY.md",
        "retro": PROJECT_ROOT / "RETRO.md",
    }
    config_path = PROJECT_ROOT / ".claude-agile" / "config.json"

    if files["backlog"].exists():
        state["backlog"] = parse_backlog(files["backlog"].read_text())
    if files["sprint"].exists():
        state["sprint"] = parse_sprint(files["sprint"].read_text())
    if files["daily"].exists():
        state["daily"] = parse_daily(files["daily"].read_text())
    if files["retro"].exists():
        state["retro"] = parse_retro(files["retro"].read_text())
    if config_path.exists():
        try:
            state["config"] = json.loads(config_path.read_text())
        except json.JSONDecodeError:
            pass

    state["methodology"] = state["config"].get("methodology", "lean-xp")
    state["blockers"] = collect_blockers(state["sprint"], state["daily"])
    state["sprint_health"] = compute_sprint_health(state["sprint"], state["retro"])
    state["burndown"] = compute_burndown(state["sprint"], state["retro"])
    state["velocity"] = compute_velocity(state["retro"])
    state["github"] = read_github_info()
    state["team"] = read_team_roles()
    state["workspaces"] = _load_workspaces()

    total_active = len(state["backlog"]["active"])
    total_done_backlog = len(state["backlog"]["completed"])
    in_progress = len(state["sprint"]["in_progress"])
    done_cycle = len(state["sprint"]["done"])

    state["summary"] = {
        "total_items": total_active + total_done_backlog,
        "backlog_count": total_active,
        "in_progress_count": in_progress,
        "done_count": done_cycle + total_done_backlog,
        "wip_limit": state["sprint"]["wip_limit"],
        "wip_ok": in_progress <= state["sprint"]["wip_limit"],
        "sessions_count": len(state["daily"]),
    }

    return state


# ─── API Endpoints ────────────────────────────────────────────────────


# ─── Serve React Frontend ─────────────────────────────────────────────

FRONTEND_DIST = DASHBOARD_DIR / "frontend" / "dist"

@app.get("/", response_class=HTMLResponse)
async def index():
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    # Fallback to legacy index.html
    return FileResponse(DASHBOARD_DIR / "index.html")


@app.get("/api/requirement/{slug}")
async def get_requirement(slug: str):
    """Read a persisted requirement file."""
    path = PROJECT_ROOT / ".claude-agile" / "requerimientos" / slug / "requerimiento.md"
    if path.exists():
        return {"content": path.read_text(encoding="utf-8"), "slug": slug}
    return {"error": "Not found"}


@app.get("/api/state")
async def get_state():
    return read_project_state()


@app.get("/api/chat/history")
async def get_chat_history(limit: int = 50):
    """Read team chat messages from the active module's log."""
    worker = _worker_pool.get_or_create(_active_module)
    messages = worker.read_chat(limit)
    return {"messages": messages, "available": True}


@app.post("/api/chat/send")
async def send_chat(body: dict):
    """User sends a message — the module's worker picks it up automatically."""
    message = body.get("message", "")
    if not message:
        return {"error": "No message"}

    worker = _worker_pool.get_or_create(_active_module)
    entry = worker.add_chat("user", message)
    return {"ok": True, "id": entry["id"]}


@app.get("/api/skills")
async def get_skills():
    """List all loaded skills."""
    return {"skills": _skill_registry.list_all()}


@app.get("/api/pipeline")
async def get_pipeline():
    """Get current pipeline state + worker status."""
    worker = _worker_pool.get_or_create(_active_module)
    state = worker.pipeline.load()
    if not state:
        return {"active": False, "module": _active_module}
    result = {
        "active": True,
        "module": _active_module,
        "phase": state.phase,
        "task_id": state.task_id,
        "title": state.title,
        "fix_attempts": state.fix_attempts,
        "status_line": worker.pipeline.get_status_line(state),
        "phase_history": state.phase_history,
    }
    if worker._worker_manager:
        result["workers"] = worker._worker_manager.get_status()
    return result


# ─── Workspace API ────────────────────────────────────────────────────


@app.get("/api/workspaces")
async def get_workspaces():
    config = _load_workspaces()
    config["active_module"] = _active_module
    return config


@app.put("/api/workspaces/active")
async def set_active_workspace(body: dict):
    name = body.get("name", "")
    if not name:
        return {"error": "name required"}
    if not _switch_workspace(name):
        return {"error": f"Workspace '{name}' not found or path invalid"}
    return {"ok": True, "active": name, "state": read_project_state()}


@app.post("/api/workspaces")
async def add_workspace(body: dict):
    name = body.get("name", "").strip()
    path = body.get("path", "").strip()
    if not name or not path:
        return {"error": "name and path required"}

    resolved = Path(path).resolve()
    if not resolved.exists():
        try:
            resolved.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {"error": f"Could not create directory '{path}': {e}"}

    if not resolved.is_dir():
        return {"error": f"Path '{path}' is not a valid directory"}

    config = _load_workspaces()
    if any(w["name"] == name for w in config["workspaces"]):
        return {"error": f"Workspace '{name}' already exists"}

    config["workspaces"].append({"name": name, "path": str(resolved), "modules": []})
    _save_workspaces(config)
    return {"ok": True, "workspaces": config}


@app.delete("/api/workspaces/{name}")
async def delete_workspace(name: str):
    config = _load_workspaces()
    if config["active"] == name:
        return {"error": "Cannot delete the active workspace"}
    config["workspaces"] = [w for w in config["workspaces"] if w["name"] != name]
    _save_workspaces(config)
    return {"ok": True, "workspaces": config}


@app.put("/api/modules/active")
async def set_active_module(body: dict):
    """Switch the active module context. Empty string = global."""
    module = body.get("module", "")
    if module:
        config = _load_workspaces()
        ws = next((w for w in config["workspaces"] if w["name"] == config.get("active")), None)
        if not ws or module not in ws.get("modules", []):
            return {"error": f"Module '{module}' not found in active workspace"}
    _switch_module(module)
    return {"ok": True, "module": module}


@app.post("/api/workspaces/{name}/modules")
async def add_module(name: str, body: dict):
    module = body.get("module", "").strip()
    if not module:
        return {"error": "module required"}
    config = _load_workspaces()
    ws = next((w for w in config["workspaces"] if w["name"] == name), None)
    if not ws:
        return {"error": f"Workspace '{name}' not found"}
    if module not in ws["modules"]:
        ws["modules"].append(module)
        _save_workspaces(config)

        # Create module directory structure
        mod_dir = Path(ws["path"]) / ".claude-agile" / "modules" / module
        mod_dir.mkdir(parents=True, exist_ok=True)
        (mod_dir / "history").mkdir(exist_ok=True)
        (mod_dir / "plans").mkdir(exist_ok=True)
        (mod_dir / "sessions").mkdir(exist_ok=True)

    return {"ok": True, "modules": ws["modules"]}


@app.delete("/api/workspaces/{ws_name}/modules/{module}")
async def delete_module(ws_name: str, module: str):
    config = _load_workspaces()
    ws = next((w for w in config["workspaces"] if w["name"] == ws_name), None)
    if not ws:
        return {"error": f"Workspace '{ws_name}' not found"}
    ws["modules"] = [m for m in ws["modules"] if m != module]
    _save_workspaces(config)
    return {"ok": True, "modules": ws["modules"]}


# ─── WebSocket ────────────────────────────────────────────────────────

connected_clients: set[WebSocket] = set()


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.add(ws)
    try:
        await ws.send_json({"type": "state", "data": read_project_state()})
        while True:
            try:
                data = await asyncio.wait_for(ws.receive_text(), timeout=3.0)
                msg = json.loads(data)
                if msg.get("type") == "refresh":
                    await ws.send_json({"type": "state", "data": read_project_state()})
            except asyncio.TimeoutError:
                await ws.send_json({"type": "state", "data": read_project_state()})
    except WebSocketDisconnect:
        connected_clients.discard(ws)
    except Exception:
        connected_clients.discard(ws)


# ─── Static Assets ────────────────────────────────────────────────────

_assets_dir = DASHBOARD_DIR / "frontend" / "dist" / "assets"
if _assets_dir.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")


# ─── Main ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

    # Discover modules for this project
    _ws_config = _load_workspaces()
    _ws_entry = next((w for w in _ws_config.get("workspaces", []) if Path(w["path"]).resolve() == PROJECT_ROOT.resolve()), None)
    _modules = _ws_entry.get("modules", []) if _ws_entry else []

    print(f"\n  claude-agile Dashboard v4.0 (multi-module workers)")
    print(f"  http://localhost:{PORT}")
    print(f"  Project: {PROJECT_ROOT}")
    print(f"  Modules: {_modules if _modules else ['(global only)']}")
    print(f"  Mode: {'project' if IS_PROJECT_MODE else 'standalone'}\n")

    # Start workers: global + all modules
    _worker_pool.start_all(_modules)

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
