# Daily Standup — Reference Knowledge

This document provides guidance on running effective daily standups, tracking the right metrics, and identifying blockers early.

---

## Purpose of the Daily Standup

The daily standup is a synchronization point, not a status report. Its goals are:

1. **Surface blockers** before they become delays
2. **Coordinate work** to avoid duplication or conflicts
3. **Track momentum** — is the sprint/cycle on track?
4. **Maintain focus** — remind the team (and PO) of the sprint goal

In the claude-agile context, the "team" is the AI agent and the PO (user). The standup is a quick check-in between sessions.

---

## Standup Format

### Three Questions (Classic)

1. **What was completed since last check-in?**
   - List specific items, not general activities
   - Reference story IDs when possible
   - Include both code work and non-code work (design decisions, research, etc.)

2. **What's in progress right now?**
   - What's currently being worked on
   - How far along is it (percentage or description)
   - Expected completion: this session, next session, or later

3. **What's blocked or at risk?**
   - Anything preventing progress
   - Decisions needed from the PO
   - Technical unknowns that need investigation
   - External dependencies waiting on others

### Enhanced Format (for claude-agile)

In addition to the three classic questions, include:

4. **Sprint/cycle health check:**
   - Points completed vs points remaining
   - Days elapsed vs days remaining
   - Are we on pace to complete the sprint goal?

5. **Recommendation:**
   - Based on current trajectory, what should the PO focus on?
   - Should we adjust scope, reprioritize, or continue as planned?

---

## Metrics to Track

### Universal Metrics

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| Items Completed | Throughput | Are we shipping? |
| Items In Progress | WIP | Are we focused? |
| Items Blocked | Flow issues | Do we need to unblock? |
| Points Remaining | Sprint progress | Will we finish on time? |

### Scrum-Specific Metrics

**Burndown Chart (Simplified Text Version)**
```
Day 1:  ████████████████████ 40 pts
Day 3:  ███████████████      30 pts (ideal: 34)
Day 5:  ████████████         24 pts (ideal: 28)
Day 7:  █████████            18 pts (ideal: 20)  ← On track
Day 10: ██████               12 pts (ideal: 12)  ← On track
```

If actual is above the ideal line → behind schedule
If actual is below the ideal line → ahead of schedule

**Velocity Tracking**
- Current sprint velocity (points done so far)
- Projected velocity (if current pace continues)
- Historical average (last 3 sprints)

### Kanban-Specific Metrics

**Cycle Time**
- Track how long each item stays in "In Progress"
- Alert if any item exceeds 2x the average cycle time
- Target: reduce cycle time over time

**WIP Compliance**
- Are WIP limits being respected?
- If WIP is at limit: good, flow is managed
- If WIP exceeds limit: alert — something needs to move forward or be parked

**Throughput**
- Items completed per session/day/week
- Trend: is throughput stable, increasing, or decreasing?

### Shape Up-Specific Metrics

**Hill Chart Position**
```
Uphill (Figuring Out)     Downhill (Executing)
    /\                         /\
   /  \                       /  \
  /    \    ← We are here    /    \
 /      \                   /      \
/        \                 /        \
0%       50%              50%       100%
```

- Items in "figuring out" phase: high risk, uncertain
- Items in "executing" phase: lower risk, predictable
- Alert if items stay uphill too long

**Appetite Burn**
- Time spent vs appetite budget
- If 50% of time is used but less than 30% of scope is done: scope hammer time

### Lean/XP-Specific Metrics

**TDD Compliance**
- Tests written before code: yes/no per item
- Test coverage percentage
- Failing tests: 0 is the target

**Waste Detection**
- Partially done work (items started but not finished)
- Context switching (items moved back from In Progress)
- Waiting time (items blocked for more than 1 session)

---

## Identifying and Resolving Blockers

### Blocker Categories

| Category | Example | Resolution |
|----------|---------|------------|
| **Decision Needed** | "Which auth provider should we use?" | Escalate to PO for immediate decision |
| **Technical Unknown** | "Not sure how to handle concurrent writes" | Time-box a spike (max 2 hours) |
| **External Dependency** | "Waiting for API access" | Work around with mocks, flag for follow-up |
| **Scope Ambiguity** | "Story is unclear about edge cases" | Clarify with PO, update acceptance criteria |
| **Resource Conflict** | "Need access to staging environment" | Identify alternative or escalate |

### Blocker Escalation Protocol

1. **Identify** — Name the blocker specifically
2. **Assess Impact** — What items does it affect? How much delay?
3. **Propose Solution** — Always come with a suggestion, not just a problem
4. **Set Deadline** — "We need this resolved by <date> or <consequence>"
5. **Track** — Add to DAILY.md and follow up next standup

### Red Flags to Watch For

- Same blocker appearing in multiple standups → escalation needed
- Item "in progress" for more than 2 sessions → likely stuck, needs help
- Multiple items blocked simultaneously → systemic issue
- Sprint progress significantly behind ideal → scope adjustment needed
- PO repeatedly deferring decisions → decision fatigue, simplify choices
