# claude-agile Pipeline Flow

## Overview

claude-agile implements an autonomous multi-agent pipeline that processes user requirements end-to-end. The system is inspired by [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) and adapted to claude-agile's 12-role specialist team.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    claude-agile Dashboard                         │
│                    http://localhost:4000                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User (Product Owner)                                            │
│    │                                                             │
│    ▼                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────────┐  │
│  │  SM (Intake) │──▶│  TL (Plan)  │──▶│   DEV (Exec)         │  │
│  │  Scrum Master│   │  Tech Lead  │   │   N workers tmux     │  │
│  └─────────────┘   └─────────────┘   │  ┌────┐ ┌────┐       │  │
│        ▲                              │  │ W1 │ │ W2 │ ...   │  │
│        │                              │  └────┘ └────┘       │  │
│   User confirma                       └──────────┬───────────┘  │
│   User Story                                     │              │
│                                                   ▼              │
│                              ┌─────────────┐   ┌─────────────┐  │
│                              │  DEV (Fix)   │◀──│  QA (Verify)│  │
│                              │  max 3 loops │──▶│  Pass/Fail  │  │
│                              └─────────────┘   └──────┬──────┘  │
│                                                       │         │
│                                                       ▼         │
│                                                 ┌──────────┐   │
│                                                 │ Complete  │   │
│                                                 │ o Failed  │   │
│                                                 └──────────┘   │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Skills (20)  │  Pipeline State  │  Session Artifacts            │
└──────────────────────────────────────────────────────────────────┘
```

## Pipeline Phases

### Phase 1: Intake (Scrum Master)

**Trigger:** User sends a requirement via the dashboard chat.

**Flow:**
1. SM recibe el requerimiento del Product Owner
2. Hace hasta 3 preguntas de clarificación (Rule of Three)
3. Escribe la User Story en formato estándar:
   - As a / I want / So that
   - 3-5 Acceptance Criteria (Given/When/Then)
   - Story Points (Fibonacci: 1,2,3,5,8,13)
   - Priority (P0-P3)
4. Clasifica el tipo de tarea y activa roles especialistas
5. Presenta la User Story al usuario para confirmación

**Output:** User Story + Acceptance Criteria
**Advance marker:** `[PIPELINE:ADVANCE_TO_PLAN]`
**Skills auto-injected:** `po-intake`, `communication-protocol`

### Phase 2: Plan (Tech Lead)

**Trigger:** User confirms the User Story.

**Flow:**
1. TL recibe la User Story y Acceptance Criteria
2. Diseña la arquitectura técnica
3. Descompone en tareas concretas y numeradas
4. Identifica dependencias y riesgos
5. Estima esfuerzo por tarea

**Output:** Implementation plan (saved to `.claude-agile/plans/TASK-NNN-plan.md`)
**Advance marker:** `[PIPELINE:ADVANCE_TO_EXEC]`
**Skills auto-injected:** `communication-protocol`, specialist skills by task type

### Phase 3: Exec (Developer — Parallel Workers)

**Trigger:** TL completes the plan.

**Flow:**
1. El plan se parsea en tareas individuales
2. Si hay >1 tarea: se crean N workers en tmux (default: 2)
3. Cada worker ejecuta `claude -p` con su tarea asignada
4. Watchdog monitorea cada 5s:
   - Detecta workers completados → asigna siguiente tarea
   - Detecta stalls (timeout 180s) → kill y requeue
5. Cuando todos terminan, se genera resumen consolidado

**Parallel execution (tmux):**
```
tmux session: claude-agile-workers
┌────────────────┬────────────────┐
│   Worker 0     │   Worker 1     │
│   Task: API    │   Task: UI     │
│   Status: done │   Status: ...  │
└────────────────┴────────────────┘
```

**Output:** Implementation summary
**Advance marker:** `[PIPELINE:ADVANCE_TO_VERIFY]`
**Fallback:** Si solo 1 tarea, ejecuta secuencialmente (sin tmux)

### Phase 4: Verify (QA)

**Trigger:** All exec tasks completed.

**Flow:**
1. QA recibe la User Story, Acceptance Criteria, y resumen de implementación
2. Verifica cada criterio de aceptación: PASS o FAIL con evidencia
3. Revisa seguridad (OWASP top 10), edge cases, tests
4. Emite veredicto final

**Verdicts:**
- **PASS** → `[PIPELINE:COMPLETE]` — pipeline exitoso
- **FAIL** → `[PIPELINE:ADVANCE_TO_FIX]` — entra al fix loop

**Skills auto-injected:** `communication-protocol`, `security-engineer` (if auth/payment related)

### Phase 5: Fix (Developer — Loop)

**Trigger:** QA finds failures.

**Flow:**
1. DEV recibe los issues específicos del QA
2. Identifica root cause y aplica fix mínimo
3. Se re-ejecuta la fase Verify
4. Loop hasta 3 intentos máximo

**Guard:** `fix_attempts < 3` — después de 3 intentos, pipeline falla

```
DEV(fix) ──▶ QA(verify) ──▶ PASS? ──▶ Complete
                │
                └──▶ FAIL? ──▶ DEV(fix) [attempt 2]
                                │
                                └──▶ QA(verify) ──▶ ...
