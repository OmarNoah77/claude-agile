# Claude Code Context -- claude-agile Plugin (v2.1: Full Specialist Team)

## What This Is

claude-agile is an **agile methodology layer** on top of [ccpm](https://github.com/automazeio/ccpm) (Claude Code Project Manager). It adds methodology selection, a 12-role specialist team, role-based communication protocol, onboarding wizard, and audit trails.

### The Layer Architecture

```
+-----------------------------------------+
|          claude-agile (this plugin)      |
|  Methodology | 12 Roles | Ceremonies   |
|  Communication Protocol | Audit Trails  |
+-----------------------------------------+
|              ccpm (dependency)           |
|  PRDs | Epics | Tasks | GitHub | Agents |
+-----------------------------------------+
|          Claude Code / Agent Harness     |
+-----------------------------------------+
```

## Dependencies

### Required: ccpm
- **Install:** `git clone https://github.com/automazeio/ccpm.git && ln -s $(pwd)/ccpm/skill/ccpm .claude/skills/ccpm`
- **What it provides:** Five-phase workflow (Plan, Structure, Sync, Execute, Track)
- **How claude-agile uses it:** Every command wraps or delegates to ccpm

### Optional: everything-claude-code (ECC)
- **What it provides:** `/tdd`, `/verification-loop`, `/security-scan`
- **How claude-agile uses it:** `implement` calls `/tdd`, `review` calls `/verification-loop` and `/security-scan`

## Architecture

### The 12-Role Specialist Team

#### Core Team (always active)
- **Scrum Master** (`[SM]`, purple) -- init, intake, daily, plan, close
- **Tech Lead** (`[TL]`, teal) -- plan, architecture decisions
- **Developer** (`[DEV]`, blue) -- implement
- **QA** (`[QA]`, green) -- review

#### Infra Team (activates on infrastructure tasks)
- **Cloud Architect** (`[ARCH]`, orange) -- cost, scalability, multi-region, new services
- **DevOps Engineer** (`[DEVOPS]`, yellow) -- CI/CD, Docker, GitHub Actions, deploy
- **DBA** (`[DBA]`, brown) -- queries, schema, migrations, indexing
- **Observability Engineer** (`[OBS]`, cyan) -- logging, alerts, SLOs, monitoring

#### Security Team (activates on auth/payment/data tasks)
- **Security Engineer** (`[SEC]`, red) -- OWASP, JWT, rate limiting, PCI, GDPR
- **Penetration Tester** (`[PENTEST]`, dark red) -- API fuzzing, auth bypass, vuln scanning

#### Product Team (activates on UI/data tasks)
- **UX Designer** (`[UX]`, pink) -- UX heuristics, accessibility, mobile-first
- **Data Engineer** (`[DATA]`, indigo) -- analytics, privacy, data modeling

### Role Activation Matrix
The Scrum Master classifies each task and activates relevant roles:
- `feature` → SM + TL + Dev + QA
- `infra/deploy` → DevOps (+ Cloud Architect if design)
- `database` → DBA (+ TL if schema change)
- `security` → Security Engineer (always on auth/payment)
- `performance` → Observability + DBA
- `UI/UX` → UX Designer → Dev + QA
- `data/analytics` → Data Engineer + DBA
- `major release` → Pen Tester + Security + QA

### Communication Protocol
Every role-tagged message follows: `[TAG] #TASK-NNN TYPE — Summary`
- Types: INTAKE / DECISION / ASSESSMENT / QUESTION / BLOCKER / UPDATE / APPROVAL
- See `skills/core/communication-protocol.md` for full specification

### Commands (Slash Commands)

| Command | Role | claude-agile Layer | ccpm Delegation |
|---------|------|--------------------|-----------------|
| `init` | Scrum Master | Onboarding interview (22 questions), methodology selection, team config | Project scaffolding |
| `intake` | Scrum Master | NLP intake, user stories, role activation, specialist assessments | PRD creation (Plan) |
| `plan` | SM + Tech Lead | Methodology-specific planning, capacity, specialist input | Task decomposition (Structure), GitHub sync |
| `implement` | Developer | Role assignment, sprint tracking, TDD rules | Parallel execution (Execute) |
| `review` | QA | AC verification, security scan, quality gates | Issue closure, PR management |
| `daily` | Scrum Master | Team health, methodology metrics, recommendations | Status scripts (Track) |
| `close` | Scrum Master | Retro, velocity, audit trail archiving | Issue/milestone closure |

### Skills (Reference Knowledge)
Skills in `skills/` provide domain knowledge that commands reference:

- `skills/core/` -- Methodology selection, intake, standup, communication protocol
- `skills/scrum/` -- Sprint planning, close, retrospective
- `skills/kanban/` -- Board management, WIP, flow metrics
- `skills/shape-up/` -- Pitch writing, betting table, hill charts
- `skills/lean-xp/` -- TDD enforcement, waste elimination
- `skills/infra/` -- Cloud Architect, DevOps, DBA, Observability
- `skills/security/` -- Security Engineer, Pen Tester
- `skills/product/` -- UX Designer, Data Engineer

### Project Files (Created in User's Project)

```
.claude-agile/
├── config.json           # Methodology, team config, velocity
├── project-profile.json  # Onboarding interview answers
├── history/              # Task audit trails
│   └── TASK-NNN.md
├── decisions/            # Auto-generated decision records
│   ├── ADR-NNN.md
│   ├── SEC-NNN.md
│   └── DB-NNN.md
└── sprints/              # Sprint archives
    └── sprint-N/
        ├── planning.md
        ├── retro.md
        └── velocity.md
```

Plus root-level: `BACKLOG.md`, `SPRINT.md`, `DAILY.md`, `RETRO.md`

## Conventions

- Commands always read `.claude-agile/config.json` before acting
- Commands check for ccpm availability and warn if missing
- Specialist roles are activated by the Scrum Master based on task classification
- Every task gets an audit trail in `.claude-agile/history/TASK-NNN.md`
- Architecture decisions auto-generate ADRs when Tech Lead participates
- Security findings auto-generate SEC reports when Security Engineer participates
- Story IDs: `US-NNN` | Task IDs: `TASK-NNN` | ADRs: `ADR-NNN`
