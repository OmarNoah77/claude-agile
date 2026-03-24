# TDD Enforcer — Lean/XP Reference Knowledge

This document covers Test-Driven Development enforcement, the Red-Green-Refactor cycle, test-first development practices, and pair programming guidance.

---

## The TDD Discipline

Test-Driven Development is not optional in Lean/XP — it is the foundational engineering practice. Every line of production code must be justified by a failing test.

### The Three Laws of TDD (Robert C. Martin)

1. **You may not write production code until you have written a failing unit test.**
2. **You may not write more of a unit test than is sufficient to fail** (and not compiling counts as failing).
3. **You may not write more production code than is sufficient to pass the currently failing test.**

These laws create a tight feedback loop measured in minutes, not hours.

---

## Red-Green-Refactor Cycle

### The Cycle

```
    ┌──────────┐
    │   RED    │  Write a failing test
    │ (fail)   │  Test should fail for the RIGHT reason
    └────┬─────┘
         │
         v
    ┌──────────┐
    │  GREEN   │  Write minimal code to pass
    │ (pass)   │  Don't over-engineer — just make it green
    └────┬─────┘
         │
         v
    ┌──────────┐
    │ REFACTOR │  Clean up code and tests
    │ (clean)  │  All tests still pass after refactoring
    └────┬─────┘
         │
         └──── → back to RED
```

### Phase Details

#### RED: Write a Failing Test

1. **Think about the next small behavior** to implement
2. **Write a test** that describes that behavior
3. **Run the test** — it MUST fail
4. **Verify the failure reason:** The test should fail because the behavior doesn't exist yet, NOT because of a typo, missing import, or wrong assertion

**Good test failure:**
```
Expected: calculate_total([10, 20, 30]) to return 60
Actual: function calculate_total does not exist
```

**Bad test failure:**
```
Error: Cannot import module 'calculator' — file not found
```
(This is a setup problem, not a meaningful test failure)

**Guidelines for the RED phase:**
- Write the SMALLEST test that drives the next increment of behavior
- Name the test descriptively: `test_empty_cart_returns_zero_total`
- Start with the simplest case (empty input, single item, happy path)
- Work toward edge cases and error handling progressively

#### GREEN: Make the Test Pass

1. **Write the simplest possible code** that makes the test pass
2. **Do NOT write elegant code** — that comes in the refactor phase
3. **Do NOT write more code than needed** — resist the temptation to "finish" the feature
4. **Run ALL tests** — the new test passes AND all previous tests still pass

**The "simplest possible code" examples:**

Test: `test_greet_returns_hello_name`
```python
# WRONG — too much at once
def greet(name, formal=False, time_of_day=None):
    if formal:
        prefix = "Dear"
    elif time_of_day == "morning":
        prefix = "Good morning"
    else:
        prefix = "Hello"
    return f"{prefix}, {name}!"

# RIGHT — just enough to pass THIS test
def greet(name):
    return f"Hello, {name}!"
```

The extra features (formal, time_of_day) should be driven by their OWN failing tests.

#### REFACTOR: Clean Up

1. **Look for duplication** — in production code AND test code
2. **Improve naming** — variables, functions, test names
3. **Simplify structure** — extract functions, reduce nesting
4. **Run all tests** — refactoring must not change behavior
5. **Commit** — refactoring is complete when all tests pass and code is clean

**Refactoring is not optional.** Skipping it creates technical debt that slows future cycles.

**What to refactor:**
- Duplicate code → extract to helper function
- Long function → split into smaller functions
- Unclear naming → rename for clarity
- Complex conditional → simplify or use polymorphism
- Magic numbers → extract to named constants
- Test duplication → use setup/fixtures/parameterized tests

---

## Test Design Principles

### Test Structure: Arrange-Act-Assert (AAA)

```python
def test_user_can_update_email():
    # Arrange — set up the test conditions
    user = create_user(email="old@example.com")

    # Act — perform the action being tested
    user.update_email("new@example.com")

    # Assert — verify the expected outcome
    assert user.email == "new@example.com"
```

### Test Naming Convention

