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
    and `len` on a **string** (taught by a new U07 rung). Already shipped in U07: `sum(range(...))`
    (`u07l026`/`u07l027`). `sum`/`len` of lists wait for U10 (U09's `len(line.split())` is the one
    exception).
  - U08 adds: `import random`, `random.seed(4)`, `randint`, `choice` — on a `range(...)` or on a
    **string** (e.g. `choice("HT")`, taught by a new rung).
  - U09 adds: indexing (positive, then negative), slices incl. open ends and the reversing slice
    `[::-1]`, `for ch in text`, `in` on strings, `upper`/`lower`/`strip`/`replace` + the widened
    `split`, `join` on a string (`"-".join("abc")`), `find`, `startswith`/`endswith`, `isdigit`/`isalpha`.
    **`split` rule (D3):** only word iteration — `for word in line.split():` and `len(line.split())`.
    The ban is on subscripting the list that `split()` returns (`parts[0]`); indexing a *string* that
    the loop hands you (`word[0]`) is ordinary string indexing and is allowed.
    **`[::-1]`:** plan 075's authoring rule ("do not teach `s[::-1]`") is lifted from U09 on for the reversing slice ONLY (other steps such as `[::2]` stay out of the toolkit; the Phase E audit flags any step other than `-1`) — design
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
3. After the `sum_to_n` section (`u07l023`–`u07l025`): **composition** — `sum_of_squares(n)` calls a
   `square(x)` helper (the exercise Primes Below then applies the same idea to `is_prime`).
4. Built-ins section (`u07l026`–`u07l028`): a rung `print(len("banner"))` → 6 (`len` counts the
   characters of a string); rewrite the `u07l026` sentence "`len(...)` … we meet it in Unit 09" to "`len`
   counts characters in a string today and items in a list in Unit 10"; then a **default parameter**
   rung (`def rule(n, symbol="-"):` — the exercise Bar with a Default is a different function).
5. `no-exec` real-input cells: L1 read a temperature → `celsius_to_f`; L2 read n → `is_prime`;
   L3 read a Celsius value → `safe_temperature`.

