# Plan 080 — Book 1b enrichment: Units 01–03 (Output & Variables, Numbers, Decisions)

**Goal:** Apply design 006 (D3–D8) to U01–U03: gentler ladders, ASCII-art and algorithm-variant
exercises, the real-input (CP-ready) pattern, and the missing facets the audit found.

**Spec:** `docs/designs/006-book1b-enrichment.md` — D3 (repair/predict/fixed-art "No real
version", bare-`input()` fences, sample-input parity, per-lesson exemption until `input()`/`int()`
are taught) and D7 (U01–U02 thresholds 3/2) as amended in this plan's own commit; U01–U03 audit.

## Global constraints

- **Pre-function house form (U01–U06):** solutions capture each output line in a named variable,
  print it, assert it. No `def` in U01–U03.
- **One new idea per code cell** (D6). Every new rung is inserted **after the Notice/explanation
  cell that follows its anchor code cell**, never between an example and its explanation.
  **Lead-in rule:** in these notebooks a Notice cell often ends with the NEXT rung's lead-in
  sentence (e.g. `**Realistic:** …`, `**Minimal:** …`, `One twist: …`). When inserting rungs after
  such a Notice, cut that trailing lead-in out of the Notice and place it in its own markdown cell
  directly above the code cell it introduces (after the inserted rungs); each inserted rung gets its
  own one-sentence lead-in. Affected anchors: `u02l007`→`u02l008`,
  `u02l012`→`u02l013`, `u02l039`→`u02l040`, `u03l025`→`u03l026`, and `u03l021` (its
  "**Minimal:** reverse one boolean" lead-in moves down to sit above `u03l029`), and `u03l034`
  (its "**Realistic:** accept either of two exact values." lead-in moves above `u03l034a` after the
  chained-comparison rung).
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
    Fixed-art exercises that read nothing end with
    `**No real version:** this exercise prints fixed art.`
    The existing "Fixed-Value …" exercises (U01/U02/U03 Ex 8) are reframed as ordinary exercises
    with a Real version line (their stand-in already exists).
  - Solutions: after each exercise's executable stand-in cell, a markdown cell
    `**The real program** (reads <what>):` + a fenced ```python block reading stdin **one value per
    line** with **bare `input()` — no prompt text** (so stdout is exactly the stand-in's output
    lines), followed by
    `Sample input:` and `Expected output:` fenced text blocks whose values equal the stand-in's fixed
    values and asserted outputs. Solution CODE cells never call `input()`.
- **Values:** the tables below are binding. Distinctive literals (words, tuples, showcase numbers)
  are unique across shipped Book 1b; plain small integers are distinct within the unit.

## U01 — Output & Variables

**Rungs (lesson):**
1. New `### Printing several things` after Notice `f101b910dc48` (the end of the Print-output
   ladder; `3fe905d22497` keeps its example→lead-in→`79f51979aec5` sequence intact):
   (a) `print("Name:", "Maya")` — a comma adds a space;
   (b) `print("red", "teal", "gold", sep=" / ")`;
   (c) ONE cell: `print("Loading", end="")` then `print("...done")` — `end` keeps the line open.
2. New `### Special characters` after Notice `77355aa20921`: (a) `\n`; (b) `\t`; (c) `\"` inside a
   double-quoted string; (d) a triple-quoted 3-line picture (no backslashes).
3. Lesson Two `### Input from a person`: the existing markdown input snippet becomes a `no-exec`
   code cell (`name = input("Name: ")` then `print("Hello,", name)` — the comma form from rung 1;
   string `+` is not taught until Lesson Three). The second markdown `input()` snippet in
   `6b9548f7319b` (`favorite_color`) becomes a `no-exec` code cell too, and `67533836dd4a`'s intro
   sentence ("…shown as text") is rewritten to introduce runnable-at-home `no-exec` cells.
4. Lesson Three after the f-string section: `no-exec` "real card" cell (two inputs, one f-string).

