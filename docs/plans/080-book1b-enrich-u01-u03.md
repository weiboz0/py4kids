# Plan 080 — Book 1b enrichment: Units 01–03 (Output & Variables, Numbers, Decisions)

**Goal:** Apply design 006 (D3–D8) to U01–U03: gentler ladders, ASCII-art and algorithm-variant
exercises, the real-input (CP-ready) pattern, and the missing facets the audit found.

**Spec:** `docs/designs/006-book1b-enrichment.md` (as amended by plan 079: D3 repair/predict
"No real version" exemption and fence sample-input parity); U01–U03 audit (2026-09-24).

## Global constraints

- **Pre-function house form (U01–U06):** solutions capture each output line in a named variable,
  print it, assert it. No `def` in U01–U03.
- **One new idea per code cell** (D6). Every new rung is inserted **after the Notice/explanation
  cell that follows its anchor code cell**, never between an example and its explanation.
- **Per-unit allowed toolkit (core AND More Practice AND stretch AND fences):**
  - U01: `print` (incl. several arguments, `sep=`, `end=`), comments, string literals incl. escapes
    `\n` `\t` `\"` and triple-quoted strings, variables, `input()`, string `+`, f-strings.
    **No string repetition in U01** (design 006 D4: repetition is taught in U02 as a facet of
    `string-concat`, where ints are first taught).
  - U02 adds int/float, `+ - * / // % **`, precedence and parentheses, `int()`/`float()`/`str()`,
    comparisons, booleans, f-string `:.2f`, string repetition `"=" * n`.
  - U03 adds `if`/`elif`/`else`, `and`/`or`/`not`, nested `if`, chained comparison.
  - Never in U01–U03 (any cell or fence): loops, lists, `def`, `max`/`min`/`len`/`round`/`abs`/
    `sorted`, string methods, `+=`, tuple assignment, zero-padding format specs.
    Declared exception: the existing design-005 fastforward peek cell `u02l050` (unchanged).
- **ASCII art:** built as one named string variable per row (or one triple-quoted string), asserted
  exactly, printed last. **No backslashes in art** (`\_` is an invalid escape); triple-quoted art
  starts right after the opening quotes (no leading newline) unless the assert includes it.
- **Real-input pattern (D3, design 006's expansion of Book 1's mechanics):**
  - Lessons: each lesson **from the point `input()` and the needed conversion are taught** gets ≥1
    `no-exec` code cell running that lesson's idea on real input. Enumerated: U01 L1 exempt (input
    not yet taught), U01 L2 ✓, U01 L3 ✓; U02 L1 exempt (`int()` not yet taught), U02 L2 ✓, U02 L3 ✓;
    U03 L1 ✓, L2 ✓, L3 ✓. Existing markdown-fenced `input()` snippets in lessons (U01 near
    `67533836dd4a`, `u02l032`, U03 near `u03l040`) are converted into those `no-exec` code cells.
  - Exercises: every exercise ends with `**Real version:** the real program reads <what> with
    input() — see the solution.` Repair and predict-the-output exercises instead end with
    `**No real version:** this exercise fixes (or traces) code rather than reading input.`
    The existing "Fixed-Value …" exercises (U01/U02/U03 Ex 8) are reframed as ordinary exercises
    with a Real version line (their stand-in already exists).
  - Solutions: after each exercise's executable stand-in cell, a markdown cell
    `**The real program** (reads <what>):` + a fenced ```python block reading stdin **one value per
    line** (short prompt labels at most; output lines identical to the stand-in's), followed by
    `Sample input:` and `Expected output:` fenced text blocks whose values equal the stand-in's fixed
    values and asserted outputs. Solution CODE cells never call `input()`.
- **Values:** the tables below are binding. Distinctive literals (words, tuples, showcase numbers)
  are unique across shipped Book 1b; plain small integers are distinct within the unit.

## U01 — Output & Variables

**Rungs (lesson):**
1. New `### Printing several things` after Notice `3fe905d22497`:
   (a) `print("Name:", "Maya")` — a comma adds a space;
   (b) `print("red", "teal", "gold", sep=" / ")`;
   (c) ONE cell: `print("Loading", end="")` then `print("...done")` — `end` keeps the line open.
2. New `### Special characters` after Notice `77355aa20921`: (a) `\n`; (b) `\t`; (c) `\"` inside a
   double-quoted string; (d) a triple-quoted 3-line picture (no backslashes).
