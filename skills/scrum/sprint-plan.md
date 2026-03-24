# Scrum Sprint Planning — Reference Knowledge

This document details the sprint planning ceremony: capacity calculation, velocity-based forecasting, sprint goal definition, and team commitment.

---

## Sprint Planning Overview

Sprint Planning is a time-boxed ceremony at the start of each sprint where the team selects work from the Product Backlog and creates a plan for delivering it.

**Duration:** Maximum 4 hours for a 2-week sprint (2 hours for 1-week sprints)
**Attendees:** Product Owner (user), Scrum Master, Development Team
**Inputs:** Product Backlog (prioritized), velocity history, team capacity
**Outputs:** Sprint Goal, Sprint Backlog, initial plan

---

## Part 1: The "What" — Selecting Sprint Items

### Capacity Calculation

Capacity = available time adjusted for non-sprint work.

**For solo developers (claude-agile context):**
- Base capacity: 10 working days per 2-week sprint
- Subtract known absences, meetings, and overhead
- Convert to story points using velocity (if available)

**First Sprint (no velocity history):**

| Team Size | Suggested Starting Capacity |
|-----------|---------------------------|
| Solo | 15-20 points |
| 2-5 people | 30-50 points |
| 5+ people | 50-80 points |

These are intentionally conservative. It's better to finish early and pull in more work than to overcommit.

**Subsequent Sprints (velocity-based):**
- Use the average of the last 3 sprints' velocity
- Apply a confidence factor:
  - High confidence (stable velocity, no changes): use average
  - Medium confidence (some variance): use average - 10%
  - Low confidence (new team, changing scope): use lowest of last 3

### Velocity-Based Forecasting

```
Sprint 1: 18 points (no history, learning)
Sprint 2: 22 points (improving)
Sprint 3: 20 points (stabilizing)
Average: 20 points ← use this for Sprint 4 planning
```

Velocity typically follows a pattern:
1. Sprints 1-2: Lower (learning the process)
2. Sprints 3-5: Stabilizing (finding rhythm)
3. Sprints 6+: Mature (predictable, gradual improvement)

### Item Selection Process

1. **PO presents the top-priority items** from the Product Backlog
2. **For each item, the team asks:**
   - Is this ready? (Clear acceptance criteria, dependencies resolved)
   - Can we complete it this sprint?
   - Does it fit within remaining capacity?
3. **Running total:** Track points as items are selected
4. **Stop when:** capacity is reached OR PO has no more priority items

**Selection Rules:**
- All P0 items must be included (if they fit capacity)
- P1 items are strongly recommended
- P2/P3 items fill remaining capacity
- Never exceed capacity — this protects the team and builds trust

---

## Part 2: The "How" — Sprint Goal & Planning

### Defining the Sprint Goal

The Sprint Goal is a single, clear objective that gives the sprint meaning beyond individual stories.

**Good Sprint Goals:**
- "Users can complete the checkout flow end to end"
- "API performance meets the 200ms SLA"
- "Authentication system is secure and tested"

**Bad Sprint Goals:**
- "Complete stories US-5, US-6, US-7" (that's a list, not a goal)
- "Make progress on the project" (too vague)
- "Fix bugs" (no clear success criterion)

**Formula:** "By the end of this sprint, [user/stakeholder] will be able to [action/outcome]."

### Task Breakdown

For each selected story, break it down into tasks:

```
US-5: User can reset password (3 points)
  Tasks:
  - [ ] Add "forgot password" link to login page
  - [ ] Create password reset request endpoint
  - [ ] Implement email sending with reset token
  - [ ] Create password reset form page
  - [ ] Add token validation and password update
  - [ ] Write tests for all paths (happy, expired token, invalid token)
```

Tasks should be:
- Small enough to complete in hours, not days
- Concrete and actionable
- Ordered by dependency (what must come first)

---

## Commitment and Confidence

### The Commitment Question

After selecting items and breaking them down, ask the team:
> "Given what we know, are we confident we can deliver these items and achieve the Sprint Goal?"

**Confidence levels:**
- **High (80%+):** Proceed as planned
- **Medium (50-80%):** Identify and mitigate risks, consider removing the riskiest item
- **Low (<50%):** Reduce scope until confidence is medium or high

### Over-Commitment Prevention

Signs of over-commitment:
- "We'll just work a bit harder this sprint" — no, use actual velocity
- Taking on items with unresolved dependencies — risky
- Including too many large stories (8+ points) — less room for error
- No buffer for unexpected work — always leave 10-15% slack

### Sprint Backlog as Forecast

The Sprint Backlog is a forecast, not a contract. However:
- Items should NOT be added mid-sprint (protect focus)
- Items CAN be removed if the Sprint Goal is still achievable
- The PO can cancel the sprint if the Sprint Goal becomes obsolete

---

## Sprint Planning Checklist

Before closing the planning ceremony:

- [ ] Sprint Goal is defined and clear
- [ ] Sprint Backlog has selected items with point totals
- [ ] Capacity is not exceeded (planned points <= velocity)
- [ ] All selected items have clear acceptance criteria
- [ ] Dependencies between items are identified and ordered
- [ ] No P0 items left unselected (unless capacity is full)
- [ ] Team (or solo developer) is confident in the plan
- [ ] SPRINT.md is updated with the plan
- [ ] Start and end dates are recorded