**Shipped text to rewrite:** `u07l026` (above); `u07e001` intro ("Core work is Exercises 1–7.
Exercises 8–9 are optional Challenges" → the new partition); U07 teacher-notes "Challenges (8–9)" lines.

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Triangle Picture | C | `draw_triangle(3)` → `"*\n**\n***"` (one loop; each row is `"*" * i`; rows joined with `+ "\n"`) | ASCII art |
| Name Banner | C | `banner("Hi")` → `"******\n* Hi *\n******"` (width = `len(text) + 4`) | ASCII art, layout |
| Least Common Multiple | C | `lcm(4, 6)` → 12, `lcm(21, 6)` → 42 — calls `gcd` | number theory |
| Digital Root | MP | `digital_root(9875)` → 2 (9875 → 29 → 11 → 2), calling `digit_sum` | number theory |
| Primes Below | MP | `count_primes_below(100)` → 25, calling `is_prime` | number theory |
| Roman Numeral | MP | `to_roman(38)` → `"XXXVIII"`, `to_roman(14)` → `"XIV"` (1–39; a `while n > 0` loop whose body is an `if`/`elif` chain subtracting 10, 9, 5, 4, 1) | sequences & bases |
| Days in a Month | MP | `days_in_month(2, 2000)` → 29, `(2, 2100)` → 28, `(4, 2023)` → 30, `(1, 2023)` → 31 — calls `is_leap` | calendar & time |
| Weekday Name | MP | `weekday_name(0)` → `"Sunday"` … `(6)` → `"Saturday"` (0 = Sunday); `day_of_week(day, first_weekday)` = `(first_weekday + day - 1) % 7` → `day_of_week(15, 3)` → 3 | calendar & time |
| Bar with a Default | MP | `bar(5)` → `"#####"`, `bar(3, "=")` → `"==="` | ASCII art |
| Fix the Scope Bug | MP | broken (`no-exec`): `def set_total():` / `    total = 12` / `def show():` / `    print(total)` / `set_total()` / `show()` → `NameError: name 'total' is not defined`; repaired: `set_total` returns 12, `show(total)` takes it → prints `12` (No real version) | debug & repair |
| Fix the Missing Argument | MP | broken (`no-exec`): `def area(width, height):` / `    return width * height` / `print(area(5))` → `TypeError: area() missing 1 required positional argument: 'height'`; repaired `print(area(5, 3))` → `15` (No real version) | debug & repair |
| Fix the Call Before Define | MP | broken (`no-exec`): `print(triple(4))` / `def triple(n):` / `    return 3 * n` → `NameError: name 'triple' is not defined`; repaired (define first) → `12` (No real version) | debug & repair |
| Shadowed Parameter | MP | predict: `n = 10` / `def double(n):` / `    n = n * 2` / `    return n` / `print(double(3), n)` → `6 10` (the parameter `n` is a new local name; the global `n` is untouched) (No real version) | tracing, scope |
| Fresh Locals | MP | predict: `def tick():` / `    count = 0` / `    count = count + 1` / `    return count` / `print(tick(), tick())` → `1 1` (a local is created fresh on every call) (No real version) | tracing, scope |
| Predict the Scope | MP | predict: `x = 5` / `def change():` / `    x = 99` / `change()` / `print(x)` → `5` (No real version) | tracing |
| Two Totals | MP | global `total = 100`; `add_up(3)` keeps its own local `total` → returns 6; `print(add_up(3), total)` → `6 100` | scope |
| Rounded Fahrenheit | MP | `rounded_fahrenheit(21)` → `round(celsius_to_f(21))` → 70 (69.8 rounded) | composition, built-ins |
| Distance Apart | MP | `distance_apart(3, 11)` → 8, `(15, 4)` → 11 (`abs`) | built-ins |
| Clamp a Score | MP | `clamp(120)` → 100, `clamp(-5)` → 0, `clamp(64)` → 64 (`min(max(score, 0), 100)`) | built-ins |
| Star Function | MP | turtle asset: `draw_star(size)` draws a closed 5-point star (5 × `forward(size)`, `right(144)`); the script calls `draw_star(80)` (No real version: turtle) | turtle |
| Polygon Row | MP | turtle asset: `draw_polygon(sides, length)` + `polygon_row()` calling it 3 times for hexagons of side 30, pen-up `forward(70)` after each, then pen-up `backward(210)` back to the start (closed) (No real version: turtle) | turtle, composition |
| Challenge: Month Calendar | S | `month_calendar(30, 3)` RETURNS (0 = Sunday) `"Su Mo Tu We Th Fr Sa\n          1  2  3  4\n 5  6  7  8  9 10 11\n12 13 14 15 16 17 18\n19 20 21 22 23 24 25\n26 27 28 29 30"` — built with one growing `row` string (no lists): each cell is `str(d)` padded to two characters with a leading space when `d < 10` (blank cells `"  "`; no format-width specs — `:2` is never taught), cells separated by one space (`row = cell` if `row == ""` else `row + " " + cell`), a row closes when `(first_weekday + d - 1) % 7 == 6`; the last row is not padded | calendar, layout |
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
| Die Face Art | C | `die_face(n)` returns 3 rows of 3 characters, chosen by an `if`/`elif` chain on `n`, with `.` filler: 1 `...`/`.o.`/`...`; 2 `o..`/`...`/`..o`; 3 `o..`/`.o.`/`..o`; 4 `o.o`/`...`/`o.o`; 5 `o.o`/`.o.`/`o.o`; 6 `o.o`/`o.o`/`o.o` — `die_face(5)` → `"o.o\n.o.\no.o"` (real version reads the face) | ASCII art |
| Roll Until Six | C | seed 4, `randint(1, 6)` until the target face → `Rolls: 4` (real version reads the target face 6) | simulation |
| Longest Heads Streak | C | seed 4, 20 flips of `choice("HT")` (`HTHTTHHHHTTHHTTHHTHH`) → `Longest streak: 4` (real version reads the flip count 20) | simulation, counting |
| Two-Dice Histogram | MP | for each total 2..12: reseed 4, roll 36 pairs, count that total; rows `label + ":" + "#" * count`, where `label = str(total)` gets a leading space when `total < 10` (no `:2` format width) → ` 2:##` / ` 3:##` / ` 4:######` / ` 5:#####` / ` 6:####` / ` 7:###` / ` 8:#####` / ` 9:#######` / `10:#` / `11:#` / `12:` (real version reads the pair count 36) | simulation, statistics |
| Pig Turn | MP | seed 4, roll until the turn total reaches the goal or a 1 appears (`if roll == 1:` → score 0 and stop, `elif total >= goal:` → stop): rolls 2, 3, 1 → `Turn score: 0` (real version reads the goal 20) | games |
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

**Shipped text to rewrite:** `u09l008` ("Measure the sequence" — now a recall: "`len` from Unit 07"), `u09l011` ("This unit uses only `upper`, `lower`, `strip`, and
`replace`"), `u09l037` ("the four taught methods"), U09 teacher-notes lines 6, 21–22 ("step slices are
never taught"), 47; `u09e001` intro; the headings "## Exercise 8 — Challenge" / "## Exercise 9 —
Challenge" (renumbered below).

**New exercises:**

| title | kind | fixture → exact result | genre |
|---|---|---|---|
| Word Count | C | `word_count("rockets need fuel to fly")` → 5 (`split` iteration with a counter); the stand-in and real program print `f"Words: {count}"` → `Words: 5` (purpose comment required) | text |
| Initials | C | `initials("grace brewster hopper")` → `"GBH"` (`word[0].upper()` per word; purpose comment required) | text |
| Valid PIN | C | `is_valid_pin("4071")` → True, `"40a1"` → False, `"407"` → False (`if len(pin) != 4:` → False, `elif not pin.isdigit():` → False, `else` → True; purpose comment required) | validation |
| Longest Word | MP | `longest_word("nova rover launch pad")` → `"launch"` (first longest); prints `f"Longest: {word}"` → `Longest: launch` | text, find-extreme |
| Sentence Palindrome | MP | `is_sentence_palindrome("Was it a car or a cat I saw")` → True (`replace`, `lower`, `[::-1]`) | text |
| Run-Length Encoding | MP | `rle("aaabcc")` → `"a3b1c2"` | encoding |
| Atbash Cipher | MP | lowercase alphabet only: `if ch in alphabet:` then `alphabet[25 - alphabet.find(ch)]`, anything else (capitals, spaces, punctuation) unchanged → `atbash("abc xyz!")` → `"zyx cba!"`, `atbash("Abc!")` → `"Ayx!"` | encoding |
| File Type | MP | `file_type("game.py")` → `"python"`, `"notes.txt"` → `"text"`, else `"other"` (`endswith`) | text |
| Word Triangle | MP | `word_triangle("CODE")` → `"C\nCO\nCOD\nCODE"` (must use `word[:i]`) | ASCII art |
| Center Text | MP | `center_text("gnat", 10)` → `"   gnat   "` with `left = (width - len(text)) // 2`, `right = width - len(text) - left` (so `("gnat", 9)` → `"  gnat   "`) | text layout |
| Letter Spacer | MP | `spaced("ROBOT")` → `"R-O-B-O-T"` (`join`) | text layout |
| Rotate Left | MP | `rotate_left("nova")` → `"ovan"` (`word[1:] + word[0]`) | text, slices |
| Ends of a Word | MP | `ends("telescope", 3)` → `"tel...ope"` (`word[:k]`, `word[-k:]`) | text, slices |
| Spam Check | MP | `is_spammy("You WIN a prize")` → True, `"See you at noon"` → False (`"win" in text.lower()` or `"free" in …`) | validation |
| Common Letters | MP | `common_letters("thunder", "under")` → `"under"` (keep a letter if `in` the second word and not already `in` the result) | text |
| Word Box | MP | `word_box("CODE")` → `"CODE\nO  D\nD  O\nEDOC"` (first word, then `word[i] + spaces + word[-1 - i]`, then `word[::-1]`; design 006 D4's word frame) | ASCII art |
| First Vowel | MP | `first_vowel("rhythm and blues")` → 7; `for i in range(len(text))` returning `i` at the first vowel (early exit), `-1` if none (`first_vowel("rhythm")` → -1) | search |
| Has a Digit | MP | `has_digit("launch42")` → True, `has_digit("nova")` → False; return `True` at the first `ch.isdigit()` (early exit), `False` after the loop | search, validation |
| Challenge: Word Wrap | S | `wrap("the quick brown fox jumps", 10)` → `"the quick\nbrown fox\njumps"`: greedy; a word joins the line when `len(line) + 1 + len(word) <= width`; the first word never gets a leading space; a word longer than `width` sits alone | text layout |
| Challenge: Safe Number | S | `to_number("42")` → 42, `"4x"` → -1 (`isdigit` validation; negatives are not accepted) | validation & parsing |

## Binding final exercise order (Challenges last; `More Practice: ` prefix)

- **U07 (32):** 1–7 existing core · 8 Triangle Picture · 9 Name Banner · 10 Least Common Multiple ·
  11–28 MP: Digital Root, Primes Below, Roman Numeral, Days in a Month, Weekday Name, Bar with a Default,
  Fix the Scope Bug, Fix the Missing Argument, Fix the Call Before Define, Shadowed Parameter, Fresh
  Locals, Predict the Scope, Two Totals,
  Rounded Fahrenheit, Distance Apart, Clamp a Score, Star Function, Polygon Row · 29–32 Challenges:
  Euclid's GCD Tool (was 8), Prime Gate (was 9), Month Calendar, Longest Collatz.
- **U08 (20):** 1–7 existing core · 8 Die Face Art · 9 Roll Until Six · 10 Longest Heads Streak ·
  11–17 MP: Two-Dice Histogram, Pig Turn, Nim Winner, Three Heads in a Row, Average Roll, Random Polygon,
  Random Color Row · 18–20 Challenges: Highest Twenty-Sided Roll (was 8), Multiples in a Random Range
  (was 9), Random Password.
- **U09 (29):** 1–7 existing core · 8 Word Count · 9 Initials · 10 Valid PIN · 11–25 MP: Longest Word,
  Sentence Palindrome, Run-Length Encoding, Atbash Cipher, File Type, Word Triangle, Center Text, Letter
  Spacer, Rotate Left, Ends of a Word, Spam Check, Common Letters, Word Box, First Vowel, Has a Digit ·
  26–29 Challenges:
  Alternating Case (was 8), Caesar Shift (was 9), Word Wrap, Safe Number.

No real version: U07 Ex 2 (repair), Ex 7 and the new turtle exercises (Star Function, Polygon Row),
the three U07 repairs, Shadowed Parameter, Fresh Locals, Predict the Scope; U08 Ex 7 (turtle walk),
Random Polygon, Random Color Row; U09 none. Every other exercise has a real program.

## Depth (D7: introduced ≥5, practiced ≥3; Phase E prints the full table)

Rule for practiced tags: every tag kept in `practices` has ≥3 exercises that genuinely use it, named
below or pinned in the specs; Phase E's honesty scan may ADD a tag only with 3 named reps and DROPS a
shipped tag that cannot reach 3 (design 005 fastforward), recorded in the post-execution report.

- **U07 introduces:** `def-function`/`parameters`/`return-value` ≥27; `builtin-functions` 5 (Ex 4
  `max`/`min`, Name Banner `len`, Rounded Fahrenheit `round`, Distance Apart `abs`, Clamp a Score
  `min`/`max`); `scope` 5 — an exercise earns scope credit only when its answer depends on local vs.
  global names: Fix the Scope Bug, Shadowed Parameter, Fresh Locals, Predict the Scope, Two Totals.
- **U07 practices:** `import-statement`/`turtle-basics`/`turtle-drawing` 3 (Ex 7, Star Function,
  Polygon Row); `error-messages` 3 (Fix the Scope Bug `NameError`, Fix the Missing Argument
  `TypeError`, Fix the Call Before Define `NameError`); `accumulator`/`running-total`/`loop-counter` ≥3
  (Digital Root, Primes Below, Roman Numeral, Longest Collatz); `float-type` 3 (Rounded Fahrenheit's `69.8`
  before rounding, Ex 7's `360 / n` turn, Polygon Row's `360 / sides` = `60.0`); `int-type`/`comment`/`naming` ≥3.
- **U08 introduces:** `random-module` ≥15. **Practices:** `builtin-functions` 3 (shipped Ex 5 and Ex 6
  `max`/`round`, Ex 8 `max`); `float-type` 3 (Ex 5, Ex 6, Average Roll); `turtle-*` 3 (Ex 7, Random
  Polygon, Random Color Row); `comment` 3 (required in Die Face Art, Roll Until Six, Longest Heads
  Streak); `count-by-condition`/`running-total`/`accumulator` ≥3 (Two-Dice Histogram, Longest Heads
  Streak, Average Roll, Three Heads in a Row); `int-type`/`naming` ≥3. **`scope` is dropped from U08
  `practices`** — no U08 exercise's answer depends on local vs. global names (it is introduced with 5
  reps in U07).
- **U09 introduces:** `string-index` ≥6; `string-slice` 6 (Ex 1, Sentence Palindrome, Word Triangle,
  Rotate Left, Ends of a Word, Word Box); `string-methods` ≥10; `in-operator` 5 (Ex 4, Ex 5, Atbash,
  Spam Check, Common Letters); `transform-each` ≥5; `linear-search` 5 (Ex 3 Palindrome Gate's early
  `False`, Ex 6 First Matching Position, First Vowel, Has a Digit, Caesar Shift's `position` helper).
- **U09 practices:** `f-string` 3 (Ex 7, Word Count `Words: 5`, Longest Word `Longest: launch`);
  `string-concat` ≥3 (Run-Length Encoding, Atbash Cipher, Word Box, Letter Spacer's result);
  `elif-else` 3 (Ex 4, File Type, Valid PIN); `accumulator`/`count-by-condition`/`loop-counter` ≥3
  (Word Count, Run-Length Encoding, Common Letters, Spam Check); `builtin-functions` ≥3 (`len` in Valid
  PIN, Center Text, Ends of a Word); `int-type`/`type-conversion` 3 (Safe Number `int`, Run-Length
  Encoding `str(count)`, shipped Ex 1 Badge Line's `str(len(code))`); `comment` 3 (Word Count, Initials, Valid PIN);
  `naming` ≥3.

## Metadata deltas (manifest + coverage-map, identically; confirmed by Phase E's honesty scan)

- **U07** `practices` += `string-concat` (Triangle Picture, Name Banner, Month Calendar, Bar with a
  Default), `elif-else` (Days in a Month, Weekday Name, Roman Numeral's pinned `if`/`elif` chain),
  `input` and `type-conversion` (every real program — ≥20). No `nested-loops` tag (no pinned spec
  needs one).
- **U08** `practices` += `input`, `type-conversion` (every real program), `elif-else` (Die Face Art's
  pinned chain, Pig Turn's `if`/`elif`, Random Color Row), `string-concat` (Die Face Art, Two-Dice
  Histogram rows, Longest Heads Streak's flip string, Random Password), `if-statement` (Roll Until Six,
  Nim Winner, Three Heads in a Row, …), `while-loop` (Roll Until Six, Pig Turn, Three Heads in a Row);
  `practices` −= `scope`. New U07/U08 work uses no f-string (padding is explicit).
- **U09** `practices` += `input` (every real program). `for-loop`/`range-function` are already in
  `requires`; `find-extreme` is not added (one rep).

## Phases

- **Phase B (Codex gpt-6-sol ×3, direct `codex exec` in the main checkout):** statements.
- **Phase C (Codex ×3, separate sessions):** solutions; seeded values computed by running the code and
  matching the tables; real-program fences with Sample input / Expected output; U07/U08 turtle assets
  in the U06 format.
- **Phase D (inline):** teacher-notes (incl. D9 genre notes and the rewrites above), metadata deltas.
- **Phase E (audits first, ci-local last):** toolkit AST audit of every cell, fence and turtle asset;
  the exercise-contract + fence-parity audit (plan 080's script — every fence is EXECUTED with its pinned Sample input and its stdout compared to Expected output and the stand-in); turtle command-trace check (Random
  Polygon 4 pen-down; Random Color Row 16 pen-down + 4 travels + `backward(120)`, colors `rgrb` — `fake_turtle.state()` does not record colors, so the companion wraps `turtle.pencolor` with a small recording spy (as U06's ring check does) to assert the sequence; Polygon
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
- `[glm]` APPROVE WITH NITS (reviewed HEAD 9425125) — metadata deltas incomplete (U07
  input/type-conversion/f-string, U08 while-loop/f-string); `:2` format width untaught; Initials vs. the
  split rule + a typo; D7 projections below 5 (incl. `linear-search`); step-slice lift too broad; state
  fence execution in Phase E.

### Round 1 — fold (this rewrite)

- `[FIXED]` `len` on a string taught by a U07 rung; toolkit line corrected; `u07l026` rewritten.
- `[FIXED]` depth: U07 builtin-functions 5 (Rounded Fahrenheit, Distance Apart, Clamp a Score added),
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

### Round 1 — [glm] fold

- `[FIXED]` metadata deltas: U07 `elif-else`/`input`/`type-conversion` tied to their exercises; U08
  adds `while-loop`; `f-string` avoided by explicit padding.
- `[FIXED]` `:2` format width removed from Month Calendar and Two-Dice Histogram (leading-space padding
  via `str()`).
- `[FIXED]` `linear-search` (introduced in U09) reaches 5 with First Vowel and Has a Digit (U09 → 29).
- `[FIXED]` Initials/split rule, the typo, and the other D7 counts were already resolved by the
  [sol]/[fable] rewrite (split rule clarified; scope 5, builtin-functions 5, in-operator 5).
- `[FIXED]` step-slice lift is reversing-slice-only; Phase E states fence execution explicitly.

### Round 2 — verdicts (HEAD e8afccf)

- `[fable]` APPROVE WITH NITS — all round-1 blockers resolved, every output re-verified; nits: state
  practiced depth for U08/U09 and allow dropping tags; lesson rungs duplicated two exercises
  (`count_primes_below`, `bar`); `display_temperature` name reused; `len(line.split())` exception;
  `sum(range(...))` already shipped; `u09l008` becomes a recall.
- `[sol]` **REJECT** — U07 `scope` has only 3 exercises whose answer depends on scope (Ex 5, Ex 7 do
  not); proposed practice tags need 3 named reps each (`nested-loops`, `elif-else`); fixtures `cat`
  and `orbit` collide with shipped U09.

### Round 2 — fold

- `[FIXED]` scope 5 without Ex 5/Ex 7: added **Shadowed Parameter** (`6 10`) and **Fresh Locals**
  (`1 1`) (U07 → 32).
- `[FIXED]` practice tags: explicit rule (≥3 named reps or the tag is dropped); `nested-loops` removed
  from U07 deltas; `elif-else` pinned in Roman Numeral, Die Face Art, Pig Turn, Valid PIN; U09 f-string,
  comment and type-conversion reps pinned; U08 `scope` dropped (no honest reps).
- `[FIXED]` fixtures: `cat` → `gnat`, `orbit` → `nova` (grep-clean).
- `[FIXED]` lesson rungs renamed (`sum_of_squares`/`square`, `rule(n, symbol="-")`); the exercise is
  now Rounded Fahrenheit; toolkit notes `sum(range(...))` and `len(line.split())`; `u09l008` added to
  the U09 rewrite list.

### Round 3 — CONSENSUS

- `[sol]` APPROVE WITH NITS (r3) — all blockers resolved; outputs recomputed. Nits folded: U09
  `type-conversion` third rep is Badge Line's `str(len(code))`; the `rgrb` colour assertion uses a
  `pencolor` recording spy.
- `[fable]` APPROVE WITH NITS (r2, nits folded) · `[glm]` APPROVE WITH NITS (r1, nits folded) ·
  `[self]` APPROVE WITH NITS.

**Consensus reached — implementation may start after plan 081 merges.**

## Content Review

### Round 1 — verdicts (HEAD a4c6071)

- `[self]` APPROVE WITH NITS — Phase E audit 0 findings; all notebooks execute through the CI executor;
  teacher-notes value plans renumbered; the U07 60-minute-cut claim about `gcd` corrected (core Ex 10
  now needs it).
- `[fable]` APPROVE WITH NITS — blind-solved 26 exercises, ran all 68 fences, replayed the four new turtle
  solutions; findings: missing lead-in above `u08l007` (Should Fix), histogram reseeding note, predict
  starters, Pig Turn update order, Bar default convention, Challenge heading style.
- `[glm]` APPROVE WITH NITS — blind-solved 7; U08 `if-statement` delta; Month Calendar blank-cell padding
  style.
- `[sol]` **REJECT** — malformed Sample-input fence in `u09sol-ex1-real`; the U08 notes' "every non-turtle
  exercise is seeded" claim.

### Round 1 — fold

- `[FIXED]` `u09sol-ex1-real` closing fence on its own line.
- `[FIXED]` U08 notes: "every exercise that uses randomness is seeded"; reseeding-per-total equivalence.
- `[FIXED]` U08 lesson: lead-in `u08l050` above `u08l007`; heading "Choose from a range or a string".
- `[FIXED]` U07 predict starters ask for a written prediction; Bar with a Default's Real version names the
  empty-line default; Pig Turn states add-then-test.
- `[WONTFIX]` U09 "Challenge 1:" headings — the numbered form matches U04–U06 and the shipped U09 cells.
- `[WONTFIX]` Month Calendar blank padding `row + "   "` — byte-identical output.
- `[WONTFIX]` U08 `if-statement`: already declared in U08 `requires` (shipped); the honesty scan passes,
  so the planned `practices` tag is not duplicated.

## Post-Execution Report

**Status: implemented; Phase E audits clean; ci-local ALL GREEN (2026-09-24).**

- **Execution:** Codex gpt-6-sol via direct `codex exec` in the main checkout (statements and solutions in
  separate fresh sessions); branch rebased onto `main` after plan 081 merged.
- **Phase B:** rungs as planned (U07 print-only functions, early `return`, composition, `len` on a
  string, default parameter; U08 import/seed/randint rungs, `choice("HT")`, one fixed point before π;
  U09 positive/negative index, open slices, `[::-1]`, one method per rung, the widened methods, index loop
  and one mirror pair before the palindrome); every listed shipped sentence rewritten; `no-exec`
  real-input cells U07 4, U08 3, U09 3. Exercises U07 9 → 32, U08 9 → 20, U09 9 → 29 in the binding order.
- **Phase C:** stand-ins + asserts; 68 real-program fences; four new turtle solution assets with
  fake-turtle companions (the colour row uses a `pencolor` spy).
- **Phase D:** teacher-notes U07–U09 (pacing, partitions, common mistakes, D9 ideas, value plans
  renumbered); metadata deltas applied to manifests and `coverage-map.yaml` together (U07 +string-concat,
  elif-else, input, type-conversion; U08 +input, type-conversion, elif-else, string-concat, while-loop,
  −scope; U09 +input).
- **Phase E:** contract + fence-parity audit 0 findings (every fence executed); toolkit AST audit clean
  (no lists/dicts/tuple assignment; `split` never subscripted; `[::-1]` the only step slice); seeded
  values and turtle traces re-verified independently by `[fable]` and `[sol]`; `scripts/ci-local.sh`
  ALL GREEN.
- **Deltas:** 64 new exercises, ~50 new lesson cells, 4 new turtle solution assets.

