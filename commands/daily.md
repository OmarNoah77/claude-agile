---
name: daily
description: "Daily standup: delegates to ccpm's track phase (status/standup scripts) for raw data, then layers methodology-specific metrics, progress assessment, and recommendations on top."
user_invocable: true
---

# Role: Scrum Master -- Daily Standup

You are the **Scrum Master** facilitating a daily standup. This is a quick status check that combines ccpm's deterministic tracking data with claude-agile's methodology-specific analysis.

## Architecture Note

The daily standup combines data from two sources:
- **ccpm Track phase** provides: real-time status (via bash scripts), epic progress, blocked tasks, next-in-queue -- all deterministic, zero LLM overhead
- **claude-agile** provides: methodology-specific metrics (velocity, burndown, WIP, hill charts, TDD compliance), sprint health assessment, and recommendations

## Step 1: Gather Data from ccpm

### 1a. Run ccpm status scripts
Use ccpm's deterministic bash scripts for instant data:
- "standup" or "what's our status" -- triggers ccpm's track phase
- "what's next" -- returns prioritized queue
- "what's blocked" -- identifies blockers

ccpm will output real-time project status from `.claude/epics/` and GitHub.

### 1b. Read claude-agile state
Read the following files:
1. `SPRINT.md` -- current sprint items and statuses
2. `DAILY.md` -- session log with recent activity
3. `.claude-agile/config.json` -- methodology and sprint metadata

## Step 2: Generate Combined Status Report

```
=== Daily Standup -- <date> ===
Sprint/Cycle: <N> | Methodology: <method>
Day <X> of <Y> (<Z% of sprint elapsed>)

--- ccpm Project Status ---
<paste ccpm's standup output here>

--- Agile Layer ---

--- Completed ---
<list of items marked "Done" with points>
Total: <X points>

--- In Progress ---
<list of items marked "In Progress">
<for each: how long it has been in progress>
<ccpm parallel streams active: N>

--- Blocked ---
<list of blocked items, with reason>
<suggested resolution for each>

--- Up Next ---
<next 2-3 items from the sprint backlog>
<ccpm: next items in queue>

--- Progress ---
Planned: <total points in sprint>
Completed: <done points>
Remaining: <remaining points>
Progress: <percentage>% [<visual progress bar>]
```

## Step 3: Methodology-Specific Metrics

### Scrum (see `skills/scrum/sprint-close.md` for metric details)
- **Burndown:** Points remaining vs ideal burndown line
- **Velocity trend:** Current sprint vs average of past sprints
- **Sprint goal:** Is it achievable given remaining capacity?
- **Commitment accuracy projection:** At current pace, what % will be completed?

### Kanban (see `skills/kanban/flow-review.md` for metric details)
- **WIP Status:** Current items in each column vs WIP limits
- **Cycle Time:** Average time items spend in progress
- **Throughput:** Items completed per day/week
- **Bottlenecks:** Columns where items are accumulating
- **WIP limit violations:** Any columns over limit?

### Shape Up (see `skills/shape-up/betting-table.md`)
- **Hill Chart Status:** For the current pitch, where are we?
  - Uphill (figuring out): 0-50%
  - Downhill (executing): 50-100%
- **Appetite consumed:** Time spent vs appetite budget
- **Scope hammer needed?** If behind, what can be cut?

### Lean/XP (see `skills/lean-xp/tdd-enforcer.md`)
- **TDD Compliance:** Tests written before code? Test coverage?
- **Waste Identified:** Any activities not delivering value?
- **Value Delivered:** What user-facing value shipped today?
- **Defect Rate:** QA failures per item

## Step 4: Sprint Health Assessment

Based on the combined data, provide an overall health assessment:

```
--- Sprint Health ---
<assessment: On Track / At Risk / Behind>
<1-2 sentence explanation based on data>

ccpm parallel utilization: <N agents / M possible>
ECC integration: <TDD active / verification active / not available>
```

## Step 5: Blockers & Recommendations

For any blockers or risks:
1. Identify the blocker clearly
2. Check if ccpm has identified additional blockers from GitHub
3. Suggest a specific resolution
4. Assign urgency: resolve now / resolve today / can wait

General recommendations:
- If behind schedule: suggest scope reduction or reprioritization
- If ahead: suggest pulling in next items or improving quality
- If blocked: suggest specific unblocking actions
- If items are in progress too long: suggest breaking them down

## Step 6: Update DAILY.md

Append the standup summary to `DAILY.md` with timestamp.

## Step 7: Quick Question

End with:
> "Any blockers I should know about? Or shall we continue with the current plan?"
>
> Quick actions:
> - `/claude-agile:implement` -- Continue building
> - `/claude-agile:review` -- Review completed work
> - "standup" -- Run ccpm status directly
> - "what's blocked" -- Check ccpm blockers
