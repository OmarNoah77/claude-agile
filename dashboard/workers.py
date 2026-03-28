"""
tmux-based parallel worker manager for claude-agile pipeline.

Spawns multiple Claude Code workers in tmux panes for parallel task execution.
Inspired by oh-my-claudecode's team runtime.

Usage:
    manager = WorkerManager(project_root, num_workers=2)
    manager.start(tasks)  # List of task dicts
    manager.wait()        # Block until all done
    results = manager.results()
    manager.shutdown()
"""

import json
import logging
import os
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger("claude-agile.workers")

TMUX_SESSION = "claude-agile-workers"
WORKER_TIMEOUT = 600  # seconds per task (10 min)
HEARTBEAT_INTERVAL = 5
STALL_THRESHOLD = 3  # missed heartbeats before kill


@dataclass
class Task:
    id: str
    title: str
    description: str
    status: str = "pending"       # pending, in_progress, completed, failed
    owner: str = ""               # worker name
    result: str = ""              # worker output
    started_at: float = 0.0
    completed_at: float = 0.0


@dataclass
class Worker:
    name: str
    pane_id: str = ""
    task_id: str = ""
    status: str = "idle"          # idle, working, done, failed
    pid: int = 0
    heartbeat: float = 0.0


class WorkerManager:
    """Manages parallel Claude Code workers in tmux panes."""

    def __init__(self, project_root: Path, state_dir: Path, num_workers: int = 2,
                 on_chat: callable = None):
        self.project_root = project_root
        self.state_dir = state_dir / "workers"
        self.num_workers = min(num_workers, 4)  # Cap at 4 to avoid overload
        self.on_chat = on_chat  # Callback to post messages to team chat

        self.tasks: list[Task] = []
        self.workers: list[Worker] = []
        self._lock = threading.Lock()
        self._running = False
        self._watchdog_thread: Optional[threading.Thread] = None

    # ─── Setup ────────────────────────────────────────────────────

    def _ensure_dirs(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        for i in range(self.num_workers):
            (self.state_dir / f"worker-{i}").mkdir(exist_ok=True)

    def _chat(self, text: str, role: str = "DEV"):
        """Post a message to the team chat."""
        if self.on_chat:
            self.on_chat("system", text, role)

    # ─── tmux Management ─────────────────────────────────────────

    def _run_tmux(self, *args) -> tuple[bool, str]:
        """Run a tmux command, return (success, output)."""
        try:
            result = subprocess.run(
                ["tmux"] + list(args),
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            log.error(f"tmux error: {e}")
            return False, str(e)

    def _session_exists(self) -> bool:
        ok, _ = self._run_tmux("has-session", "-t", TMUX_SESSION)
        return ok

    def _create_session(self):
        """Create a detached tmux session for workers."""
        if self._session_exists():
            self._kill_session()
        self._run_tmux(
            "new-session", "-d", "-s", TMUX_SESSION,
            "-x", "200", "-y", "50",
        )
        # Propagate API keys to the tmux session environment
        for key in ["ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "RESEND_API_KEY"]:
            val = os.environ.get(key)
            if val:
                self._run_tmux("set-environment", "-t", TMUX_SESSION, key, val)
        log.info(f"Created tmux session: {TMUX_SESSION}")

    def _kill_session(self):
        """Kill the worker tmux session."""
        self._run_tmux("kill-session", "-t", TMUX_SESSION)
        log.info(f"Killed tmux session: {TMUX_SESSION}")

    def _create_pane(self, worker_name: str) -> str:
        """Create a new tmux pane and return its pane_id."""
        ok, output = self._run_tmux(
            "split-window", "-h",
            "-t", TMUX_SESSION,
            "-d", "-P", "-F", "#{pane_id}",
        )
        if ok and output:
            pane_id = output.strip()
            # Rebalance layout
            self._run_tmux("select-layout", "-t", TMUX_SESSION, "tiled")
            log.info(f"Created pane {pane_id} for {worker_name}")
            return pane_id
        log.error(f"Failed to create pane for {worker_name}: {output}")
        return ""

    def _kill_pane(self, pane_id: str):
        """Kill a specific tmux pane."""
        if pane_id:
            self._run_tmux("kill-pane", "-t", pane_id)

    def _pane_alive(self, pane_id: str) -> bool:
        """Check if a tmux pane still exists."""
        ok, _ = self._run_tmux("has-session", "-t", pane_id)
        return ok

    def _send_to_pane(self, pane_id: str, command: str):
        """Send a command to a tmux pane."""
        self._run_tmux("send-keys", "-t", pane_id, command, "Enter")

    # ─── Task Management ─────────────────────────────────────────

    def _next_pending_task(self) -> Optional[Task]:
        """Get the next pending task."""
        with self._lock:
            for task in self.tasks:
                if task.status == "pending":
                    return task
        return None

    def _all_done(self) -> bool:
        """Check if all tasks are completed or failed."""
        with self._lock:
            return all(t.status in ("completed", "failed") for t in self.tasks)

    def _save_task_state(self):
        """Persist task state to disk."""
        self._ensure_dirs()
        state_file = self.state_dir / "tasks.json"
        with self._lock:
            data = [{
                "id": t.id, "title": t.title, "status": t.status,
                "owner": t.owner, "result": t.result[:500],
            } for t in self.tasks]
        state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # ─── Worker Execution ────────────────────────────────────────

    def _build_worker_prompt(self, task: Task) -> str:
        """Build the prompt for a worker to execute a specific task."""
        return f"""You are a Developer (DEV) worker executing a specific task as part of a parallel team.

## Your Task
**{task.title}**

{task.description}

## Project Root: {self.project_root}

## Instructions
1. Focus ONLY on this specific task — do not work on other tasks
2. Implement the task completely
3. Describe the changes you would make (files to modify, code to write)
4. Be specific with file paths and code snippets
5. When done, write EXACTLY: [WORKER:DONE]
6. If you cannot complete the task, write: [WORKER:FAILED] with the reason
7. Write ONLY plain text — no tool calls
8. Respond in Spanish
"""

    def _spawn_worker(self, worker: Worker, task: Task):
        """Spawn a Claude Code worker in a tmux pane for a task."""
        with self._lock:
            task.status = "in_progress"
            task.owner = worker.name
            task.started_at = time.time()
            worker.task_id = task.id
            worker.status = "working"
            worker.heartbeat = time.time()

        prompt = self._build_worker_prompt(task)
        worker_dir = self.state_dir / worker.name

        # Write task info to worker directory
        (worker_dir / "task.json").write_text(json.dumps({
            "id": task.id, "title": task.title, "description": task.description,
        }, ensure_ascii=False), encoding="utf-8")

        # Write the prompt to a file (avoids shell escaping issues)
        prompt_file = worker_dir / "prompt.txt"
        prompt_file.write_text(prompt, encoding="utf-8")

        # Output file for capturing result
        output_file = worker_dir / "output.txt"
        if output_file.exists():
            output_file.unlink()

        # Build the command to run in the pane (interactive mode with full tools, using OAuth session)
        cmd = f'unset ANTHROPIC_API_KEY && claude -p "$(cat {prompt_file})" --permission-mode bypassPermissions < /dev/null > {output_file} 2>&1; echo "[EXIT:$?]" >> {output_file}'

        self._chat(f"[DEV] Worker {worker.name} iniciando: {task.title[:60]}...", "DEV")
        log.info(f"Spawning {worker.name} for task {task.id}: {task.title[:60]}")

        # Send command to tmux pane
        self._send_to_pane(worker.pane_id, f'cd "{self.project_root}" && {cmd}')

    def _check_worker_completion(self, worker: Worker) -> Optional[str]:
        """Check if a worker has completed by reading its output file."""
        output_file = self.state_dir / worker.name / "output.txt"
        if not output_file.exists():
            return None

        try:
            content = output_file.read_text(encoding="utf-8")
            if "[EXIT:" in content or "[WORKER:DONE]" in content or "[WORKER:FAILED]" in content:
                return content
        except Exception:
            pass
        return None

    # ─── Watchdog ────────────────────────────────────────────────

    def _watchdog(self):
        """Background thread that monitors workers and assigns tasks."""
        log.info("Watchdog started")

        while self._running and not self._all_done():
            time.sleep(HEARTBEAT_INTERVAL)

            for worker in self.workers:
                if worker.status == "working":
                    # Check if worker completed
                    output = self._check_worker_completion(worker)
                    if output:
                        task = next((t for t in self.tasks if t.id == worker.task_id), None)
                        if task:
                            with self._lock:
                                if "[WORKER:FAILED]" in output:
                                    task.status = "failed"
                                    task.result = output
                                    self._chat(f"[DEV] Worker {worker.name} falló: {task.title[:40]}", "DEV")
                                else:
                                    task.status = "completed"
                                    task.result = output
                                    self._chat(f"[DEV] Worker {worker.name} completó: {task.title[:40]}", "DEV")
                                task.completed_at = time.time()
                                worker.status = "idle"
                                worker.task_id = ""

                        self._save_task_state()

                    # Check for stall (timeout)
                    elif time.time() - worker.heartbeat > WORKER_TIMEOUT:
                        log.warning(f"Worker {worker.name} stalled on task {worker.task_id}")
                        task = next((t for t in self.tasks if t.id == worker.task_id), None)
                        if task:
                            with self._lock:
                                task.status = "failed"
                                task.result = "Timeout"
                                task.completed_at = time.time()
                        self._kill_pane(worker.pane_id)
                        worker.pane_id = self._create_pane(worker.name)
                        worker.status = "idle"
                        worker.task_id = ""
                        self._chat(f"[DEV] Worker {worker.name} timeout — restarted", "DEV")

                # Assign new tasks to idle workers
                if worker.status == "idle":
                    next_task = self._next_pending_task()
                    if next_task:
                        self._spawn_worker(worker, next_task)

        log.info("Watchdog finished — all tasks done")
        self._running = False

    # ─── Public API ──────────────────────────────────────────────

    def start(self, tasks: list[dict]):
        """Start parallel execution of tasks."""
        self._ensure_dirs()

        # Convert task dicts to Task objects
        self.tasks = [
            Task(
                id=t.get("id", f"task-{i}"),
                title=t.get("title", f"Task {i+1}"),
                description=t.get("description", t.get("title", "")),
            )
            for i, t in enumerate(tasks)
        ]

        if not self.tasks:
            log.warning("No tasks to execute")
            return

        self._chat(f"[DEV] Iniciando {len(self.tasks)} tareas con {self.num_workers} workers paralelos", "DEV")

        # Create tmux session and worker panes
        self._create_session()
        self.workers = []
        for i in range(min(self.num_workers, len(self.tasks))):
            name = f"worker-{i}"
            pane_id = self._create_pane(name) if i > 0 else ""
            if i == 0:
                # First worker uses the initial pane
                ok, output = self._run_tmux(
                    "list-panes", "-t", TMUX_SESSION, "-F", "#{pane_id}",
                )
                pane_id = output.split("\n")[0].strip() if ok else ""
            self.workers.append(Worker(name=name, pane_id=pane_id))

        # Assign initial tasks
        self._running = True
        for worker in self.workers:
            task = self._next_pending_task()
            if task:
                self._spawn_worker(worker, task)

        # Start watchdog
        self._watchdog_thread = threading.Thread(target=self._watchdog, daemon=True)
        self._watchdog_thread.start()

    def wait(self, timeout: float = 600) -> bool:
        """Wait for all tasks to complete. Returns True if all done."""
        if self._watchdog_thread:
            self._watchdog_thread.join(timeout=timeout)
        return self._all_done()

    def results(self) -> list[dict]:
        """Get results of all tasks."""
        with self._lock:
            return [{
                "id": t.id, "title": t.title, "status": t.status,
                "result": t.result[:1000], "owner": t.owner,
                "duration": (t.completed_at - t.started_at) if t.completed_at else 0,
            } for t in self.tasks]

    def shutdown(self):
        """Clean up tmux session and state."""
        self._running = False
        if self._session_exists():
            self._kill_session()
        self._save_task_state()
        log.info("Worker manager shut down")

    def get_status(self) -> dict:
        """Get current worker status for the dashboard."""
        with self._lock:
            pending = sum(1 for t in self.tasks if t.status == "pending")
            in_progress = sum(1 for t in self.tasks if t.status == "in_progress")
            completed = sum(1 for t in self.tasks if t.status == "completed")
            failed = sum(1 for t in self.tasks if t.status == "failed")
            return {
                "total": len(self.tasks),
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
                "failed": failed,
                "workers": [{
                    "name": w.name, "status": w.status, "task_id": w.task_id,
                } for w in self.workers],
            }
