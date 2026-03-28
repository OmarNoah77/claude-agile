"""
Lean prompt builders for each pipeline phase.

The heavy context (roles, protocol, markers) lives in system-prompt-base.md
and is passed via --append-system-prompt-file. These prompts only contain
phase-specific context: user message, artifacts, and instructions.
"""

from pathlib import Path
from typing import Optional

from skills import SkillRegistry


CLAUDE_AGILE_DIR = Path(__file__).resolve().parent.parent

_skill_registry: Optional[SkillRegistry] = None


def _get_skills() -> SkillRegistry:
    global _skill_registry
    if _skill_registry is None:
        _skill_registry = SkillRegistry(Path.cwd(), CLAUDE_AGILE_DIR)
    return _skill_registry


def init_skills(project_root: Path):
    global _skill_registry
    _skill_registry = SkillRegistry(project_root, CLAUDE_AGILE_DIR)
    _skill_registry.load(force=True)


def _chat_context(chat_history: list, limit: int = 10) -> str:
    lines = []
    for m in chat_history[-limit:]:
        sender = m.get("sender", "?")
        role = m.get("role", "")
        prefix = f"[{role}] " if role else ""
        lines.append(f"{sender}: {prefix}{m.get('text', '')[:200]}")
    return "\n".join(lines) if lines else "(Sin mensajes previos)"


# ─── Phase Prompts (lean — no duplicated context) ────────────────────


def intake_prompt(user_message: str, chat_history: list, project_root: str, methodology: str = "lean-xp") -> str:
    return f"""[SM] Intake Phase — Methodology: {methodology}

## Project: {project_root}

## Recent Chat
{_chat_context(chat_history)}

## User's Message
{user_message}

## Your Task — IMPORTANT: Follow these steps in order

### Step 1: Persist the requirement
- Create the folder: `{project_root}/.claude-agile/requerimientos/`
- Extract a short slug from the requirement (e.g. "financiero", "auth-module", "dashboard-ui")
- Create: `{project_root}/.claude-agile/requerimientos/<slug>/requerimiento.md`
- Write the FULL user message into that file as-is (preserve everything)
- This is critical for traceability

### Step 2: Analyze and decompose
- Read the saved requirement file
- Identify the main features/components described
- Decompose into User Stories (each with: title, As a/I want/So that, 3-5 AC in Given/When/Then)
- Estimate Story Points (Fibonacci) and Priority (P0-P3) per story
- Identify which specialist roles are needed

### Step 3: Present to the Product Owner
- List all User Stories found with a brief summary
- Suggest an implementation order
- Ask: "¿Confirmas estas User Stories para pasar a planificación?"
- If user confirms: output [PIPELINE:ADVANCE_TO_PLAN]
"""


def plan_prompt(state_dict: dict, chat_history: list, project_root: str) -> str:
    return f"""[TL] Plan Phase

## User Story
{state_dict.get('user_story', '(No user story)')}

## Acceptance Criteria
{state_dict.get('acceptance_criteria', '(No criteria)')}

## Project: {project_root}
## Story Points: {state_dict.get('story_points', '?')} | Priority: {state_dict.get('priority', 'P2')}

## Recent Chat
{_chat_context(chat_history)}

## Your Task — IMPORTANT: Descomponer en subtareas concretas
1. READ the project files to understand the codebase structure
2. Break this task into 2-4 CONCRETE subtasks, each completable in ~15 min
3. For each subtask specify:
   - Exact files to create or modify (full paths)
   - What to implement (specific functions, endpoints, components)
   - Dependencies on other subtasks
4. Format:
   ### Subtask 1: [Title]
   Files: path/to/file.ts
   Action: Create/Modify [specific description]

   ### Subtask 2: [Title]
   Files: path/to/file.ts
   Depends on: Subtask 1
   Action: [specific description]
5. End with [PIPELINE:ADVANCE_TO_EXEC]
"""


