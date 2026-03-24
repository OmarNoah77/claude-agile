# Scrum Retrospective — Reference Knowledge

This document covers retrospective facilitation techniques, formats, and practices for driving continuous improvement.

---

## Purpose of the Retrospective

The Retrospective is the team's dedicated time for self-improvement. It answers: "How can we be more effective next sprint?"

**Principles:**
- **Psychological safety:** Everyone should feel safe to speak honestly
- **Blameless:** Focus on systems and processes, not individuals
- **Actionable:** Every retro should produce at least one concrete action item
- **Time-boxed:** 1-1.5 hours for a 2-week sprint

In the claude-agile context, the retro is a structured reflection between the AI agent and the PO (user). The AI analyzes data from DAILY.md and SPRINT.md to provide objective insights.

---

## Start / Stop / Continue Format

This is the primary format used by claude-agile. It's simple, actionable, and easy to facilitate.

### Start (What should we begin doing?)
Things the team is NOT currently doing that could improve the process.

**How to identify "Start" items:**
- Look at blockers from DAILY.md — what practices could prevent them?
- Look at failed items — what process would have caught issues earlier?
- Look at industry best practices not yet adopted
- Ask: "What's one thing we could try next sprint?"

**Examples:**
- "Start writing acceptance criteria before implementation"
- "Start time-boxing spikes to 2 hours maximum"
- "Start running tests before marking items as done"
- "Start breaking stories larger than 5 points"

### Stop (What should we stop doing?)
Things the team IS doing that are wasteful, harmful, or not helping.

**How to identify "Stop" items:**
- Look at activities that consumed time but didn't produce value
- Look at processes that felt like ceremony without purpose
- Look for patterns of frustration in session logs
- Ask: "What frustrated us this sprint?"

**Examples:**
- "Stop starting new items before finishing current ones"
- "Stop skipping tests to save time (it costs more later)"
- "Stop over-estimating to pad the sprint (be honest)"
- "Stop working on unplanned items mid-sprint"

### Continue (What's working well?)
Things the team IS doing that are valuable and should be maintained.

**How to identify "Continue" items:**
- Look at items that went smoothly — what practices were in place?
- Look at metrics that improved — what caused the improvement?
- Ask: "What went well that we want to keep doing?"

**Examples:**
- "Continue writing tests first — caught 3 bugs before they shipped"
- "Continue daily standup check-ins — blockers are surfaced quickly"
- "Continue the intake process — stories are clear and well-defined"
- "Continue small stories (3 points or less) — they flow better"

---

## Data-Driven Retrospective

### Metrics to Review

Pull these from SPRINT.md, DAILY.md, and config.json:

1. **Velocity:** This sprint vs average — improving, stable, or declining?
2. **Commitment Accuracy:** Completed / Planned — are we estimating well?
3. **Cycle Time per Item:** How long did each item take from start to done?
4. **Blocker Count and Duration:** How many blockers? How long to resolve?
5. **Scope Changes:** Were items added or removed mid-sprint?
6. **Defect Rate:** Items that failed QA review — how many, and why?

### Pattern Recognition

Look across multiple sprints for recurring themes:

| Pattern | What It Means | Action |
|---------|---------------|--------|
| Consistently over-committing | Stories are underestimated or too much is planned | Reduce capacity by 15% |
| Same blocker type recurring | Systemic issue not addressed | Root cause analysis needed |
| Large stories always incomplete | Stories aren't split small enough | Enforce 5-point max |
| Velocity declining | Tech debt, burnout, or external factors | Investigate and address |
| Frequent scope changes | Requirements not stable enough for sprints | Consider Kanban or better backlog grooming |

---

## Action Items

### Every Retro Must Produce Action Items

An action item is:
- **Specific:** "Add linting to pre-commit hooks" not "improve code quality"
- **Assignable:** Someone (PO or team) owns it
- **Time-bound:** Due by a specific date (usually next retro)
- **Measurable:** You can tell if it was done

### Action Item Template

| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | Add pre-commit linting | Team | Sprint 5 start | Pending |
| 2 | Split stories > 5 points during planning | Scrum Master | Ongoing | Pending |
| 3 | Create spike template for unknowns | Tech Lead | Sprint 5 Day 3 | Pending |

### Action Item Limits

- Maximum 3 action items per retro
- Fewer is better — focus on the highest impact change
- Carry forward uncompleted actions from last retro (but question if they're still relevant)

### Following Up

At the start of the NEXT retro:
1. Review action items from the previous retro
2. For each: Completed? If yes, did it help? If no, why not?
3. This creates accountability and shows that retros lead to real change

---

## Alternative Retro Formats

While Start/Stop/Continue is the default, here are alternatives for variety:

### 4Ls: Liked, Learned, Lacked, Longed For
- **Liked:** What did you enjoy?
- **Learned:** What did you discover?
- **Lacked:** What was missing?
- **Longed For:** What do you wish you had?

### Mad, Sad, Glad
- **Mad:** What frustrated you?
- **Sad:** What disappointed you?
- **Glad:** What made you happy?

### Sailboat
- **Wind (propellers):** What pushed us forward?
- **Anchor (drag):** What slowed us down?
- **Rocks (risks):** What risks do we see ahead?
- **Island (goal):** Where are we trying to get to?

### For solo developers (claude-agile primary use case)
The Start/Stop/Continue format works best for solo work because:
- It's quick (5-10 minutes)
- It's data-driven (can be generated from session logs)
- It produces actionable items
- It doesn't require group facilitation techniques
