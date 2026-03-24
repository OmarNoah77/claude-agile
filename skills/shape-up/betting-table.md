# Shape Up Betting Table — Reference Knowledge

This document covers the betting table process: evaluating pitches, selecting work for the next cycle, and managing the bet.

---

## What Is the Betting Table?

The betting table is a meeting where leadership (or in the case of a solo developer/small team, the Product Owner) decides which pitches to "bet on" for the next 6-week cycle.

**Key concept:** This is a BET, not a COMMITMENT. You're betting that this problem is worth spending X weeks on. If it doesn't pan out, you stop at the end of the cycle — no extensions.

### Betting Table vs Sprint Planning

| Aspect | Sprint Planning (Scrum) | Betting Table (Shape Up) |
|--------|------------------------|--------------------------|
| Frequency | Every 2 weeks | Every 6 weeks (+ 2 week cooldown) |
| Selection | Multiple small items | 1-2 large bets or several small batches |
| Scope | Fixed (committed points) | Variable (appetite is the budget) |
| Backlog | Persistent, groomed | No persistent backlog — pitches are fresh |
| Decision maker | Team + PO | PO / leadership |

---

## The No-Backlog Principle

Shape Up intentionally has **no persistent backlog.** This is one of its most distinctive (and controversial) features.

**Why no backlog:**
1. **Backlogs are graveyards:** Most items in a backlog will never be done. Maintaining them is waste.
2. **Recency bias is useful:** If something is important, it'll come up again naturally.
3. **Fresh eyes:** Each cycle starts with fresh pitches, not stale backlog items.
4. **Reduced guilt:** No one feels bad about the 200-item backlog that keeps growing.

**What happens to ideas that aren't selected:**
- They're NOT saved to a backlog
- If the idea is important, someone will pitch it again next cycle
- If no one pitches it again, it probably wasn't that important
- People can keep personal notes, but there's no official "waiting list"

**In claude-agile context:** BACKLOG.md still exists (for compatibility with other commands), but in Shape Up mode, it's treated as a "pitch inbox" — items are pitched fresh each cycle and old unfunded pitches are archived or removed.

---

## Evaluating Pitches

### Evaluation Criteria

For each pitch, assess:

#### 1. Problem Validity (Is this worth solving?)
- **Impact:** How many users are affected? How painful is the problem?
- **Evidence:** Do we have data supporting the problem exists?
- **Strategic fit:** Does solving this advance our goals?
- **Urgency:** Will the problem get worse if we wait?

Score: **Must have / Should have / Nice to have / Not now**

#### 2. Solution Quality (Is the pitch well-shaped?)
- **Clarity:** Is the solution clear enough to build from?
- **Abstraction level:** Not too detailed, not too vague?
- **Rabbit holes identified:** Are risks called out?
- **No-gos defined:** Are boundaries clear?

Score: **Ready / Needs work / Not shaped enough**

#### 3. Appetite Fit (Is the budget realistic?)
- **Can it be built in the stated appetite?** Based on team experience and complexity
- **Is the appetite proportional to the value?** Are we spending the right amount?
- **Risk assessment:** What's the probability of needing scope cuts?

Score: **Confident / Possible / Unlikely**

#### 4. Opportunity Cost (What are we NOT doing?)
- **If we bet on this, what pitches don't get funded?**
- **Are there higher-value alternatives?**
- **Can this wait one more cycle without significant cost?**

### Decision Framework

```
IF problem = "Must have" AND solution = "Ready" AND appetite = "Confident":
    → Strong bet — select for cycle

IF problem = "Should have" AND solution = "Ready" AND appetite = "Possible":
    → Good bet — select if capacity allows

IF solution = "Needs work":
    → Send back for more shaping — don't bet yet

IF appetite = "Unlikely":
    → Reduce scope or increase appetite — rethink the pitch

IF problem = "Not now":
    → Don't bet — let it come back next cycle if still relevant
```

---

## Running the Betting Table

### Before the Meeting

1. **Collect pitches:** All shaped pitches are available for review
2. **Pre-read:** Everyone reads the pitches before the meeting (saves time in the meeting)
3. **Cooldown review:** What happened during cooldown? Any discoveries that affect priorities?

### During the Meeting

**Step 1: Review the cycle context**
- How did the last cycle go? (Completed? Scope hammered? Failed?)
- Any urgent items that must be addressed?
- What's the team's appetite for risk this cycle?

**Step 2: Present each pitch (5 minutes each)**
- Pitcher summarizes: Problem, Appetite, Solution (1 minute)
- Group asks clarifying questions (2 minutes)
- Quick temperature check: thumbs up / sideways / down (1 minute)
- Note concerns or suggestions (1 minute)

**Step 3: Select bets**
- For a solo developer: select 1 large batch (6 weeks) OR 2-3 small batches (1-2 weeks each)
- For a team: select based on capacity — typically 1 large batch per team of 2-3 people
- Leave room for cooldown work (bug fixes, exploration, tech debt)

**Step 4: Confirm and commit**
- Selected pitches become the cycle plan
- Unselected pitches are NOT saved — they can be re-pitched next cycle
- Team has full autonomy on implementation within the appetite

### After the Meeting

- Update SPRINT.md with selected pitch(es) and cycle dates
- Start the build cycle immediately or after cooldown
- No further scope changes during the cycle

---

## Managing the Bet During the Cycle

### The Circuit Breaker

Shape Up has a built-in "circuit breaker": if work is not completed within the appetite, it stops. No extensions.

**This is by design:**
- If it couldn't be done in the appetite, the pitch wasn't shaped well enough
- Extensions create unpredictable schedules
- Stopping forces better shaping next time

### What Happens When a Bet Fails

1. **Assess:** Why didn't it complete?
   - Scope was too large → shape a smaller pitch next cycle
   - Unexpected complexity → document the rabbit hole for next time
   - Approach was wrong → try a different solution next cycle
   - Team was blocked → address the blocker

2. **Decide:**
   - **Re-pitch:** Shape a better version for next cycle's betting table
   - **Abandon:** The problem wasn't as important as we thought
   - **Simplify:** Find a simpler solution to the same problem

3. **Key rule:** Work done doesn't carry over automatically. The sunk cost is irrelevant. The question is: "Knowing what we know now, would we bet on this again?"

### Cooldown Period (2 Weeks)

Between cycles, there's a mandatory cooldown period for:
- **Bug fixes:** Address issues from the previous cycle
- **Tech debt:** Clean up technical shortcuts
- **Exploration:** Prototype ideas for future pitches
- **Rest:** Sustainable pace is important
- **Shaping:** Prepare pitches for the next betting table

The cooldown is NOT optional. Skipping it leads to burnout and accumulating debt.

---

## Betting Table for Solo Developers

When the "team" is one person (common in claude-agile):

### Simplified Process
1. **Shape 2-3 pitches** during cooldown (or between sessions)
2. **Self-evaluate:** Which pitch has the highest value/effort ratio?
3. **Pick one:** Select the most impactful pitch
4. **Set appetite:** Be honest — how much time can you invest?
5. **Build:** Execute with full autonomy
6. **Review:** At the end of the cycle, did the bet pay off?

### Solo Betting Rules
- Maximum 1 large batch OR 2 small batches per cycle
- Always include cooldown time (even if it's just 2-3 days)
- Be honest about appetite — it's easy to overcommit when you're the only one deciding
- If a bet fails, don't beat yourself up — learn and re-pitch
