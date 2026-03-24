# Agile Methodology Selector — Reference Knowledge

This document contains detailed knowledge about the four supported agile methodologies, their characteristics, strengths, weaknesses, and selection criteria.

---

## 1. Scrum

### Overview
Scrum is an iterative framework that organizes work into fixed-length sprints (typically 2 weeks). It defines clear roles (Product Owner, Scrum Master, Development Team), ceremonies (Sprint Planning, Daily Standup, Sprint Review, Sprint Retrospective), and artifacts (Product Backlog, Sprint Backlog, Increment).

### Core Principles
- **Empiricism:** Decisions are based on observation and experimentation, not speculation
- **Transparency:** All aspects of the process must be visible to those responsible for the outcome
- **Inspection:** Artifacts and progress are inspected frequently to detect variances
- **Adaptation:** Processes are adjusted as soon as deviation is detected

### Ceremonies
| Ceremony | Duration | Purpose |
|----------|----------|---------|
| Sprint Planning | 2-4 hours | Select and plan sprint work |
| Daily Standup | 15 minutes | Synchronize, surface blockers |
| Sprint Review | 1-2 hours | Demo increment to stakeholders |
| Sprint Retrospective | 1-1.5 hours | Reflect and improve process |

### Artifacts
- **Product Backlog:** Ordered list of everything needed in the product
- **Sprint Backlog:** Items selected for the sprint plus a plan for delivering them
- **Increment:** The sum of all completed items, in a usable state

### Strengths
- Predictable cadence gives stakeholders confidence
- Regular retrospectives drive continuous improvement
- Clear roles reduce ambiguity about who does what
- Velocity tracking enables forecasting
- Sprint boundaries force prioritization decisions

### Weaknesses
- Ceremony overhead can feel heavy for small teams
- Fixed sprints can feel artificial if work doesn't fit neatly
- Sprint commitments can create pressure to cut corners
- Requires discipline to maintain — easy to do "Scrum-but" (Scrum minus the hard parts)
- Mid-sprint scope changes are discouraged, reducing flexibility

### Best For
- Teams of 3-9 people
- Somewhat-to-very predictable requirements
- Stakeholders who need regular visibility
- Teams that benefit from structure and accountability
- Projects with clear deliverables and deadlines

### Not Ideal For
- Solo developers (overhead is too high)
- Highly unpredictable work (support tickets, incident response)
- Teams that need to ship continuously throughout the day

---

## 2. Kanban

### Overview
Kanban is a flow-based method that visualizes work, limits work in progress (WIP), and optimizes the flow of value delivery. Unlike Scrum, there are no fixed iterations — work flows continuously through a series of stages.

### Core Principles
- **Visualize the workflow:** Make all work visible on a board
- **Limit WIP:** Restrict the number of items in each stage
- **Manage flow:** Monitor and optimize how work moves through the system
- **Make policies explicit:** Define clear rules for how work progresses
- **Implement feedback loops:** Regular cadences for review and improvement
- **Improve collaboratively:** Use models and metrics to evolve the process

### Board Structure
```
| Backlog | Ready | In Progress | Review | Done |
|---------|-------|-------------|--------|------|
| item    | item  | item (WIP:2)| item   | item |
```

### Key Metrics
- **Lead Time:** Total time from request to delivery
- **Cycle Time:** Time from work started to work completed
- **Throughput:** Number of items completed per time period
- **WIP:** Number of items currently in progress
- **Cumulative Flow Diagram (CFD):** Visual representation of items in each state over time

### WIP Limits — The Heart of Kanban
WIP limits are the single most important practice in Kanban. They:
- Prevent overcommitment and context switching
- Surface bottlenecks immediately (when a column hits its limit)
- Force conversations about priorities and blockers
- Improve quality by ensuring focus

Recommended starting WIP limits:
- Solo: In Progress = 1-2
- Small team (2-5): In Progress = team size - 1
- Larger team: In Progress = team size / 2

### Strengths
- Minimal overhead — no sprints, no planning ceremonies
- Continuous delivery — ship when ready
- Highly visual — easy to see what's happening
- Flexible — adapts to changing priorities instantly
- Surfaces bottlenecks quickly through WIP limits
- No artificial time boundaries

### Weaknesses
- No built-in planning cadence — easy to lose strategic direction
- Requires discipline to respect WIP limits (temptation to ignore them)
- Harder to forecast when things will be done (no velocity)
- Can feel unstructured for teams that need ceremony
- Stakeholder communication is less natural without sprint boundaries
- Risk of "infinite backlog" without regular grooming

### Best For
- Continuous flow of incoming work (support, maintenance, ops)
- Unpredictable requirements or priorities
- Teams that ship continuously
- Low process overhead tolerance
- Mixed work types (bugs, features, tech debt)

### Not Ideal For
- Teams needing strong stakeholder cadence
- Projects with fixed deadlines and scope
- Teams that benefit from the commitment of sprint goals

---

## 3. Shape Up

### Overview
Shape Up, developed at Basecamp (37signals), organizes work into 6-week cycles followed by 2-week cooldown periods. Work is "shaped" (defined at the right level of abstraction) before being "bet on" by leadership. Teams then have full autonomy to build within the appetite.

