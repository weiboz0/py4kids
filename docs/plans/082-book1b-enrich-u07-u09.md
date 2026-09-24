# Plan 082 — Book 1b enrichment: Units 07–09 (Functions, Randomness, Strings)

**Goal:** Apply design 006 (D3–D9) to U07–U09: gentler function/string ladders, ASCII shape
functions, dice games and simulations, ciphers/text layout/validation, the widened string methods
(plan 079), and the real-input pattern in function form.

**Spec:** `docs/designs/006-book1b-enrichment.md` (D3/D7 as amended by plans 079/080, D9 genres);
U07–U09 audit (2026-09-24). Conventions are those of plans 080/081 (lead-in rule, binding numbering,
values tables, depth rule, fence parity, bare-`input()` fences, pinned repairs, metadata deltas).

## Global constraints

- **Function form from U07:** solutions define the function(s) and assert several distinct cases; the
  real program (fence) reads stdin with bare `input()`, calls the function, prints the result.
  Seeded work uses `import random` + literal `random.seed(4)` before first use (notebooks.py policy);
  only `seed`/`randint`/`choice`.
- **Per-unit toolkit (every cell, tier and fence):**
  - U07 adds: `def`, parameters, **default parameters**, `return` (incl. early return), local scope,
    **composition** (your functions calling your functions), `abs`/`round`/`min`/`max` on numbers,
    and `len` on a **string** (taught by a new U07 rung; `sum` and `len` of lists wait for U10).
  - U08 adds: `import random`, `random.seed(4)`, `randint`, `choice` — on a `range(...)` or on a
    **string** (e.g. `choice("HT")`, taught by a new rung).
  - U09 adds: indexing (positive, then negative), slices incl. open ends and the reversing slice
    `[::-1]`, `for ch in text`, `in` on strings, `upper`/`lower`/`strip`/`replace` + the widened
    `split`, `join` on a string (`"-".join("abc")`), `find`, `startswith`/`endswith`, `isdigit`/`isalpha`.
    **`split` rule (D3):** only word iteration — `for word in line.split():` and `len(line.split())`.
    The ban is on subscripting the list that `split()` returns (`parts[0]`); indexing a *string* that
    the loop hands you (`word[0]`) is ordinary string indexing and is allowed.
    **`[::-1]`:** plan 075's authoring rule ("do not teach `s[::-1]`") is lifted from U09 on — design
    006 §1 lists the reversing slice as a missing facet (no scanner rule is involved; any slice scans
    as `string-slice`).
  - Never in U07–U09: list literals, `append`, dicts, files, classes, tuple assignment, comprehensions,
    `ord`/`chr`, `count`.
