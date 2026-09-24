# Plan 082 — Book 1b enrichment: Units 07–09 (Functions, Randomness, Strings)

**Goal:** Apply design 006 (D3–D9) to U07–U09: gentler function/string ladders, ASCII shape
functions, dice games and simulations, ciphers/text layout/validation, the widened string methods
(plan 079), and the real-input pattern in function form.

**Spec:** `docs/designs/006-book1b-enrichment.md` (D3/D7 as amended by plans 079/080, D9 genres);
U07–U09 audit (2026-09-24). Conventions identical to plans 080/081: lead-in rule, binding numbering
(new core/MP before existing Challenges; Challenges last; `More Practice: ` prefix), values tables,
depth rule (introduced ≥5, practiced ≥3), fence parity, bare-`input()` fences.

## Global constraints

- **Function form from U07:** solutions define the function(s) and assert several distinct cases;
  the real program (fence) reads stdin with bare `input()`, calls the function, prints the result.
  Seeded work uses `import random` + literal `random.seed(4)` before first use (notebooks.py policy);
  only `seed`/`randint`/`choice`.
- **Per-unit toolkit (every cell, tier and fence):**
  - U07 adds: `def`, parameters, **default parameters**, `return` (incl. early return), local scope,
    **calling your own functions from other functions (composition)**, `len`/`min`/`max`/`abs`/
    `round`/`sum` on numbers (`sum`/`min`/`max` of lists stay for U10).
  - U08 adds: `import random`, `random.seed(4)`, `randint`, `choice` (incl. `choice` on a string).
  - U09 adds: indexing incl. negative indexes, slices incl. open ends and the reversing slice
    `[::-1]` (this plan lifts the build-time step-slice ban from U09 on — design 006 §1 lists it as a
    missing facet), `len`, `for ch in text`, `in` on strings, string methods
    `upper/lower/strip/replace` + the widened `split` (word iteration only: `for word in
    line.split():`, `len(line.split())` — no indexing into the pieces, D3), `join` on a string
    (`"-".join("abc")`), `find`, `startswith`/`endswith`, `isdigit`/`isalpha`.
  - Never in U07–U09: list literals, `append`, dicts, files, classes, tuple assignment, comprehensions,
    `ord`/`chr`, `count`.
- **ASCII art** (functions RETURN the picture as one string with `"\n"` between rows; asserted
  exactly; no backslashes; no trailing spaces — the Center Text answer is the one deliberate exception).
- **Conventions inherited from plans 080/081:** lead-in rule (a Notice's trailing lead-in moves above the
  code it introduces); one new idea per code cell; binding final numbering (below; Challenges last,
  `More Practice: ` prefix); every exercise ends with exactly one `**Real version:**` or
  `**No real version:**` line (repair/predict and fixed-art exercises take the latter); real programs
  use bare `input()` with `Sample input` / `Expected output` equal to the stand-in; repair exercises pin
  the broken code, its exact error type, and the repaired output.

## U07 — Functions

**Rungs:** (1) before `u07l003`: a no-parameter function that prints (`def greet():`), then a
one-parameter printing function (`def greet(name):`) — then the existing `celsius_to_f` with
`return`; (2) before `u07l015` (after the `u07l014` intro): an early-`return` rung
(`first_multiple(start, k)`) — `return` leaves the function at once; (3) after the `sum_to_n`
section: **composition** — `count_primes_below(n)` calls `is_prime`; (4) after the built-ins
section: a **default parameter** rung (`def bar(n, symbol="#"):`); (5) `no-exec` real-input cells per
lesson (L1 read a temperature → `celsius_to_f`; L2 read n → `is_prime`; L3 read a Celsius value →
`safe_temperature`).

**New exercises** (C/MP/S):

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Triangle Picture | C | `draw_triangle(3)` → `"*\n**\n***"` | ASCII art |
| Name Banner | C | `banner("Hi")` → `"******\n* Hi *\n******"` (width = `len(text) + 4`) | ASCII art, layout |
| Least Common Multiple | C | `lcm(4, 6)` → 12, `lcm(21, 6)` → 42 — calls `gcd` (composition) | number theory |
| Digital Root | MP | `digital_root(9875)` → 2 (9875 → 29 → 11 → 2), calling `digit_sum` | number theory |
| Primes Below | MP | `count_primes_below(100)` → 25, calling `is_prime` | number theory |
| Roman Numeral | MP | `to_roman(38)` → `"XXXVIII"`, `to_roman(14)` → `"XIV"` (1–39, `while` subtracting 10, 9, 5, 4, 1) | sequences & bases |
| Days in a Month | MP | `days_in_month(2, 2024)` → 29, `(4, 2023)` → 30, `(1, 2023)` → 31 — calls `is_leap` | calendar & time |
| Weekday Name | MP | `weekday_name(0)` → `"Sunday"` … `(6)` → `"Saturday"`; `day_of_week(day, first_weekday)` = `(first_weekday + day - 1) % 7` → `day_of_week(15, 3)` → 3 | calendar & time |
| Bar with a Default | MP | `bar(5)` → `"#####"`, `bar(3, "=")` → `"==="` | ASCII art |
| Fix the Scope Bug | MP | broken (`no-exec`): `def set_total():` / `    total = 12` / `def show():` / `    print(total)` / `set_total()` / `show()` → `NameError: name 'total' is not defined`; repaired: `set_total` returns 12 and `show(total)` takes a parameter → prints `12` (No real version) | debug & repair |
| Challenge: Month Calendar | S | `month_calendar(30, 3)` → header `"Su Mo Tu We Th Fr Sa"` + week rows of `f"{d:2}"` cells joined by single spaces, the first row starting after 3 blank cells (`"  "` each); no trailing spaces | calendar, layout |
| Challenge: Longest Collatz | S | `longest_collatz_below(20)` → 18 (the smallest start below 20 with the most steps, 20), calling a `collatz_steps(n)` helper | number theory |

