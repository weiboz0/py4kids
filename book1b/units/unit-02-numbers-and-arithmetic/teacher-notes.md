# Teacher Notes — Unit 02: Numbers & Arithmetic

## Goals

Students leave able to work with integers and floats, use the arithmetic operators (`+ - * / // %`),
follow that `/` gives a float while `//` gives a whole number, convert between text and numbers with
`int()` / `float()` / `str()`, store and print a Boolean, compare values with `== < > <= >= !=`, and
read a `TypeError` when text and a number are joined with `+`.
Success looks like: every student computes a real result (hours-and-minutes, an average, a digit split)
and can explain why `10 / 2` prints `5.0`.

## Pacing

Budget: three lessons of 60–90 minutes; each concept is a short worked-example ladder (minimal → one
twist → realistic, with a *Notice* per rung).

- **Lesson 1 — Calculate with Whole Numbers (int-type, arithmetic, `//`/`%`).** Open on the problem:
  turn a number of minutes into hours-and-minutes (`135 // 60`, `135 % 60`). Keep `//`/`%` on
  non-negative numbers — they mean "whole groups" and "leftover".
- **Lesson 2 — Work with Number Types (float-type, type-conversion).** `/` gives a float — a Notice pins
  `10 / 2` → `5.0` vs `10 // 2` → `5`. Then the **deliberate TypeError beat**: `print("Age: " + 12)`
  raises `TypeError`; fix with `str()` or an f-string. Contrast `"3" + "4"` → `"34"` with `3 + 4` → `7`,
  which is exactly why `int()` on typed text (`int("12")`) matters.
- **Lesson 3 — Ask Number Questions (boolean, comparison).** Compare values and *print the Boolean*
  (`print(first_score >= second_score)`, and all six operators `< <= > >= == !=`), split the digits of a
  two-digit number (`n // 10`, `n % 10`), then the
  **Final build**. End with the boxed **"Peek ahead — not needed for the exercises"** cell that sums
  `1..100` with a `for` loop (→ `5050`): **read it aloud, do not teach it** — it just shows why loops
  (Unit 04/05) exist. Students never modify it.

60-MINUTE CUT (any lesson): teach rungs 1–2 live and leave the last rung as a "try it"; the *Notice*
lines let students self-serve it.

## Exercises — core vs. extra vs. challenge

Core (Exercises 1–7): Supply Total, Trip Time (h:m), Equal Share (a fair-share division → a float),
Next-Year Age, Compare Two Scores (prints Booleans with the comparison operators, no `if`), Two-Digit
Report (digit split), Repair the Age Label (the TypeError beat). The comparison rung in the lesson shows
all six operators (`< <= > >= == !=`). Extra (Exercise 8): Fixed-Value Price. Challenges (9–10): Reverse Two Digits,
Three-Digit Places. No core exercise depends on a Challenge. All pre-function (no `def`); `input()` is
practiced only via the "try it yourself" snippet + a fixed stand-in — graded cells never call `input()`.

## Common mistakes

- Expecting `10 / 2` to print `5` — `/` always gives a float (`5.0`); use `//` for a whole number.
- Forgetting `int()` around typed text before doing math (`"12" + 1` → `TypeError`).
- Joining a number to text with `+` without `str()` / an f-string (the planned `TypeError`).
- Reading `//`/`%` on negative numbers (out of scope here — keep operands non-negative).
- `=` (assignment) where `==` (comparison) was meant.
- Mismatched output vs. the worked sample — compare every digit, space, and the `.0`.

## Discussion prompts

- Why does the computer print `5.0` and not `5` for `10 / 2`?
- When do you want `//` and `%` instead of `/`?
- What are two ways to put a number inside a sentence (`str()` vs. an f-string)?
- How do `n // 10` and `n % 10` pull apart a two-digit number?

## Differentiation

- Strugglers: give the arithmetic pre-written and have them only change the given values and predict the output.
- Fast finishers: Extra (8), then the Challenges (9–10).
- Middle tier: rewrite one `+`/`str()` line as an f-string and confirm identical output.
