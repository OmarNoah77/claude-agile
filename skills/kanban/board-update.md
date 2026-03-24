# Kanban Board Management — Reference Knowledge

This document covers Kanban board management: WIP limits, swimlanes, the pull system, and bottleneck detection.

---

## Board Structure

A Kanban board visualizes work as it flows through stages. In claude-agile, the board is maintained in SPRINT.md using a markdown table.

### Standard Columns

```
| Backlog | Ready | In Progress | Review | Done |
|---------|-------|-------------|--------|------|
```

**Column definitions:**

| Column | Entry Criteria | Exit Criteria |
|--------|---------------|---------------|
| **Backlog** | Story is written with acceptance criteria | Prioritized and estimated |
| **Ready** | Prioritized, estimated, dependencies clear | Pulled into In Progress |
| **In Progress** | Developer starts working | Code complete, self-reviewed |
| **Review** | Ready for QA verification | All acceptance criteria verified |
| **Done** | QA passed | Deployed or merged |

### Extended Board (Optional)

For more granular tracking:
```
| Backlog | Ready | Design | In Progress | Code Review | QA | Done |
```

Only add columns if they represent a real stage where work waits. Don't add columns just because they exist in a textbook.

---

## WIP Limits

### What WIP Limits Do

WIP (Work In Progress) limits cap the number of items allowed in each column. They are the single most important element of Kanban.

**Why WIP limits matter:**
1. **Prevent multitasking:** Context switching is expensive (research shows 20-40% productivity loss per additional concurrent task)
2. **Surface bottlenecks:** When a column hits its limit, upstream work stops, making the bottleneck visible
3. **Force completion:** You can't start new work until current work moves forward
4. **Improve quality:** Focus on fewer items means more attention per item

### Setting WIP Limits

| Column | Solo Developer | Small Team (2-5) | Larger Team (5+) |
|--------|---------------|-------------------|-------------------|
| Ready | 5 | 8-10 | 10-15 |
| In Progress | 1-2 | team size - 1 | team size / 2 |
| Review | 1-2 | 2-3 | 3-5 |

**The "In Progress" limit is the most critical.** Start strict and relax only if you have evidence it's too restrictive.

### Starting WIP Limits

If you've never used Kanban before:
1. Set "In Progress" WIP limit = 2 (for solo) or team size - 1
2. Run for 1-2 weeks
3. Observe: Are you hitting the limit frequently? Do items flow smoothly?
4. Adjust: If items pile up in one column, either increase its limit or investigate why items aren't moving

### WIP Limit Violations

When a column is at its WIP limit and someone wants to add an item:

**STOP.** Before adding, you must either:
1. **Complete an existing item** in that column (move it forward)
2. **Block an existing item** (move it to a "blocked" state with reason)
3. **Abandon an existing item** (move it back to backlog with explanation)

Never simply ignore the WIP limit. The discomfort of hitting the limit IS the point — it forces the conversation about what's really important.

---

## The Pull System

### Push vs Pull

- **Push:** Work is assigned to a stage (someone says "work on this next")
- **Pull:** Workers pull work from the previous stage when they have capacity

Kanban uses a **pull system.** This means:
- No one assigns work to you — you pull the next highest-priority item when you're ready
- Items are pulled from left to right (Backlog → Ready → In Progress → Review → Done)
- You only pull when you have capacity (your column's WIP limit is not reached)

### Pull Priority Rules

When pulling work from the "Ready" column:
1. **First:** Items that unblock other items (dependency resolution)
2. **Second:** Highest priority (P0 > P1 > P2 > P3)
3. **Third:** Oldest items (prevent aging/starvation)
4. **Fourth:** Smallest items (if everything else is equal, finish small wins quickly)

### Handling Expedited Items

Sometimes a critical item needs to bypass the normal flow (production bug, security issue).

**Expedite Lane:** A special swimlane with its own WIP limit (typically 1) that bypasses normal priorities.

```
| Expedite | [ CRITICAL BUG: login broken ] | → | → | → |
|----------|------|-------------|--------|------|
| Normal   | item | item        | item   | item |
|          | item | item        |        | item |
```

Rules for expedite:
- Only P0/critical items qualify
- WIP limit of 1 — only one expedited item at a time
- Must be resolved before any normal work continues (if it's truly critical)

---

## Swimlanes

Swimlanes are horizontal divisions of the board for different work types:

### Common Swimlane Configurations

**By Work Type:**
```
| Feature    | item | item | item |      |
| Bug Fix    |      | item |      | item |
| Tech Debt  | item |      |      | item |
```

**By Size:**
```
| Small (1-2 pts) | item | item |      | item |
| Medium (3-5 pts) | item |      | item |      |
| Large (8+ pts)  |      | item |      |      |
```

**By Priority:**
```
| Expedite (P0) |      |      |      |      |
| Standard (P1-P2) | item | item | item | item |
| Low (P3)      | item |      |      | item |
```

### When to Use Swimlanes

- When different work types have different flow characteristics
- When you need to ensure certain work types aren't starved
- When WIP limits should differ by work type
- For solo developers: usually not needed (keep it simple)

---

## Bottleneck Detection

### How to Spot Bottlenecks

A bottleneck is a column where work accumulates. It's the constraint that limits the entire system's throughput.

**Visual indicators:**
1. **Full column:** Column is at WIP limit frequently
2. **Empty downstream:** Columns after the bottleneck are often empty
3. **Full upstream:** Columns before the bottleneck are filling up
4. **Long cycle time:** Items spend disproportionate time in the bottleneck column

### Common Bottlenecks and Solutions

| Bottleneck Location | Likely Cause | Solutions |
|---------------------|-------------|-----------|
| **In Progress** | Work is complex, not enough capacity | Split items smaller, pair program, reduce WIP |
| **Review** | Review takes too long or is deprioritized | Set SLA for reviews, make review higher priority than starting new work |
| **Ready** | Too much grooming backlog, not enough doing | Stop adding to ready, focus on completing in-progress work |
| **Testing** | Testing is manual and slow | Automate tests, shift-left testing (TDD) |

### Theory of Constraints Applied to Kanban

1. **Identify** the constraint (bottleneck column)
2. **Exploit** the constraint (maximize throughput at that column — don't waste any capacity there)
3. **Subordinate** everything else (other columns should work at the bottleneck's pace)
4. **Elevate** the constraint (add capacity, improve processes at the bottleneck)
5. **Repeat** (the bottleneck will shift; find the new one)

### Aging Work Items

Track how long items stay in each column. Alert when:
- Any item exceeds 2x the average cycle time for that column
- An item has been in the same column for more than 3 sessions
- An item moves backward (from Review back to In Progress)

Aging items indicate problems:
- Item is too large (split it)
- Item is blocked (identify and resolve the blocker)
- Item is unclear (return to PO for clarification)
- Item is deprioritized (move back to backlog or drop it)
