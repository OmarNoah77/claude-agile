"""
Pipeline state machine for claude-agile.

Phases: intake → plan → exec → verify → fix → complete
Maps to roles: SM(intake) → TL(plan) → DEV(exec) → QA(verify) → DEV(fix)

Inspired by oh-my-claudecode's team-pipeline architecture.
"""

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ─── Phase Definitions ───────────────────────────────────────────────

PHASES = ["intake", "plan", "exec", "verify", "fix", "complete", "failed"]

TRANSITIONS = {
    "intake": ["plan", "failed"],
    "plan": ["exec", "failed"],
    "exec": ["verify", "failed"],
    "verify": ["fix", "complete", "failed"],
    "fix": ["verify", "exec", "failed"],
}

PHASE_ROLES = {
    "intake": {"tag": "SM", "name": "Scrum Master", "color": "#a855f7"},
    "plan": {"tag": "TL", "name": "Tech Lead", "color": "#14b8a6"},
    "exec": {"tag": "DEV", "name": "Developer", "color": "#3b82f6"},
    "verify": {"tag": "QA", "name": "QA", "color": "#22c55e"},
    "fix": {"tag": "DEV", "name": "Developer", "color": "#3b82f6"},
}

PHASE_LABELS = {
    "intake": "Recopilando requerimientos",
    "plan": "Diseñando arquitectura y plan",
    "exec": "Implementando",
    "verify": "Verificando calidad",
    "fix": "Corrigiendo issues",
    "complete": "Completado",
    "failed": "Fallido",
}

MAX_FIX_ATTEMPTS = 3


# ─── Pipeline State ──────────────────────────────────────────────────

@dataclass
class PipelineState:
    """Persistent state for a pipeline execution."""
    task_id: str = ""
    title: str = ""
    phase: str = "intake"
    phase_history: list = field(default_factory=list)
    fix_attempts: int = 0
    created_at: float = 0.0
    updated_at: float = 0.0

    # Artifacts produced by each phase
    user_story: str = ""          # intake → user story text
    acceptance_criteria: str = "" # intake → AC list
    plan_path: str = ""           # plan → implementation plan file
    verify_report: str = ""       # verify → QA report
    fix_reason: str = ""          # verify → why fix is needed

    # Metadata
    story_points: int = 0
    priority: str = "P2"
    activated_roles: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PipelineState":
        state = cls()
        for k, v in d.items():
            if hasattr(state, k):
                setattr(state, k, v)
        return state


class Pipeline:
    """Manages pipeline state and transitions."""

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = self.state_dir / "pipeline-state.json"
        self.plans_dir = self.state_dir / "plans"
        self.history_dir = self.state_dir / "history"

    def _ensure_dirs(self):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(exist_ok=True)
        self.history_dir.mkdir(exist_ok=True)

    # ─── State Persistence ────────────────────────────────────────

    def load(self) -> Optional[PipelineState]:
        """Load current pipeline state, or None if no active pipeline."""
        if not self.state_file.exists():
            return None
        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            return PipelineState.from_dict(data)
        except (json.JSONDecodeError, Exception):
            return None

    def save(self, state: PipelineState):
        """Persist pipeline state atomically."""
        self._ensure_dirs()
        state.updated_at = time.time()
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.state_file)

    def clear(self):
        """Remove active pipeline state."""
        if self.state_file.exists():
            self.state_file.unlink()

    # ─── Pipeline Lifecycle ───────────────────────────────────────

    def start(self, task_id: str, title: str) -> PipelineState:
        """Start a new pipeline for a task."""
        self._ensure_dirs()
        state = PipelineState(
            task_id=task_id,
            title=title,
            phase="intake",
            created_at=time.time(),
            updated_at=time.time(),
            phase_history=[{
                "phase": "intake",
                "timestamp": time.time(),
                "reason": "Pipeline started",
            }],
        )
        self.save(state)
        return state

    def can_transition(self, state: PipelineState, target: str) -> tuple[bool, str]:
        """Check if a transition is valid. Returns (ok, reason)."""
        current = state.phase

        if current in ("complete", "failed"):
            return False, f"Pipeline already in terminal state: {current}"

        allowed = TRANSITIONS.get(current, [])
        if target not in allowed:
            return False, f"Cannot transition from {current} to {target}. Allowed: {allowed}"

        # Guard: fix attempts limit
        if target == "fix" and state.fix_attempts >= MAX_FIX_ATTEMPTS:
            return False, f"Max fix attempts ({MAX_FIX_ATTEMPTS}) reached"

        # Guard: exec requires a plan
        if target == "exec" and not state.plan_path and not state.user_story:
            return False, "Exec requires a plan or user story"

        return True, "OK"

    def transition(self, state: PipelineState, target: str, reason: str = "") -> PipelineState:
        """Advance pipeline to the next phase."""
        ok, msg = self.can_transition(state, target)
        if not ok:
            raise ValueError(f"Invalid transition: {msg}")

        state.phase = target
        state.phase_history.append({
            "phase": target,
            "timestamp": time.time(),
            "reason": reason,
        })

        if target == "fix":
            state.fix_attempts += 1

        self.save(state)
        return state

    def get_role(self, phase: str = None) -> dict:
        """Get the role info for a phase."""
        return PHASE_ROLES.get(phase or "intake", PHASE_ROLES["intake"])

    def get_label(self, phase: str = None) -> str:
        """Get human-readable label for a phase."""
        return PHASE_LABELS.get(phase or "intake", "Desconocido")

    # ─── Artifact Management ──────────────────────────────────────

    def save_plan(self, state: PipelineState, plan_content: str) -> str:
        """Save implementation plan and update state."""
        self._ensure_dirs()
        plan_path = self.plans_dir / f"{state.task_id}-plan.md"
        plan_path.write_text(plan_content, encoding="utf-8")
        state.plan_path = str(plan_path)
        self.save(state)
        return str(plan_path)

    def save_history(self, state: PipelineState):
        """Archive completed pipeline to history."""
        self._ensure_dirs()
        history_file = self.history_dir / f"{state.task_id}.json"
        history_file.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save_session(self, state: PipelineState, chat_messages: list = None):
        """Save a session artifact with pipeline summary and chat log."""
        self._ensure_dirs()
        sessions_dir = self.state_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        duration = state.updated_at - state.created_at if state.created_at else 0
        phases_completed = [h["phase"] for h in state.phase_history]

        session = {
            "session_id": state.task_id,
            "title": state.title,
            "result": state.phase,  # complete or failed
            "duration_seconds": round(duration, 1),
            "phases_completed": phases_completed,
            "fix_attempts": state.fix_attempts,
            "story_points": state.story_points,
            "priority": state.priority,
            "created_at": state.created_at,
            "completed_at": state.updated_at,
            "chat_message_count": len(chat_messages) if chat_messages else 0,
        }

        session_file = sessions_dir / f"{state.task_id}.json"
        session_file.write_text(
            json.dumps(session, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    # ─── Status ───────────────────────────────────────────────────

    def get_status_line(self, state: PipelineState) -> str:
        """Get a status line for the dashboard."""
        role = self.get_role(state.phase)
        label = self.get_label(state.phase)
        fix_info = f" (intento {state.fix_attempts}/{MAX_FIX_ATTEMPTS})" if state.phase == "fix" else ""
        return f"[{role['tag']}] {label}{fix_info} — {state.title}"
