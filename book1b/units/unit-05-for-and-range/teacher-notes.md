# Teacher Notes — Unit 05: For & Range

## Goals

Students leave able to write a counting loop with `for` over `range`, read `range(n)` (from 0),
`range(a, b)` (stop value excluded) and `range(a, b, step)` (including a negative step), skip one pass with
`continue` or leave early with `break`, reuse the accumulator/counting techniques from Unit 04 over a
range, and stack one loop inside another (nested loops) to build tables and **ASCII pictures**.
Success looks like: every student replaces a hand-written `while` counter with a `for`/`range` loop, draws
a triangle, a pyramid and a hollow box from a height they type in, and can say which loop is the row and
which is the column.
`for i in range(n)` is introduced as a **named shorthand** for the manual `while` counter students already
built in Unit 04.

## Pacing

Budget: three lessons of 60–90 minutes; one new idea per code cell, a *Notice* per rung.

- **Lesson 1 — Visit a Range (`for`, `range`).** Reproduce Unit 04's 5050 sum as
  `for n in range(1, 101): total = total + n` — same result, less typing (the motivation for `range`).
  Teach `range(n)` and `range(a, b)` with the Notice **"the stop value is not included"**; then the new
  step rungs `range(0, 20, 5)` and `range(10, 0, -1)` (count down with a negative step). A `no-exec`
  real-input cell reads `n` and prints 1 to `n`.
- **Lesson 2 — Calculate across a Range.** Running total and count-by-condition over a range →
  **FizzBuzz** (an `elif` ladder inside a `for`) → the new **`continue`** rung (skip multiples of 3 in
  1–10) → a `no-exec` cell that reads `n` and prints FizzBuzz up to it → the early exit **before** the flag:
  find the first divisor of 91 and `break` (→ 7) → the full prime flag (spec `n ≥ 2`; `range(2, 2)` is
  empty so `n == 2` stays prime).
- **Lesson 3 — Put One Loop inside Another (`nested-loops`) and the ASCII pattern ladder.** First ONE loop
  builds one row of stars (`row_text = row_text + "*"`); then that loop inside an outer loop makes a
  **rectangle** — the first nested loop (Notice on the 8-space inner body and the dedent trap; `break`
  exits only the inner loop). Then the growing triangle (the row number controls the inner loop), the
  `"*" * r` one-liner beside it (loop-built vs. repetition — same picture), `print(piece, end="")` then
  `print()`, a single number row `1 2 3 4 5`, the multiplication table, and the new **width rung**
  `f"{number:3}"` (pads on the left so table columns line up — used by Challenge 29). Then the **pattern
  ladder** in design order: inverted triangle (`range(h, 0, -1)`), right-aligned triangle
  `" " * (h - r) + "*" * r`, centered pyramid `" " * (h - r) + "*" * (2 * r - 1)`. A `no-exec` cell reads
  a height and draws the pyramid. Final build.

60-MINUTE CUT: L1 — the negative-step rung is a good "try it". L2 — primality can wait; keep `continue` and
FizzBuzz live. L3 — teach the triangle and the table live; hand the pattern ladder over as a worksheet
(each rung is one formula change).

## Exercises — core vs. More Practice vs. challenge

31 exercises. Pre-function; either `x = x + 1` or `x += 1` (taught in Unit 04); rows are built as strings
(or with `end=""`), never with lists.

- **Core (1–13)** — the in-class path: **Triangle Number** (1: `n = 250` → `Total: 31375`, rewritten from a
  copy of the lesson cell), Stop-Bound Inspector, Divisible-by-Four Census, FizzBuzz Board, Prime-Flag Test,
  Four-by-Four Times Table, Nested Classification Count, Growing Signal Triangle (the right triangle),
  Factorial over a Range, plus **Countdown by Twos** (10: `20 18 … 2`), **Inverted Triangle** (11),
  **Right-Aligned Triangle** (12: `   *` / `  **` / ` ***` / `****`) and **Hollow Box** (13: 6×4, the
  edge-ROW test outside and the edge-COLUMN test inside its `else`).