3. Lesson Two `### Input from a person`: the existing markdown input snippet becomes a `no-exec`
   code cell (`name = input("Name: ")` then `print("Hello, " + name)`).
4. Lesson Three after the f-string section: `no-exec` "real card" cell (two inputs, one f-string).

**New exercises** (C = core, MP = More Practice, S = stretch):

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 14 | Comma Print | C | `club = "Origami"`, `room = "B12"` → `Club: Origami` / `Room: B12` via `print("Club:", club)` | print, variable, comment (purpose comment required) |
| 15 | Room Sign | C | `building = "West"`, `room_number = "204"` → `West Wing, Room 204` with `+` | string-concat, comment |
| 16 | Escape Poem | C | one string `"Sun comes up\nBirds sing\n\tThe end"` printed once | string-literal, comment |
| 17 | Predict the Output | MP | predictions for `print("A", "B")`, `print("x", "y", "z", sep="-")`, `print("Go", end="!")`+`print("Now")` → `"A B"`, `"x-y-z"`, `"Go!Now"` (No real version) | print |
| 18 | Swap Two Values | MP | `left = "apple"`, `right = "plum"` → swapped with a temporary variable → `left: plum` / `right: apple` | variable, naming |
| 19 | Fix the NameError | MP | given `favorite = "kiwi"` then `print(Favorite)` (NameError) → repaired `print(favorite)` → `kiwi` (No real version) | error-messages |
| 20 | Triple-Quote Cat | MP | art `=^.^=` / `(   )` / ` | | ` as one triple-quoted string | string-literal |

## U02 — Numbers & Arithmetic

**Rungs (lesson):**
1. Before `u02l008`: (a) `print(2 + 3 * 4)`; (b) `print((2 + 3) * 4)`.
2. Lesson One: `print(2 ** 5)` after the basic operators.
3. Before `u02l013`: `print(f"{3 + 4}")`.
4. Lesson One: string repetition — (a) `print("=" * 12)`; (b) a divider/title/divider cell.
5. Lesson Two floats: `price = 3.5` then `print(f"{price:.2f}")`.
6. Lesson Two conversion: `no-exec` `int("abc")` ValueError (read the traceback); the existing
   `u02l032` markdown snippet becomes a `no-exec` `age = int(input("Age: "))` real-input cell.
7. Lesson Three: `print(8 == 8)` and `print(8 != 9)` as **two separate** minimal rungs; the current
   `u02l040` becomes the realistic rung; a `no-exec` digit-split cell reading the number.
8. Manifest: **unchanged** `practices` — the `u02l050` peek is design 005 §5's in-book
   demonstration of forward-reaching practices (U01 teacher-notes point to it); it stays.

**New exercises:**

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 11 | Coin Change | C | `cents = 91` → `Quarters: 3` / `Dimes: 1` / `Nickels: 1` / `Pennies: 1` | arithmetic, int-type, comment |
| 12 | Seconds Breakdown | C | `seconds = 4000` → `Hours: 1` / `Minutes: 6` / `Seconds: 40` (labeled lines, no colons/padding) | arithmetic, comment |
| 13 | Boolean Report | C | `score = 66` → `print(score >= 60)` `True`, `score == 100` `False`, `score != 0` `True` | comparison, boolean |
| 14 | Three-Digit Sum | MP | `number = 468` → `18` | arithmetic |
| 15 | Power Pair | MP | `side = 7` → `Square: 49` / `Cube: 343` | arithmetic |
| 16 | Clock Arithmetic | MP | `hour = 10`, `added = 5` → formula given: `(hour - 1 + added) % 12 + 1` → `3 o'clock` | arithmetic |
| 17 | Progress Bar | MP | `score = 38`, `filled = score // 10` → `"#" * filled + "-" * (10 - filled)` = `###-------` | string-concat, arithmetic |
| 18 | Box Banner | MP | `title = "STAR LAB"` (8 characters, given) → `+----------+` / `\| STAR LAB \|` / `+----------+` using `"-" * 10` | string-concat |
| 19 | Precedence Predictions | MP | predict `6 + 4 * 2`=14, `(6 + 4) * 2`=20, `20 // 3 % 4`=2, `2 ** 3 * 2`=16, `7 + 1 > 2 * 4`=False (No real version) | arithmetic, comparison, boolean |
| 20 | Read the ValueError | MP | given `int("6.25")` crash → repaired with `float` → `6.25` (No real version) | error-messages, float-type, type-conversion |
| 21 | Challenge: The 1089 Trick | S | `number = 841` (hundreds > ones, stated) → reverse `148`, difference `693`, reverse the difference **as three digits** (`// 100`, `// 10 % 10`, `% 10`) `396`, sum `1089`; Notice: a difference like `99` reverses as `099` → `990` | arithmetic |
| 22 | Challenge: Receipt Line | S | `2.4`, `3.15` → `Total: $5.55` via `:.2f` | float-type, f-string |
| 23 | Challenge: Framed Title | S | `title = "GO TEAM"` (7 characters, given), `width = 11` → `***********` / `* GO TEAM *` / `***********` | string-concat |

