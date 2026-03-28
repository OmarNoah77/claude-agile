---
name: Communication Protocol
description: Defines how specialist roles communicate in Team Chat during task execution
phases: [intake, plan, verify]
roles: [SM, TL, QA]
priority: 8
---

## Task Communication Flow

Every task follows this communication pattern:

```
PO requirement → Scrum Master intake
    ↓ (creates task card with ID)
Scrum Master → announces in Team Chat which roles join
    ↓
Tech Lead → architecture decision (if needed)
    ↓ (comments on task card)
Specialist roles → each adds their assessment
    ↓ (Security, UX, DBA comment before implementation)
Developer → implements
    ↓ (updates task status to In Progress)
QA → verifies
    ↓ (PASS or FAIL with reasons)
Scrum Master → closes task, writes summary
```

## Message Format

Every message in Team Chat must include:
1. **Role tag**: `[SCRUM MASTER]` / `[TECH LEAD]` / `[SEC]` / `[DBA]` / etc.
2. **Task reference**: `#TASK-001`
3. **Message type**: `INTAKE` / `DECISION` / `ASSESSMENT` / `QUESTION` / `BLOCKER` / `UPDATE` / `APPROVAL`

## Role Activation by Task Type

The Scrum Master classifies the incoming requirement and activates the relevant roles:

| Task Type | Roles Activated |
|-----------|----------------|
| `feature` | Scrum Master + Tech Lead + Developer + QA |
| `infra/deploy` | DevOps Engineer (+ Cloud Architect if design needed) |
| `database` | DBA (+ Tech Lead if schema change) |
| `security` | Security Engineer (always on auth/payment tasks) |
| `performance` | Observability Engineer + DBA |
| `UI/UX` | Product Designer → then Developer + QA |
| `data/analytics` | Data Engineer + DBA |
| `major release` | Pen Tester + Security Engineer + QA |

## Role Colors

| Role | Color | Tag |
|------|-------|-----|
| Scrum Master | `#a855f7` (purple) | `[SM]` |
| Tech Lead | `#14b8a6` (teal) | `[TL]` |
| Developer | `#3b82f6` (blue) | `[DEV]` |
| QA | `#22c55e` (green) | `[QA]` |
| Cloud Architect | `#f97316` (orange) | `[ARCH]` |
| DevOps Engineer | `#eab308` (yellow) | `[DEVOPS]` |
| DBA | `#92400e` (brown) | `[DBA]` |
| Observability | `#06b6d4` (cyan) | `[OBS]` |
| Security Engineer | `#ef4444` (red) | `[SEC]` |
| Pen Tester | `#991b1b` (dark red) | `[PENTEST]` |
| UX Designer | `#ec4899` (pink) | `[UX]` |
| Data Engineer | `#6366f1` (indigo) | `[DATA]` |

## Auto-Generated Documents

When a task closes, the following are generated automatically based on which roles participated:

| Condition | Document |
|-----------|----------|
| Tech Lead made architecture decisions | ADR (Architecture Decision Record) |
| Security flagged findings | Security Report (SEC-NNN.md) |
| DBA was involved | DB Migration notes (DB-NNN.md) |
| Any task closes | Retrospective entry appended |
