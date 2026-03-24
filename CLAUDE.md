# Claude Code Context -- claude-agile Plugin (v2: ccpm Layer)

## What This Is

claude-agile is an **agile methodology layer** on top of [ccpm](https://github.com/automazeio/ccpm) (Claude Code Project Manager). It does NOT replicate ccpm's project management mechanics. Instead, it adds what ccpm lacks: methodology selection, role-based workflows, natural language PO intake, and agile ceremonies.

### The Layer Architecture

```
+-----------------------------------------+
|          claude-agile (this plugin)      |
|  Methodology | Roles | Ceremonies | ECC |
+-----------------------------------------+
|              ccpm (dependency)           |
|  PRDs | Epics | Tasks | GitHub | Agents |
+-----------------------------------------+
|          Claude Code / Agent Harness     |
+-----------------------------------------+
```

- **ccpm** handles: spec-driven development, PRD creation, epic/task decomposition, GitHub sync, parallel execution, deterministic status tracking
- **claude-agile** handles: Scrum/Kanban/Shape Up/Lean-XP methodology, Scrum Master/Tech Lead/Developer/QA roles, sprint ceremonies, velocity tracking, retrospectives
- **ECC** (optional): TDD enforcement, verification loops, security scanning

## Dependencies

### Required: ccpm
- **Repository:** https://github.com/automazeio/ccpm
- **Install:** `git clone https://github.com/automazeio/ccpm.git && ln -s $(pwd)/ccpm/skill/ccpm .claude/skills/ccpm`
- **What it provides:** Five-phase workflow (Plan, Structure, Sync, Execute, Track), natural language intent routing, 14 deterministic bash scripts, GitHub integration
- **How claude-agile uses it:** Every command wraps or delegates to ccpm. `intake` triggers ccpm's Plan phase. `plan` triggers Structure and Sync. `implement` triggers Execute. `daily` triggers Track.

### Optional: everything-claude-code (ECC)
- **What it provides:** `/tdd`, `/verification-loop`, `/security-scan`
- **How claude-agile uses it:** `implement` calls `/tdd` for test-driven development. `review` calls `/verification-loop` and `/security-scan` for automated QA.

## Architecture

### Plugin Registration
- `.claude-plugin/plugin.json` -- Plugin metadata with ccpm listed as dependency

### Commands (Slash Commands)
Commands are defined in `commands/*.md`. Each wraps ccpm functionality with an agile methodology layer:

| Command | Role | claude-agile Layer | ccpm Delegation |
|---------|------|--------------------|-----------------|
| `init` | Scrum Master | 5 discovery questions, methodology selection | Project scaffolding |
| `intake` | Scrum Master | NLP intake, user stories, acceptance criteria | PRD creation (Plan phase) |
| `plan` | SM + Tech Lead | Methodology-specific planning, capacity, goals | Task decomposition (Structure), GitHub sync (Sync) |
| `implement` | Developer | Role assignment, sprint tracking, TDD rules | Parallel execution (Execute), worktree management |
| `review` | QA | Acceptance criteria verification, quality gates | Issue closure, PR management |
| `daily` | Scrum Master | Methodology metrics, sprint health, recommendations | Status scripts (Track phase) |
| `close` | Scrum Master | Retrospective, velocity, sprint archiving | Issue/milestone closure, epic merging |

### Command Flow: How claude-agile Wraps ccpm

```
User: /claude-agile:intake "I want users to sign up with email"
  |
  v
claude-agile: Asks clarifying questions (max 3)
claude-agile: Writes user story with AC to BACKLOG.md
claude-agile: Assigns priority and story points
  |
  v  (delegation)
ccpm: "I want to build user signup with email" -> guided brainstorming
ccpm: Creates PRD at .claude/prds/user-signup.md
  |
  v
claude-agile: Links story to PRD, confirms with PO
```

### Skills (Reference Knowledge)
Skills in `skills/` provide domain knowledge that commands reference. They are NOT commands -- they are knowledge bases unique to claude-agile:

- `skills/core/` -- Methodology selection, intake techniques, standup guidance
- `skills/scrum/` -- Sprint planning, sprint close, retrospective facilitation
- `skills/kanban/` -- Board management, WIP limits, flow metrics
- `skills/shape-up/` -- Pitch writing, betting table, hill charts
- `skills/lean-xp/` -- TDD enforcement, waste elimination, pair programming

### Templates
Templates in `templates/` extend ccpm's project structure with agile-specific files:

| Template | Purpose | Relation to ccpm |
|----------|---------|-----------------|
| `BACKLOG.md` | Prioritized product backlog | Extends ccpm PRDs with agile prioritization |
| `SPRINT.md` | Sprint/cycle plan | Maps to ccpm epics with methodology context |
| `DAILY.md` | Session log | Extends ccpm Track with methodology metrics |
| `RETRO.md` | Retrospective | Unique to claude-agile (ccpm has no retro) |
| `PRD.md` | Product Requirements | Used before delegating to ccpm PRD format |
| `ADR.md` | Architecture Decisions | Supplements ccpm's epic architecture notes |

### Hooks
`hooks/hooks.json` defines a SessionStart hook that runs ccpm's status check and overlays agile methodology context.

## Key Integration Points

### Project Files (Created in User's Project)
When `init` runs, these files are created alongside ccpm's project structure:
- `.claude-agile/config.json` -- Methodology config, velocity, role assignments, ccpm/ECC detection
- `BACKLOG.md` -- Agile-formatted backlog (references ccpm PRDs)
- `SPRINT.md` -- Methodology-specific sprint plan (references ccpm epics)
- `DAILY.md` -- Session log with methodology metrics

ccpm creates its own structure:
- `.claude/prds/` -- Product requirements documents
- `.claude/epics/<feature>/` -- Technical epics and task files
- `.claude/skills/ccpm/` -- ccpm skill files and scripts

### Mapping: claude-agile Concepts to ccpm Phases

| claude-agile | ccpm Phase | Integration |
|-------------|-----------|-------------|
| User Story | Plan | Story -> PRD creation via ccpm brainstorming |
| Sprint Planning | Structure | Selected stories -> ccpm task decomposition |
| GitHub Sync | Sync | ccpm creates issues, worktrees, mappings |
| Implementation | Execute | ccpm analyzes parallel streams, launches agents |
| Daily Standup | Track | ccpm bash scripts + methodology metrics overlay |
| Sprint Close | (manual) | ccpm closes issues; claude-agile does retro |

### Role System
The user acts as Product Owner. AI agents fill these roles based on command context:
- **Scrum Master** (init, intake, daily, plan, close) -- facilitates ceremonies
- **Tech Lead** (plan) -- provides technical analysis
- **Developer** (implement) -- writes code following methodology rules
- **QA** (review) -- verifies against acceptance criteria

## Conventions

- Commands always read `.claude-agile/config.json` before acting
- Commands check for ccpm availability and warn if missing
- Commands update `DAILY.md` with session activity
- Commands delegate to ccpm for project management mechanics
- Story IDs follow `US-NNN` format (claude-agile's backlog)
- ccpm uses its own numbering for epics and tasks
- Velocity is tracked in `config.json` (claude-agile's metric)

## Methodology Routing

The chosen methodology (stored in `config.json`) affects how commands behave:
- **Scrum:** Sprint-based planning, velocity tracking, burndown, full ceremonies
- **Kanban:** WIP limits, flow metrics, continuous pull, no sprints
- **Shape Up:** Appetite-based cycles, pitches, betting table, hill charts, scope hammering
- **Lean/XP:** TDD enforcement (via ECC), waste tracking, value stream analysis
