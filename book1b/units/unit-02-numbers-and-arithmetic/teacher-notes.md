# Teacher Notes — Unit 02: Numbers & Arithmetic

## Goals

Students leave able to work with integers and floats, use the arithmetic operators (`+ - * / // % **`),
predict results using operator precedence and parentheses, put an expression inside f-string braces,
format money with `:.2f`, repeat text with `"=" * 12`, convert between text and numbers with `int()` /
`float()` / `str()`, store and print a Boolean, compare values with `== < > <= >= !=`, and read the
`TypeError` (text + number) and `ValueError` (`int("abc")`) tracebacks.
Success looks like: every student computes a real result (hours/minutes, coins, a digit split), can
explain why `10 / 2` prints `5.0` and why `2 + 3 * 4` is 14, and can run the real version of an exercise
by typing its input.

## Pacing

Budget: three lessons of 60–90 minutes; each concept is a worked-example ladder with one new idea per
code cell and a *Notice* per rung.

- **Lesson 1 — Calculate with Whole Numbers (int-type, arithmetic, `//`/`%`).** Minutes → hours and
  minutes. New rungs: `2 + 3 * 4` then `(2 + 3) * 4` (precedence), `2 ** 5` (power), `f"{3 + 4}"`
  (an expression in braces), then string repetition `"=" * 12` and a divider/title/divider card.
  Keep `//`/`%` on non-negative numbers. Lesson 1 has no real-input cell (`int()` comes in Lesson 2).
- **Lesson 2 — Work with Number Types (float-type, type-conversion).** `/` gives a float; `:.2f` for
  money; the deliberate `TypeError` beat; `int("12")`; the new `no-exec` `int("abc")` cell to read a
  `ValueError`; the `no-exec` real-input cell `age = int(input("Age: "))`.
- **Lesson 3 — Ask Number Questions (boolean, comparison).** `print(8 == 8)` and `print(8 != 9)` as two
  small rungs, then the realistic comparisons and all six operators; the digit split; a `no-exec` cell
  that reads a number and splits it; the **Final build**; then the boxed **"Peek ahead — not needed for
  the exercises"** loop cell (read it aloud, do not teach it — it is design 005's forward-practice demo).

60-MINUTE CUT: teach rungs 1–2 live and leave the last rung as a "try it"; `**` and the f-string
expression rung are good self-serve rungs.

## Exercises — core vs. More Practice vs. challenge

23 exercises:
- **Core (1–11):** Supply Total, Trip Time, Equal Share, Next-Year Age, Compare Two Scores, Two-Digit
  Report, Repair the Age Label, Price (was "Fixed-Value Price"), **Coin Change** (83¢ → 3 quarters, 0
  dimes, 1 nickel, 3 pennies), **Seconds Breakdown** (4000 s → Hours 1 / Minutes 6 / Seconds 40),
  **Boolean Report** (score 66 → True / False / True). Coin Change and Seconds Breakdown require a
  purpose comment.
- **More Practice (12–18):** Three-Digit Sum (468 → 18), Power Pair (7 → 49 / 343), Clock Arithmetic
  (`(hour - 1 + added) % 12 + 1`: 10 + 5 → 3 o'clock), Progress Bar (38 → `###-------`), Box Banner
  (`STAR LAB` in a 12-wide box), Precedence Predictions (14, 20, 2, 16, False), Read the ValueError
  (`int("6.25")` → fixed with `float`).
- **Challenges (19–23):** Reverse Two Digits, Three-Digit Places, **The 1089 Trick** (841 → 148 → 693 →
  396 → 1089; the hundreds digit must be larger than the ones digit, and a difference like 99 is reversed
  as 099 → 990), **Receipt Line** (2.4 + 3.15 → `Total: $5.55`), **Framed Title** (`GO TEAM`, width 11).

**Real versions:** every exercise except 7, 17 and 18 (repair/predict) has a Real version line and a
real program in the solutions that reads numbers with `int(input())` / `float(input())`, one per line.

## Common mistakes

- Expecting `10 / 2` to print `5` — `/` always gives a float (`5.0`); use `//` for a whole number.
- Precedence: `*`, `/`, `//`, `%` happen before `+` and `-`; `**` happens first of all. Parentheses win.
- Forgetting `int()` around typed text before doing math; `int("6.25")` fails — use `float` for decimals.
- Joining a number to text with `+` without `str()` / an f-string (the planned `TypeError`).
- `"=" * 12` repeats text; `"12" * 2` is `"1212"`, not 24.
- `=` (assignment) where `==` (comparison) was meant.
- Clock arithmetic: `(10 + 5) % 12` is 3, but `(9 + 3) % 12` is 0 — that is why the formula shifts by 1.

## Discussion prompts

- Why does the computer print `5.0` and not `5` for `10 / 2`?
- Why is `2 + 3 * 4` 14? Where would you add parentheses to get 20?
- When do you want `//` and `%` instead of `/`? How do they make change from 83¢?
- What are two ways to put a number inside a sentence (`str()` vs. an f-string)?

## Differentiation

- Strugglers: give the arithmetic pre-written and have them change the given values and predict output;
  Precedence Predictions works well done aloud as a class.
- Fast finishers: More Practice, then the Challenges; type in the Coin Change real program and try your own
  amounts.
- Middle tier: rewrite a `+`/`str()` line as an f-string; format a price with `:.2f`.

## More Practice ideas (design 006 D9 genres)

- **Calendar & time:** "what day of the week is it 100 days after a Monday?" with `% 7`.
- **Measurement:** convert centimetres to feet and inches with `//` and `%`.
- **Number tricks:** the "multiply by 9, the digits add to 9" check for a two-digit multiple of 9.
- **ASCII art:** a two-line progress bar for two scores, drawn with `"#" *` and `"-" *`.