## U08 — Randomness (all seeded values computed with the exact call order stated)

**Rungs:** (1) before `u08l004`: `import random` → `random.seed(4)` → `print(random.randint(1, 6))`
(one idea each) before the first function; (2) before `u08l020` (π): test ONE fixed point
`(0.3, 0.4)` inside the quarter circle before the loop; (3) `random.choice("HT")` on a string;
(4) `no-exec` real-input cells: read the number of rolls/trials.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Die Face Art | C | `die_face(5)` → `"o o\n o\no o"` (faces 1–6 specified row by row; no randomness) | ASCII art |
| Roll Until Six | C | seed 4, count `randint(1, 6)` rolls through the first 6 → 4 | simulation |
| Longest Heads Streak | C | seed 4, 20 flips of `choice("HT")` (`HTHTTHHHHTTHHTTHHTHH`) → 4 | simulation, counting |
| Two-Dice Histogram | MP | for each total 2..12: reseed 4, roll two dice 36 times, count that total; rows `f"{total:2}:" + "#" * count` → ` 2:##` … `12:` (no trailing space) | simulation, statistics |
| Pig Turn | MP | seed 4, roll until the turn total reaches 20 or a 1 appears (a 1 scores 0): rolls 2, 3, 1 → 0 | games |
| Nim Winner | MP | take 1–3 stones; `first_player_wins(stones)` → `stones % 4 != 0`: 12 → False, 13 → True | games |
| Three Heads in a Row | MP | seed 4, flip `choice("HT")` until three `H` in a row (`HTHTTHHH`) → `Flips: 8` | simulation, counting |
| Average Roll | MP | seed 4, ten `randint(1, 6)` rolls → `Average: 2.5` | simulation, statistics |
| Random Polygon | MP | turtle asset: `random.seed(4)`, `sides = random.randint(3, 8)` (→ 4), draw a closed regular polygon of side 70 with `360 / sides` turns | turtle, simulation |
| Random Color Row | MP | turtle asset: `random.seed(4)`, four side-30 squares in a row, each color from `random.choice("rgb")` (→ r, g, r, b) mapped by `if`/`elif`/`else` to red/green/blue; returns to the start (closed) | turtle, decisions |
| Challenge: Random Password | S | seed 4, 6 `choice` picks from `"abcdefghijkmnpqrstuvwxyz23456789"` → `rvg38j` | games, text |

## U09 — Strings

**Rungs:** (1) negative index `word[-1]`; (2) open-ended slices `word[:3]`, `word[3:]`; (3) the
reversing slice `word[::-1]`; (4) before `u09l017` (palindrome): an index loop
`for i in range(len(w)): print(i, w[i])`, then comparing ONE mirror pair, then the existing half-walk;
(5) replace the 4-method chain at `u09l012` with one method per rung (strip → lower → replace), the
chain last; (6) widened methods, one rung each: `find`, `startswith`/`endswith`, `isdigit`/
`isalpha`, `"-".join("abc")`, `line.split()` word iteration; (7) `no-exec` real-input cells: read a
word → palindrome; read a line → word count; read a PIN → validity.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Word Count | C | `word_count("rockets need fuel to fly")` → 5 (`split`) | text processing |
| Initials | C | `initials("grace brewster hopper")` → `"GBH"` | text processing |
| Valid PIN | C | `is_valid_pin("4071")` → True, `"40a1"` → False, `"407"` → False (`isdigit` + `len`) | validation |
| Longest Word | MP | `longest_word("orbit rover launch pad")` → `"launch"` (first longest) | text, find-extreme |
| Sentence Palindrome | MP | `is_sentence_palindrome("Never odd or even")` → True (`replace`, `lower`, `[::-1]`) | text |
| Run-Length Encoding | MP | `rle("aaabcc")` → `"a3b1c2"` | encoding |
| Atbash Cipher | MP | `atbash("abc")` → `"zyx"` via `alphabet.find(ch)` and `alphabet[25 - i]`; non-letters unchanged | encoding |
| File Type | MP | `file_type("game.py")` → `"python"`, `"notes.txt"` → `"text"`, else `"other"` | text |
| Word Triangle | MP | `word_triangle("CODE")` → `"C\nCO\nCOD\nCODE"` | ASCII art |
| Center Text | MP | `center_text("cat", 9)` → `"   cat   "` (pads computed; a right pad this time IS part of the answer) | text layout |
| Letter Spacer | MP | `spaced("ROBOT")` → `"R-O-B-O-T"` (`join`) | text layout |
| Challenge: Word Wrap | S | `wrap("the quick brown fox jumps", 10)` → `"the quick\nbrown fox\njumps"` (greedy, `split`) | text layout |
| Challenge: Safe Number | S | `to_number("42")` → 42, `"4x"` → -1 (`isdigit` validation, no negatives) | validation & parsing |