### Core Concepts
- **Appetite:** How much time you're willing to spend (the budget), NOT an estimate
- **Shaping:** Defining the problem and solution at the right level of abstraction — not too abstract (wireframe), not too concrete (mockup)
- **Betting Table:** Leadership selects which pitches to fund for the next cycle
- **Hill Chart:** Progress tracking showing "figuring out" (uphill) vs "executing" (downhill)
- **Scope Hammering:** Cutting scope to fit the appetite when time runs short

### Cycle Structure
```
[--- 6-week Build Cycle ---][-- 2-week Cooldown --]
   Teams work on pitches       Fix bugs, explore,
   Full autonomy               tech debt, prototype
```

### The Pitch Format
1. **Problem:** What pain point or opportunity?
2. **Appetite:** How much time are we willing to spend? (Small batch: 1-2 weeks, Big batch: 6 weeks)
3. **Solution:** Rough sketch of the approach (fat marker sketches, not detailed specs)
4. **Rabbit Holes:** Known risks and complexities to avoid
5. **No-Gos:** Explicitly out of scope for this pitch

### Strengths
- Fixed time, variable scope — prevents projects from dragging on
- Autonomy — teams decide HOW to build within the appetite
- No backlogs — if it's important enough, it'll come back as a new pitch
- Cooldown periods prevent burnout and allow for exploration
- Shaping prevents wasted effort on poorly defined work

### Weaknesses
- Requires skilled shapers who can define work at the right level
- 6-week cycles may feel long for some teams
- No backlog means important-but-not-urgent work can fall through cracks
- Less visibility into progress within a cycle (intentionally)
- Doesn't work well when stakeholders need frequent updates
- Cooldown discipline is hard to maintain (temptation to start next cycle early)

### Best For
- Solo or small autonomous teams (2-5 people)
- Product-focused work (building features, not running services)
- Teams that want autonomy over implementation
- Projects where scope can flex but time cannot
- Low process overhead tolerance

### Not Ideal For
- Large teams needing coordination
- Maintenance-heavy projects
- Stakeholders who need weekly visibility
- Work that's inherently unpredictable in size

---

## 4. Lean/XP (Extreme Programming)

### Overview
Lean Software Development (inspired by Toyota's Lean Manufacturing) combined with Extreme Programming (XP) practices. Focuses on eliminating waste, delivering value early, and maintaining technical excellence through engineering practices like TDD, pair programming, and continuous integration.

### Lean Principles (from Mary and Tom Poppendieck)
1. **Eliminate Waste:** Remove anything that doesn't deliver value to the user
2. **Amplify Learning:** Short feedback loops, experimentation
3. **Decide as Late as Possible:** Keep options open, defer commitments
4. **Deliver as Fast as Possible:** Short cycle times, small batches
5. **Empower the Team:** Trust people to make decisions
6. **Build Integrity In:** Quality is not negotiable
7. **Optimize the Whole:** Don't sub-optimize parts at the expense of the system

### XP Practices
| Practice | Description |
|----------|-------------|
| TDD | Write tests before code — Red, Green, Refactor |
| Pair Programming | Two developers, one screen, continuous review |
| Continuous Integration | Integrate and test frequently (multiple times per day) |
| Refactoring | Continuously improve code structure without changing behavior |
| Simple Design | The simplest thing that could possibly work |
| Collective Code Ownership | Anyone can change any code |
| Coding Standards | Agreed-upon conventions, enforced consistently |
| Sustainable Pace | No death marches, consistent productivity |

### Seven Wastes of Software Development
1. **Partially Done Work:** Unfinished features, branches not merged
2. **Extra Features:** Gold-plating, features nobody asked for
3. **Relearning:** Lack of documentation, knowledge silos
4. **Handoffs:** Work passing between people/teams
5. **Task Switching:** Context switching between projects
6. **Delays:** Waiting for decisions, reviews, deployments
7. **Defects:** Bugs that could have been prevented

### Strengths
- Highest code quality of any methodology
- TDD creates a comprehensive regression safety net
- Waste elimination drives efficiency
- Technical excellence prevents technical debt
- Short feedback loops catch issues early
- Pair programming spreads knowledge and catches bugs

### Weaknesses
- TDD and pair programming have a learning curve
- Initial velocity is lower (investment in quality pays off later)
- Requires strong technical discipline
- Can feel rigid for teams not used to engineering practices
- Pair programming doesn't suit all personality types
- Hard to adopt partially — practices reinforce each other

### Best For
- Projects where quality is critical from day one (financial, healthcare, infrastructure)
- Teams with strong technical skills
- Long-lived codebases that must remain maintainable
- Projects where bugs are expensive (production systems)
- Teams willing to invest in practices for long-term payoff

### Not Ideal For
- Prototyping or throwaway code
- Teams without testing experience (steep learning curve)
- Projects with extreme time pressure and no quality requirements
- Solo developers who can't pair (though TDD still applies)

---

## Decision Matrix Summary

| Factor | Scrum | Kanban | Shape Up | Lean/XP |
|--------|-------|--------|----------|---------|
| Team Size | 3-9 | Any | 1-5 | 2-8 |
| Requirements | Predictable | Unpredictable | Mixed | Any |
| Stakeholders | Regular cadence | Ad-hoc | End of cycle | Continuous |
| Overhead | Medium-High | Low | Low-Medium | Medium |
| Quality Focus | Good | Good | Good | Excellent |
| Flexibility | Per-sprint | Continuous | Per-cycle | Continuous |
| Best Artifact | Sprint Backlog | Kanban Board | Pitch | Tested Code |
