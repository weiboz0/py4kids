# Teacher Notes — Unit 03: Decisions

## Goals

Students leave able to branch with `if`, add alternatives with `elif`/`else`, combine conditions with
`and`/`or`/`not`, nest a conditional inside another, order an `elif` ladder correctly, and read the
`SyntaxError` that comes from writing `=` where `==` was meant.
Success looks like: every student writes a decision that prints a different verdict for different given
values, and can explain why an `elif` ladder must be ordered from the most specific test down.

## Pacing

Budget: three lessons of 60–90 minutes; worked-example ladders with a *Notice* per rung.

- **Lesson 1 — Choose with `if` (if-statement).** Two possible paths: an `if`/`else` on a given value.
  The **deliberate SyntaxError beat**: `if score = 90:` → `SyntaxError`; fix to `==` and read it together.
- **Lesson 2 — Choose among Several Paths (elif-else, logical-ops).** Teach the logical operators
  `and`/`or`/`not` first (a Notice shows `not True` → `False`), then the `if`/`elif`/`else` ladder
  **top-down** (most specific first) — a Notice explains why the most specific test must come first.
  In-range is written `x >= 0 and x <= 10` (chained `0 <= x <= 10` mentioned only as a Notice).
- **Lesson 3 — Build Clear Decision Trees (conditional-nesting).** Nest a decision inside a decision,
  then the leap-year rule `(year % 4 == 0 and year % 100 != 0) or year % 400 == 0` — pre-explained as
  "divisible by 4, except centuries, except every 400", shown for 1900/2000/2024 and run on 2024. Then the **Final build**.

60-MINUTE CUT (any lesson): teach rungs 1–2 live and leave the last rung as a "try it".

## Exercises — core vs. extra vs. challenge

Core (Exercises 1–7): Target Message, Even or Odd, Inclusive Range (`and`), Weekend Label, Medal Ladder
(order-sensitive `elif`), Repair the Exact-Score Check (`=`→`==`), Permission and Score (a **nested**
decision — an `if` inside an `if`). Extra (Exercise 8): Fixed-Value Temperature. Challenges (9–11):
Triangle Logic Puzzle, Leap-Year Logic Puzzle, Closed Sign (the `not` operator: print `Closed` when
`not is_open`). The design's "logic puzzles" live in Challenge only; no core exercise depends on a
Challenge. Exercise 5 (Medal Ladder) is the one whose output is only correct with the right `elif`
order — use it to teach ordering. All pre-function; `input()` only via the try-it snippet + fixed stand-in.

## Common mistakes

- `=` (assignment) where `==` (comparison) was meant — the planned `SyntaxError`.
- Ordering an `elif` ladder broad-test-first so a later, more specific branch never runs.
- `and`/`or` precedence — parenthesize the leap-year test; `and` binds tighter than `or`.
- Forgetting the final `else`, so some inputs print nothing.
- Testing a range with a single comparison (`x >= 0`) and forgetting the upper bound.

## Discussion prompts

- Why must the grade ladder test `>= 90` before `>= 80`?
- When do you need `and` vs. `or`? Give an everyday example of each.
- Why do the parentheses matter in the leap-year rule?
- What is the difference between `=` and `==`, and how does Python tell you when you confuse them?

## Differentiation

- Strugglers: give a fill-in-the-branches skeleton (the conditions written, the verdicts blank).
- Fast finishers: Extra (8), then the Challenges (9–11).
- Middle tier: rewrite a nested `if` as an `elif` ladder and confirm identical verdicts.
