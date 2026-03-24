# Kanban Flow Review — Reference Knowledge

This document covers flow metrics analysis: cycle time, throughput, lead time, and cumulative flow diagrams.

---

## Flow Metrics Overview

Kanban's power comes from measuring and optimizing flow. Unlike Scrum (which measures velocity in points per sprint), Kanban measures how quickly and smoothly work moves through the system.

### Key Metrics

| Metric | Definition | Formula |
|--------|-----------|---------|
| **Lead Time** | Time from request to delivery | Delivery date - Request date |
| **Cycle Time** | Time from work started to work completed | Done date - In Progress date |
| **Throughput** | Number of items completed per period | Items done / Time period |
| **WIP** | Number of items currently in progress | Count of items in active columns |

### The Relationship (Little's Law)

```
Average Cycle Time = Average WIP / Average Throughput
```

This means:
- To reduce cycle time → reduce WIP or increase throughput
- To increase throughput → reduce WIP (counterintuitive but proven)
- WIP is the lever you can control most directly

---

## Cycle Time

### What It Measures
Cycle time measures how long an item takes from the moment work begins to the moment it's completed. It does NOT include time waiting in the backlog.

### Tracking Cycle Time

For each completed item, record:
```
| Item ID | Start Date | Done Date | Cycle Time |
|---------|-----------|-----------|------------|
| US-01   | Mar 1     | Mar 3     | 2 days     |
| US-02   | Mar 2     | Mar 2     | 0.5 days   |
| US-03   | Mar 3     | Mar 6     | 3 days     |
| US-04   | Mar 5     | Mar 7     | 2 days     |
```

### Cycle Time Analysis

**Average Cycle Time:** Sum of all cycle times / number of items
- Track over time to see if it's improving
- Compare by item size (small items should have shorter cycle time)

**Percentile Analysis:**
- 50th percentile (median): "Most items complete in X days"
- 85th percentile: "85% of items complete in X days" — use for commitments
- 95th percentile: "Almost all items complete in X days" — use for SLAs

**Cycle Time Scatter Plot (text representation):**
```
Days |
  5  |          *
  4  |    *
  3  |       *     *
  2  | *  *     *     *  *
  1  |    *  *           *
  0  |________________________
      US1 US2 US3 US4 US5 US6
```

Look for:
- Items above the 85th percentile line — these are outliers, investigate why
- Trends: Is the scatter getting tighter (more predictable) or wider (less predictable)?
- Clusters: Do certain types of items consistently take longer?

---

## Throughput

### What It Measures
Throughput measures how many items the team completes per time period (typically per week).

### Tracking Throughput

```
| Week | Items Completed | Notes |
|------|----------------|-------|
| W1   | 3              | First week, getting started |
| W2   | 4              | Steady |
| W3   | 2              | Blocked by external API |
| W4   | 5              | Unblock resolved, catch-up |
```

### Throughput Analysis

**Average Throughput:** Total items completed / Number of weeks
- More stable than velocity (in Scrum) because it counts items, not estimated points
- Less influenced by estimation errors

**Throughput for Forecasting:**
- "At our current throughput of 3.5 items/week, the 12-item backlog will take approximately 3.4 weeks"
- Use the 85th percentile cycle time for individual item commitments
- Use throughput range (min-max over last 4 weeks) for batch forecasting

### Throughput vs Velocity

| Aspect | Throughput (Kanban) | Velocity (Scrum) |
|--------|-------------------|-----------------|
| Unit | Items per period | Points per sprint |
| Sensitivity to estimation | Low (counts items) | High (weighted by estimates) |
| Granularity | Any period | Per sprint only |
| Comparability | Across teams (items are items) | Only within team (points are relative) |

---

## Lead Time

### What It Measures
Lead time measures the total time from when a request is made to when it's delivered. This includes wait time in the backlog.

