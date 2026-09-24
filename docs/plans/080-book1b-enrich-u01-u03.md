# Plan 080 — Book 1b enrichment: Units 01–03 (Output & Variables, Numbers, Decisions)

**Goal:** Apply design 006 (D3–D8) to U01–U03: gentler ladders, ASCII-art and algorithm-variant
exercises, Book 1's real-input (CP-ready) pattern, and the missing facets the audit found.

**Spec:** `docs/designs/006-book1b-enrichment.md`; audit findings (U01–U03 auditor, 2026-09-24).

## Global constraints (from design 006 + the original build)

- **Pre-function form (U01–U06):** solutions use the house form — capture each output line in a
  named variable, print it, assert it. No `def` in U01–U03 solutions.
- **One new idea per code cell** (D6). New rungs are small demos placed immediately before the cell
  that previously jumped.
- **Real-input pattern (D3):**
  - Lessons: from the point `input()` (U01 L2) and any needed conversion (`int()`, U02 L2) are
    taught, every later lesson section gets ≥1 `no-exec` code cell running the idea on real input.
  - Exercises: every exercise (old and new) ends with one line
    `**Real version:** the real program reads <what> with input() — see the solution.`
  - Solutions: every exercise gets a markdown cell `**The real program** (reads <what>):` with a
    fenced ```python block that reads stdin one value per line, computes, prints — beside the
    unchanged executable fixed-value stand-in + asserts. Solution CODE cells never call `input()`.
  - Book 1b fences are not CI-scanned (design 006 D3 enforcement boundary): every fence must use
    only concepts the unit's manifest allows; Phase E audits this.
- **ASCII art (D4)** is assertable: the picture is built as string variables (rows) and asserted.
- **Value-distinctness:** every new fixture value distinct from the unit's lesson rungs, from other
  exercises, and from shipped Book 1b content (grep before finalizing).
- **Allowed toolkit per unit** (units are fastforward, but core teaching stays taught-before-used):
  U01 = print (incl. multi-arg, `sep=`, `end=`), comments, string literals incl. escapes and
  triple-quoted strings, variables, `input()`, `+` and `*` on strings, f-strings.
  U02 adds int/float, `+ - * / // % **`, precedence/parentheses, `int()`/`float()`/`str()`,
  comparisons, booleans, f-string `:.2f`. U03 adds if/elif/else, and/or/not, nesting, chained
  comparison. No loops, lists, `round`/`max`/`min`/`len` in core U01–U03 content.
- Student notebooks: no outputs, unique cell ids, no `input()` in executed cells, stretch cells tagged.

## U01 — Output & Variables

**Rungs to insert (lesson):**
1. Lesson One, new subsection `### Printing several things` after cell `81093061275f`:
   `print("Name:", "Maya")` (comma adds a space) → `print("red", "teal", "gold", sep=" / ")` →
   `print("Loading", end="")` + `print("...done")` (two cells; `end` explained).
2. Lesson One, new subsection `### Special characters` after the string-literals block
   (`d2b67c9f7d94`): `\n` → `\t` → `\"` inside double quotes → a triple-quoted multi-line string
   printing a 3-line ASCII picture (one idea per cell).
3. Lesson Three, after the `+` joining cells (`84743c4e4b4f`): string repetition `print("=" * 12)`
   → a divider around a title (`"=" * 12`, title, `"=" * 12`).
4. Lesson Two `### Input from a person` (`67533836dd4a`): add a `no-exec` code cell
   `name = input("What is your name? ")` + `print("Hello, " + name)`; Lesson Three after the
   f-strings: a `no-exec` "real card from input" cell (two inputs, one f-string line).

**New exercises** (numbered after the existing 13; core unless noted; "MP" = More Practice):
- `ASCII Box Banner` — 3 lines: `+` + `"-" * 10` + `+`, `|` + padded title + `|`, bottom line.
- `Escape Poem` — one print with `\n` and `\t` producing an exact 3-line poem (assert the string).
- `Predict the Output` (MP) — given `print(a, b)`, `sep=`, `end=` snippets, store each predicted
  output line as a string variable; asserts check the predictions.
- `Swap Two Values` (MP) — swap two variables with a temporary variable; print both.
- `Triple-Quote Critter` (MP, ASCII) — a 4-line animal picture in one triple-quoted string.
- `Challenge: Framed Title` (stretch, ASCII) — a title framed on all sides with `*`, width set by a
  `width` variable and `"*" * width`.

## U02 — Numbers & Arithmetic

