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
  Lessons: U04 L1 countdown from an input number; L2 sentinel sum "read numbers until 0" written
  with a plain condition (`number = int(input())` / `while number != 0:` … read again) because
  `break` is taught in L3; L3 read n → Collatz steps. (U04's sentinel form deviates from design D3's
  "read `n` then `n` lines" idiom deliberately: sentinel loops ARE U04's concept.) U05 L1 read n → print 1..n; L2 read n → FizzBuzz 1..n;
  L3 read a height → pyramid. All `no-exec`.
  Exercises: `**Real version:**` line (or `**No real version:**` for repair exercises).
  Solutions: `**The real program**` fence with **bare `input()`** (no prompt text) + `Sample input:`
  + `Expected output:` after every exercise that has a Real version; sentinel real programs read
  until a `0` line (`while True:` + `break`). Lesson `no-exec` cells may show prompts.
- **ASCII art:** no backslashes; each row asserted exactly (trailing spaces never emitted).
- **Values:** tables below are binding; distinctive literals unique across shipped Book 1b
  (grep-verified: 90210, 3721, 12321, 482615, 73185, 58193, 31375, 233168 all unused).

## U04 — Loops & Counting

**Rungs:** (1) after Notice `u04l028`: `total += number` shorthand + Notice (lead-in rule: the
`u04l028` lead-in to `u04l029` moves down); (2) after Notice `u04l038`: digit-count loop
(`n = 4827` → 4) before the digit sum (lead-in rule: the digit-tools lead-in moves above
`u04l039`); (3) after Notice `u04l040`: best-so-far — largest digit of 4827 (one new idea:
`if d > best: best = d`); (4) **after the section intro `u04l044`** (rewritten to introduce `break`
in two steps): `break` inside an ordinary `while n <= 100:` loop, then the existing `while True:`
cell `u04l045`; (5) final build `u04l051` rewritten as a plain `while n != 1:` loop, and its Notice
`u04l052` rewritten to match; (6) three `no-exec` real-input cells (see above).
**Shipped text that must be rewritten** (it contradicts the new facets): `u04l005` ("this course
uses the longer form" → now introduces `+=` as the shorthand taught in Lesson Two), `u04e002`
("not the shortcut form" → either form accepted), U04 teacher-notes ("never `+=`").

**New exercises:**

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | Countdown Liftoff | C | `start = 5` → `5` `4` `3` `2` `1` `Liftoff!` (6 lines) | while, loop-counter |
| 13 | Count the Digits | C | `n = 90210` → `Digits: 5` | loop-counter |
| 14 | Reverse a Number | C | `n = 3721` → `Reversed: 1273` | accumulator |
| 15 | Palindrome Number | MP | `n = 12321` → `12321 is a palindrome` (statement: save the original in `original` before peeling digits) | accumulator, if |
| 16 | Doubling Past a Limit | MP | `value = 5`, `limit = 500` → `640 after 7 doublings` (`while True` + `break`) | break, loop-counter, sentinel-loop |
| 17 | Sum of Even Digits | MP | `n = 482615` → `Even digits: 4` / `Even-digit sum: 20` | running-total, count-by-condition |
| 18 | Count the Odd Digits | MP | `n = 73185` → `Odd digits: 4` | count-by-condition |
| 19 | Largest Digit | MP | `n = 58193` → `Largest digit: 9` | best-so-far |
| 20 | Loop-Built Star Bar | MP | `n = 7` → `Stars: *******` built by `bar = bar + "*"` in a `while` loop | string-concat, loop-counter |
| 21 | First Square Over 300 | MP | → `18 squared is 324` (`break` inside `while n <= 100:`) | break |
| 22 | Fix the Infinite Loop | MP | broken (`no-exec`): `count = 0` / `while count < 5:` / `    print(count)` (never advances); repaired: add `count = count + 1` in the body → prints `0` `1` `2` `3` `4` (No real version) | error-messages |
| 23 | Fix the Missing Starting Value | MP | broken (`no-exec`): `n = 1` / `while n <= 4:` / `    total = total + n` / `    n = n + 1` / `print(total)` → `NameError: name 'total' is not defined`; repaired: `total = 0` before the loop → `10` (No real version) | error-messages |
| 24 | Challenge: Collatz Peak | S | `n = 15` → `Peak: 160` | best-so-far, sentinel-loop |
| 26 | Lucky Sevens | MP | `n = 707172` → `Sevens: 3` | count-by-condition |
| 27 | Savings Streak | MP | deposits start at 10 and grow by 5 each week for 8 weeks → `Week 8 total: 220` | running-total, loop-counter |
| 28 | Triangular Numbers | MP | running totals 1, 1+2, … below 50 → `1 3 6 10 15 21 28 36 45` (genre: sequences) | running-total, sentinel-loop |
| 29 | Decimal to Binary | MP | `n = 37` → `100101` by repeated `// 2`, prepending `str(n % 2)` (genre: number bases) | accumulator, string-concat, type-conversion |
| 30 | Guessing Robot | MP | secret 42 in 1..100, always guess the middle → `Guesses: 50 25 37 43 40 41 42` / `Found 42 in 7 guesses` (genre: games). Real version reads the SECRET and runs the same robot (identical transcript — D3 parity); the human-player version is a lesson `no-exec` cell in L3 instead | sentinel-loop, break, loop-counter |
| 31 | Challenge: Count the Steps | S | GCD of 270 and 192 both ways → `Subtraction steps: 10` / `Remainder steps: 4` / `GCD: 6` (genre: tracing & efficiency) | loop-counter |
| 25 | Challenge: Powers of Two | S | → `2^0 = 1` … `2^7 = 128` (8 lines) then `Total: 255` | while, running-total |

Real programs for existing Ex 3 (read amounts until 0 → total) and Ex 9 (read scores until 0 →
tier counts) are sentinel loops (`break` + `sentinel-loop` depth).

## U05 — For & Range

**Rungs:** (1) after Notice `u05l010`: `range(0, 20, 5)` then `range(10, 0, -1)` (two cells);
(2) after Notice `u05l021`: `continue` rung (`for n in range(1, 11)`, skip multiples of 3);
(3) after the section intro `u05l022` (rewritten: first the early exit, then the flag): "first
divisor, then `break`" (`for d in range(2, 91)`, `91 % d == 0` → 7) before the full prime flag
`u05l023`; (4) **after the Lesson Three heading `u05l025`** (its intro rewritten): one loop builds one
row string of stars (`row = row + "*"`) before the first nested loop `u05l026`; (5) move the section "A growing
triangle" (`u05l031`–`u05l033`) before "A multiplication table" (`u05l028`–`u05l030`); (6) before
the table: a single-loop number row `1 2 3 4 5`; (7) after the triangle: the `"*" * r` one-liner
version + Notice (loop-built vs repetition); (8) Notice: `print(piece, end="")` then `print()`;
(9) new section "ASCII pattern ladder" before the final build: right-aligned triangle
`" " * (h - r) + "*" * r`, then centered pyramid `" " * (h - r) + "*" * (2 * r - 1)`;
(10) three `no-exec` real-input cells (see above).
Existing Ex 1 (a word-for-word copy of `u05l004`) is rewritten as **Triangle Number**:
`n = 250` → `Total: 31375`.
**Shipped text that must be rewritten:** `u05l010` ("Keep that third form as a Notice or Challenge
for now" → the step form is now taught), `u05l024` ("This is the final Lesson Two rung"), U05 Ex 10
statement ("the Challenge-only three-argument form" → an easy Challenge that uses a now-taught form),
U05 teacher-notes line 36 ("`x = x + 1` only" → either form, `+=` taught in U04).

**New exercises:**

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | Countdown by Twos | C | `range(20, 0, -2)` → `20 18 16 14 12 10 8 6 4 2` | range (step) |
| 13 | Hollow Box | C | `width = 6`, `height = 4` → `######` / `#    #` / `#    #` / `######` (nested `if` required: the edge-ROW test outside, the edge-COLUMN test inside its `else`) | nested-loops, conditional-nesting |
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
| 26 | Leap Years in a Range | MP | years 1990..2030; the statement spells out the nested form itself (`% 4` outer → `% 100` inside → `% 400` innermost) — U03 taught only the one-line `and`/`or` form → `Leap years: 10` | conditional-nesting, count-by-condition |
| 27 | Pythagorean Triples | MP | all a < b < c ≤ 20 with a² + b² = c² → 6 lines `3 4 5`, `6 8 10`, `5 12 13`, `9 12 15`, `8 15 17`, `12 16 20` (loop c outer, b, then a; genre: puzzle search) | nested-loops |
| 28 | Chickens and Rabbits | MP | 20 heads, 56 legs → `Chickens: 12, Rabbits: 8` by trying every split (genre: puzzle search) | for-loop, if |
| 29 | Coin Combinations | MP | ways to make 50¢ from 5¢, 10¢, 25¢ coins → `Ways: 10` (three nested loops; genre: puzzle search) | nested-loops, count-by-condition |
| 30 | Challenge: Pascal's Triangle | S | 5 rows via `c = c * (row - k) // (k + 1)` → `1` / `1 1` / `1 2 1` / `1 3 3 1` / `1 4 6 4 1` (genre: sequences) | nested-loops, accumulator |
| 25 | Challenge: Primes up to 50 | S | → `2 3 5 7 11 13 17 19 23 29 31 37 41 43 47` and `Count: 15` | nested-loops, break |

## U06 — Turtle Geometry (input-exempt)

**Rungs:** (1) move the section "Travel without drawing" (`u06l008`–`u06l010`, including its run Notice)
after "Replace repetition with a loop" (`u06l011`–`u06l012`), so the loop is taught before a travel cell uses it;
(2) before the ring (`u06l027`): a new asset `l3_two_squares.py` — a side-60 square, `left(90)`,
a second side-60 square, then `right(90)` to restore the heading (closed: position and heading
return) — then the nested ring; (3) cell `u06l013` says "loop variable", not "loop counter", for
`side_number` (a for-variable is not a counter).

**New exercises** (each: statement cell + starter asset `exN_*.py` + solution asset
`solutions_exN.py` + headless companion code cell with ≥3 asserts, per the U06 format; each asset
closes or carries `# turtle-check: open-path`):

| # | title | kind | spec |
|---|---|---|---|
| 10 | Row of Squares | C | 4 squares of side 40; after EACH square (4 times) pen up, `forward(60)`, pen down (nested loops); finally pen up + `backward(240)` back to the start (closed) |
| 11 | Dashed Line | C | 24 alternating 10-step segments (`for i in range(24)`), pen down when `i % 2 == 0`; `dashes = dashes + 1` only on the 12 pen-down segments → prints `Dashes: 12` (`# turtle-check: open-path`) |
| 12 | Color-Alternating Ring | MP | 8 squares around a point, `pencolor` chosen by `if`/`elif`/`else` on `i % 3` (0 → red, 1 → blue, else green); accumulates `turned = turned + 45` and a counter `count = count + 1`, printing `Turned: 360` and `Squares: 8` |
| 13 | Growing Squares | MP | 5 squares sharing a corner, sides 20, 40, 60, 80, 100 grown with `side = side + 20` (required) |
| 14 | Seven-Point Star | MP | 7 points, turn `3 * 360 / 7` each time (true division, never rounded — 154 leaves a 2° gap) |
| 18 | Fix the Indentation | MP | the statement shows a loop whose body line is not indented and its `IndentationError`; the repaired `ex18` asset draws a closed pentagon of side 60 (`360 / 5` turns) (No real version) |
| 16 | Fix the Misspelled Command | MP | the statement shows `turtle.foward(50)` and its `AttributeError`; the student's `ex16` asset is the repaired closed square of side 50 (No real version) |
| 17 | Fix the Missing Import | MP | the statement shows a script without `import turtle` and its `NameError`; the repaired `ex17` asset draws a closed triangle of side 70 (No real version) |
| 15 | Challenge: Grid of Squares | S | 3×3 grid of side-30 squares, travel 45 (nested loops); the statement states the pen-up return path back to the start (closed) |

## Depth rule (as plan 080, U04–U06 thresholds: introduced ≥5, practiced ≥3)

Counted per exercise over the stand-in code AND its real-program fence (U06: over the solution
asset). Technique concepts: `loop-counter` = a variable increased by 1 inside a loop;
`running-total` = an accumulator adding the loop variable/value; `count-by-condition` = a counter
increased inside an `if` in a loop; `sentinel-loop` = a loop whose stop is a value test
(`while x != …`, or `while True` + `break`); best-so-far counts toward `find-extreme` (practice,
not required). `conditional-nesting` = an `If` inside an `If`. Shortfalls are fixed before the gate.

## Genre coverage (design 006 D9)

U04: arithmetic & number tricks, counting & accumulation, number theory, ASCII art, sequences &
number bases, small games, tracing & efficiency, debug/repair. U05: counting, number theory,
ASCII art, brute-force puzzle search, sequences, decisions. U06: turtle geometry, patterns,
accumulation, debug/repair. All ≥ 4.

## Projected depth matrix

| unit | concept | existing | + new | projected | need |
|---|---|---|---|---|---|
| U04 | while-loop, accumulator | 11 / 10 | +16 | 27 / ≥20 | 5 |
| U04 | break-statement | 1 (Ex 11) | +2 (Doubling, First Square) + sentinel fences Ex 3, Ex 9 | 5 | 5 |
| U04 | loop-counter | ≥4 (Ex 1, 4, 7, 11) | +5 (Digits, Doubling, Star Bar, Savings, Guessing Robot; Countdown's value decreases, so no credit) | ≥9 | 5 |
| U04 | sentinel-loop | 2 (Ex 7, 11) | +2 (Doubling, Collatz Peak) + fences Ex 3, 9 | 6 | 5 |
| U04 | running-total | 2 (Ex 3, 6) | +3 (Even Digits, Savings, Powers) | 5 | 5 |
| U04 | count-by-condition | 2 (Ex 4, 9) | +3 (Even Digits, Odd Digits, Lucky Sevens) | 5 | 5 |
| U04 practices | error-messages | 1 (Ex 2) | +2 (Infinite Loop, Missing Start) | 3 | 3 |
| U04 practices | comment | 0 required | +3 (Countdown, Digits, Reverse require a purpose comment) | 3 | 3 |
| U05 | for-loop, range-function | 11 | +15 | 26 | 5 |
| U05 | nested-loops | 3 | +9 (Hollow Box, Checkerboard, Diamond, Floyd, Times Table, Primes, Pythagorean Triples, Coin Combinations, Pascal) | 12 | 5 |
| U05 practices | conditional-nesting | 1 (Ex 7) | +2 (Hollow Box, Leap Years) | 3 | 3 |
| U05 practices | break-statement | 2 (Ex 5, 11) | +2 (Skip the Sevens `continue`, Primes) | 4 | 3 |
| U05 practices | running-total / count-by-condition | 2 (Ex 1, 10) / 2 (Ex 3, 7) | +3 (Skip the Sevens, Multiples of 3 or 5, Perfect Number) / +3 (Divisor Count, Leap Years, Coin Combinations) | 5 / 5 | 3 |
| U06 | import-statement, turtle-basics, turtle-drawing | 9 | +8 | 17 | 5 |
| U06 practices | nested-loops | 1 (Ex 6) | +3 (Row, Ring, Grid) | 4 | 3 |
| U06 practices | accumulator | 1 (Ex 7) | +2 (Ring `turned`, Growing Squares side) | 3 | 3 |
| U06 practices | error-messages | 0 (Ex 9 is a predict/explain task, not a repair) | +3 (Misspelled Command, Missing Import, Indentation) | 3 | 3 |
| U06 practices | loop-counter | 0 (for-variables are not counters) | +3 (Ring `count`, Dashed Line `dashes = dashes + 1`, Grid `squares = squares + 1`) | 3 | 3 |

## Phases

- **Phase B (Codex ×3, per unit, parallel):** lesson rungs/moves + no-exec input cells (U04/U05) +
  exercise statements (new exercises + Real/No-real-version lines) + U06 starter assets.
- **Phase C (Codex ×3, SEPARATE fresh sessions):** solutions — stand-ins + asserts, real-program
  fences with Sample input/Expected output (U04/U05); U06 solution assets + headless companions.
- **Phase D (inline):** teacher-notes U04–U06 (pacing incl. 60-minute cuts, core/MP/challenge,
  values, common mistakes: `continue` in `while`, off-by-one in `range` step, trailing spaces in art,
  forgetting to reset the row string); manifests + coverage-map honesty (e.g. U05 practices
  `string-concat` already; add any newly used concept).
- **Phase E — VERIFICATION** (specialized audits FIRST; `scripts/ci-local.sh` LAST, and re-run after
  any audit-driven correction):
  1. AST audit of every code cell, fence and U06 asset against the per-unit toolkit.
  2. Fence parity: run each fence with its Sample input; stdout must equal Expected output and the
     stand-in's asserted lines.
  3. **U06 command-trace check:** replay every new/changed asset through `tools/fake_turtle` with a
     trace recorder and compare the recorded moves, turns, pen transitions, colors and stdout with
     the exercise contract (e.g. 4 squares + 4 travels + `backward(240)`; exactly 12 pen-down dashes;
     the ring's color cycle; `Turned: 360` / `Squares: 8`); `turtle-check` alone cannot see these.
  4. **Fixture/value-use audit:** every value in the tables is used by its exercise, and no counter
     or variable exists only to inflate depth credit.
  5. Depth + genre tables; cell/page deltas.
  6. `scripts/ci-local.sh` ALL GREEN (final); post-execution report.

## Out of scope

U01–U03 (plan 080), U07+ (plans 082–084), checkpoints (084), tooling.

## Plan Review

### Round 1 — [fable] APPROVE WITH NITS (folded; [sol]/[glm] pending)

- `[FIXED]` shipped text that contradicts `+=`/`range` step named for rewrite (`u04l005`, `u04e002`,
  U04 teacher-notes, `u05l010`, `u05l024`, U05 Ex 10, `u04l052`); rung 4 moved after `u04l044`.
- `[FIXED]` lead-in anchors enumerated (`u04l028`, `u04l038`); U05 rung anchors `u05l022`, `u05l025`.
- `[FIXED]` U04 L2 real-input cell uses a plain condition (no `break` before L3); D3 idiom deviation
  stated.
- `[FIXED]` U06 move includes `u06l010`; U06 loop-counter credit via explicit counters; depth-row
  arithmetic corrected; Leap Years spells out its own nesting.
- `[FIXED]` nits: Hollow Box nesting shape, Growing Squares `side = side + 20`, return paths, save the
  original in Palindrome, Doubling start varied (5 → 640 in 7), unrounded star angle.
- `[sol]` round 1 **REJECT** (fold below).
- **User direction (2026-09-24):** genre coverage (design 006 D9) folded — U04 Triangular Numbers,
  Decimal to Binary, Guessing Robot, Count the Steps; U05 Pythagorean Triples, Chickens and Rabbits,
  Coin Combinations, Pascal's Triangle.

### Round 1 — [sol] fold

- `[FIXED]` Guessing Robot real version reads the secret and runs the same robot (D3 parity); the
  human-player game moves to a U04 L3 `no-exec` lesson cell.
- `[FIXED]` U04 repair exercises pin the broken program and the repaired output.
- `[FIXED]` U06: third real repair (Fix the Indentation) → `error-messages` 3; `l3_two_squares.py`
  restores its heading; Row of Squares travels after each square then `backward(240)`; Dashed Line
  runs 24 segments counting 12 dashes; `u06l013` says "loop variable".
- `[FIXED]` stray `768` removed; U05 teacher-notes line 36 added to the rewrites; depth rows
  recomputed exercise-by-exercise (U04 loop-counter +5; U05 nested +9, running-total and
  count-by-condition 5/5).
- `[FIXED]` Phase E: audits first, ci-local last (re-run after corrections); U06 instrumented
  command-trace check; fixture/value-use audit.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