```
Lead Time = Cycle Time + Queue Time

|--- Queue Time ---|--- Cycle Time ---|
Request    →    Work Starts    →    Delivered
```

### Why Lead Time Matters

- **Customer perspective:** The customer doesn't care about your internal processes — they care about how long it takes from asking to receiving
- **Queue time is often the biggest waste:** An item might take 2 days to build but sit in the backlog for 2 weeks — lead time is 16 days, not 2 days

### Reducing Lead Time

1. **Reduce queue time:** Prioritize ruthlessly, limit backlog size, pull frequently
2. **Reduce cycle time:** Smaller items, fewer handoffs, better tooling
3. **Reduce batch size:** Deliver incrementally rather than in large batches

---

## Cumulative Flow Diagram (CFD)

### What It Shows
A CFD plots the number of items in each stage over time. The horizontal axis is time, the vertical axis is item count, and each stage is a band of color.

### Text-Based CFD Representation

```
Items
  20 |         DDDDDDDDDDD
  18 |       DDDDDDDDDDDDD
  16 |     DDDRRRRRRRRRRRRR
  14 |   DDDRRRRRRRRRRRRRRR
  12 |  DDDRRRIIIIIIIIIIIIII
  10 | DDDRRRIIIIIIIIIIIIIII
   8 |DDDRRRIIIRRRRRRRRRRRRRR
   6 |DDRRRIIIRRRRRRRRRRRRRR
   4 |DRRIIIRRRRBBBBBBBBBBBB
   2 |RIIIRRRBBBBBBBBBBBBBBB
   0 |________________________
      W1   W2   W3   W4   W5

D=Done  R=Review  I=In Progress  B=Backlog
```

### Reading the CFD

**Band width = WIP for that stage**
- Wide band → many items in that stage → potential bottleneck
- Narrow band → few items → flow is smooth

**Band width changes over time:**
- Widening → items are accumulating (work entering faster than leaving)
- Narrowing → items are draining (work leaving faster than entering)
- Constant → flow is balanced

**Vertical distance between bands = Lead Time**
- Measure from the bottom of one band to where it reaches "Done"
- Increasing vertical distance → lead time is growing (bad)
- Decreasing vertical distance → lead time is shrinking (good)

**Flat top line (Done) = No items being completed**
- If "Done" stops growing, throughput has stopped
- Investigate immediately — is there a blockage?

### CFD Patterns

| Pattern | Meaning | Action |
|---------|---------|--------|
| Bands are parallel and evenly spaced | Healthy flow | Continue current practices |
| "In Progress" band widening | WIP is growing, bottleneck forming | Reduce WIP, address bottleneck |
| "Done" band flattening | Throughput has stopped | Check for blockers, system issues |
| Large "Backlog" band | Too many items queued | Groom backlog, reduce intake |
| Bands converging | Flow is improving | Identify what changed and keep doing it |

---

## Service Level Expectations (SLEs)

### What They Are
SLEs are commitments about how long items will take, based on historical data.

### Setting SLEs

Based on cycle time percentiles:
- **Standard items:** "85% of items will be completed within X days"
- **Expedited items:** "95% of expedited items will be completed within Y days"

### Example

```
Historical data: 50 items completed

Cycle Time Distribution:
  < 1 day:   15 items (30%)
  1-2 days:  20 items (40%)  ← 70th percentile
  2-3 days:   8 items (16%)  ← 86th percentile
  3-5 days:   5 items (10%)  ← 96th percentile
  > 5 days:   2 items (4%)   ← 100th percentile

SLE: "85% of standard items complete within 3 days"
```

### Using SLEs for Forecasting

When a PO asks "when will this be done?":
1. Look at the SLE: "Based on our data, 85% of similar items complete within 3 days"
2. Note uncertainty: "The remaining 15% take up to 5 days"
3. Give a range: "You can expect this between 2-5 days, most likely around 3 days"

This is more honest and data-driven than a single-point estimate.