**Rungs to insert (lesson):**
1. Before `u02l008`: `print(2 + 3 * 4)` → `print((2 + 3) * 4)` (precedence and parentheses).
2. Lesson One: `print(2 ** 5)` power rung after the basic operators.
3. Before `u02l013`: `print(f"{3 + 4}")` (an expression inside f-string braces).
4. Lesson Two floats: f-string `:.2f` money formatting rung (`price = 3.5`, `f"{price:.2f}"`).
5. Lesson Two conversion: a `no-exec` cell showing `int("abc")` → ValueError (read the traceback),
   and a `no-exec` real-input cell `age = int(input("Age? "))` + next-year print.
6. Lesson Three: split `==`/`!=` out of `u02l040` into their own minimal rung (`print(8 == 8)`,
   `print(8 != 9)`) before the realistic use; add a `no-exec` digit-split cell reading the number.
7. Manifest: remove `for-loop`, `range-function`, `accumulator` from U02 `practices` (they come only
   from the borrowed `u02l050` peek, which earns no practice credit); coverage-map entry mirrors it.
   (All three stay practiced by U04/U05, so the practice-coverage anchor stays green.)

**New exercises:**
- `Coin Change` — cents → quarters/dimes/nickels/pennies with `//` and `%`.
- `Seconds to Clock` — seconds → `h:mm:ss` pieces (`//`, `%`).
- `Three-Digit Sum` — digit sum of a 3-digit number.
- `Power Pair` (MP) — square and cube with `**`.
- `Clock Arithmetic` (MP) — hour after adding hours, 12-hour clock (`%`), f-string.
- `Progress Bar` (MP, ASCII) — `"#" * filled + "-" * (10 - filled)` where `filled = score // 10`.
- `Precedence Predictions` (MP) — predict four expressions as int variables; asserts.
- `Challenge: The 1089 Trick` (stretch) — reverse a 3-digit number with digits, subtract, reverse,
  add → 1089.
- `Challenge: Receipt Line` (stretch) — two prices, total with `:.2f`.

## U03 — Decisions

**Rungs to insert (lesson):**
1. `u03l003` hook: add a one-line markdown note above it: "Preview — you will build every part of
   this by the end of the unit."
2. After `u03l029` (`not`): `print(True and False)` → `print(True or False)` truth rungs.
3. Before `u03l026` (triangle): a two-condition `and` inside `elif` rung.
4. Before `u03l043` (leap year): `print(year % 4 == 0)` → `... and year % 100 != 0` →
   `... or year % 400 == 0` (three cells), then the existing full rule.
5. New rungs: chained comparison `print(0 <= x <= 10)`; string equality is case-sensitive
   (`print("Yes" == "yes")`); a markdown Notice on `and` binding tighter than `or`.
6. `no-exec` real-input cells: L1 `score = int(input())` + if/else; L2 day-name input + weekend
   check; L3 year input + leap rule.

**New exercises:**
- `FizzBuzz for One Number` — print Fizz / Buzz / FizzBuzz / the number.
- `Largest of Three` — if/elif with `and` (no `max`).
- `Order Three Numbers` (MP) — print smallest, middle, largest.
- `Rock-Paper-Scissors Judge` (MP) — two moves → "Player 1 wins" / "Player 2 wins" / "Tie".
- `Quadrant Finder` (MP) — (x, y) → quadrant or axis.
- `Valid Triangle` (MP) — triangle inequality with `and`.
- `Traffic Light Art` (MP, ASCII) — state → 3-line lamp picture (`(R)`, `( )` …) built in variables.
- `Mood Face` (MP, ASCII) — score band → a 3-line ASCII face.
- `Challenge: Ticket Price` (stretch) — age bands × weekday/weekend.
- `Challenge: Valid Clock Time` (stretch) — chained comparisons on hour/minute.

## Phases

- **Phase A (inline):** branch; this plan; plan-review gate.
- **Phase B (Codex ×3, one per unit, parallel — distinct files):** lesson rungs + no-exec input cells
  + exercise statements (new exercises + `**Real version:**` line on every exercise).
- **Phase C (Codex ×3, SEPARATE fresh sessions):** solutions — stand-ins + asserts for new exercises,
  `**The real program**` fenced block for every exercise.
- **Phase D (inline):** teacher-notes for U01–U03 (pacing, core/MP/challenge lists, value plans,
  common mistakes for new facets); manifests + coverage-map honesty (tags for newly used concepts,
  U02 practices fix); design 006 D4 wording (string repetition is taught in U01).
- **Phase E — VERIFICATION:** `scripts/ci-local.sh` ALL GREEN; static AST/grep audit (no loops/
  lists/`def`/`max`/`len`/`round` in core U01–U03 code; bans; every fence parsed and checked against
  the unit's allowed toolkit; every exercise has a Real version line and a real-program fence);
  depth count (D7: introduces ≥5 exercises, practices ≥3 — report table); cell/page deltas;
  post-execution report.

## Out of scope

Checkpoint real-version notes (plan 084); U04+ units; tooling changes.

## Plan Review
_(4-way plan-review gate — filled before implementation.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_
