# Plan 081 — Book 1b enrichment: Units 04–06 (Loops & Counting, For & Range, Turtle Geometry)

**Goal:** Apply design 006 (D3–D8) to U04–U06: gentler loop ladders, the full ASCII-art pattern
ladder (U05), algorithm variants, the real-input (CP-ready) pattern for U04–U05, and the missing
loop facets (`+=`, best-so-far, digit count, `range` step/negative step, `continue`, `end=`,
string-repetition shapes).

**Spec:** `docs/designs/006-book1b-enrichment.md` (D3/D7 as amended by plans 079/080); U04–U06 audit
(2026-09-24). Structure mirrors plan 080 (house form, lead-in rule, values tables, numbering,
depth rule, fence parity).

## Global constraints

- **Pre-function house form (U01–U06):** solutions build output as named string variables (a loop
  accumulates the lines of a report into one string joined with `"\n"`), print, assert. No `def`.
- **One new idea per code cell**; new rungs are inserted after the Notice cell that follows the
  anchor code cell. **Lead-in rule (as plan 080):** when that Notice ends with the next rung's
  lead-in (`**Realistic:** …`, `**Minimal:** …`, `One twist: …`), move the lead-in into its own
  markdown cell directly above the code cell it introduces, after the inserted rungs; each inserted
  rung gets its own one-sentence lead-in.
- **Numbering:** new core/MP exercises go before each unit's existing Challenges; every exercise is
  renumbered so Challenges stay last (statements, solution headings and teacher-notes agree). The
  `#` column below is provisional.
- **Per-unit allowed toolkit (every cell, every exercise tier, every fence):**
  - U04 adds to U01–U03: `while`, `break` (inside ordinary `while cond:` and `while True:`),
    counters, accumulators and `+=` (taught here as an `accumulator` facet), sentinel loops (real
    programs read until 0), best-so-far tracking.
  - U05 adds: `for`, `range` with 1, 2 and 3 arguments (incl. negative step), nested loops,
    `continue` (taught here as a loop-control facet of `break-statement`), `print(..., end="")`,
    f-string width `:3`.
  - U06: turtle scripts in `assets/*.py` only (the pinned `fake_turtle` subset: forward/backward/
    left/right/penup/pendown/pencolor/color/pensize/speed/bgcolor/done — no fill/circle/goto/
    setheading), if/elif on a loop counter is allowed (U03).
  - Never in U04–U06: lists, `def`, `len`/`max`/`min`/`sum`/`round`/`sorted`, string methods,
    tuple assignment, `in` on strings. `continue` never inside a `while` (infinite-loop trap).
- **Real-input pattern (D3):** U04 and U05 only (U06 turtle is exempt).
  Lessons: U04 L1 countdown from an input number; L2 sentinel sum "read numbers until 0";
  L3 read n → Collatz steps. U05 L1 read n → print 1..n; L2 read n → FizzBuzz 1..n;
  L3 read a height → pyramid. All `no-exec`.
  Exercises: `**Real version:**` line (or `**No real version:**` for repair exercises).
  Solutions: `**The real program**` fence with **bare `input()`** (no prompt text) + `Sample input:`
  + `Expected output:` after every exercise that has a Real version; sentinel real programs read
  until a `0` line (`while True:` + `break`). Lesson `no-exec` cells may show prompts.
- **ASCII art:** no backslashes; each row asserted exactly (trailing spaces never emitted).
- **Values:** tables below are binding; distinctive literals unique across shipped Book 1b
  (grep-verified: 90210, 3721, 12321, 482615, 73185, 58193, 31375, 233168, 768 all unused).

## U04 — Loops & Counting

**Rungs:** (1) after Notice `u04l028`: `total += number` shorthand + Notice; (2) after Notice
`u04l038`: digit-count loop (`n = 4827` → 4) before the digit sum; (3) after Notice `u04l040`:
best-so-far — largest digit of 4827 (one new idea: `if d > best: best = d`); (4) after Notice
`u04l043`: `break` inside an ordinary `while n <= 100:` loop, before `while True`; (5) final build
`u04l051` rewritten as a plain `while n != 1:` loop (no artificial `while True`); (6) three `no-exec`
real-input cells (see above).

