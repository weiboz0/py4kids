# Teacher Notes — Unit 03: Decisions

## Goals

Students leave able to branch with `if`, add alternatives with `elif`/`else`, combine conditions with
`and`/`or`/`not` (and know that `and` binds tighter than `or`), test a range with a chained comparison
`0 <= x <= 10` or the `and` form, remember that string equality is case-sensitive, nest a conditional
inside another, order an `elif` ladder correctly, and read the `SyntaxError` from `=` where `==` was meant.
Success looks like: every student writes a decision that prints a different verdict for different
inputs — and runs its real version, typing values and watching the verdict change.

## Pacing

Budget: three lessons of 60–90 minutes; one new idea per code cell, a *Notice* per rung.
The opening leap-year cell is marked as a **preview** — students read it; they build every part of it
by the end of the unit.

- **Lesson 1 — Choose with `if` (if-statement).** `if`/`else`; the deliberate `SyntaxError` beat
  (`if score = 90:`); a `no-exec` real-input cell that reads a score and decides.
- **Lesson 2 — Choose among Several Paths (elif-else, logical-ops).** New minimal rungs first:
  `print(True and False)`, `print(True or False)`, then `not`. The `elif` ladder top-down; a two-part
  `and` inside `elif` before the triangle example (whose three-way `or` gets its own Notice). The range
  test is now taught both ways — `x >= 0 and x <= 10` and the chained `0 <= x <= 10`; then
  `"Yes" == "yes"` (False: case matters) and a Notice that `and` binds tighter than `or`. A `no-exec` cell
  reads a day name and prints whether it is the weekend.
- **Lesson 3 — Build Clear Decision Trees (conditional-nesting).** Nested decisions; the leap-year rule
  is now built in three steps (`year % 4 == 0` → `and year % 100 != 0` → `or year % 400 == 0`) before the
  full rule; a `no-exec` cell reads a year and applies it; the **Final build**.

60-MINUTE CUT: teach rungs 1–2 live and leave the last rung as a "try it"; the case-sensitivity rung and
the chained-comparison rung are good self-serve rungs.

## Exercises — core vs. More Practice vs. challenge

21 exercises:
- **Core (1–10):** Target Message, Even or Odd, Inclusive Range (either the `and` or the chained form),
  Weekend Label, Medal Ladder (order-sensitive `elif`), Repair the Exact-Score Check, Permission and
  Score (nested), Temperature (was "Fixed-Value Temperature"), **FizzBuzz for One Number** (75 →
  `FizzBuzz`; check 15 first), **Largest of Three** (14, 31, 22 → `Largest: 31`, no `max`).
- **More Practice (11–16):** Order Three Numbers (19, 4, 11 → `4 11 19` using only comparisons and
  temporary-variable swaps), Rock-Paper-Scissors Judge (nested; tie first), Quadrant Finder (nested;
  `(-3, 5)` → Quadrant II, plus Origin / on an axis), Valid Triangle (2, 5, 9 → `Not a triangle`),
  Traffic Light Art (`yellow` → `( )` / `(Y)` / `( )`), Mood Face (72 → `o o` / ` -` / `---`).
- **Challenges (17–21):** Triangle Logic Puzzle, Leap-Year Logic Puzzle, Closed Sign, **Ticket Price**
  (nested; age 15 on a Thursday → `Ticket: $8`), **Valid Clock Time** (nested + chained; 23:60 →
  `Invalid minute`).

**Real versions:** every exercise except 6 (a repair) has a Real version; its real program reads the
values with `input()` (numbers through `int(input())`), one per line, and prints the same verdict.

## Common mistakes

- `=` (assignment) where `==` (comparison) was meant — the planned `SyntaxError`.
- Ordering an `elif` ladder broad-test-first so a later, more specific branch never runs (FizzBuzz: test
  15 before 3 and 5).
- `and`/`or` precedence — `and` binds tighter; parenthesize the leap-year test.
- `"Yes" == "yes"` is False — case matters.
- A chained comparison `0 <= x <= 10` reads naturally; writing `0 <= x and <= 10` is a SyntaxError.
- Forgetting the final `else`, so some inputs print nothing.
- Order Three Numbers: forgetting to compare again after a swap.

## Discussion prompts

- Why must the grade ladder test `>= 90` before `>= 80`? Why must FizzBuzz test 15 first?
- When do you need `and` vs. `or`? Give an everyday example of each.
- Nested `if` or `and`? Rewrite Permission and Score both ways — which reads better?
- What is the difference between `=` and `==`, and how does Python tell you when you confuse them?

## Differentiation

- Strugglers: give a fill-in-the-branches skeleton (conditions written, verdicts blank); Core 9–10 are
  short.
- Fast finishers: More Practice, then the Challenges; run the Rock-Paper-Scissors real program against a
  partner.
- Middle tier: rewrite a nested `if` as an `elif` ladder and confirm identical verdicts.

## More Practice ideas (design 006 D9 genres)

- **Calendar & time:** "is this a valid date?" for month/day (ignore leap years first, then add them).
- **Games:** a one-round "higher or lower" judge for two cards.
- **Input validation (preview):** decide whether a typed age is a child, teen or adult, and what to do
  with an age below 0.
- **ASCII art:** a battery icon `[###  ]` chosen from a charge percentage by an `elif` ladder.