## Binding final exercise order

- **U07 (21):** 1–7 existing core · 8 Triangle Picture · 9 Name Banner · 10 Least Common Multiple ·
  11–17 MP: Digital Root, Primes Below, Roman Numeral, Days in a Month, Weekday Name, Bar with a Default,
  Fix the Scope Bug · 18–21 Challenges: Euclid's GCD Tool (was 8), Prime Gate (was 9), Month Calendar,
  Longest Collatz.
- **U08 (20):** 1–7 existing core · 8 Die Face Art · 9 Roll Until Six · 10 Longest Heads Streak ·
  11–17 MP: Two-Dice Histogram, Pig Turn, Nim Winner, Three Heads in a Row, Average Roll, Random Polygon,
  Random Color Row · 18–20 Challenges: Highest Twenty-Sided Roll (was 8), Multiples in a Random Range
  (was 9), Random Password.
- **U09 (22):** 1–7 existing core · 8 Word Count · 9 Initials · 10 Valid PIN · 11–18 MP: Longest Word,
  Sentence Palindrome, Run-Length Encoding, Atbash Cipher, File Type, Word Triangle, Center Text,
  Letter Spacer · 19–22 Challenges: Alternating Case (was 8), Caesar Shift (was 9), Word Wrap, Safe Number.

Real versions: every exercise except repairs (U07 Fix the Scope Bug; U07 Ex 2 repair) and the U08 turtle
assets (turtle is input-exempt) has one; seeded U08 real programs read the number of rolls/flips.

## Depth & genres

Each unit: introduced ≥5, practiced ≥3 (Phase E table); D9 genres — U07: ASCII art, number theory,
sequences, calendar, debug (5); U08: simulation, games, statistics, ASCII art (4); U09: text, encoding,
layout, validation, ASCII art (5).

Projected depth highlights (Phase E prints the full table; thresholds introduced ≥5 / practiced ≥3):
U07 `def-function`/`parameters`/`return-value` ≥17 each, `scope` ≥4 (Fix the Scope Bug + every
function's locals are taught but only counted where the exercise names it: Scope lesson exercises, Bar
with a Default, Fix the Scope Bug, Digital Root's helper), `builtin-functions` ≥4 (Name Banner `len`,
Primes Below, Longest Collatz, Month Calendar); U08 `random-module` ≥15, `float-type` 3 (Ex 5, Ex 6,
Average Roll), turtle-basics/turtle-drawing 3 (Ex 7, Random Polygon, Random Color Row), `comment` ≥3
(required in Die Face Art, Roll Until Six, Longest Heads Streak); U09 `string-index` ≥6,
`string-slice` ≥5, `string-methods` ≥10, `in-operator` ≥3, `transform-each` ≥5, `linear-search` ≥4.

## Metadata deltas (manifest + coverage-map, identically)

To be confirmed by Phase E's honesty scan; expected: U07 `practices` += `string-concat`, `nested-loops`
(Triangle Picture, Month Calendar); U08 `practices` += `input`, `type-conversion`, `elif-else`,
`string-concat` (histogram bars); U09 `practices` += `input`, `find-extreme` (Longest Word — only if ≥3
reps, else leave to fastforward), `for-loop`, `range-function`.

## Phases

- **Phase B (Codex gpt-6-sol ×3, direct `codex exec` in the main checkout):** statements.
- **Phase C (Codex ×3, separate sessions):** solutions, seeded values computed by running the code
  (and matching the values above), real-program fences with Sample input / Expected output.
- **Phase D (inline):** teacher-notes (incl. D9 genre notes), metadata deltas.
- **Phase E (audits first, ci-local last):** toolkit AST audit of every cell, fence and U07/U08 turtle
  asset; exercise-contract + fence-parity audit (the Phase E script from plan 080); U08 turtle
  command-trace check; fixture/value-use audit; manifest ↔ coverage-map diff and honesty scan; depth +
  genre tables; `scripts/ci-local.sh`; post-execution report.

## Out of scope

U10+ (plans 083–084); checkpoints (084); tooling.

## Plan Review
_(4-way plan-review gate — filled before implementation.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
