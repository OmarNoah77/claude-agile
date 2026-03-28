---
name: po-intake
description: "Guide for running PO intake sessions: elicit requirements, write user stories, estimate effort"
triggers: [requirement, feature, user story, intake, requerimiento, funcionalidad]
phases: [intake]
roles: [SM]
priority: 10
---

# Product Owner Intake — Reference Knowledge

This document provides guidance on running effective Product Owner intake sessions: how to elicit requirements, write good user stories, estimate effort, and map dependencies.

---

## Eliciting Requirements

### The Art of Asking Clarifying Questions

When a PO describes a feature, they often have a clear picture in their mind but communicate only a fraction of it. Your job is to fill in the gaps without overwhelming them with questions.

**Rule of Three:** Ask no more than 3 clarifying questions. If you need more context, make reasonable assumptions and state them explicitly.

### Key Question Categories

**1. User & Context Questions**
- Who will use this feature? (End user, admin, API consumer, internal team?)
- How often will they use it? (Once, daily, continuously?)
- What's their technical level? (Novice, intermediate, expert?)
- Where do they use it? (Desktop, mobile, CLI, API?)

**2. Behavior Questions**
- What happens when it works correctly? (Happy path)
- What happens when something goes wrong? (Error cases)
- What happens at the boundaries? (Edge cases: empty input, max values, concurrent access)
- What should NOT happen? (Anti-requirements)

**3. Constraint Questions**
- How fast does it need to be? (Performance requirements)
- Who should and shouldn't have access? (Security/auth requirements)
- Does it need to work with existing features? (Integration requirements)
- Are there regulatory or compliance needs? (Legal requirements)

**4. Value Questions**
- Why does this matter? What problem does it solve?
- What's the cost of NOT doing this?
- How will we know if it's successful? (Success metrics)

### Handling Vague Requirements

When a PO says something vague, use these techniques:

| Vague Input | Technique | Example Response |
|------------|-----------|-----------------|
| "Make it faster" | Quantify | "What response time would feel fast enough? Under 200ms? Under 1s?" |
| "Add search" | Scope | "Search across what? Just titles, or full content? With filters?" |
| "Fix the login" | Reproduce | "What specific behavior are you seeing? What should happen instead?" |
| "Make it better" | Decompose | "Better in what way? Easier to use? More reliable? More features?" |
| "Like competitor X" | Differentiate | "What specifically about X's approach do you like? What would you change?" |

---

## Writing User Stories

### The Format

```
As a <user role>
I want <feature or capability>
So that <benefit or value>
```

### INVEST Criteria — Every Good Story Is:

- **I**ndependent: Can be developed and delivered on its own
- **N**egotiable: Details can be discussed; it's not a rigid contract
- **V**aluable: Delivers value to a user or stakeholder
- **E**stimable: The team can estimate the effort
- **S**mall: Can be completed in one sprint/cycle
- **T**estable: Clear criteria for "done"

### Common Anti-Patterns

| Anti-Pattern | Example | Fix |
|-------------|---------|-----|
| Too vague | "As a user, I want the system to work" | Add specifics about what "work" means |
| Too technical | "As a developer, I want to refactor the ORM layer" | Reframe as user value: "As a user, I want pages to load faster" |
| Too large | "As a user, I want a complete e-commerce system" | Split into smaller stories (cart, checkout, payment, etc.) |
| No value | "As a user, I want a blue button" | Ask why — what behavior does the button enable? |
| Compound | "As a user, I want to search AND filter AND sort" | Split into 3 stories |

### Story Splitting Techniques

When a story is too large (8+ points), split it using these patterns:

1. **By workflow step:** Registration → Login → Password Reset
2. **By data variation:** Text posts → Image posts → Video posts
3. **By operation:** Create → Read → Update → Delete
4. **By platform:** Web → Mobile → API
5. **By user role:** Admin view → User view → Guest view
6. **By acceptance criteria:** Each AC becomes its own story
7. **By happy/sad path:** Success case → Error handling