- **More Practice (14–26)**, grouped by genre:
  - *ASCII pattern ladder (continues 8 → 11 → 12 → 13):* Checkerboard (`#.#.` / `.#.#` …), Pyramid (height 4),
    Diamond (size 3), Tree with Trunk (the pyramid plus `   |`), Floyd's Triangle (`1` / `2 3` / `4 5 6` /
    `7 8 9 10`).
  - *Number theory:* Skip the Sevens (`continue` → `Sum: 189`), Multiples of 3 or 5 (below 1000 →
    `Sum: 233168`), Perfect Number Check (28), Divisor Count (36 → 9 divisors), Leap Years in a Range
    (1990–2030 → 10, written as nested `if`s — the statement spells out the nesting).
  - *Brute-force puzzle search:* Pythagorean Triples (c ≤ 20 → 6 triples, `a * a + b * b == c * c`),
    Chickens and Rabbits (20 heads, 56 legs → 12 and 8), Coin Combinations (50¢ from 5/10/25 → 10 ways).
- **Challenges (27–31)** — optional: Step-Range Total, Count the Primes, Aligned Times Table (`f"{p:3}"`
  columns), Primes up to 50 (15 primes), Pascal's Triangle (5 rows via `c = c * (row - k) // (k + 1)`).

**Real versions.** Every exercise has a Real version. Art exercises read their height/width/size; Ex 3 and
Ex 7 use the "read `n`, then `n` numbers" idiom (design 006 D3) — the first time students see it. Graded
solution cells never call `input()`; type a real program in and draw a pyramid of height 6 live.

## Common mistakes

- `range` bounds: `range(1, 5)` gives 1–4, not 1–5 — the stop value is excluded; with a negative step,
  `range(10, 0, -1)` stops at 1.
- Nested-loop indentation: the inner body is 8 spaces; `print(row)` belongs at 4 (after the inner loop).
- Forgetting to reset `row = ""` at the start of each outer pass — the rows grow into one long line.
- Trailing spaces in art: build only the leading spaces, never pad the right side.
- `continue` skips the rest of this pass only; it is not `break`.
- Primality flag: forgetting to `break`, or a wrong upper bound; `range(2, 2)` is empty so `2` stays prime.
- FizzBuzz `elif` order: test `% 15` (or `% 3 and % 5`) before `% 3`/`% 5`.
- Pyramid width: row `r` has `2 * r - 1` stars and `h - r` leading spaces — check row 1 and row `h` on paper.

## Discussion prompts

- How is `for i in range(n)` the same as the Unit 04 `while` counter? How is it shorter?
- Why does `range(1, 5)` stop at 4? What does `range(20, 0, -2)` produce?
- In a times table, which loop is the row and which is the column?
- The triangle can be built with an inner loop or with `"*" * r` — when is each easier to read?
- Puzzle search tries every possibility — how many tries does Coin Combinations make?

## Differentiation

- Strugglers: give the outer loop and have them write only the inner loop / the `row` accumulation;
  Countdown by Twos and Inverted Triangle are short.
- Fast finishers: walk the pattern ladder to the Tree, then the puzzle searches, then the Challenges.
- Middle tier: rewrite a `while` counter from Unit 04 as a `for`/`range` loop and confirm identical output;
  redraw the triangle both ways.

## More Practice ideas (design 006 D9 genres)

- **ASCII art:** an hourglass (inverted pyramid then pyramid); a staircase of `#` blocks two wide.
- **Brute-force search:** find all two-digit numbers equal to the sum of their digits times 7.
- **Sequences:** print the first 10 square numbers and the gaps between them (odd numbers!).
- **Calendar & time:** print a 3-row "days of the month" grid for days 1–21 using `f"{d:3}"`.
