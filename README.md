# claude-agile

An **agile methodology layer** on top of [ccpm](https://github.com/automazeio/ccpm). **You are the Product Owner.** A 12-role AI specialist team handles everything from Scrum ceremonies to security reviews, infrastructure design, and UX assessment -- using ccpm for project management mechanics underneath.

Supports four agile methodologies:
- **Scrum** -- Structured sprints with full ceremonies
- **Kanban** -- Continuous flow with WIP limits
- **Shape Up** -- 6-week cycles with pitches and betting
- **Lean/XP** -- TDD-first development with waste elimination

## Full Team (12 Roles)

### Core Team (always active)

| Role | Tag | What They Do |
|------|-----|-------------|
| **Scrum Master** | `[SM]` | Facilitates ceremonies, intake, role activation, sprint close |
| **Tech Lead** | `[TL]` | Architecture decisions, technical analysis, ADRs |
| **Developer** | `[DEV]` | Implementation with TDD, code writing |
| **QA** | `[QA]` | Acceptance criteria verification, quality gates |

### Infra Team (activates on infrastructure tasks)

| Role | Tag | Color | Triggers |
|------|-----|-------|----------|
| **Cloud Architect** | `[ARCH]` | Orange | Cost optimization, scalability, multi-region, new services |
| **DevOps Engineer** | `[DEVOPS]` | Yellow | CI/CD, Docker, GitHub Actions, deploy issues, secrets |
| **DBA** | `[DBA]` | Brown | Slow queries, schema changes, migrations, indexing |
| **Observability Engineer** | `[OBS]` | Cyan | Production debugging, logging, alerts, SLOs, monitoring |

### Security Team (activates on auth/payment/data tasks)

| Role | Tag | Color | Triggers |
|------|-----|-------|----------|
| **Security Engineer** | `[SEC]` | Red | Auth, payments, user data, API endpoints, OWASP |
| **Penetration Tester** | `[PENTEST]` | Dark Red | Major releases, new endpoints, auth changes |

### Product Team (activates on UI/data tasks)

| Role | Tag | Color | Triggers |
|------|-----|-------|----------|
| **UX Designer** | `[UX]` | Pink | New UI features, user flows, accessibility, mobile |
| **Data Engineer** | `[DATA]` | Indigo | Analytics, reporting, data exports, privacy |

## Role Activation

The Scrum Master automatically activates specialist roles based on task type:

| Task Type | Roles Activated |
|-----------|----------------|
| `feature` | Scrum Master + Tech Lead + Developer + QA |
| `infra/deploy` | DevOps Engineer (+ Cloud Architect if design) |
| `database` | DBA (+ Tech Lead if schema change) |
| `security` | Security Engineer (always on auth/payment) |
| `performance` | Observability Engineer + DBA |
| `UI/UX` | Product Designer → Developer + QA |
| `data/analytics` | Data Engineer + DBA |
| `major release` | Pen Tester + Security Engineer + QA |

## Why a Layer on ccpm?

ccpm is excellent at **project management mechanics**: PRDs, epics, task decomposition, GitHub sync, parallel execution, and deterministic status tracking. But it does not have opinions about agile methodologies.

claude-agile adds what ccpm lacks:

| claude-agile Adds | ccpm Provides |
|-------------------|---------------|
| Methodology selection (Scrum/Kanban/Shape Up/Lean-XP) | PRD creation and brainstorming |
| Natural language PO intake with User Stories | Epic and task decomposition |
| 12-role specialist team with auto-activation | Parallel execution with multiple agents |
| Sprint/cycle planning ceremonies | GitHub sync (issues, worktrees) |
| Communication protocol with role-tagged messages | Deterministic status scripts |
| Onboarding wizard with structured interview | N/A |
| Audit trails and auto-generated ADRs | Issue and milestone management |
| ECC integration (TDD, verification) | N/A |

## Prerequisites

### 1. Install ccpm (required)

```bash
git clone https://github.com/automazeio/ccpm.git
ln -s $(pwd)/ccpm/skill/ccpm .claude/skills/ccpm
```

### 2. Install everything-claude-code (optional, recommended)

For TDD enforcement and automated QA verification. See [ECC](https://github.com/anthropics/everything-claude-code).

## Install claude-agile

```bash
git clone https://github.com/OmarNoah77/claude-agile.git
claude plugin add ./claude-agile
```

## Commands

| Command | Role | What claude-agile Does | What ccpm Does |
|---------|------|----------------------|----------------|
| `/claude-agile:init` | Scrum Master | Onboarding interview → methodology + team config | Project scaffolding |
| `/claude-agile:intake` | Scrum Master | NLP intake → User Story → role activation | PRD creation (Plan) |
| `/claude-agile:plan` | SM + Tech Lead | Methodology planning + specialist assessments | Task decomposition (Structure) + GitHub sync |
| `/claude-agile:implement` | Developer | Role assignment + TDD (via ECC) | Parallel execution (Execute) |
| `/claude-agile:review` | QA | AC verification + security scan | Issue closure + PR management |
| `/claude-agile:daily` | Scrum Master | Team health + methodology metrics | Status scripts (Track) |
| `/claude-agile:close` | Scrum Master | Retro + velocity + audit trail archiving | Issue/milestone closure |

## Quick Start

```bash
# 1. Initialize -- structured interview picks methodology + configures team
/claude-agile:init

# 2. Add your first story (NLP intake → role activation → ccpm PRD)
/claude-agile:intake
> "I want users to be able to sign up with email and password"
# → Security Engineer activates (auth task)
# → UX Designer activates (new UI flow)

# 3. Plan your sprint (specialist assessments → ccpm task decomposition)
/claude-agile:plan

# 4. Build (developer role + ccpm parallel execution + ECC /tdd)
/claude-agile:implement

# 5. Status (team health + methodology metrics)
/claude-agile:daily

# 6. Review (QA + security scan + ECC /verification-loop)
/claude-agile:review

# 7. Close sprint (retro + audit trail + ccpm cleanup)
/claude-agile:close
```

## Communication Protocol

Every role-tagged message in Team Chat follows this format:

```
[ROLE TAG] #TASK-NNN MESSAGE_TYPE — Summary
  → Detail 1
  → Detail 2
```

Message types: `INTAKE` | `DECISION` | `ASSESSMENT` | `QUESTION` | `BLOCKER` | `UPDATE` | `APPROVAL`

### Example Task Flow

```
[SM] #TASK-001 INTAKE — "Módulo financiero: cuentas y gastos"
  → User Story: US-001 (5 pts)
  → Roles activados: Tech Lead, Security, DBA, Developer, QA

[TL] #TASK-001 DECISION — Tabla `accounts` + `transactions`
  → Patrón: repository pattern

[SEC] #TASK-001 ASSESSMENT — ⚠️ MEDIUM risk
  → Datos financieros requieren encryption at rest
  → Rate limiting en endpoints de transacciones

[DBA] #TASK-001 ASSESSMENT — Índices recomendados:
  → idx_transactions_user_date
  → idx_accounts_user_id

[DEV] #TASK-001 UPDATE — Implementando...
  → Tests escritos primero (TDD)

[QA] #TASK-001 APPROVAL ✅ — 47 tests passing

[SM] #TASK-001 CLOSED — US-001 completada
  → 5 story points → velocity actualizada
```

## Project Files

### claude-agile Creates

| File/Dir | Purpose |
|----------|---------|
| `.claude-agile/config.json` | Methodology, team config, velocity, integrations |
| `.claude-agile/project-profile.json` | Onboarding interview answers |
| `.claude-agile/history/TASK-NNN.md` | Full audit trail per task |
| `.claude-agile/decisions/ADR-NNN.md` | Architecture Decision Records |
| `.claude-agile/decisions/SEC-NNN.md` | Security decisions |
| `.claude-agile/decisions/DB-NNN.md` | Database decisions |
| `.claude-agile/sprints/sprint-N/` | Sprint archives (planning, retro, velocity) |
| `BACKLOG.md` | Prioritized product backlog |
| `SPRINT.md` | Sprint/cycle plan |
| `DAILY.md` | Session log with methodology metrics |
| `RETRO.md` | Sprint retrospective |

### ccpm Creates

| Path | Purpose |
|------|---------|
| `.claude/prds/` | Product requirements documents |
| `.claude/epics/<feature>/` | Technical epics, tasks, analysis |
| `.claude/skills/ccpm/` | ccpm skill files and scripts |

## Plugin Structure

```
claude-agile/
├── .claude-plugin/plugin.json     # Plugin metadata (v2.1.0)
├── commands/                      # Slash commands (all wrap ccpm)
│   ├── init.md                    # Onboarding wizard + methodology selection
│   ├── intake.md                  # NLP intake + role activation
│   ├── plan.md                    # Methodology planning
│   ├── implement.md               # Developer role + TDD
│   ├── review.md                  # QA verification
│   ├── daily.md                   # Standup + team health
│   └── close.md                   # Sprint close + retro
├── skills/
│   ├── core/                      # Cross-methodology knowledge
│   │   ├── methodology-selector.md
│   │   ├── po-intake.md
│   │   ├── daily.md
│   │   └── communication-protocol.md  # Role communication rules
│   ├── scrum/                     # Scrum-specific
│   ├── kanban/                    # Kanban-specific
│   ├── shape-up/                  # Shape Up-specific
│   ├── lean-xp/                   # Lean/XP-specific
│   ├── infra/                     # Infrastructure team
│   │   ├── cloud-architect.md
│   │   ├── devops-engineer.md
│   │   ├── dba.md
│   │   └── observability-engineer.md
│   ├── security/                  # Security team
│   │   ├── security-engineer.md
│   │   └── pen-tester.md
│   └── product/                   # Product team
│       ├── ux-designer.md
│       └── data-engineer.md
├── templates/                     # File templates
├── hooks/hooks.json               # Session start hook
├── CLAUDE.md
└── README.md
```

## Methodology Guide

### Scrum
Best for teams (2-9 people) with somewhat predictable requirements and stakeholders who need regular visibility.
- **Cadence:** 2-week sprints
- **Ceremonies:** Sprint Planning, Daily Standup, Sprint Review, Retrospective
- **Key metric:** Velocity (story points per sprint)

### Kanban
Best for continuous flow work where priorities shift frequently.
- **Cadence:** Continuous (no sprints)
- **Core practice:** WIP limits per board column
- **Key metrics:** Cycle Time, Throughput, Lead Time

### Shape Up
Best for solo developers or small autonomous teams building features with fixed time budgets.
- **Cadence:** 6-week build cycles + 2-week cooldowns
- **Core practice:** Pitching and betting, scope hammering
- **Key metric:** Appetite consumed vs delivered scope

### Lean/XP
Best for projects where technical quality is non-negotiable from day one.
- **Cadence:** Continuous
- **Core practice:** TDD (Red-Green-Refactor) enforced via ECC
- **Key metric:** TDD compliance, defect rate

## License

MIT License. See [LICENSE](LICENSE) for details.