- **ASCII art:** functions RETURN the picture as one string with `"\n"` between rows; asserted exactly;
  no backslashes; no trailing spaces (Center Text's right padding is the one deliberate exception).
- **Lead-in rule:** when a new rung lands where a markdown cell ends with the lead-in to the next code
  cell, that lead-in moves to its own cell directly above the code it introduces (after the new
  rungs), and each new rung gets its own lead-in. Named per unit below.
- **Contract lines:** every exercise ends with exactly one `**Real version:**` or `**No real
  version:**` line. No-real cases: repair/predict exercises ("fixes (or traces) code rather than
  reading input"), fixed art, and **every turtle exercise** ("turtle drawings run as scripts, not stdin
  programs" — design 006 D3 exempts turtle work). Real programs use bare `input()`; `Sample input` /
  `Expected output` equal the stand-in's values and printed lines.
- **Repairs** pin the broken code, its exact error type and the repaired output.

## U07 — Functions

**Rungs (lesson):**
1. Lesson 1: split the `celsius_to_f` lead-in out of `u07l002` (keep the heading); insert a new
   section "Functions that only print": `def greet():` + call (one idea), then `def greet(name):`
   (a parameter); then the moved lead-in and the existing `u07l003` (`return`).
2. After the Lesson 2 heading `u07l013`, before the `u07l014` prime section: a new section "Leave
   early with `return`" — `first_multiple(start, k)` (one idea: `return` leaves at once).
3. After the `sum_to_n` section (`u07l023`–`u07l025`): **composition** — `count_primes_below(n)` calls
   `is_prime`.
4. Built-ins section (`u07l026`–`u07l028`): a rung `print(len("banner"))` → 6 (`len` counts the
   characters of a string); rewrite the `u07l026` sentence "`len(...)` … we meet it in Unit 09" to "`len`
   counts characters in a string today and items in a list in Unit 10"; then a **default parameter**
   rung (`def bar(n, symbol="#"):`).
5. `no-exec` real-input cells: L1 read a temperature → `celsius_to_f`; L2 read n → `is_prime`;
   L3 read a Celsius value → `safe_temperature`.

**Shipped text to rewrite:** `u07l026` (above); `u07e001` intro ("Core work is Exercises 1–7.
Exercises 8–9 are optional Challenges" → the new partition); U07 teacher-notes "Challenges (8–9)" lines.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Triangle Picture | C | `draw_triangle(3)` → `"*\n**\n***"` | ASCII art |
| Name Banner | C | `banner("Hi")` → `"******\n* Hi *\n******"` (width = `len(text) + 4`) | ASCII art, layout |
| Least Common Multiple | C | `lcm(4, 6)` → 12, `lcm(21, 6)` → 42 — calls `gcd` | number theory |
| Digital Root | MP | `digital_root(9875)` → 2 (9875 → 29 → 11 → 2), calling `digit_sum` | number theory |
| Primes Below | MP | `count_primes_below(100)` → 25, calling `is_prime` | number theory |
| Roman Numeral | MP | `to_roman(38)` → `"XXXVIII"`, `to_roman(14)` → `"XIV"` (1–39; `while` subtracting 10, 9, 5, 4, 1) | sequences & bases |
| Days in a Month | MP | `days_in_month(2, 2000)` → 29, `(2, 2100)` → 28, `(4, 2023)` → 30, `(1, 2023)` → 31 — calls `is_leap` | calendar & time |
| Weekday Name | MP | `weekday_name(0)` → `"Sunday"` … `(6)` → `"Saturday"` (0 = Sunday); `day_of_week(day, first_weekday)` = `(first_weekday + day - 1) % 7` → `day_of_week(15, 3)` → 3 | calendar & time |
| Bar with a Default | MP | `bar(5)` → `"#####"`, `bar(3, "=")` → `"==="` | ASCII art |
| Fix the Scope Bug | MP | broken (`no-exec`): `def set_total():` / `    total = 12` / `def show():` / `    print(total)` / `set_total()` / `show()` → `NameError: name 'total' is not defined`; repaired: `set_total` returns 12, `show(total)` takes it → prints `12` (No real version) | debug & repair |
| Fix the Missing Argument | MP | broken (`no-exec`): `def area(width, height):` / `    return width * height` / `print(area(5))` → `TypeError: area() missing 1 required positional argument: 'height'`; repaired `print(area(5, 3))` → `15` (No real version) | debug & repair |
| Fix the Call Before Define | MP | broken (`no-exec`): `print(triple(4))` / `def triple(n):` / `    return 3 * n` → `NameError: name 'triple' is not defined`; repaired (define first) → `12` (No real version) | debug & repair |
| Predict the Scope | MP | predict: `x = 5` / `def change():` / `    x = 99` / `change()` / `print(x)` → `5` (No real version) | tracing |
| Two Totals | MP | global `total = 100`; `add_up(3)` keeps its own local `total` → returns 6; `print(add_up(3), total)` → `6 100` | scope |
| Display Temperature | MP | `display_temperature(21)` → `round(celsius_to_f(21))` → 70 (69.8 rounded) | composition, built-ins |
| Distance Apart | MP | `distance_apart(3, 11)` → 8, `(15, 4)` → 11 (`abs`) | built-ins |
| Clamp a Score | MP | `clamp(120)` → 100, `clamp(-5)` → 0, `clamp(64)` → 64 (`min(max(score, 0), 100)`) | built-ins |
| Star Function | MP | turtle asset: `draw_star(size)` draws a closed 5-point star (5 × `forward(size)`, `right(144)`); the script calls `draw_star(80)` (No real version: turtle) | turtle |
| Polygon Row | MP | turtle asset: `draw_polygon(sides, length)` + `polygon_row()` calling it 3 times for hexagons of side 30, pen-up `forward(70)` after each, then pen-up `backward(210)` back to the start (closed) (No real version: turtle) | turtle, composition |
| Challenge: Month Calendar | S | `month_calendar(30, 3)` RETURNS (0 = Sunday) `"Su Mo Tu We Th Fr Sa\n          1  2  3  4\n 5  6  7  8  9 10 11\n12 13 14 15 16 17 18\n19 20 21 22 23 24 25\n26 27 28 29 30"` — built with one growing `row` string (no lists): each cell is `f"{d:2}"` (blank cells `"  "`), cells separated by one space (`row = cell` if `row == ""` else `row + " " + cell`), a row closes when `(first_weekday + d - 1) % 7 == 6`; the last row is not padded | calendar, layout |
| Challenge: Longest Collatz | S | `longest_collatz_below(20)` → 18 (the smallest start below 20 with the most steps, 20; strict `>` keeps the first) via a `collatz_steps(n)` helper | number theory |

## U08 — Randomness (seeded values computed with `random.seed(4)` in the stated call order)

**Rungs (lesson):** (1) before `u08l004`: split the "Predict the total before running this cell" lead-in
out of `u08l003`; new rungs `import random` → `random.seed(4)` → `print(random.randint(1, 6))` (one idea
each); the moved lead-in; then `u08l004`. (2) a `random.choice("HT")` rung (choice on a string) in the
"Choose from a range" section. (3) before `u08l020` (π): split the `u08l019` lead-in; a rung that tests
ONE fixed point `(0.3, 0.4)` inside the quarter circle; the moved lead-in; `u08l020`. (4) `no-exec`
real-input cells: read the number of rolls/flips.

**Shipped text to rewrite:** `u08l006` ("`random.choice` always receives a `range(...)`"), `u08l008`
("only `randint` and `choice(range(...))`"), U08 teacher-notes lines 6/18/48 (same claims), `u08e001`
intro ("For Exercises 1–6 and 8–9" → the new partition).

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Die Face Art | C | `die_face(n)` returns 3 rows of 3 characters with `.` filler: 1 `...`/`.o.`/`...`; 2 `o..`/`...`/`..o`; 3 `o..`/`.o.`/`..o`; 4 `o.o`/`...`/`o.o`; 5 `o.o`/`.o.`/`o.o`; 6 `o.o`/`o.o`/`o.o` — `die_face(5)` → `"o.o\n.o.\no.o"` (real version reads the face) | ASCII art |
| Roll Until Six | C | seed 4, `randint(1, 6)` until the target face → `Rolls: 4` (real version reads the target face 6) | simulation |
| Longest Heads Streak | C | seed 4, 20 flips of `choice("HT")` (`HTHTTHHHHTTHHTTHHTHH`) → `Longest streak: 4` (real version reads the flip count 20) | simulation, counting |
| Two-Dice Histogram | MP | for each total 2..12: reseed 4, roll 36 pairs, count that total; rows `f"{total:2}:" + "#" * count` → ` 2:##` / ` 3:##` / ` 4:######` / ` 5:#####` / ` 6:####` / ` 7:###` / ` 8:#####` / ` 9:#######` / `10:#` / `11:#` / `12:` (real version reads the pair count 36) | simulation, statistics |
| Pig Turn | MP | seed 4, roll until the turn total reaches the goal or a 1 appears (a 1 scores 0): rolls 2, 3, 1 → `Turn score: 0` (real version reads the goal 20) | games |
| Nim Winner | MP | take 1–3 stones; `first_player_wins(stones)` → `stones % 4 != 0`: 12 → `First player wins: False`, 13 → `First player wins: True` (real version reads the stone count) | games |
| Three Heads in a Row | MP | seed 4, flip `choice("HT")` until the streak length is reached (`HTHTTHHH`) → `Flips: 8` (real version reads the streak length 3) | simulation |
| Average Roll | MP | seed 4, ten `randint(1, 6)` rolls (2, 3, 1, 6, 4, 4, 2, 1, 1, 1) → `Average: 2.5` (real version reads the roll count 10) | simulation, statistics |
| Random Polygon | MP | U06 turtle format (starter asset, `solutions_exN.py`, headless companion with ≥3 asserts: `sides == 4`, `angle == 90.0`, 4 pen-down moves): `random.seed(4)`, `sides = random.randint(3, 8)` → 4, closed polygon of side 70 turning `360 / sides` (No real version: turtle) | turtle, simulation |
| Random Color Row | MP | U06 turtle format (companion asserts the color sequence `rgrb`, 16 pen-down moves, closure): `random.seed(4)`; four side-30 squares, each colored from `random.choice("rgb")` (r, g, r, b → red/green/red/blue via `if`/`elif`/`else`), pen-up `forward(30)` after each, then pen-up `backward(120)` (closed) (No real version: turtle) | turtle, decisions |
| Challenge: Random Password | S | seed 4, `length` picks from `"abcdefghijkmnpqrstuvwxyz23456789"` → `rvg38j` (real version reads the length 6) | games, text |

Teacher-notes: reseeding per total in the histogram is the same as tallying ONE 36-pair sample.

## U09 — Strings

**Rungs (lesson):** (1) split `u09l003` into positive indexing, then negative indexing (one idea
each); (2) open-ended slices `word[:3]` and `word[3:]`; (3) the reversing slice `word[::-1]`;
(4) before `u09l017` (palindrome): split the `u09l016` lead-in; an index loop
`for i in range(len(w)): print(i, w[i])`; then comparing ONE mirror pair; the moved lead-in; `u09l017`;
(5) at `u09l012` replace the four-method chain with one method per rung (`upper` → `lower` → `strip` →
`replace`), the chain last; (6) widened methods, one rung each: `find`, `startswith`/`endswith`,
`isdigit`/`isalpha`, `"-".join("abc")`, `for word in line.split():`; (7) `no-exec` real-input cells:
read a word → palindrome; read a line → word count; read a PIN → validity.

**Shipped text to rewrite:** `u09l011` ("This unit uses only `upper`, `lower`, `strip`, and
`replace`"), `u09l037` ("the four taught methods"), U09 teacher-notes lines 6, 21–22 ("step slices are
never taught"), 47; `u09e001` intro; the headings "## Exercise 8 — Challenge" / "## Exercise 9 —
Challenge" (renumbered below).

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Word Count | C | `word_count("rockets need fuel to fly")` → 5 (`split` iteration) | text |
| Initials | C | `initials("grace brewster hopper")` → `"GBH"` (`word[0].upper()` per word) | text |
| Valid PIN | C | `is_valid_pin("4071")` → True, `"40a1"` → False, `"407"` → False (`isdigit` + `len`) | validation |
| Longest Word | MP | `longest_word("orbit rover launch pad")` → `"launch"` (first longest) | text, find-extreme |
| Sentence Palindrome | MP | `is_sentence_palindrome("Was it a car or a cat I saw")` → True (`replace`, `lower`, `[::-1]`) | text |
| Run-Length Encoding | MP | `rle("aaabcc")` → `"a3b1c2"` | encoding |
| Atbash Cipher | MP | lowercase alphabet only: `if ch in alphabet:` then `alphabet[25 - alphabet.find(ch)]`, anything else (capitals, spaces, punctuation) unchanged → `atbash("abc xyz!")` → `"zyx cba!"`, `atbash("Abc!")` → `"Ayx!"` | encoding |
| File Type | MP | `file_type("game.py")` → `"python"`, `"notes.txt"` → `"text"`, else `"other"` (`endswith`) | text |
| Word Triangle | MP | `word_triangle("CODE")` → `"C\nCO\nCOD\nCODE"` (must use `word[:i]`) | ASCII art |
| Center Text | MP | `center_text("cat", 9)` → `"   cat   "` with `left = (width - len(text)) // 2`, `right = width - len(text) - left` (so `("cat", 8)` → `"  cat   "`) | text layout |
| Letter Spacer | MP | `spaced("ROBOT")` → `"R-O-B-O-T"` (`join`) | text layout |
| Rotate Left | MP | `rotate_left("orbit")` → `"rbito"` (`word[1:] + word[0]`) | text, slices |
| Ends of a Word | MP | `ends("telescope", 3)` → `"tel...ope"` (`word[:k]`, `word[-k:]`) | text, slices |
| Spam Check | MP | `is_spammy("You WIN a prize")` → True, `"See you at noon"` → False (`"win" in text.lower()` or `"free" in …`) | validation |
| Common Letters | MP | `common_letters("thunder", "under")` → `"under"` (keep a letter if `in` the second word and not already `in` the result) | text |
| Word Box | MP | `word_box("CODE")` → `"CODE\nO  D\nD  O\nEDOC"` (first word, then `word[i] + spaces + word[-1 - i]`, then `word[::-1]`; design 006 D4's word frame) | ASCII art |
| Challenge: Word Wrap | S | `wrap("the quick brown fox jumps", 10)` → `"the quick\nbrown fox\njumps"`: greedy; a word joins the line when `len(line) + 1 + len(word) <= width`; the first word never gets a leading space; a word longer than `width` sits alone | text layout |
| Challenge: Safe Number | S | `to_number("42")` → 42, `"4x"` → -1 (`isdigit` validation; negatives are not accepted) | validation & parsing |

## Binding final exercise order (Challenges last; `More Practice: ` prefix)

- **U07 (30):** 1–7 existing core · 8 Triangle Picture · 9 Name Banner · 10 Least Common Multiple ·
  11–26 MP: Digital Root, Primes Below, Roman Numeral, Days in a Month, Weekday Name, Bar with a Default,
  Fix the Scope Bug, Fix the Missing Argument, Fix the Call Before Define, Predict the Scope, Two Totals,
  Display Temperature, Distance Apart, Clamp a Score, Star Function, Polygon Row · 27–30 Challenges:
  Euclid's GCD Tool (was 8), Prime Gate (was 9), Month Calendar, Longest Collatz.
- **U08 (20):** 1–7 existing core · 8 Die Face Art · 9 Roll Until Six · 10 Longest Heads Streak ·
  11–17 MP: Two-Dice Histogram, Pig Turn, Nim Winner, Three Heads in a Row, Average Roll, Random Polygon,
  Random Color Row · 18–20 Challenges: Highest Twenty-Sided Roll (was 8), Multiples in a Random Range
  (was 9), Random Password.
- **U09 (27):** 1–7 existing core · 8 Word Count · 9 Initials · 10 Valid PIN · 11–23 MP: Longest Word,
  Sentence Palindrome, Run-Length Encoding, Atbash Cipher, File Type, Word Triangle, Center Text, Letter
  Spacer, Rotate Left, Ends of a Word, Spam Check, Common Letters, Word Box · 24–27 Challenges:
  Alternating Case (was 8), Caesar Shift (was 9), Word Wrap, Safe Number.

No real version: U07 Ex 2 (repair), Ex 7 and the new turtle exercises (Star Function, Polygon Row),
the three U07 repairs, Predict the Scope; U08 Ex 7 (turtle walk), Random Polygon, Random Color Row;
U09 none. Every other exercise has a real program.

## Depth (D7: introduced ≥5, practiced ≥3; Phase E prints the full table)

- **U07 introduces:** `def-function`/`parameters`/`return-value` ≥27; `builtin-functions` 5 (Ex 4
  `max`/`min`, Name Banner `len`, Display Temperature `round`, Distance Apart `abs`, Clamp a Score
  `min`/`max`); `scope` 5 — an exercise earns scope credit when its spec relies on local vs. global
  names: Ex 5 (`sum_to_n`'s local total), Ex 7 (the polygon tool's parameters), Fix the Scope Bug,
  Predict the Scope, Two Totals. **U07 practices:** `import-statement`/`turtle-basics`/`turtle-drawing`
  3 (Ex 7, Star Function, Polygon Row); `error-messages` 3 (Fix the Scope Bug `NameError`, Fix the
  Missing Argument `TypeError`, Fix the Call Before Define `NameError`); `accumulator`/`running-total`/
  `loop-counter` ≥3 (Digital Root, Primes Below, Roman Numeral, Longest Collatz); `int-type`/
  `float-type`/`comment`/`naming` ≥3.
- **U08 introduces:** `random-module` ≥15. **Practices:** `float-type` 3 (Ex 5, Ex 6, Average Roll);
  `turtle-*` 3 (Ex 7, Random Polygon, Random Color Row); `comment` 3 (required in Die Face Art, Roll
  Until Six, Longest Heads Streak); `count-by-condition`/`running-total`/`accumulator` ≥3.
- **U09 introduces:** `string-index` ≥6; `string-slice` 6 (Ex 1, Sentence Palindrome, Word Triangle,
  Rotate Left, Ends of a Word, Word Box); `string-methods` ≥10; `in-operator` 5 (Ex 4, Ex 5, Atbash,
  Spam Check, Common Letters); `transform-each` ≥5; `linear-search` ≥4.

## Metadata deltas (manifest + coverage-map, identically; confirmed by Phase E's honesty scan)

Expected: U07 `practices` += `string-concat`, `nested-loops` (Triangle Picture, Month Calendar),
`elif-else`, `input`, `type-conversion`; U08 `practices` += `input`, `type-conversion`, `elif-else`,
`string-concat`, `if-statement`; U09 `practices` += `input`, `for-loop`, `range-function`,
`find-extreme` (only if ≥3 reps, else leave to fastforward).

## Phases

- **Phase B (Codex gpt-6-sol ×3, direct `codex exec` in the main checkout):** statements.
- **Phase C (Codex ×3, separate sessions):** solutions; seeded values computed by running the code and
  matching the tables; real-program fences with Sample input / Expected output; U07/U08 turtle assets
  in the U06 format.
- **Phase D (inline):** teacher-notes (incl. D9 genre notes and the rewrites above), metadata deltas.
- **Phase E (audits first, ci-local last):** toolkit AST audit of every cell, fence and turtle asset;
  the exercise-contract + fence-parity audit (plan 080's script); turtle command-trace check (Random
  Polygon 4 pen-down; Random Color Row 16 pen-down + 4 travels + `backward(120)`, colors `rgrb`; Polygon
  Row 18 pen-down + `backward(210)`; Star Function 5 pen-down); fixture/value-use audit; manifest ↔
  coverage-map diff + honesty scan; depth + genre tables; `scripts/ci-local.sh`; post-execution report.

## Out of scope

U10+ (plans 083–084); checkpoints (084); tooling.

## Plan Review

### Round 1 — verdicts (HEAD 9425125)

- `[self]` APPROVE WITH NITS.
- `[sol]` **REJECT** — U07 `scope` < 5 and turtle practice has 1 rep; shipped contradictions
  (`u09l003`, `u09l011`, `u09l037`, `u08l008`); histogram/calendar/Atbash under-specified;
  `"Never odd or even"` reuse; no U09 word frame; U07 turtle real-version rule unstated.
- `[fable]` **REJECT** — verified every seeded value and all 25 U07/U09 exercises by running them;
  blockers: `len` on a string untaught; D7 shortfalls (U07 builtin-functions, scope; U09 string-slice,
  in-operator); no shipped-text rewrite list; five lead-in-splitting anchors; Die Face under-specified;
  fixture collision; byte-exact pins for calendar/wrap/center/Atbash/U08 real inputs.
- `[glm]` pending.

### Round 1 — fold (this rewrite)

- `[FIXED]` `len` on a string taught by a U07 rung; toolkit line corrected; `u07l026` rewritten.
- `[FIXED]` depth: U07 builtin-functions 5 (Display Temperature, Distance Apart, Clamp a Score added),
  scope 5 (Predict the Scope, Two Totals; explicit counting rule), error-messages 3 (Fix the Missing
  Argument, Fix the Call Before Define added), turtle practice 3 (Star Function, Polygon Row); U09
  string-slice 6 (Rotate Left, Ends of a Word, Word Box), in-operator 5 (Spam Check, Common Letters,
  Atbash's `in`).
- `[FIXED]` shipped-text rewrite lists per unit; lead-in splits named (`u07l002`, `u07l013`/`u07l014`,
  `u08l003`, `u08l019`, `u09l016`); `u09l003` split into positive/negative; standalone `upper` rung.
- `[FIXED]` byte-exact pins: full histogram rows, full Month Calendar string + algorithm, Word Wrap
  join test, Center Text padding formula, Atbash capitals, all six die faces (`.` filler), every U08
  real-program input and output label.
- `[FIXED]` fixtures: `"Was it a car or a cat I saw"`, `days_in_month(2, 2000)`/`(2, 2100)`,
  `telescope`, `thunder`/`under` (grep-clean); Word Box added as D4's U09 word frame.
- `[FIXED]` turtle exercises (U07 and U08) carry "No real version: turtle"; U08 turtle assets use the
  U06 format with named companion asserts and command-trace expectations.
- `[FIXED]` `split` rule clarified (no subscripting the split list; string indexing of the iterated
  word is fine); step-slice note cites plan 075's authoring rule.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
