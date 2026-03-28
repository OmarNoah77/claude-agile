"""
Skill system for claude-agile.

Skills are markdown files with YAML frontmatter that get auto-injected
into agent prompts based on triggers, phase, and role matching.

Skill locations (in priority order):
  1. Project-scoped: <project>/.claude-agile/skills/*.md
  2. Plugin-scoped:  <claude-agile>/skills/**/*.md  (existing role skills)
  3. User-scoped:    ~/.claude-agile/skills/*.md

Inspired by oh-my-claudecode's skill system.
"""

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger("claude-agile.skills")


@dataclass
class Skill:
    """A skill definition loaded from a markdown file."""
    name: str
    description: str = ""
    path: str = ""
    content: str = ""

    # Matching criteria
    triggers: list[str] = field(default_factory=list)   # keywords that activate this skill
    phases: list[str] = field(default_factory=list)      # pipeline phases (intake, plan, exec, etc.)
    roles: list[str] = field(default_factory=list)       # role tags (SM, TL, DEV, QA, etc.)

    # Metadata
    priority: int = 0              # higher = injected first
    max_chars: int = 2000          # max content to inject
    source: str = ""               # project, plugin, or user


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML-like frontmatter from a markdown file.

    Returns (metadata_dict, body_content).
    Supports simple key: value and key: [list] syntax.
    """
    metadata = {}
    body = text

    # Check for frontmatter delimiters
    if not text.startswith("---"):
        return metadata, body

    parts = text.split("---", 2)
    if len(parts) < 3:
        return metadata, body

    frontmatter = parts[1].strip()
    body = parts[2].strip()

    for line in frontmatter.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        # Parse list values: [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            metadata[key] = [i for i in items if i]
        elif value.lower() in ("true", "yes"):
            metadata[key] = True
        elif value.lower() in ("false", "no"):
            metadata[key] = False
        elif value.isdigit():
            metadata[key] = int(value)
        else:
            metadata[key] = value

    return metadata, body


def _load_skill_file(path: Path, source: str) -> Optional[Skill]:
    """Load a single skill file."""
    try:
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)

        name = meta.get("name", path.stem)
        if not name:
            return None

        return Skill(
            name=name,
            description=meta.get("description", ""),
            path=str(path),
            content=body,
            triggers=meta.get("triggers", []),
            phases=meta.get("phases", []),
            roles=meta.get("roles", []),
            priority=meta.get("priority", 0),
            max_chars=meta.get("max_chars", 2000),
            source=source,
        )
    except Exception as e:
        log.warning(f"Failed to load skill {path}: {e}")
        return None


class SkillRegistry:
    """Loads, caches, and matches skills for prompt injection."""

    def __init__(self, project_root: Path, plugin_dir: Path):
        self.project_root = project_root
        self.plugin_dir = plugin_dir
        self._skills: list[Skill] = []
        self._loaded_at: float = 0
        self._cache_ttl: float = 30  # Reload skills every 30s

    def _scan_dirs(self) -> list[tuple[Path, str]]:
        """Return (directory, source) pairs to scan for skills."""
        dirs = []

        # 1. Project-scoped skills
        project_skills = self.project_root / ".claude-agile" / "skills"
        if project_skills.is_dir():
            dirs.append((project_skills, "project"))

        # 2. Plugin-scoped skills (claude-agile's own skills/)
        plugin_skills = self.plugin_dir / "skills"
        if plugin_skills.is_dir():
            dirs.append((plugin_skills, "plugin"))

        # 3. User-scoped skills
        user_skills = Path.home() / ".claude-agile" / "skills"
        if user_skills.is_dir():
            dirs.append((user_skills, "user"))

        return dirs

    def load(self, force: bool = False):
        """Load/reload all skills from all directories."""
        if not force and self._skills and (time.time() - self._loaded_at) < self._cache_ttl:
            return  # Use cache

        skills = []
        seen_names = set()

        for skill_dir, source in self._scan_dirs():
            for md_file in sorted(skill_dir.rglob("*.md")):
                skill = _load_skill_file(md_file, source)
                if skill and skill.name not in seen_names:
                    skills.append(skill)
                    seen_names.add(skill.name)

        self._skills = sorted(skills, key=lambda s: -s.priority)
        self._loaded_at = time.time()
        log.info(f"Loaded {len(self._skills)} skills from {len(self._scan_dirs())} directories")

    def match(self, *, phase: str = "", role: str = "", context: str = "",
              max_skills: int = 5) -> list[Skill]:
        """Find skills matching the current context.

        Args:
            phase: Current pipeline phase (intake, plan, exec, etc.)
            role: Current agent role tag (SM, TL, DEV, QA, etc.)
            context: Text context (user message, chat history) for trigger matching
            max_skills: Maximum number of skills to return
        """
        self.load()
        matched = []
        context_lower = context.lower()

        for skill in self._skills:
            score = 0

            # Phase match
            if skill.phases:
                if phase and phase in skill.phases:
                    score += 10
                elif phase:
                    continue  # Phase specified but doesn't match — skip

            # Role match
            if skill.roles:
                if role and role in skill.roles:
                    score += 10
                elif role:
                    continue  # Role specified but doesn't match — skip

            # Trigger match (keyword search in context)
            if skill.triggers and context:
                trigger_hits = sum(1 for t in skill.triggers if t.lower() in context_lower)
                if trigger_hits > 0:
                    score += trigger_hits * 5
                elif skill.triggers:
                    continue  # Has triggers but none matched — skip

            # If no criteria specified on the skill, it's a universal skill
            if not skill.phases and not skill.roles and not skill.triggers:
                score += 1  # Low priority universal match

            if score > 0:
                matched.append((score, skill))

        # Sort by score descending, return top N
        matched.sort(key=lambda x: -x[0])
        return [s for _, s in matched[:max_skills]]

    def inject(self, *, phase: str = "", role: str = "", context: str = "",
               max_chars: int = 4000) -> str:
        """Get injectable skill content for a prompt.

        Returns a formatted string of matched skill content, ready to be
        inserted into an agent prompt.
        """
        skills = self.match(phase=phase, role=role, context=context)
        if not skills:
            return ""

        parts = ["\n## Relevant Skills\n"]
        total_chars = 0

        for skill in skills:
            content = skill.content[:skill.max_chars]
            if total_chars + len(content) > max_chars:
                break
            parts.append(f"### {skill.name}")
            if skill.description:
                parts.append(f"*{skill.description}*\n")
            parts.append(content)
            parts.append("")
            total_chars += len(content)

        return "\n".join(parts)

    def list_all(self) -> list[dict]:
        """List all loaded skills (for API/dashboard)."""
        self.load()
        return [{
            "name": s.name,
            "description": s.description,
            "source": s.source,
            "triggers": s.triggers,
            "phases": s.phases,
            "roles": s.roles,
            "priority": s.priority,
        } for s in self._skills]