**New exercises** (C = core, MP = More Practice, S = stretch):

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 14 | Comma Print | C | `club = "Origami"`, `room = "B12"` → `Club: Origami` / `Room: B12` via `print("Club:", club)` | print, variable, comment (purpose comment required) |
| 15 | Room Sign | C | `building = "West"`, `room_number = "204"` → `West Wing, Room 204` with `+` | string-concat, comment |
| 16 | Escape Poem | C | one string `"Sun comes up\nBirds sing\n\tThe end"` printed once (No real version: fixed art) | string-literal, comment |
| 17 | Predict the Output | MP | predictions for `print("A", "B")`, `print("x", "y", "z", sep="-")`, `print("Go", end="!")`+`print("Now")` → `"A B"`, `"x-y-z"`, `"Go!Now"` (No real version) | print |
| 18 | Swap Two Values | MP | `left = "pear"`, `right = "plum"` → swapped with a temporary variable → `left: plum` / `right: pear` | variable, naming |
| 19 | Fix the NameError | MP | given `favorite = "mango"` then `print(Favorite)` (NameError) → repaired `print(favorite)` → `mango` (No real version) | error-messages |
| 20 | Triple-Quote Cat | MP | rows `=^.^=` / `(   )` / ` \| \|` (no trailing spaces; the closing `"""` follows the last row directly — no trailing newline) as one triple-quoted string (No real version: fixed art) | string-literal |

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
| 11 | Coin Change | C | `cents = 83` → `Quarters: 3` / `Dimes: 0` / `Nickels: 1` / `Pennies: 3` | arithmetic, int-type, comment |
| 12 | Seconds Breakdown | C | `seconds = 4000` → `Hours: 1` / `Minutes: 6` / `Seconds: 40` (labeled lines — no `h:mm:ss` clock form, no zero padding) | arithmetic, comment |
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
5. Chained comparison `print(0 <= x <= 10)` rung, inserted after Notice `u03l034` (lead-in rule);
   the Notice `u03l034` ("we will use the `and`
   form") is rewritten to present both forms; Ex 3 accepts either.
6. `print("Yes" == "yes")` rung (case-sensitive equality), after the Notice that follows
   `u03l034a`; a Notice: `and` binds tighter than `or`.
7. `no-exec` real-input cells: L1 score → if/else; L2 day name → weekend check; L3 year → leap rule
   (the `u03l040` markdown snippet becomes one of these).

**New exercises** (nested `if` is REQUIRED where marked N):

| # | title | kind | fixture → exact output | depth |
|---|---|---|---|---|
| 12 | FizzBuzz for One Number | C | `n = 75` → `FizzBuzz` (check 15 first; other branches `Fizz`, `Buzz`, else the number itself, e.g. `7`) | if-statement, elif-else, arithmetic |
| 13 | Largest of Three | C | `14, 31, 22` → `Largest: 31` (comparisons with `and`; no `max`) | logical-ops, f-string |
| 14 | Order Three Numbers | MP | `19, 4, 11` → `4 11 19` using only comparisons, `if` and temporary-variable swaps (no loops/lists/`sorted`/`min`/`max`) | if-statement, f-string |
| 15 | Rock-Paper-Scissors Judge | MP, N | `"rock"`, `"scissors"` → `Player 1 wins` (tie first → `Tie`; else nested on player 1's move → `Player 1 wins` / `Player 2 wins`) | conditional-nesting |
| 16 | Quadrant Finder | MP, N | `x = -3`, `y = 5` → `(-3, 5) is in Quadrant II`; `(0, 0)` → `(0, 0) is the Origin`; one coordinate 0 → `(x, y) is on an axis` | conditional-nesting, f-string |
| 17 | Valid Triangle | MP | `2, 5, 9` → `Not a triangle` (valid sides → `Triangle`) | logical-ops |
| 18 | Traffic Light Art | MP | `state = "yellow"` → rows `( )` / `(Y)` / `( )`; `"red"` → `(R)` / `( )` / `( )`; `"green"` → `( )` / `( )` / `(G)` (if/elif/else) | if-statement, elif-else, string-literal |
| 19 | Mood Face | MP | `score = 72` → band 50–79 → rows `o o` / ` -` / `---`; 80+ → `^ ^` / ` -` / `(_)`; under 50 → `- -` / ` -` / `...` (no backslashes, no trailing spaces) | if-statement, elif-else |
| 20 | Challenge: Ticket Price | S, N | `age = 15`, `day = "Thursday"` (weekday) → `Ticket: $8` (under 13 → 6; 13–17 → 8 weekday / 9 weekend; 18+ → 12 / 14) | conditional-nesting, f-string |
| 21 | Challenge: Valid Clock Time | S, N | `hour = 23`, `minute = 60` → `Invalid minute` (other outcomes `Invalid hour`, `Valid time`; nested; chained comparisons) | conditional-nesting, comparison |

`conditional-nesting` reaches 5 (existing Ex 7 + 15, 16, 20, 21).
If any U03 art uses string `+`/`*`, add `string-concat` to U03 `practices` (manifest + coverage-map).

## Numbering

New core/MP exercises are inserted **before** each unit's existing Challenge exercises, and every
exercise is renumbered so Challenges stay last; statements, solutions (headings mirror) and
teacher-notes use the same final numbers. The `#` column in the tables above is provisional; the
**binding final order** is below. More Practice titles are prefixed `More Practice: `; Challenges
keep `Challenge N: ` and the `stretch` tag.

- **U01 (20):** 1–11 existing core · 12 Comma Print · 13 Room Sign · 14 Escape Poem ·
  15 MP Predict the Output · 16 MP Swap Two Values · 17 MP Fix the NameError · 18 MP Triple-Quote
  Cat · 19 Challenge 1: Two Member Badges (was 12) · 20 Challenge 2: Error Detective Card (was 13).
- **U02 (23):** 1–8 existing core · 9 Coin Change · 10 Seconds Breakdown · 11 Boolean Report ·
  12 MP Three-Digit Sum · 13 MP Power Pair · 14 MP Clock Arithmetic · 15 MP Progress Bar ·
  16 MP Box Banner · 17 MP Precedence Predictions · 18 MP Read the ValueError ·
  19 Challenge 1: Reverse Two Digits (was 9) · 20 Challenge 2: Three-Digit Places (was 10) ·
  21 Challenge 3: The 1089 Trick · 22 Challenge 4: Receipt Line · 23 Challenge 5: Framed Title.
- **U03 (21):** 1–8 existing core · 9 FizzBuzz for One Number · 10 Largest of Three ·
  11 MP Order Three Numbers · 12 MP Rock-Paper-Scissors Judge · 13 MP Quadrant Finder ·
  14 MP Valid Triangle · 15 MP Traffic Light Art · 16 MP Mood Face ·
  17 Challenge 1: Triangle Logic Puzzle (was 9) · 18 Challenge 2: Leap-Year Logic Puzzle (was 10) ·
  19 Challenge 3: Closed Sign (was 11) · 20 Challenge 4: Ticket Price · 21 Challenge 5: Valid Clock Time.

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

**Projected depth matrix** (existing exercises from a scanner pass over the current solutions +
manual attribution; "+" = new exercises from the tables):

| unit | concept (introduces) | existing | + new | projected | need |
|---|---|---|---|---|---|
| U01 | print, string-literal, variable, naming, run-program | 13 | +7 | 20 | 3 |
| U01 | f-string | 10 | 0 | 10 | 3 |
| U01 | input (real-program fences) | 0 | fences on ~14 of 20 | ~14 | 3 |
| U01 | string-concat | 2 (Ex 4, Ex 9) | +1 (Room Sign) | 3 | 3 |
| U01 | comment | 0 required | +3 (Comma Print, Room Sign, Escape Poem) | 3 | 3 |
| U01 | error-messages | 2 (Ex 6, 13) | +1 (Fix the NameError) | 3 | 3 |
| U02 | arithmetic, int-type | 8 | +9 | 17 | 3 |
| U02 | float-type | 2 (Ex 3, 8) | +2 (Read the ValueError, Receipt) | 4 | 3 |
| U02 | type-conversion | 3 (Ex 4, 7, 8) | +1 (+ every numeric fence's `int(input())`) | ≥4 | 3 |
| U02 | comparison, boolean | 1 (Ex 5) | +2 (Boolean Report, Precedence Predictions) | 3 | 3 |
| U02 practices | comment | 0 | +2 (Coin Change, Seconds Breakdown) | 2 | 2 |
| U02 practices | error-messages | 1 (Ex 7) | +1 (Read the ValueError) | 2 | 2 |
| U02 practices | string-concat | 1 | +3 (Progress Bar, Box Banner, Framed Title) | 4 | 2 |
| U03 | if-statement, elif-else | 11 / 9 | +10 | 21 / ≥17 | 5 |
| U03 | logical-ops | 5 | +2 (Largest of Three, Valid Triangle) | 7 | 5 |
| U03 | conditional-nesting | 1 (Ex 7) | +4 (RPS, Quadrant, Ticket, Clock) | 5 | 5 |
| U03 practices | f-string | 2 | +4 (Largest, Order, Quadrant, Ticket) | 6 | 3 |
| U03 practices | type-conversion, input | 1 / 0 | + numeric real-program fences | ≥10 | 3 |
| U02 practices | string-literal, naming, run-program | 9 / all / all | +13 | ≥20 | 2 |
| U03 practices | int-type, string-literal, naming | all numeric / 11 / all | +10 | ≥18 | 3 |

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
  (fixture 841); art has no backslashes.
- `[FIXED]` per-lesson input rule enumerated with exemptions; existing markdown input snippets
  converted; repair/predict → No real version; "Fixed-Value" exercises reframed.
- `[FIXED]` binding values table (grep-audited); precise D7 depth rule + pass thresholds; added
  Comma Print (in-class), Boolean Report, Fix the NameError, Read the ValueError, mandated nesting in
  RPS/Quadrant/Ticket/Clock.
- `[FIXED]` U02 manifest removal dropped (keeps design 005's demo; resolves the citation error).
- `[FIXED]` Order Three Numbers constrained; audit covers every cell and fence; Phase E fence parity.

### Round 2 — verdicts (HEAD 571cd0e)

- `[self]` APPROVE.
- `[glm]` APPROVE — all seven round-1 nits verified resolved.
- `[fable]` APPROVE WITH NITS — all 30 new exercises solved exactly under the unit toolkits; must-folds:
  spec citation (design amendments were on the 079 branch, not this base); lead-in-splitting
  anchors; prompt labels break fence parity; parameter-less art needs a no-real-version line;
  nits: `Friday`/`kiwi`/`apple` collide, cat row trailing space, unspecified branch labels, depth
  ids, numbering.
- `[sol]` **REJECT** — the same lead-in and prompt-parity issues; `91`/`kiwi`/`apple` collide and the
  732 note was a false positive (a cell-id match); Mood Face/Seconds rows underspecified; the actual
  depth matrix is missing; the U01 L1/U02 L1 exemptions are not in design D3.

### Round 2 — fold

- `[FIXED]` design 006 amended in this plan's commit (the branch is now rebased on main, which carries
  plan 079's D3 amendments): per-lesson exemption until `input()`/`int()` are taught; bare-`input()`
  fences; fixed-art "No real version" line; D7 U01–U02 thresholds 3/2.
- `[FIXED]` lead-in rule + the six affected anchors named; U01 rung 1 anchors after `f101b910dc48`.
- `[FIXED]` fixtures: cents 83 (3/0/1/3), pear/plum, mango, Thursday (all grep-clean); 732 note removed.
- `[FIXED]` every branch output specified (FizzBuzz, RPS, Traffic Light, Mood Face bands, Quadrant,
  Clock); Seconds wording; cat rows; catalog ids in the depth column.
- `[FIXED]` numbering rule (Challenges stay last); projected depth matrix table.

### Round 3 — [fable] APPROVE WITH NITS (folded)

- `[FIXED]` U01 Lesson Two input cell uses the comma form (`+` is taught in Lesson Three); second
  snippet `6b9548f7319b` converted; intro sentence rewritten.
- `[FIXED]` dropped `3fe905d22497` from the affected-anchor list; named the `u03l034` →
  `u03l034a` lead-in anchor and the rung-6 position.
- `[FIXED]` U03 fixtures varied: Mood Face 72, Valid Triangle 2/5/9 (no shared small ints).

### Round 3 — verdicts — CONSENSUS

- `[self]` APPROVE. `[glm]` APPROVE (round 2). `[fable]` APPROVE WITH NITS (folded above).
- `[sol]` APPROVE WITH NITS — all five round-2 items resolved; nit: make the depth matrix exhaustive
  over the manifests → `[FIXED]` (U02/U03 trivially-satisfied practice rows added).
- Binding final exercise numbering added (Numbering section) so statement and solution sessions agree.

**Consensus: REACHED** — cleared for implementation.

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