**New exercises:**

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | Countdown Liftoff | C | `start = 5` → `5` `4` `3` `2` `1` `Liftoff!` (6 lines) | while, loop-counter |
| 13 | Count the Digits | C | `n = 90210` → `Digits: 5` | loop-counter |
| 14 | Reverse a Number | C | `n = 3721` → `Reversed: 1273` | accumulator |
| 15 | Palindrome Number | MP | `n = 12321` → `12321 is a palindrome` | accumulator, if |
| 16 | Doubling Past a Limit | MP | `value = 3`, `limit = 500` → `768 after 8 doublings` (`while True` + `break`) | break, loop-counter, sentinel-loop |
| 17 | Sum of Even Digits | MP | `n = 482615` → `Even digits: 4` / `Even-digit sum: 20` | running-total, count-by-condition |
| 18 | Count the Odd Digits | MP | `n = 73185` → `Odd digits: 4` | count-by-condition |
| 19 | Largest Digit | MP | `n = 58193` → `Largest digit: 9` | best-so-far |
| 20 | Loop-Built Star Bar | MP | `n = 7` → `Stars: *******` built by `bar = bar + "*"` in a `while` loop | string-concat, loop-counter |
| 21 | First Square Over 300 | MP | → `18 squared is 324` (`break` inside `while n <= 100:`) | break |
| 22 | Fix the Infinite Loop | MP | given a `while` whose counter never changes → repaired (No real version) | error-messages |
| 23 | Fix the Missing Starting Value | MP | given `total = total + n` with no initializer (NameError) → repaired (No real version) | error-messages |
| 24 | Challenge: Collatz Peak | S | `n = 15` → `Peak: 160` | best-so-far, sentinel-loop |
| 26 | Lucky Sevens | MP | `n = 707172` → `Sevens: 3` | count-by-condition |
| 27 | Savings Streak | MP | deposits start at 10 and grow by 5 each week for 8 weeks → `Week 8 total: 220` | running-total, loop-counter |
| 25 | Challenge: Powers of Two | S | → `2^0 = 1` … `2^7 = 128` (8 lines) then `Total: 255` | while, running-total |

Real programs for existing Ex 3 (read amounts until 0 → total) and Ex 9 (read scores until 0 →
tier counts) are sentinel loops (`break` + `sentinel-loop` depth).

## U05 — For & Range

**Rungs:** (1) after Notice `u05l010`: `range(0, 20, 5)` then `range(10, 0, -1)` (two cells);
(2) after Notice `u05l021`: `continue` rung (`for n in range(1, 11)`, skip multiples of 3);
(3) before `u05l023` (after that Notice): "first divisor, then `break`" (`for d in range(2, 91)`,
`91 % d == 0` → 7) before the full prime flag; (4) after Notice `u05l024`: one loop builds one row
string of stars (`row = row + "*"`) before the first nested loop; (5) move the section "A growing
triangle" (`u05l031`–`u05l033`) before "A multiplication table" (`u05l028`–`u05l030`); (6) before
the table: a single-loop number row `1 2 3 4 5`; (7) after the triangle: the `"*" * r` one-liner
version + Notice (loop-built vs repetition); (8) Notice: `print(piece, end="")` then `print()`;
(9) new section "ASCII pattern ladder" before the final build: right-aligned triangle
`" " * (h - r) + "*" * r`, then centered pyramid `" " * (h - r) + "*" * (2 * r - 1)`;
(10) three `no-exec` real-input cells (see above).
Existing Ex 1 (a word-for-word copy of `u05l004`) is rewritten as **Triangle Number**:
`n = 250` → `Total: 31375`.