---

## Acceptance Criteria

### Given/When/Then Format

```
Given <precondition — the starting state>
When <action — what the user does>
Then <outcome — what should happen>
```

### Guidelines for Good Acceptance Criteria

1. **Each criterion tests ONE thing** — don't combine multiple behaviors
2. **Use concrete values** — "returns 3 items" not "returns some items"
3. **Include edge cases** — empty states, maximum values, error conditions
4. **Be testable** — someone should be able to verify pass/fail unambiguously
5. **Cover the sad path** — what happens when things go wrong?

### Example

```
Story: As a user, I want to search products by name so that I can find what I'm looking for.

AC1: Given the product catalog has items,
     When I type "laptop" into the search bar and press Enter,
     Then I see all products with "laptop" in the name, ordered by relevance.

AC2: Given the product catalog has items,
     When I type a query that matches no products,
     Then I see a "No results found" message with a suggestion to try different terms.

AC3: Given I am on the search results page,
     When the search takes more than 2 seconds,
     Then I see a loading indicator.

AC4: Given I type fewer than 2 characters,
     When I press Enter,
     Then the search is not executed and I see a hint "Enter at least 2 characters."
```

---

## Story Point Estimation

### The Modified Fibonacci Scale

| Points | Complexity | Uncertainty | Effort | Reference Example |
|--------|-----------|-------------|--------|-------------------|
| 1 | Trivial | None | Minutes-hour | Change a config value, fix a typo |
| 2 | Low | Low | Hours | Add a form field, simple bug fix |
| 3 | Moderate | Low-Medium | Half day to day | New API endpoint with validation |
| 5 | Significant | Medium | 1-3 days | Feature with multiple components |
| 8 | High | Medium-High | 3-5 days | Cross-cutting feature, integration |
| 13 | Very High | High | 1-2 weeks | Should be split into smaller stories |

### Estimation Factors

**Complexity** — How many components, systems, or concepts are involved?
- Single file change → low
- Multiple files, same module → moderate
- Cross-module or cross-system → high

**Uncertainty** — How much do we know about the solution?
- Done it before → low
- Done something similar → medium
- Never done, unfamiliar territory → high

**Effort** — Raw amount of work, assuming we know exactly what to do.
- Small change → low
- Significant new code → medium
- Large volume of work → high

### Calibration Technique

Establish a reference story that the team agrees is a "3" — something moderately complex with low uncertainty. Then estimate all other stories relative to that reference.

"Is this bigger or smaller than our reference 3? How much bigger/smaller?"

### When to Split (the "13 rule")

If an estimate is 13 or higher:
- The story is too large and should be split
- Look for natural seams: workflow steps, data types, user roles
- Each resulting story should be 5 or smaller
- It's okay to have a few 8-point stories, but they carry risk

---

## Dependency Mapping

### Types of Dependencies

1. **Technical Dependencies:** Story B requires code/infrastructure from Story A
   - Example: "Add payment" depends on "Set up Stripe integration"

2. **Knowledge Dependencies:** Story B requires decisions or designs from Story A
   - Example: "Build UI" depends on "Design mockups"

3. **External Dependencies:** Story depends on something outside the team
   - Example: "Integrate with partner API" depends on partner providing API keys

4. **Resource Dependencies:** Story requires a specific person or skill
   - Example: "Set up CI/CD" requires DevOps expertise

### Dependency Visualization

```
US-1 → US-3 → US-5
            ↘ US-6
US-2 → US-4
```

### Dependency Resolution Strategies

1. **Reorder:** Do the dependency first
2. **Stub/Mock:** Implement against an interface, build the real thing later
3. **Split:** Extract the dependent part into its own story
4. **Spike:** Do a time-boxed investigation to reduce uncertainty
5. **Accept:** Some dependencies are real constraints — plan around them