Use a consistent naming pattern that describes behavior:
```
test_<action>_<condition>_<expected_result>

Examples:
test_login_with_valid_credentials_returns_token
test_login_with_invalid_password_returns_error
test_login_with_locked_account_returns_account_locked_message
test_search_with_empty_query_returns_all_items
test_search_with_no_matches_returns_empty_list
```

### Test Independence

Each test must:
- **Set up its own state** — don't rely on other tests running first
- **Clean up after itself** — don't leave data that affects other tests
- **Pass in isolation** — running one test alone should work
- **Pass in any order** — test order should not matter

### What to Test

| Test Type | What It Verifies | When to Write |
|-----------|-----------------|---------------|
| **Unit** | Single function/method behavior | Always — for every behavior |
| **Integration** | Components working together | When components interact |
| **End-to-End** | Full user workflow | For critical paths |

### What NOT to Test

- **Implementation details:** Don't test that a function calls another specific function — test the BEHAVIOR
- **Framework/library code:** Don't test that React renders a div — test your component's behavior
- **Trivial code:** Simple getters/setters with no logic
- **Third-party APIs:** Mock them — don't test that Stripe actually charges a card

---

## TDD Enforcement in claude-agile

### Before Writing Any Production Code

The enforcer checks:
1. Is there a failing test for the behavior being implemented?
2. Does the test fail for the right reason?
3. Is the test well-structured (AAA pattern)?

### After Writing Production Code

The enforcer checks:
1. Does the new test pass?
2. Do ALL previous tests still pass?
3. Was only the minimum code written to pass the test?
4. Has refactoring been performed?

### TDD Compliance Tracking

For each story, track:
```
| Story | Tests Written First | Tests Total | Coverage | TDD Compliant |
|-------|-------------------|-------------|----------|----------------|
| US-01 | 5/5               | 5           | 95%      | Yes            |
| US-02 | 3/4               | 4           | 88%      | Partial        |
| US-03 | 0/3               | 3           | 72%      | No             |
```

"TDD Compliant" means ALL tests were written before the production code they test.

---

## Pair Programming Guidance

### What Is Pair Programming?

Two developers work together at one computer:
- **Driver:** Types the code, thinks about implementation details
- **Navigator:** Reviews in real-time, thinks about strategy and design
- **Switch roles every 15-30 minutes**

### Pair Programming Styles

#### Driver-Navigator (Classic)
- Driver writes code
- Navigator reviews, asks questions, thinks ahead
- Best for: complex logic, unfamiliar code

#### Ping-Pong (TDD Pairing)
- Person A writes a failing test
- Person B writes code to pass it
- Person B writes the next failing test
- Person A writes code to pass it
- Best for: TDD enforcement, learning

#### Strong-Style
- "For an idea to go from your head into the computer, it MUST go through the other person's hands"
- Navigator dictates, Driver types
- Best for: knowledge transfer, onboarding

### In the claude-agile Context

Since the "pair" is the user and the AI:
- **User as Navigator:** Describes what to build, reviews AI's code
- **AI as Driver:** Implements the code, writes tests
- **Or reverse:** AI describes the approach, user implements
- **Ping-Pong TDD:** User writes test, AI makes it pass (or vice versa)

---

## Eliminating Waste in Development

### The Seven Wastes Applied to TDD

1. **Partially Done Work:** Untested code is partially done — finish with tests
2. **Extra Features:** If there's no test for it, you shouldn't be building it
3. **Relearning:** Tests are documentation — they prevent relearning
4. **Handoffs:** TDD with pair programming minimizes handoff waste
5. **Task Switching:** TDD's tight loop prevents context switching
6. **Delays:** Immediate feedback from tests eliminates waiting for QA
7. **Defects:** Tests catch defects at creation time, not in production

### The TDD Promise

When TDD is practiced rigorously:
- Defect rate drops by 40-80% (research by Microsoft and IBM)
- Design improves naturally (hard-to-test code is a design smell)
- Refactoring is safe (comprehensive test suite catches regressions)
- Documentation is always current (tests describe actual behavior)
- Developer confidence is high (you KNOW the code works)