```

## State Machine

### Transitions

| From     | To       | Guard                          |
|----------|----------|-------------------------------|
| intake   | plan     | User confirms User Story       |
| plan     | exec     | Plan has tasks                 |
| exec     | verify   | All workers completed          |
| verify   | complete | All acceptance criteria pass   |
| verify   | fix      | Any criteria fails             |
| fix      | verify   | Fix applied                    |
| fix      | exec     | Re-implementation needed       |
| *        | failed   | Error or max attempts reached  |

### State Persistence

```
.claude-agile/
├── pipeline-state.json      # Active pipeline state
├── team-chat.jsonl           # Chat log (user + agent messages)
├── plans/
│   └── TASK-NNN-plan.md     # TL implementation plans
├── history/
│   └── TASK-NNN.json        # Completed pipeline archives
├── sessions/
│   └── TASK-NNN.json        # Session artifacts (duration, metrics)
├── workers/
│   ├── tasks.json            # Worker task assignments
│   ├── worker-0/             # Per-worker state
│   │   ├── task.json
│   │   ├── prompt.txt
│   │   └── output.txt
│   └── worker-1/
│       └── ...
└── config.json               # Project configuration
```

## Skill System

### How It Works

Skills are markdown files with YAML frontmatter that get auto-injected into agent prompts.

```yaml
---
name: security-engineer
description: OWASP checks for auth and payment features
triggers: [auth, payment, JWT, encryption, API]
phases: [verify, plan]
roles: [QA, TL]
priority: 10
---

# Security Assessment Guidelines
...
```

### Matching Algorithm

1. **Phase match:** skill.phases includes current phase
2. **Role match:** skill.roles includes current role
3. **Trigger match:** any trigger keyword found in context
4. Skills sorted by match score, top 5 injected into prompt

### Skill Locations (priority order)

1. **Project:** `<project>/.claude-agile/skills/*.md`
2. **Plugin:** `<claude-agile>/skills/**/*.md`
3. **User:** `~/.claude-agile/skills/*.md`

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/api/state` | GET | Project state (backlog, sprint, metrics) |
| `/api/chat/history` | GET | Chat messages |
| `/api/chat/send` | POST | Send user message |
| `/api/pipeline` | GET | Pipeline state + worker status |
| `/api/skills` | GET | List loaded skills |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_AGILE_PORT` | 4000 | Dashboard server port |
| `CLAUDE_AGILE_WORKERS` | 2 | Number of parallel tmux workers |
| `CLAUDE_AGILE_PROJECT` | cwd | Project root directory |

### Starting the Dashboard

```bash
cd /path/to/your/project
python3 ~/claude-agile/dashboard/server.py
```

Or with explicit project path:
```bash
python3 ~/claude-agile/dashboard/server.py /path/to/project
```

## Example Flow

```
User: "Quiero crear un módulo de reportes semanales de fitness"

[SM] INTAKE — 3 preguntas de clarificación:
  1. ¿Qué datos incluye el reporte?
  2. ¿Cómo se entrega? (app, email, PDF)
  3. ¿Quién lo consume?

User: "Resumen de entrenamientos, dentro de la app, para el usuario"

[SM] User Story US-001: "Reportes Semanales de Fitness"
  As a usuario de fitness
  I want ver un reporte semanal de mis entrenamientos
  So that puedo trackear mi progreso

  AC: 3 criterios, 5 SP, P1
  Roles: DEV + QA + UX

User: "Confirmo"

[SM] → [PIPELINE:ADVANCE_TO_PLAN]

[TL] PLAN — Arquitectura:
  1. Crear endpoint GET /api/fitness/weekly-report
  2. Agregar vista WeeklyReportPage en frontend
  3. Implementar query de agregación semanal
  4. Añadir gráficas de progreso

[TL] → [PIPELINE:ADVANCE_TO_EXEC]

[DEV] EXEC — 2 workers paralelos:
  Worker-0: Tasks 1,3 (backend)
  Worker-1: Tasks 2,4 (frontend)
  ... ejecutando en tmux ...

[DEV] → [PIPELINE:ADVANCE_TO_VERIFY]

[QA] VERIFY:
  AC1: GET /api/fitness/weekly-report returns data ✓ PASS
  AC2: WeeklyReportPage renders correctly ✓ PASS
  AC3: Chart shows weekly progress ✓ PASS

[QA] → [PIPELINE:COMPLETE]

Session artifact saved: .claude-agile/sessions/TASK-63787.json
```