**New exercises:**

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | Countdown by Twos | C | `range(20, 0, -2)` → `20 18 16 14 12 10 8 6 4 2` | range (step) |
| 13 | Hollow Box | C | `width = 6`, `height = 4` → `######` / `#    #` / `#    #` / `######` (nested `if` required) | nested-loops, conditional-nesting |
| 14 | Right-Aligned Triangle | C | `height = 4` → `   *` / `  **` / ` ***` / `****` | string-concat |
| 15 | Checkerboard | MP | 4×4, `(row + col) % 2` → `#.#.` / `.#.#` / `#.#.` / `.#.#` | nested-loops |
| 16 | Pyramid | MP | `height = 4` → `   *` / `  ***` / ` *****` / `*******` | string-concat |
| 17 | Diamond | MP | `size = 3` → `  *` / ` ***` / `*****` / ` ***` / `  *` | nested-loops |
| 18 | Tree with Trunk | MP | `height = 4` → the 4-row pyramid + trunk row `   |` | string-concat |
| 19 | Floyd's Triangle | MP | 4 rows → `1` / `2 3` / `4 5 6` / `7 8 9 10` | nested-loops, loop-counter |
| 20 | Skip the Sevens | MP | 1..20 skipping multiples of 7 with `continue` → `Sum: 189` | continue, running-total |
| 21 | Multiples of 3 or 5 | MP | below 1000 → `Sum: 233168` | count-by-condition, running-total |
| 22 | Perfect Number Check | MP | `n = 28` → `28 is perfect` | running-total |
| 23 | Divisor Count | MP | `n = 36` → `36 has 9 divisors` | count-by-condition |
| 24 | Challenge: Aligned Times Table | S | 6×6 with `f"{p:3}"` → 6 rows, last `  6 12 18 24 30 36` | nested-loops |
| 26 | Leap Years in a Range | MP | years 1990..2030 with the U03 nested leap rule (nested `if` required) → `Leap years: 10` | conditional-nesting, count-by-condition |
| 25 | Challenge: Primes up to 50 | S | → `2 3 5 7 11 13 17 19 23 29 31 37 41 43 47` and `Count: 15` | nested-loops, break |

## U06 — Turtle Geometry (input-exempt)

**Rungs:** (1) move the section "Travel without drawing" (`u06l008`–`u06l009`) after "Replace
repetition with a loop" (`u06l011`–`u06l012`), so the loop is taught before a travel cell uses it;
(2) before the ring (`u06l027`): a new asset `l3_two_squares.py` — two squares by hand with a turn
between them — then the nested ring.

**New exercises** (each: statement cell + starter asset `exN_*.py` + solution asset
`solutions_exN.py` + headless companion code cell with ≥3 asserts, per the U06 format; each asset
closes or carries `# turtle-check: open-path`):

| # | title | kind | spec |
|---|---|---|---|
| 10 | Row of Squares | C | 4 squares of side 40 in a row, pen up to travel 60 between them (nested loops); returns to start (closed) |
| 11 | Dashed Line | C | 12 dashes of 10 with 10-step gaps, pen chosen by `i % 2` (`# turtle-check: open-path`) |
| 12 | Color-Alternating Ring | MP | 8 squares around a point, `pencolor` chosen by `if`/`elif`/`else` on `i % 3` (0 → red, 1 → blue, else green); accumulates `turned = turned + 45` and prints `Turned: 360` |
| 13 | Growing Squares | MP | 5 squares sharing a corner, sides 20, 40, 60, 80, 100 |
| 14 | Seven-Point Star | MP | 7 points, turn `3 * 360 / 7` each time (true division) |
| 16 | Fix the Misspelled Command | MP | the statement shows `turtle.foward(50)` and its `AttributeError`; the student's `ex16` asset is the repaired closed square of side 50 (No real version) |
| 17 | Fix the Missing Import | MP | the statement shows a script without `import turtle` and its `NameError`; the repaired `ex17` asset draws a closed triangle of side 70 (No real version) |
| 15 | Challenge: Grid of Squares | S | 3×3 grid of side-30 squares, travel 45 (nested loops, returns to start) |

## Depth rule (as plan 080, U04–U06 thresholds: introduced ≥5, practiced ≥3)

