# claude-agile

An **agile methodology layer** on top of [ccpm](https://github.com/automazeio/ccpm). **You are the Product Owner.** AI agents handle the Scrum Master, Tech Lead, Developer, and QA roles -- using ccpm for the project management mechanics underneath.

Supports four agile methodologies:
- **Scrum** -- Structured sprints with full ceremonies
- **Kanban** -- Continuous flow with WIP limits
- **Shape Up** -- 6-week cycles with pitches and betting
- **Lean/XP** -- TDD-first development with waste elimination

## Why a Layer on ccpm?

ccpm is excellent at **project management mechanics**: PRDs, epics, task decomposition, GitHub sync, parallel execution, and deterministic status tracking. But it does not have opinions about agile methodologies.

claude-agile adds what ccpm lacks:

| claude-agile Adds | ccpm Provides |
|-------------------|---------------|
| Methodology selection (Scrum/Kanban/Shape Up/Lean-XP) | PRD creation and brainstorming |
| Natural language PO intake with User Stories | Epic and task decomposition |
| Explicit agent roles (SM, TL, Dev, QA) | Parallel execution with multiple agents |
| Sprint/cycle planning ceremonies | GitHub sync (issues, worktrees) |
| Velocity tracking and burndown | Deterministic status scripts |
| Retrospectives | Issue and milestone management |
| ECC integration (TDD, verification) | N/A (ccpm does not integrate ECC) |

## Prerequisites

### 1. Install ccpm (required)

ccpm must be installed first. claude-agile will not function without it.

```bash
# Clone ccpm
git clone https://github.com/automazeio/ccpm.git

# Link as a Claude Code skill
ln -s $(pwd)/ccpm/skill/ccpm .claude/skills/ccpm
```

Verify ccpm is working:
```bash
# You should see .claude/skills/ccpm/SKILL.md
ls .claude/skills/ccpm/
```

See the [ccpm README](https://github.com/automazeio/ccpm#readme) for full installation instructions.

### 2. Install everything-claude-code (optional, recommended)

For TDD enforcement and automated QA verification:

```bash
# Follow installation instructions at:
# https://github.com/anthropics/everything-claude-code
```

When ECC is installed, claude-agile's `implement` command uses `/tdd` and `review` uses `/verification-loop` and `/security-scan`.

## Install claude-agile

After ccpm is installed:

```bash
# Clone claude-agile
git clone https://github.com/OmarNoah77/claude-agile.git

# Add as a Claude Code plugin
claude plugin add ./claude-agile
```

## Commands

All commands **wrap** ccpm -- they add an agile methodology layer on top of ccpm's project management.

| Command | Role | What claude-agile Does | What ccpm Does |
|---------|------|----------------------|----------------|
| `/claude-agile:init` | Scrum Master | 5 questions -> methodology selection | Project scaffolding |
| `/claude-agile:intake` | Scrum Master | NLP intake -> User Story with AC | PRD creation (Plan phase) |
| `/claude-agile:plan` | SM + Tech Lead | Methodology planning + capacity | Task decomposition (Structure) + GitHub sync |
| `/claude-agile:implement` | Developer | Role assignment + TDD (via ECC) | Parallel execution (Execute) |
| `/claude-agile:review` | QA | AC verification + quality gates | Issue closure + PR management |
| `/claude-agile:daily` | Scrum Master | Methodology metrics + health | Status scripts (Track phase) |
| `/claude-agile:close` | Scrum Master | Retro + velocity + archiving | Issue/milestone/epic closure |

### ccpm Pass-Through

ccpm commands remain available directly for power users. You can always say:

| Natural Language | ccpm Action |
|-----------------|-------------|
| "I want to build X" | Guided brainstorming + PRD |
| "parse the X PRD" | Technical epic generation |
| "break down the X epic" | Task decomposition |
| "sync the X epic" | GitHub issues + worktree setup |
| "start working on issue N" | Parallel agent analysis + launch |
| "standup" / "what's blocked" | Real-time status (bash script) |

## Quick Start

```bash
# 1. Initialize -- answer 5 questions to pick your methodology
/claude-agile:init

# 2. Add your first story (NLP intake -> ccpm PRD)
/claude-agile:intake
> "I want users to be able to sign up with email and password"

# 3. Plan your sprint (methodology planning -> ccpm task decomposition)
/claude-agile:plan

# 4. Start building (developer role + ccpm parallel execution + ECC /tdd)
/claude-agile:implement

# 5. Check status anytime (ccpm status scripts + methodology metrics)
/claude-agile:daily

# 6. Review completed work (QA role + ECC /verification-loop)
/claude-agile:review

# 7. Close the sprint (retro + ccpm issue cleanup)
/claude-agile:close
```

## How It Works: The Layer Architecture

```
+---------------------------------------------+
|           claude-agile (this plugin)         |
|  Methodology | Roles | Ceremonies | Retros  |
+---------------------------------------------+
|                ccpm (required)               |
|  PRDs | Epics | Tasks | GitHub | Parallel   |
+---------------------------------------------+
|      ECC / everything-claude-code (optional) |
|  /tdd | /verification-loop | /security-scan |
+---------------------------------------------+
|         Claude Code / Agent Harness          |
+---------------------------------------------+
```

### Data Flow Example

```
/claude-agile:intake "I need a payment system"
    |
    v
claude-agile: Asks 3 clarifying questions
claude-agile: Writes US-001 to BACKLOG.md (Scrum Master role)
    |
    v  delegates to ccpm
ccpm: Brainstorms -> creates .claude/prds/payment-system.md
    |
    v
/claude-agile:plan
    |
    v
claude-agile: Sprint planning ceremony (methodology-specific)
claude-agile: Selects US-001 for sprint, sets capacity
    |
    v  delegates to ccpm
ccpm: "parse the payment-system PRD" -> epic
ccpm: "break down the payment-system epic" -> 5 tasks
ccpm: "sync the payment-system epic" -> GitHub issues + worktree
    |
    v
/claude-agile:implement
    |
    v
claude-agile: Assigns Developer role, updates sprint tracking
    |
    v  delegates to ccpm + ECC
ccpm: "start working on issue 42" -> 3 parallel streams
ECC:  /tdd -> Red-Green-Refactor cycle
```

## Methodology Guide

### Scrum
Best for teams (2-9 people) with somewhat predictable requirements and stakeholders who need regular visibility.

- **Cadence:** 2-week sprints
- **Ceremonies:** Sprint Planning, Daily Standup, Sprint Review, Retrospective
- **Key metric:** Velocity (story points per sprint)
- **ccpm mapping:** Each sprint selects backlog items -> ccpm decomposes into epics/tasks

### Kanban
Best for continuous flow work where priorities shift frequently.

- **Cadence:** Continuous (no sprints)
- **Core practice:** WIP limits per board column
- **Key metrics:** Cycle Time, Throughput, Lead Time
- **ccpm mapping:** Items pulled continuously -> ccpm tracks per-item progress

### Shape Up
Best for solo developers or small autonomous teams building features with fixed time budgets.

- **Cadence:** 6-week build cycles + 2-week cooldowns
- **Core practice:** Pitching and betting, scope hammering
- **Key metric:** Appetite consumed vs delivered scope
- **ccpm mapping:** One pitch -> one ccpm epic -> appetite-bounded execution

### Lean/XP
Best for projects where technical quality is non-negotiable from day one.

- **Cadence:** Continuous
- **Core practice:** TDD (Red-Green-Refactor) enforced via ECC
- **Key metric:** TDD compliance, defect rate
- **ccpm mapping:** Highest-value items first -> ccpm execution + ECC /tdd enforcement

## Project Files

### claude-agile Creates

| File | Purpose |
|------|---------|
| `.claude-agile/config.json` | Methodology, velocity, roles, integration status |
| `BACKLOG.md` | Prioritized product backlog (references ccpm PRDs) |
| `SPRINT.md` | Sprint/cycle plan (references ccpm epics) |
| `DAILY.md` | Session log with methodology metrics |
| `RETRO.md` | Sprint retrospective (created at close) |

### ccpm Creates

| Path | Purpose |
|------|---------|
| `.claude/prds/` | Product requirements documents |
| `.claude/epics/<feature>/` | Technical epics, tasks, analysis, updates |
| `.claude/skills/ccpm/` | ccpm skill files and bash scripts |

## Plugin Structure

```
claude-agile/
+-- .claude-plugin/plugin.json    # Plugin metadata (ccpm dependency declared)
+-- commands/                     # Slash commands (all wrap ccpm)
|   +-- init.md                   # /claude-agile:init
|   +-- intake.md                 # /claude-agile:intake
|   +-- plan.md                   # /claude-agile:plan
|   +-- implement.md              # /claude-agile:implement
|   +-- review.md                 # /claude-agile:review
|   +-- daily.md                  # /claude-agile:daily
|   +-- close.md                  # /claude-agile:close
+-- skills/                       # Methodology knowledge (unique to claude-agile)
|   +-- core/                     # Cross-methodology knowledge
|   +-- scrum/                    # Scrum-specific knowledge
|   +-- kanban/                   # Kanban-specific knowledge
|   +-- shape-up/                 # Shape Up-specific knowledge
|   +-- lean-xp/                  # Lean/XP-specific knowledge
+-- templates/                    # File templates (extend ccpm templates)
+-- hooks/hooks.json              # Session start hook (ccpm + methodology status)
+-- CLAUDE.md                     # Project context for Claude
+-- README.md                     # This file
```

## Works With

### ccpm (required)
[ccpm](https://github.com/automazeio/ccpm) provides the project management engine. claude-agile wraps every ccpm phase with agile methodology context.

### everything-claude-code (recommended)
When [ECC](https://github.com/anthropics/everything-claude-code) is installed:
- `/claude-agile:implement` calls `/tdd` for test-driven development
- `/claude-agile:review` calls `/verification-loop` for automated QA
- `/claude-agile:review` calls `/security-scan` for security analysis

### GitHub
GitHub integration is handled by **ccpm's Sync phase**. ccpm creates issues, milestones, worktrees, and manages PRs. claude-agile adds methodology labels and sprint/cycle context.

### MCP Agents
claude-agile works with multi-agent setups. The session start hook displays both ccpm project status and agile methodology context so any agent can pick up where you left off.

## License

MIT License. See [LICENSE](LICENSE) for details.