## U03 — Decisions

**Rungs (lesson):**
1. `u03l003` hook: a markdown line above it — "Preview — you will build every part of this by the
   end of the unit."
2. **Before** `u03l029` (so `and`/`or` get minimal rungs before `not`): `print(True and False)` →
   `print(True or False)` (two cells); then the existing `not` rung.
3. Before `u03l026`: an `elif` whose condition is a two-part `and`; the existing triangle cell then
   gets a Notice naming its three-way `or`.
4. Before `u03l043`: `print(year % 4 == 0)` → `print(year % 4 == 0 and year % 100 != 0)` →
   the full rule with `or year % 400 == 0` (three cells), then the existing build.
5. Chained comparison `print(0 <= x <= 10)` rung; the Notice `u03l034` ("we will use the `and`
   form") is rewritten to present both forms; Ex 3 accepts either.
6. `print("Yes" == "yes")` rung (case-sensitive equality); a Notice: `and` binds tighter than `or`.
7. `no-exec` real-input cells: L1 score → if/else; L2 day name → weekend check; L3 year → leap rule
   (the `u03l040` markdown snippet becomes one of these).

**New exercises** (nested `if` is REQUIRED where marked N):

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | FizzBuzz for One Number | C | `n = 75` → `FizzBuzz` (check 15 first) | if/elif, arithmetic |
| 13 | Largest of Three | C | `14, 31, 22` → `Largest: 31` (comparisons with `and`; no `max`) | logical-ops, f-string |
| 14 | Order Three Numbers | MP | `19, 4, 11` → `4 11 19` using only comparisons, `if` and temporary-variable swaps (no loops/lists/`sorted`/`min`/`max`) | if-statement, f-string |
| 15 | Rock-Paper-Scissors Judge | MP, N | `"rock"`, `"scissors"` → `Player 1 wins` (tie first; nested on player 1's move) | conditional-nesting |
| 16 | Quadrant Finder | MP, N | `x = -3`, `y = 5` → `(-3, 5) is in Quadrant II`; spec also defines `Origin` and `On an axis` | conditional-nesting, f-string |
| 17 | Valid Triangle | MP | `3, 4, 8` → `Not a triangle` | logical-ops |
| 18 | Traffic Light Art | MP | `state = "yellow"` → rows `( )` / `(Y)` / `( )` chosen by if/elif | if/elif, string-literal |
| 19 | Mood Face | MP | `score = 66` (50–79 band) → 3-row neutral face (no backslashes) | if/elif |
| 20 | Challenge: Ticket Price | S, N | `age = 15`, `day = "Friday"` (weekday) → `Ticket: $8` (under 13 → 6; 13–17 → 8 weekday / 9 weekend; 18+ → 12 / 14) | conditional-nesting, f-string |
| 21 | Challenge: Valid Clock Time | S, N | `hour = 23`, `minute = 60` → `Invalid minute` (nested; chained comparisons) | conditional-nesting, comparison |

`conditional-nesting` reaches 5 (existing Ex 7 + 15, 16, 20, 21).
If any U03 art uses string `+`/`*`, add `string-concat` to U03 `practices` (manifest + coverage-map).

## Depth rule (D7, made precise for this plan)

Counted per exercise over its stand-in code **and** its real-program fence.
Concept attribution: scanner `detect()` for detectable concepts; heuristics for manual ones —
`variable`/`naming`/`print`/`run-program`: any exercise with code; `comment`: the exercise requires a
purpose comment; `error-messages`: repair exercises; `input`: a real-program fence reads `input()`;
`int-type`: integer literals/`int()`; `conditional-nesting`: an `If` nested inside an `If`.
**Pass rule:** U01–U02 (fragile-intro exception of D7): every introduced concept ≥3 exercises,
every practiced concept ≥2. U03: introduced ≥5, practiced ≥3. Forward-reaching design-005 practices
(`for-loop`, `range-function`, `accumulator` in U02) are exempt. Phase E prints the table; any
shortfall is fixed before the content gate.

## Phases

- **Phase B (Codex ×3, one per unit, parallel):** lesson rungs + no-exec input cells + exercise
  statements (new exercises from the tables + Real version / No real version line on every exercise).
  Each session greps shipped Book 1b before finalizing any fixture it had to adjust.
- **Phase C (Codex ×3, SEPARATE fresh sessions):** solutions — stand-ins + asserts for the new
  exercises; real-program fence + Sample input + Expected output after every exercise.
- **Phase D (inline):** teacher-notes U01–U03 (pacing incl. the 60-minute cut, core/MP/challenge
  lists, value plans, common mistakes: triple-quote leading newline, `end=`, precedence, `==` vs `=`,
  chained comparisons); manifests + coverage-map honesty; design 006 D7 note that the U01–U02
  thresholds are 3/2.
- **Phase E — VERIFICATION:**
  1. `scripts/ci-local.sh` ALL GREEN.
  2. Static AST audit of **every** code cell and fenced python block in U01–U03 (lesson, exercises,
     solutions; core, MP, stretch) against the per-unit allowed toolkit (only `u02l050` exempt).
  3. **Fence parity:** extract each real-program fence, run it with its `Sample input` as stdin,
     compare stdout to its `Expected output`, and check `Expected output` equals the stand-in's
     asserted output lines; every exercise has either a Real version line + fence or a
     No real version line (and no fence).
  4. Depth table (rule above) — all pass.
  5. Cell/page deltas; post-execution report.

## Out of scope

Checkpoint real-version notes (plan 084); U04+ units; tooling changes.

## Plan Review

### Round 1 — verdicts (HEAD d00f72b)

- `[self]` APPROVE WITH NITS — U01 `"=" * 12` uses an int before U02.
- `[fable]` APPROVE WITH NITS — seven must-folds: Seconds-to-Clock padding impossible in U02;
  Clock Arithmetic `% 12` → 0; 1089 trick needs hundreds > ones + three-digit reversal; no
  backslashes in art; width-dependent frames need `len` unless paired; per-lesson input rule
  inconsistent (+ convert existing markdown snippets, No-real-version for repair/predict);
  no values plan; depth gaps (U02 comparison/boolean, U01 in-class comma print, U03 nesting).
- `[glm]` APPROVE WITH NITS — wrong practice-anchor citation; the U02 removal kills design 005's
  only in-book fastforward demo; U03 string-concat tag; audit scope must cover all cells; D7 pass
  rule must be stated; statement toolkit guidance.
- `[sol]` **REJECT** — `end=` demo must be one cell; `==`/`!=` separate rungs; anchors must follow
  the Notice cells; U01 repetition contradicts design D4 (keep it in U02; don't edit the spec
  mid-implementation); Order Three Numbers unconstrained; D7 matrix + values table missing;
  Phase E needs fence stdin→stdout parity.

### Round 1 — fold (this rewrite)

- `[FIXED]` string repetition stays in U02 (design D4); U01 art uses literals/escapes/triple quotes;
  Box Banner and Framed Title moved to U02 with given title/width pairings (no `len`).
- `[FIXED]` `end=` demo is one cell; `==`/`!=` are two rungs; all anchors follow Notice cells
  (`3fe905d22497`, `77355aa20921`, and the U03 `and`/`or` rungs now go **before** `u03l029`).
- `[FIXED]` Seconds Breakdown uses labeled lines; Clock Arithmetic gives the `(h-1+d) % 12 + 1`
  formula; 1089 Trick states hundreds > ones and three-digit reversal with the 99 Notice
  (fixture 841, since 732 already appears in U01–U03); art has no backslashes.
- `[FIXED]` per-lesson input rule enumerated with exemptions; existing markdown input snippets
  converted; repair/predict → No real version; "Fixed-Value" exercises reframed.
- `[FIXED]` binding values table (grep-audited); precise D7 depth rule + pass thresholds; added
  Comma Print (in-class), Boolean Report, Fix the NameError, Read the ValueError, mandated nesting in
  RPS/Quadrant/Ticket/Clock.
- `[FIXED]` U02 manifest removal dropped (keeps design 005's demo; resolves the citation error).
- `[FIXED]` Order Three Numbers constrained; audit covers every cell and fence; Phase E fence parity.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
