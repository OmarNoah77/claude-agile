# Scrum Sprint Close — Reference Knowledge

This document covers the Sprint Review (demo) and sprint closure process: velocity update, burndown analysis, and transition to the next sprint.

---

## Sprint Review (Demo)

### Purpose
The Sprint Review is an opportunity to inspect the Increment (what was built) and adapt the Product Backlog based on feedback. It is NOT a status meeting — it's a demonstration of working software.

### Demo Checklist

Before the demo:
- [ ] All "Done" items actually meet the Definition of Done
- [ ] The increment is in a deployable/usable state
- [ ] Edge cases from acceptance criteria have been verified
- [ ] No known critical bugs in completed items

During the demo:
1. **State the Sprint Goal** — was it achieved?
2. **Demo each completed item** — show it working, not just code
3. **Highlight any deviations** from the original plan
4. **Gather feedback** — does this meet the PO's expectations?
5. **Discuss incomplete items** — why weren't they finished?

### Definition of Done

An item is "Done" when:
- [ ] All acceptance criteria pass
- [ ] Code is written and reviewed
- [ ] Tests are written and passing
- [ ] No known bugs
- [ ] Documentation updated (if applicable)
- [ ] Code is merged to the main branch (if applicable)

If any of these are not met, the item is NOT done, regardless of how much work was invested.

---

## Velocity Calculation

### What Counts

- **Count:** Only items that are fully "Done" (met Definition of Done)
- **Don't count:** Partially completed items, even if "90% done"
- **Don't count:** Items completed but with known bugs
- **Don't count:** Carried-over items from previous sprints (they count in the sprint where they're completed)

### Velocity Formula

```
Sprint Velocity = Sum of Story Points for all "Done" items
```

### Tracking Over Time

```
Sprint | Planned | Completed | Velocity | Commitment Accuracy
-------|---------|-----------|----------|--------------------
  1    |   20    |    15     |    15    |       75%
  2    |   18    |    18     |    18    |      100%
  3    |   20    |    22     |    22    |      110%
  4    |   20    |    19     |    19    |       95%
```

**Rolling Average (last 3):** (18 + 22 + 19) / 3 = 19.7 points

### Velocity Trends

| Trend | Meaning | Action |
|-------|---------|--------|
| Stable (variance < 20%) | Team is predictable | Use average for planning |
| Increasing | Team is improving or stories are smaller | Use average, may increase capacity slightly |
| Decreasing | Tech debt, complexity, or team issues | Investigate root cause, reduce planned capacity |
| Erratic (variance > 40%) | Estimation is inconsistent | Recalibrate: re-estimate reference stories |

---

## Burndown Analysis

### Reading the Burndown

The burndown chart shows remaining work (points) over time:

```
Points
40 |*
35 |  *  .
30 |    * .
25 |      *.
20 |       *  .
15 |         *  .
10 |           * .
 5 |              *.
 0 |________________*___
    1  2  3  4  5  6  7  8  9  10
                   Days

* = actual    . = ideal
```

### Burndown Patterns and What They Mean

**Ideal:** Actual closely follows ideal line
- Team is on track, estimation is accurate

**Late Start:** Flat at top, then steep decline
- Items took longer to start than expected
- Common in first sprint; improve task breakdown

**Staircase:** Flat periods followed by sudden drops
- Items are large and completing in batches
- Break stories into smaller pieces

**Plateau then Cliff:** Flat most of sprint, drops at end
- Items aren't being completed incrementally
- Could indicate "big bang" integration or testing at the end
- Improve continuous integration practices

**Scope Creep:** Line goes UP before going down
- Items were added mid-sprint
- Enforce sprint scope protection

**Never Reaches Zero:** Work remaining at sprint end
- Over-commitment or underestimation
- Reduce planned capacity next sprint

---

## Handling Incomplete Items

### Triage Each Incomplete Item

For each item not marked "Done":

1. **Assess remaining work:**
   - Nearly done (< 20% remaining)? Consider completing in first day of next sprint
   - Significantly incomplete? Return to backlog

2. **Understand why:**
   - Blocked by external dependency? Note the dependency
   - Underestimated? Adjust the estimate for re-planning
   - Scope creep? Original story was too large
   - Deprioritized? PO decided other work was more important

3. **Decision:**
   - **Return to backlog:** Move to BACKLOG.md with a note explaining what's done and what remains
   - **Split:** If partially done, create a new story for the remaining work
   - **Drop:** If no longer needed, remove entirely

### Carry-Over Rules

- Incomplete items do NOT automatically go into the next sprint
- They return to the backlog and must be explicitly selected during next Sprint Planning
- This gives the PO the opportunity to reprioritize
- Partial work is noted so the team knows it's not starting from scratch

---

## Sprint Closure Checklist

- [ ] All items triaged as Done / Incomplete
- [ ] Velocity calculated and recorded in config.json
- [ ] Burndown analyzed — patterns identified
- [ ] Incomplete items returned to BACKLOG.md with notes
- [ ] Sprint Goal assessed: Achieved / Partially Achieved / Missed
- [ ] Commitment accuracy calculated
- [ ] SPRINT.md archived or marked as closed
- [ ] Ready for Retrospective
