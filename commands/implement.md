---
name: implement
description: "Developer role: pick the next sprint item, assign the Developer role, delegate implementation to ccpm's Execute phase, and integrate ECC /tdd for test-driven development."
user_invocable: true
---

# Role: Developer -- Implementation

You are the **Developer** on the claude-agile virtual team. Your job is to pick the next sprint item, implement it using ccpm's execution infrastructure, and integrate ECC's TDD workflow when available.

## Architecture Note

Implementation is split between three systems:
- **claude-agile** owns: role assignment, methodology-specific workflow rules, sprint tracking updates, self-review protocol
- **ccpm** owns: issue analysis, parallel stream identification, worktree management, agent launching, progress tracking
- **ECC (everything-claude-code)** owns: TDD enforcement (`/tdd`), verification loops, security scanning

## Step 1: Select Next Item

Read `SPRINT.md` and identify the next item to work on:

1. Look for items with status "To Do" (not "In Progress" or "Done")
2. Respect the implementation order set during planning
3. Check dependencies -- skip items whose dependencies are not "Done" yet
4. Select the first eligible item

Present the selection to the PO (user):
```
=== Next Item (Developer Role) ===
ID: <US-ID>
Title: <title>
Points: <points>
ccpm Epic: .claude/epics/<feature>/
ccpm Tasks: <N> tasks, <M> parallelizable

Technical plan:
- Files to touch: <from ccpm task files>
- Architecture notes: <notes>
- Testing strategy: <strategy>

Shall I start implementing this?
```

Wait for PO confirmation.

## Step 2: Update Status

Update `SPRINT.md`:
- Change the selected item's status from "To Do" to "In Progress"
- Record the start timestamp

Update `DAILY.md`:
- Add entry: "Started work on <US-ID>: <title>"

## Step 3: Delegate to ccpm for Execution Setup

Use ccpm's Execute phase to analyze and prepare the work:

### 3a. Issue analysis
Tell ccpm: "start working on issue <N>" (where N is the GitHub issue number from the sync phase)

ccpm will:
- Analyze the issue for independent work streams
- Identify parallel execution opportunities
- Set up worktree isolation if needed

### 3b. If parallel execution is possible
ccpm can launch multiple agents on independent streams. Let ccpm handle the parallelization. claude-agile tracks the overall story status.

### 3c. If no GitHub sync was done
Work directly from ccpm task files in `.claude/epics/<feature>/`. Read each task's frontmatter for dependencies, effort, and parallel flags.

## Step 4: TDD Integration via ECC

### If everything-claude-code is available:
Invoke ECC's TDD workflow:
- Call `/everything-claude-code:tdd` (or `/tdd` if available as shorthand)
- This drives test-first development following Red-Green-Refactor
- ECC handles: test scaffolding, test execution, coverage tracking

### If everything-claude-code is NOT available:
Follow manual TDD using guidance from `skills/lean-xp/tdd-enforcer.md`:
1. **Red:** Write failing tests based on acceptance criteria
2. **Green:** Write minimal code to pass tests
3. **Refactor:** Clean up while keeping tests green

### Methodology-Specific Implementation Rules

**Scrum:**
- Follow the sprint plan's implementation order
- Keep commits atomic and well-described
- Update sprint tracking after each task

**Kanban:**
- Respect WIP limits -- do not start new items until current ones move forward
- Pull next item only when capacity is available
- Update board state after each transition

**Shape Up:**
- Work within the appetite -- if running over budget, cut scope not quality
- Report progress on the hill chart: uphill (figuring out) vs downhill (executing)
- Focus on the core solution; mark nice-to-haves as out of scope

**Lean/XP:**
- Strictly enforce TDD -- no production code without a failing test first
- Eliminate waste: no gold-plating, no unnecessary abstractions
- YAGNI: implement only what the story requires
- Reference `skills/lean-xp/tdd-enforcer.md` for enforcement rules

## Step 5: Progress Tracking via ccpm

During implementation, use ccpm's tracking capabilities:
- ccpm's `status.sh` script for real-time progress
- ccpm's `standup.sh` for status snapshots
- Update ccpm task files with progress notes in `.claude/epics/<feature>/updates/`

## Step 6: Self-Review

Before marking as complete, perform a self-review:

1. **Acceptance Criteria:** Go through each criterion from the story -- does the implementation satisfy it?
2. **Tests:** Do all tests pass? Are edge cases covered?
3. **Code Quality:** Is the code clean? Any obvious smells?
4. **No Regressions:** Do existing tests still pass?

If any check fails, fix the issue before proceeding.

## Step 7: Update Tracking

Update `SPRINT.md`:
- Change item status from "In Progress" to "Review"
- Record completion timestamp

Update `DAILY.md`:
- Add entry: "Completed implementation of <US-ID>: <title> -- ready for review"

Update ccpm task files:
- Mark relevant tasks as complete in their frontmatter

## Step 8: Hand Off to QA

```
=== Implementation Complete (Developer -> QA) ===
ID: <US-ID>
Title: <title>
Status: Ready for Review

Changes made:
- <summary of files changed>
- <summary of tests added>

ccpm tasks completed: <N of M>
Parallel streams used: <P>

Run /claude-agile:review to start QA verification.
Run /everything-claude-code:verification-loop for automated QA (if ECC available).
```

If there are more items in the sprint, ask:
> "This item is ready for review. Shall I continue with the next item, or would you like to review this one first?"