Counted per exercise over the stand-in code AND its real-program fence (U06: over the solution
asset). Technique concepts: `loop-counter` = a variable increased by 1 inside a loop;
`running-total` = an accumulator adding the loop variable/value; `count-by-condition` = a counter
increased inside an `if` in a loop; `sentinel-loop` = a loop whose stop is a value test
(`while x != …`, or `while True` + `break`); best-so-far counts toward `find-extreme` (practice,
not required). `conditional-nesting` = an `If` inside an `If`. Shortfalls are fixed before the gate.

## Projected depth matrix

| unit | concept | existing | + new | projected | need |
|---|---|---|---|---|---|
| U04 | while-loop, accumulator | 11 / 10 | +16 | 27 / ≥20 | 5 |
| U04 | break-statement | 1 (Ex 11) | +2 (Doubling, First Square) + sentinel fences Ex 3, Ex 9 | 5 | 5 |
| U04 | loop-counter | ≥4 (Ex 1, 4, 7, 11) | +4 (Countdown, Digits, Doubling, Star Bar, Savings) | ≥9 | 5 |
| U04 | sentinel-loop | 2 (Ex 7, 11) | +2 (Doubling, Collatz Peak) + fences Ex 3, 9 | 6 | 5 |
| U04 | running-total | 2 (Ex 3, 6) | +3 (Even Digits, Savings, Powers) | 5 | 5 |
| U04 | count-by-condition | 2 (Ex 4, 9) | +3 (Even Digits, Odd Digits, Lucky Sevens) | 5 | 5 |
| U04 practices | error-messages | 1 (Ex 2) | +2 (Infinite Loop, Missing Start) | 3 | 3 |
| U04 practices | comment | 0 required | +3 (Countdown, Digits, Reverse require a purpose comment) | 3 | 3 |
| U05 | for-loop, range-function | 11 | +15 | 26 | 5 |
| U05 | nested-loops | 3 | +6 (Hollow Box, Checkerboard, Diamond, Floyd, Times Table, Primes) | 9 | 5 |
| U05 practices | conditional-nesting | 1 (Ex 7) | +2 (Hollow Box, Leap Years) | 3 | 3 |
| U05 practices | break-statement | 2 (Ex 5, 11) | +2 (Skip the Sevens `continue`, Primes) | 4 | 3 |
| U05 practices | running-total / count-by-condition | 0 / 2 | +4 / +3 | 4 / 5 | 3 |
| U06 | import-statement, turtle-basics, turtle-drawing | 9 | +8 | 17 | 5 |
| U06 practices | nested-loops | 1 (Ex 6) | +3 (Row, Ring, Grid) | 4 | 3 |
| U06 practices | accumulator | 1 (Ex 7) | +2 (Ring `turned`, Growing Squares side) | 3 | 3 |
| U06 practices | error-messages | 1 (Ex 9 gap) | +2 (Misspelled Command, Missing Import) | 3 | 3 |
| U06 practices | loop-counter | 1 (Ex 7) | +2 (Dashed Line `i`, Ring `i`) | 3 | 3 |

## Phases

- **Phase B (Codex ×3, per unit, parallel):** lesson rungs/moves + no-exec input cells (U04/U05) +
  exercise statements (new exercises + Real/No-real-version lines) + U06 starter assets.
- **Phase C (Codex ×3, SEPARATE fresh sessions):** solutions — stand-ins + asserts, real-program
  fences with Sample input/Expected output (U04/U05); U06 solution assets + headless companions.
- **Phase D (inline):** teacher-notes U04–U06 (pacing incl. 60-minute cuts, core/MP/challenge,
  values, common mistakes: `continue` in `while`, off-by-one in `range` step, trailing spaces in art,
  forgetting to reset the row string); manifests + coverage-map honesty (e.g. U05 practices
  `string-concat` already; add any newly used concept).
- **Phase E — VERIFICATION:** ci-local ALL GREEN (incl. `turtle-check`); AST audit of every code
  cell, fence and U06 asset against the per-unit toolkit; fence parity (run each fence with its
  Sample input); depth table; cell/page deltas; post-execution report.

## Out of scope

U01–U03 (plan 080), U07+ (plans 082–084), checkpoints (084), tooling.

## Plan Review
_(4-way plan-review gate — filled before implementation.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
