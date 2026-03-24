# Shape Up Pitch Writing — Reference Knowledge

This document covers how to write effective Shape Up pitches: defining the problem, setting appetite, sketching solutions, identifying rabbit holes, and declaring no-gos.

---

## What Is a Pitch?

A pitch is a document that proposes work for the next cycle. Unlike a user story (which describes WHAT to build), a pitch describes a PROBLEM worth solving and a SOLUTION at the right level of abstraction.

A pitch is NOT:
- A detailed specification (too concrete)
- A vague idea (too abstract)
- A list of requirements (too prescriptive)

A pitch IS:
- A well-defined problem with evidence it matters
- An appetite (time budget) the team is willing to spend
- A solution sketch that gives direction without prescribing implementation
- An honest assessment of risks and boundaries

---

## Pitch Structure

### 1. Problem

**What pain point or opportunity are we addressing?**

Write the problem as a narrative. Include:
- **Who** is affected? (Specific users, not "everyone")
- **What** happens currently? (The status quo)
- **Why** is this a problem? (Impact — wasted time, lost revenue, user frustration)
- **Evidence:** How do we know this is a real problem? (Support tickets, user feedback, analytics data, personal experience)

**Good problem statement:**
> "Customers who want to update their billing information currently have to email support and wait 1-2 business days. We get about 15 of these requests per week. This creates work for the support team and frustrates customers who expect self-service."

**Bad problem statement:**
> "We need a billing page."

The difference: the good statement explains WHY, shows evidence (15 requests/week), and identifies impact (support burden, customer frustration).

### 2. Appetite

**How much time are we willing to spend on this?**

Appetite is a budget, not an estimate. It answers: "How much is this problem worth solving?"

| Appetite | Meaning | Use When |
|----------|---------|----------|
| Small Batch: 1-2 weeks | Quick win, well-understood problem | Fix, tweak, small feature |
| Large Batch: 6 weeks | Full feature, complex problem | New capability, significant change |

**Setting the right appetite:**
- Consider the value: How much pain does this solve?
- Consider the alternatives: Could we solve it with a simpler approach?
- Consider the risk: How uncertain is the solution?

**If the appetite feels too small for the solution:** Simplify the solution, not increase the appetite. This is the key Shape Up discipline.

**If the appetite feels too large for the problem:** The problem might not be important enough, or it should be broken into smaller pitches.

### 3. Solution

**A rough sketch of the approach — not a specification.**

The solution should be at the "fat marker sketch" level: clear enough to guide implementation, abstract enough to leave room for decisions.

#### For UI features, use breadboards:
```
[Screen Name]
  - Element description
  - Element description
  → leads to [Next Screen]

Example:
[Billing Settings]
  - Current plan display
  - "Update Payment Method" button
  → leads to [Payment Form]

[Payment Form]
  - Card number / expiry / CVC fields
  - "Save" button
  - "Cancel" link
  → on save: [Confirmation] with updated info
  → on cancel: back to [Billing Settings]
```

#### For backend/technical features, use system descriptions:
```
Flow:
1. User triggers action X
2. System does Y
3. Result Z is stored/returned

Key components:
- Component A handles <responsibility>
- Component B handles <responsibility>
- They communicate via <mechanism>
```

#### Solution Principles
- **Show the key interactions** — what does the user do, what does the system respond?
- **Leave out visual design** — no colors, fonts, exact layouts
- **Leave out implementation details** — no database schemas, API contracts
- **Include affordances** — what can the user do at each point?
- **Show the flow** — how do screens/states connect?

### 4. Rabbit Holes

**Known risks, complexities, and traps to avoid.**

Rabbit holes are areas where the team could spend disproportionate time if not warned. Identify them upfront and provide guidance.

**Format:**
```
Rabbit Hole: <what could go wrong>
Guidance: <how to avoid it>
```

**Examples:**
```
Rabbit Hole: Supporting all international payment methods
Guidance: Start with Stripe's default form. International methods can be a separate pitch.

Rabbit Hole: Real-time payment validation
Guidance: Basic client-side validation is enough. Don't build a custom validation engine.

Rabbit Hole: Migration of existing payment data
Guidance: Existing customers keep their current method. Only new updates go through the new flow.
```

**How to find rabbit holes:**
- Look for scope that could expand indefinitely ("support all edge cases")
- Look for technical uncertainty ("we've never integrated with this API before")
- Look for design challenges ("make it work on all screen sizes perfectly")
- Look for integration complexity ("sync data with 3 external systems")

### 5. No-Gos

**Explicitly out of scope for this pitch.**

No-gos prevent scope creep by declaring what this pitch will NOT do. They're as important as the solution.

**Format:**
```
No-Go: <thing we are explicitly NOT doing>
Reason: <why it's out of scope>
```

**Examples:**
```
No-Go: Subscription management (upgrade/downgrade plans)
Reason: That's a separate, larger problem. This pitch only covers updating payment method.

No-Go: Payment history / receipts page
Reason: Customers can get receipts from Stripe directly. We'll pitch this separately if there's demand.

No-Go: Multi-currency support
Reason: All our customers are billed in USD. International pricing is a different initiative.
```

---

## Pitch Quality Checklist

Before submitting a pitch to the betting table:

- [ ] **Problem is real:** Evidence supports this is worth solving
- [ ] **Appetite is set:** We know our time budget
- [ ] **Solution is shaped:** Not too abstract, not too concrete
- [ ] **Rabbit holes identified:** Risks are called out with guidance
- [ ] **No-gos declared:** Scope boundaries are clear
- [ ] **Fits the appetite:** The solution can realistically be built within the time budget
- [ ] **Independent:** Can be built without depending on other pitches
- [ ] **Valuable:** Solving this problem creates clear value for users

---

## Shaping Techniques

### De-risking Before Pitching

Before investing a full cycle, reduce uncertainty:

1. **Technical spike:** Build a quick proof-of-concept for the riskiest part (time-box to 1-2 days)
2. **User research:** Talk to users who have the problem — do they confirm it?
3. **Existing solutions:** Look at how competitors solve this — can we learn from them?
4. **Prototype:** Build a rough mockup or prototype to test the interaction model

### Fat Marker Sketches

The "fat marker" metaphor means: sketch with a marker so thick you CAN'T add details. This forces you to focus on structure and flow, not pixels and polish.

**Good level of detail:**
- "A form with fields for card info and a save button"
- "A list showing recent transactions with a filter by date"

**Too detailed:**
- "A form with 16px Helvetica labels, #333 color, 48px input fields with 8px border-radius"
- "A table with sortable columns, pagination showing 25 rows, export to CSV button"

### Fixed Time, Variable Scope

The fundamental Shape Up principle: if the work is taking longer than the appetite, CUT SCOPE, don't extend time.

**Scope hammering questions:**
- "What's the simplest version of this that still solves the core problem?"
- "Can we solve 80% of the problem with 20% of the effort?"
- "What can we defer to a follow-up pitch?"
- "Is there a manual workaround for the edge cases?"