def exec_prompt(state_dict: dict, chat_history: list, project_root: str) -> str:
    plan_content = ""
    plan_path = state_dict.get("plan_path", "")
    if plan_path and Path(plan_path).exists():
        plan_content = Path(plan_path).read_text(encoding="utf-8")[:3000]

    return f"""[DEV] Execution Phase

## User Story
{state_dict.get('user_story', '')}

## Implementation Plan
{plan_content or '(Implement based on user story)'}

## Project: {project_root}

## Recent Chat (what TL planned and previous context)
{_chat_context(chat_history, limit=10)}

## Your Task — Execute step by step
1. READ the relevant project files FIRST (understand what exists)
2. Follow the plan's subtasks IN ORDER
3. For each subtask: create/modify the specified files
4. After implementing, run `npx tsc --noEmit` or equivalent to verify it compiles
5. If something fails, fix it before moving on
6. End with [PIPELINE:ADVANCE_TO_VERIFY]

IMPORTANT: Do NOT try to implement everything at once. Follow the subtasks in order. If a subtask depends on another, implement the dependency first.
"""


def verify_prompt(state_dict: dict, chat_history: list, project_root: str) -> str:
    return f"""[QA] Verification Phase

## User Story
{state_dict.get('user_story', '')}

## Acceptance Criteria
{state_dict.get('acceptance_criteria', '')}

## Recent Chat
{_chat_context(chat_history, limit=15)}

## Your Task
1. READ the changed files to review the implementation
2. Check each acceptance criterion: PASS or FAIL with evidence
3. Run tests if they exist (Bash tool)
4. Check for security issues (OWASP top 10)
5. If ALL pass: [PIPELINE:COMPLETE]
6. If ANY fail: [PIPELINE:ADVANCE_TO_FIX] with specific issues
"""


def fix_prompt(state_dict: dict, chat_history: list, project_root: str) -> str:
    return f"""[DEV] Fix Phase (attempt {state_dict.get('fix_attempts', 0)}/3)

## Issues to Fix
{state_dict.get('fix_reason', '(See QA report in chat)')[:1500]}

## User Story
{state_dict.get('user_story', '')}

## Recent Chat
{_chat_context(chat_history, limit=15)}

## Your Task
1. Fix the specific issues identified by QA
2. Minimal changes — targeted fixes only
3. End with [PIPELINE:ADVANCE_TO_VERIFY]
4. If unfixable: [PIPELINE:FAILED] with explanation
"""


# ─── Prompt Dispatcher ───────────────────────────────────────────────

PHASE_PROMPTS = {
    "intake": intake_prompt,
    "plan": plan_prompt,
    "exec": exec_prompt,
    "verify": verify_prompt,
    "fix": fix_prompt,
}

PHASE_TO_ROLE = {
    "intake": "SM", "plan": "TL", "exec": "DEV", "verify": "QA", "fix": "DEV",
}


FINAL_INSTRUCTION = """

## MANDATORY — Final Response
After completing ALL tool operations (creating files, reading code, etc.), you MUST write a final text response summarizing what you did and your analysis. If you end on a tool call without a text response, your work will be LOST. Always end with text.
"""


def build_prompt(phase: str, *, user_message: str = "", state_dict: dict = None,
                 chat_history: list = None, project_root: str = "", methodology: str = "lean-xp") -> Optional[str]:
    """Build a lean prompt for a pipeline phase. Heavy context goes in system-prompt-base.md."""
    state_dict = state_dict or {}
    chat_history = chat_history or []

    if phase == "intake":
        base = intake_prompt(user_message, chat_history, project_root, methodology)
    elif phase in PHASE_PROMPTS:
        base = PHASE_PROMPTS[phase](state_dict, chat_history, project_root)
    else:
        return None

    # Auto-inject matching skills (only relevant ones, capped)
    registry = _get_skills()
    context = user_message or state_dict.get("user_story", "")
    role = PHASE_TO_ROLE.get(phase, "")
    skill_content = registry.inject(phase=phase, role=role, context=context, max_chars=2000)

    if skill_content:
        base += f"\n{skill_content}\n"

    # Always append the mandatory final instruction
    base += FINAL_INSTRUCTION

    return base
