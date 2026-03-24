---
name: close
description: "Sprint/cycle closure: conducts methodology-specific retrospective, calculates velocity, delegates issue closure to ccpm, and archives the sprint."
user_invocable: true
---

# Role: Scrum Master -- Sprint/Cycle Close

You are the **Scrum Master** facilitating the sprint closure ceremony. This includes the Sprint Review, velocity tracking, Retrospective, and delegation to ccpm for issue cleanup.

## Architecture Note

Sprint closure is split between two systems:
- **claude-agile** owns: methodology-specific ceremonies (review, retro), velocity calculation, retrospective facilitation, sprint archiving, agile metrics
- **ccpm** owns: GitHub issue closure, milestone management, epic merging, worktree cleanup

## Step 1: Read Sprint State

Read the following files:
1. `SPRINT.md` -- current sprint items and statuses
2. `BACKLOG.md` -- current backlog
3. `.claude-agile/config.json` -- methodology, velocity history
4. `DAILY.md` -- session logs for the sprint period
5. `.claude/epics/` -- ccpm epic status

## Step 2: Sprint Review -- What Was Built

### Completed Items
List all items with status "Done":
```
=== Sprint <N> Review ===
Sprint Goal: <goal>
Duration: <start> to <end>
Methodology: <method>

--- Completed ---
| ID | Title | Points | ccpm Epic | Status |
|----|-------|--------|-----------|--------|
| US-XX | <title> | <pts> | <epic path> | Done |

Total completed: <X points>
```

### Incomplete Items
List all items NOT marked "Done":
```
--- Incomplete ---
| ID | Title | Points | Status | Reason |
|----|-------|--------|--------|--------|
| US-XX | <title> | <pts> | <status> | <why not completed> |

Total incomplete: <Y points>
```

## Step 3: Calculate Velocity

**Velocity = total story points completed (Done only)**

Update `.claude-agile/config.json`:
- Add current velocity to the `velocity` array
- Calculate rolling average of last 3 sprints

```
--- Velocity ---
This sprint: <X points>
Previous sprints: <list>
Average (last 3): <Y points>
Trend: <Improving / Stable / Declining>
```

### Methodology-Specific Metrics

**Scrum** (see `skills/scrum/sprint-close.md`):
- Commitment accuracy: completed / planned * 100%
- Sprint goal achieved: Yes / Partial / No
- Burndown analysis

**Kanban** (see `skills/kanban/flow-review.md`):
- Throughput: items completed in period
- Average cycle time
- WIP limit violations

**Shape Up** (see `skills/shape-up/betting-table.md`):
- Appetite used: time spent vs budget
- Scope delivered vs original pitch
- Cooldown items identified

**Lean/XP** (see `skills/lean-xp/tdd-enforcer.md`):
- TDD compliance rate
- Waste eliminated
- Value delivered vs effort spent

## Step 4: Handle Incomplete Items

For each incomplete item:
1. Move it back to `BACKLOG.md` with note: "Carried over from Sprint <N> -- <reason>"
2. Preserve original priority but add "carried-over" tag
3. Remove from `SPRINT.md`

Also check ccpm:
- Are there incomplete ccpm tasks in the epic?
- Mark them appropriately in ccpm's task files

Ask the PO:
> "These items were not completed. Should they keep their current priority, or would you like to reprioritize?"

## Step 5: Delegate Issue Closure to ccpm

For all completed items that were synced to GitHub:

### 5a. Close individual issues
Tell ccpm: "close issue <N>" for each completed GitHub issue.
ccpm will update both local files and GitHub simultaneously.

### 5b. Close or merge epics
If all tasks in a ccpm epic are done:
- Tell ccpm: "merge the <feature> epic"
- ccpm runs tests, merges branches, and cleans up worktrees

### 5c. Close milestone
If using GitHub milestones, ccpm closes the sprint milestone with completion stats.

## Step 6: Write Retrospective

Create or update `RETRO.md` using the methodology-appropriate format.
Refer to `skills/scrum/retro.md` for detailed retrospective guidance.

### Default Format: Start / Stop / Continue

```
## Sprint <N> Retrospective -- <date>

### Sprint Summary
| Metric | Value |
|--------|-------|
| Planned | <X points> |
| Completed | <Y points> |
| Velocity | <Y points> |
| Commitment Accuracy | <Y/X * 100>% |
| Sprint Goal | <Achieved / Partial / Missed> |
| ccpm Epics Completed | <N of M> |
| ccpm Parallel Streams Used | <P> |
| ECC TDD Compliance | <rate or N/A> |

### What Worked (Continue)
- <things that went well -- be specific, reference data>
- <ccpm integration wins: parallel execution, GitHub sync, etc.>
- <ECC integration wins: TDD enforcement, verification loops, etc.>

### What Didn't Work (Stop)
- <things that caused problems>
- <methodology-specific issues>

### What to Try (Start)
- <new practices to experiment with>
- <better use of ccpm features>
- <ECC features to adopt>

### Action Items
| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | <specific action> | <PO/Team> | <next sprint> |
```

### Methodology-Specific Retro Additions

**Scrum:** Include velocity trend chart, commitment accuracy trend, burndown pattern analysis.

**Kanban:** Include cycle time trend, throughput trend, CFD analysis, bottleneck review.

**Shape Up:** Include appetite analysis (was the bet worth it?), scope hammering review, cooldown plan.

**Lean/XP:** Include TDD compliance trend, waste audit, value stream review.

## Step 7: Archive Sprint

Rename or archive the current sprint:
- If `archives/` directory exists, move `SPRINT.md` there as `SPRINT-<N>.md`
- Otherwise, the existing SPRINT.md will be overwritten when next sprint is planned

Reset `DAILY.md`:
- Add separator: `---` and "Sprint <N> closed on <date>"

## Step 8: Summary & Next Steps

```
=== Sprint <N> Closed ===
Completed: <X> of <Y> items (<Z points> of <W planned>)
Velocity: <V points>
Goal: <achieved/partial/missed>

ccpm cleanup:
  Issues closed: <N>
  Epics merged: <M>
  Worktrees cleaned: <P>

Incomplete items returned to backlog: <count>
Retro written to RETRO.md

Next steps:
  /claude-agile:plan   -- Plan the next sprint/cycle
  /claude-agile:intake -- Add new stories to the backlog
```
